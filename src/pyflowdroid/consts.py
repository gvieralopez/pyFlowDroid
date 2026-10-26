import pathlib

# Paths and File names
PYFLOWDROID_PATH = pathlib.Path(__file__).parent.resolve()
DEFAULT_APK_FOLDER_NAME = "apks"
ANDROID_FOLDER_NAME = "android-platforms-master"
FLOWDROID_EXEC_NAME = "soot-infoflow-cmd-2.9.0-jar-with-dependencies.jar"

# URLs
FLOWDROID_DOWNLOAD_URL = f"""https://github.com/secure-software-engineering/FlowDroid/releases/download/v2.9/{FLOWDROID_EXEC_NAME}"""
SABLE_DOWNLOAD_URL = """https://github.com/Sable/android-platforms/archive/master.zip"""

# OTHERS
DEFAULT_APK_PROVIDER = 'cubapk.com'