import os
from pathlib import Path
from pyflowdroid._cli_tools import _run_command
from pyflowdroid import (
    PYFLOWDROID_PATH,
    DEFAULT_APK_FOLDER_NAME,
    ANDROID_FOLDER_NAME,
    FLOWDROID_EXEC_NAME,
)


def _save_logs(logs: str, log_path: str):
    """
    Saves a log file.

    Parameters
    ----------
    logs : str
        Content of the file.
    log_path : str
        Path to log file.
    """
    with open(log_path, "w") as f:
        f.write(logs)


def analyze_apk(path: str, sources_and_sinks: str = "", save_logs: bool = True) -> str:
    """
    Executes FlowDroid analyzis in an APK file.

    Parameters
    ----------
    path : str
        Path to the apk file.
    sources_and_sinks : path, optional
        Defines the path to the sources and sinks file. As part of this
        library there are two sources_and_sinks files: 'large.txt' and
        'small.txt'. Both can be passed as valid values of this param.
        If not specified, the default sources and sinks file is 'small.txt'.
        A path to a custom sources and sinks file can be passed as a string too.
    save_logs : bool, optional
        Defines whether or not save the logs, by default True

    Returns
    -------
    str
        Raw output of Flowdroid analyzer.

    Raises
    ------
    ValueError
        If `path` does not exist or does not point to an apk file.
    ValueError
        If `sources_and_sinks` is passed and does not point to a existing file
        or is not one of default values ('small.txt' or 'large.txt').
    """

    # Convert path to pathlib object
    apk_path = Path(path)

    # Check if path exists, is a file and its extension is .apk
    if apk_path.exists() and apk_path.is_file() and path.endswith(".apk"):

        # Create the path for required resources
        fd_path = Path(PYFLOWDROID_PATH, FLOWDROID_EXEC_NAME)
        android_path = Path(PYFLOWDROID_PATH, ANDROID_FOLDER_NAME)
        sns_path = Path(sources_and_sinks)

        # If no valid path specified, use default sources and sinks file
        if not (sns_path.exists() and sns_path.is_file()):
            if sources_and_sinks == "large.txt":
                sns_path = Path(PYFLOWDROID_PATH, "sources_sinks", "large.txt")
            elif sources_and_sinks in ["small.txt", ""]:
                sns_path = Path(PYFLOWDROID_PATH, "sources_sinks", "small.txt")
            else:
                raise ValueError("Invalid sources and sinks file path.")

        # Create the flowdroid call for the given apk file
        command = f"java -jar {fd_path} -a {apk_path} -p {android_path} -s {sns_path}"

        # Execute command and get the output
        logs = _run_command(command)

        # Save logs if save_logs is True
        if save_logs:
            log_path = path.replace(".apk", ".log")
            _save_logs(logs, log_path)

        # Return the logs
        return logs

    # Raise execption for invalid paths
    else:
        raise ValueError(f"Address {path} does not point to a valid apk file")


# def analyze_all():
#     for apk in os.listdir(APK_FOLDER):
#         analyze_apk(apk)


# def parse(log_file):
#     log_path = os.path.join(LOG_FOLDER, log_file)
#     name = log_file[:-4]

#     with open(log_path, "r") as f:
#         lines = f.readlines()

#     last = lines[-1]

#     if last.split()[-2]:
#         try:
#             errors = int(last.split()[-2])
#         except:
#             errors = 0
#     return errors


# def parse_logs():
#     for l in os.listdir(LOG_FOLDER):
#         print("{} - {}".format(parse(l), l))


# analyze_all()
# parse_logs()
