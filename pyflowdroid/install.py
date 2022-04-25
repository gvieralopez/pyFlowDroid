import zipfile
import os
import urllib.request
from settings import FLOWDROID_EXEC, ANDROID_FOLDER, APK_FOLDER

fd_link = """https://github.com/secure-software-engineering/FlowDroid/releases/download/v2.7.1/soot-infoflow-cmd-jar-with-dependencies.jar"""
sable_link = """https://github.com/Sable/android-platforms/archive/master.zip"""


def download_flowdroid():
    urllib.request.urlretrieve (fd_link, FLOWDROID_EXEC )

def download_android():
    urllib.request.urlretrieve (sable_link, 'master.zip')
    with zipfile.ZipFile("master.zip","r") as zip_ref:
        zip_ref.extractall(".")
    os.remove('master.zip') 
    if not ANDROID_FOLDER in os.listdir('.'):
        os.rename('android-platforms-master', ANDROID_FOLDER)
def create_apk_folder():
    if not APK_FOLDER  in os.listdir('.'):
        os.mkdir(APK_FOLDER)

if __name__ == '__main__':
    print('Downloading Flowdroid')
    download_flowdroid()
    print('Downloading Android')
    download_android()
    print('Creating Directories')
    create_apk_folder()
    print('Instalation Complete')