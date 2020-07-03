import os
import subprocess

from settings import FLOWDROID_EXEC, ANDROID_FOLDER, SOURCES_SINKS_FILE, APK_FOLDER, LOG_FOLDER



def run_command(cmd):
    return subprocess.getoutput(cmd)

def analyze_apk(apk_file):
    apk_path = os.path.join(APK_FOLDER, apk_file)
    command = "java -jar {} -a {} -p {} -s {}".format(FLOWDROID_EXEC, apk_path, ANDROID_FOLDER, SOURCES_SINKS_FILE)
    logs = run_command(command)
    log_path = os.path.join(LOG_FOLDER, apk_file[:-4]+'.log')
    with open(log_path, 'w') as f:
        f.write(logs)

def analyze_all():
    for apk in os.listdir(APK_FOLDER):
        analyze_apk(apk)

def parse(log_file):
    log_path = os.path.join(LOG_FOLDER, log_file)
    name = log_file[:-4]

    with open(log_path, 'r') as f:
        lines = f.readlines()

    last = lines[-1]

    if last.split()[-2]:
        try:
            errors = int(last.split()[-2])
        except:
            errors = 0
    return errors

def parse_logs():
    data = []
    for l in os.listdir(LOG_FOLDER):
        data.append(parse(l))
    print(data)


analyze_all()
parse_logs()