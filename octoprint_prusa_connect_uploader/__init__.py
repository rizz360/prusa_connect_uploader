import octoprint.plugin
import requests
from PIL import Image
from io import BytesIO
import hashlib
import uuid
from octoprint.webcams import get_default_webcam
from octoprint.util import RepeatedTimer

__plugin_name__ = "Prusa Connect Uploader"
__plugin_version__ = "1.0.6"
__plugin_pythoncompat__ = ">=3,<4"


class OctoprintPrusaConnectUploaderPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.TemplatePlugin,
):
    def __init__(self):
        self.timer = None

    def initialize(self):
        # nothing to initialize beyond defaults
        pass

    def on_after_startup(self):
        self._logger.info("PrusaConnect Uploader started!")
        self.check_settings_and_start_loop()

    def get_settings_defaults(self):
        return {
            "upload_interval": 10,
            "prusa_connect_url": "https://connect.prusa3d.com/c/snapshot",
            "token": "",
            "fingerprint": None,
        }

    def on_settings_save(self, data):
        super().on_settings_save(data)
        self.check_settings_and_start_loop()

    def is_api_protected(self):
        return True

    def check_settings_and_start_loop(self):
        token = self._settings.get(["token"])
        if token:
            if not self._settings.get(["fingerprint"]):
                self._settings.set(["fingerprint"], self.generate_fingerprint())
                self._settings.save()
            self.start_upload_loop()
        else:
            self._logger.info("Token not set. Upload loop will not start.")
            self.stop_upload_loop()

    def generate_fingerprint(self):
        device_id = str(uuid.getnode()).encode("utf-8")
        return hashlib.sha256(device_id).hexdigest()

    def capture_image(self):
        """
        Capture a snapshot image using OctoPrint's new WebcamProvider API.
        """
        try:
            # Obtain default webcam provider
            webcam = get_default_webcam(
                settings=self._settings, plugin_manager=self._plugin_manager
            )
            if not webcam:
                raise RuntimeError("No default webcam available")
            # The compatibility layer provides the actual snapshot URL
            compat = getattr(webcam.config, "compat", None)
            snapshot_url = getattr(compat, "snapshot", None) if compat else None
            if not snapshot_url:
                # Fallback to any display snapshot URL if set
                snapshot_url = getattr(webcam.config, "snapshotDisplay", None)
            if not snapshot_url:
                raise RuntimeError("Default webcam has no snapshot URL configured")
            response = requests.get(snapshot_url)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except Exception as e:
            self._logger.error(f"Error capturing image: {e}")
            return None

    def upload_to_prusa_connect(self, image):
        prusa_connect_url = self._settings.get(["prusa_connect_url"])
        token = self._settings.get(["token"])
        fingerprint = self._settings.get(["fingerprint"])

        headers = {
            "Token": token,
            "Fingerprint": fingerprint,
            "Content-Type": "image/jpeg",
        }

        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format="JPEG")
        try:
            response = requests.put(
                prusa_connect_url,
                headers=headers,
                data=img_byte_arr.getvalue(),
            )
            if response.status_code in (401, 403):
                self._logger.error(
                    "Unauthorized or Forbidden response received. Stopping plugin."
                )
                self.stop_upload_loop()
                return
            response.raise_for_status()
            self._logger.debug("Image uploaded successfully.")
        except requests.exceptions.RequestException as e:
            self._logger.error(f"Failed to upload image: {e}")

    def start_upload_loop(self):
        interval = self._settings.get_int(["upload_interval"])
        if self.timer:
            self.stop_upload_loop()
        # RepeatedTimer uses a daemon thread by default
        self.timer = RepeatedTimer(interval, self.upload_loop)
        self.timer.start()

    def stop_upload_loop(self):
        if self.timer:
            try:
                self.timer.cancel()
            except Exception:
                pass
            self.timer = None

    def upload_loop(self):
        image = self.capture_image()
        if image:
            self.upload_to_prusa_connect(image)

    def on_shutdown(self):
        self.stop_upload_loop()

    def get_template_configs(self):
        return [
            dict(
                type="settings",
                custom_bindings=False,
                template="prusa_connect_uploader_settings.jinja2",
            )
        ]

    def get_update_information(self):
        return {
            "prusa_connect_uploader": {
                "displayName": self._plugin_name,
                "displayVersion": self._plugin_version,
                "type": "github_release",
                "user": "rizz360",
                "repo": "prusa_connect_uploader",
                "current": self._plugin_version,
                "pip": "https://github.com/rizz360/prusa_connect_uploader/archive/{target}.zip",
            }
        }


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = OctoprintPrusaConnectUploaderPlugin()
