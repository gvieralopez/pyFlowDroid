import os
import logging
import zipfile
import urllib.request
from pyflowdroid.consts import (
    FLOWDROID_DOWNLOAD_URL,
    SABLE_DOWNLOAD_URL,
    DEFAULT_APK_FOLDER_NAME,
    FLOWDROID_EXEC_NAME,
    PYFLOWDROID_PATH,
)
from pathlib import Path

def download_flowdroid():
    flowdroid_path = Path(PYFLOWDROID_PATH, FLOWDROID_EXEC_NAME)
    urllib.request.urlretrieve(FLOWDROID_DOWNLOAD_URL, flowdroid_path)


def download_android():
    github_zip = "master.zip"
    urllib.request.urlretrieve(SABLE_DOWNLOAD_URL, github_zip)
    with zipfile.ZipFile(github_zip, "r") as zip_ref:
        zip_ref.extractall(PYFLOWDROID_PATH)
    os.remove(github_zip)


def create_apk_folder():
    DEFAULT_APK_PATH = Path(PYFLOWDROID_PATH, DEFAULT_APK_FOLDER_NAME)
    DEFAULT_APK_PATH.mkdir(parents=True, exist_ok=True)


def install_all():
    logging.info("Downloading Flowdroid")
    download_flowdroid()
    logging.info("Downloading Android")
    download_android()
    logging.info("Creating Directories")
    create_apk_folder()
    logging.info("Instalation Complete")
