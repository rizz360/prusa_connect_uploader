from setuptools import setup, find_packages

setup(
    name="OctoPrint-PrusaConnectUploader",
    version="1.0.2b",
    packages=find_packages(),
    install_requires=["OctoPrint", "requests", "Pillow"],
    entry_points={
        "octoprint.plugin": [
            "prusa_connect_uploader = prusa_connect_uploader"
        ],
    },
    include_package_data=True,
)
