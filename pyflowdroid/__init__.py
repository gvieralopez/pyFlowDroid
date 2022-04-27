import logging
import pathlib

def configure_logging():
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.INFO,
    )


configure_logging()

# Paths and File names
PYFLOWDROID_PATH = pathlib.Path(__file__).parent.resolve()
DEFAULT_APK_FOLDER_NAME = "apks"
ANDROID_FOLDER_NAME = "android-platforms-master"
FLOWDROID_EXEC_NAME = "soot-infoflow-cmd-2.9.0-jar-with-dependencies.jar"

# URLs
FLOWDROID_DOWNLOAD_URL = f"""https://github.com/secure-software-engineering/FlowDroid/releases/download/v2.9/{FLOWDROID_EXEC_NAME}"""
SABLE_DOWNLOAD_URL = """https://github.com/Sable/android-platforms/archive/master.zip"""
