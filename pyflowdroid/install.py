import os
import logging
import zipfile
import urllib.request
from pathlib import Path

from pyflowdroid import (
    FLOWDROID_DOWNLOAD_URL,
    SABLE_DOWNLOAD_URL,
    DEFAULT_APK_FOLDER_NAME,
    FLOWDROID_EXEC_NAME,
    PYFLOWDROID_PATH,
)
from pyflowdroid._cli_tools import ProgressBar


def download_flowdroid():
    """
    Fetches Flowdroid from the internet.
    """

    # Create a path object for the Flowdroid executable
    flowdroid_path = PYFLOWDROID_PATH / FLOWDROID_EXEC_NAME

    # Download executable from GitHub
    logging.info("Downloading Flowdroid")
    urllib.request.urlretrieve(FLOWDROID_DOWNLOAD_URL, flowdroid_path, ProgressBar())


def download_android():
    """
    Fetches Android from the internet.
    """

    # Download project from GitHub
    github_zip = "master.zip"
    logging.info("Downloading Android")
    urllib.request.urlretrieve(SABLE_DOWNLOAD_URL, github_zip, ProgressBar())

    # Extract project
    logging.info("Uncompressing Android")
    with zipfile.ZipFile(github_zip, "r") as zip_ref:
        zip_ref.extractall(PYFLOWDROID_PATH)
    os.remove(github_zip)


def create_apk_folder():
    """
    Creates the APK folder.
    """

    # Create a path object for the apk folder
    logging.info("Creating Directories")
    apk_path = Path(DEFAULT_APK_FOLDER_NAME)

    # Create the folder if the folder does not exist
    apk_path.mkdir(parents=True, exist_ok=True)


def install_all():
    """
    Creates default apk folder and installs Flowdroid and Android.
    """
    download_flowdroid()
    download_android()
    create_apk_folder()
    logging.info("Instalation Complete")
