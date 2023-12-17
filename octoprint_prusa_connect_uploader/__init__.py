import octoprint.plugin
import requests
import threading
from PIL import Image
from io import BytesIO
import time
import hashlib
import uuid

class OctoprintPrusaConnectUploaderPlugin(octoprint.plugin.StartupPlugin,
                                          octoprint.plugin.SettingsPlugin,
                                          octoprint.plugin.TemplatePlugin):

    def __init__(self):
        self.keep_running = True

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
            "token": None,  # User must provide this
            "fingerprint": None  # Fingerprint will be generated if not existing
        }

    def check_settings_and_start_loop(self):
        if self._settings.get(["token"]):  # Check if token is provided
            if not self._settings.get(["fingerprint"]):
                self._settings.set(["fingerprint"], self.generate_fingerprint())
                self._settings.save()
            self.start_upload_loop()
        else:
            self._logger.info("Token not set. Upload loop will not start.")

    def get_camera_snapshot_url(self):
        webcam_settings = self._settings.global_get(["webcam", "snapshot"])
        if webcam_settings:
            return webcam_settings
        else:
            self._logger.error("No camera snapshot URL configured.")
            return None

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
            return None

    @staticmethod
    def generate_fingerprint():
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
            response.raise_for_status()
            if response.status_code in [401, 403]:
                self._logger.error("Unauthorized or Forbidden response received. Stopping plugin.")
                self.keep_running = False
            else:
                self._logger.info("Image uploaded successfully.")
        except requests.exceptions.RequestException as e:
            self._logger.error(f"Failed to upload image: {e}")

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False, template="prusa_connect_uploader_settings.jinja2")
        ]

    def start_upload_loop(self):
        interval = self._settings.get_int(["upload_interval"])
        while self.keep_running:
            image = self.capture_image()
            if image:
                self.upload_to_prusa_connect(image)
            time.sleep(interval)

    def on_shutdown(self):
        self.keep_running = False

__plugin_name__ = "Prusa Connect Uploader"
__plugin_pythoncompat__ = ">=3,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = OctoprintPrusaConnectUploaderPlugin()
