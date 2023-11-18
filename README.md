# Prusa Connect Uploader

This OctoPrint plugin allows users to automatically upload snapshots from their 3D printer's camera to Prusa Connect, supporting enhanced monitoring and management of 3D printing processes.

## Installation

1. In OctoPrint, navigate to **Settings** > **Plugin Manager** > **Get More**.
2. Enter the following URL for the plugin archive: <https://github.com/rizz360/prusa_connect_uploader/archive/refs/tags/1.0.2.zip>
3. Click "Install" to add the plugin to your OctoPrint instance.

## Configuration

After installation, a new tab will appear in the OctoPrint settings where you can configure the Prusa Connect Uploader plugin:

1. Go to the Prusa Connect website at `connect.prusa3d.com`.
2. Navigate to **Cameras** and click on **+ Add new other camera**.
3. Copy the provided token and paste it into the plugin's settings token field in OctoPrint.

## Usage

The plugin will begin to automatically upload snapshots at the interval specified in the settings once the token has been provided.

## Note on Webcam Functionality

The current webcam functionality utilizes parts of the OctoPrint system that have been marked as deprecated and may be removed in future releases. This could cause the webcam-related features of this plugin to break. We will endeavor to update the plugin when OctoPrint releases the new webcam API.

## Contributing

Contributions are welcome! Please submit any bug reports, feature requests, or pull requests to the repository on GitHub.

## Acknowledgments

Thanks to the OctoPrint community and Prusa Research for their support and for providing the APIs used by this plugin.
