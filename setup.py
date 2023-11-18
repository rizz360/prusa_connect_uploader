from setuptools import setup, find_packages

setup(
    name="OctoPrint-PrusaConnectUploader",
    version="1.0.2",
    packages=find_packages(),
    install_requires=["OctoPrint", "requests", "Pillow"],
    entry_points={
        "octoprint.plugin": [
            "prusa_connect_uploader = octoprint_prusa_connect_uploader"
        ],
    },
    include_package_data=True,
)
