import octoprint.plugin
import requests
import threading
from PIL import Image
from io import BytesIO
import hashlib
import uuid

__plugin_version__ = "1.0.4"

class OctoprintPrusaConnectUploaderPlugin(octoprint.plugin.StartupPlugin,
                                 octoprint.plugin.SettingsPlugin,
                                 octoprint.plugin.TemplatePlugin):

    def on_after_startup(self):
        self._logger.info("PrusaConnect Uploader started!")
        self.check_settings_and_start_loop()

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.check_settings_and_start_loop()

    def get_settings_defaults(self):
        return {
            "upload_interval": 10,
            "prusa_connect_url": "https://connect.prusa3d.com/c/snapshot",
            "token": "",  # Initialize token with an empty string
            "fingerprint": None  # Fingerprint will be generated if not existing
        }

    def check_settings_and_start_loop(self):
        token = self._settings.get(["token"])
        if token is not None and token != "":  # Check if token is provided and not empty
            if not self._settings.get(["fingerprint"]):
                self._settings.set(["fingerprint"], self.generate_fingerprint())
                self._settings.save()
            self.start_upload_loop()
        else:
            self._logger.info("Token not set. Upload loop will not start.")

    def get_camera_snapshot_url(self):
        """Return the snapshot URL of the default webcam."""
        try:
            import octoprint.webcam
            webcam = octoprint.webcam.get_default_webcam()
            if webcam:
                info = webcam.as_dict()
                return info.get("snapshot")
        except Exception as e:
            self._logger.warning(
                f"Failed to get snapshot URL via get_default_webcam: {e}, falling back to legacy setting"
            )
        return self._settings.global_get(["webcam", "snapshot"])

    def capture_image(self):
        snapshot_url = self.get_camera_snapshot_url()
        if snapshot_url:
            try:
                response = requests.get(snapshot_url)
                response.raise_for_status()
                return Image.open(BytesIO(response.content))
            except Exception as e:
                self._logger.error(f"Error capturing image: {e}")
                return None
        else:
            self._logger.error("No camera snapshot URL configured.")
            return None

    def generate_fingerprint(self):
        # Using the Raspberry Pi's unique hardware ID
        device_id = str(uuid.getnode()).encode('utf-8')
        return hashlib.sha256(device_id).hexdigest()

    def upload_to_prusa_connect(self, image):
        prusa_connect_url = self._settings.get(["prusa_connect_url"])
        token = self._settings.get(["token"])
        fingerprint = self._settings.get(["fingerprint"])

        headers = {
            "Token": token,
            "Fingerprint": fingerprint,
            "Content-Type": "image/jpg"
        }

        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        try:
            response = requests.put(prusa_connect_url, headers=headers, data=img_byte_arr)
            if response.status_code in [401, 403]:
                self._logger.error("Unauthorized or Forbidden response received. Stopping plugin.")
                return  # Stopping further execution
            response.raise_for_status()
            self._logger.info("Image uploaded successfully.")
        except requests.exceptions.RequestException as e:
            self._logger.error(f"Failed to upload image: {e}")

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False, template="prusa_connect_uploader_settings.jinja2")
        ]


    def start_upload_loop(self):
        interval = self._settings.get_int(["upload_interval"])
        self.timer = threading.Timer(interval, self.upload_loop)
        self.timer.daemon = True
        self.timer.start()

    def upload_loop(self):
        image = self.capture_image()
        if image:
            self.upload_to_prusa_connect(image)
        if self.timer.is_alive():
            self.start_upload_loop()

    def on_shutdown(self):
        if self.timer:
            self.timer.cancel()

    ##~~ Softwareupdate hook
    def get_update_information(self):
        return {
            "prusa_connect_uploader": {
                "displayName": "Prusa Connect Uploader",
                "displayVersion": self._plugin_version,
                "type": "github_release",
                "user": "rizz360",
                "repo": "prusa_connect_uploader",
                "current": self._plugin_version,
                "pip": "https://github.com/rizz360/prusa_connect_uploader/archive/{target_version}.zip",
            }
        }

__plugin_name__ = "Prusa Connect Uploader"
__plugin_pythoncompat__ = ">=3,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = OctoprintPrusaConnectUploaderPlugin()
