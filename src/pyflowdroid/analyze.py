import logging
from pathlib import Path
from pyflowdroid._cli_tools import _run_command, cli_header
from pyflowdroid.consts import (
    PYFLOWDROID_PATH,
    DEFAULT_APK_FOLDER_NAME,
    ANDROID_FOLDER_NAME,
    FLOWDROID_EXEC_NAME,
)


def _save_logs(logs: str, log_path: str):
    """
    Save a log file.

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
    Execute FlowDroid analysis in an APK file.

    Parameters
    ----------
    path : str
        Path-like object pointing to the apk file.
    sources_and_sinks : path, optional
        Defines the path to the sources and sinks file. As part of this
        library there are two sources_and_sinks files: 'large.txt' and
        'small.txt'. Both can be passed as valid values of this param.
        If not specified, the default sources and sinks file is 'small.txt'.
        A path to a custom sources and sinks file can be passed as a string too.
    save_logs : bool, optional
        Defines whether or not save raw logs from FlowDroid, by default True

    Returns
    -------
    str
        Logs with the raw output of FlowDroid analyzer.

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
    if apk_path.exists() and apk_path.is_file() and str(path).endswith(".apk"):

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

        # Log the sources and sinks file being used
        logging.info(f"Using sources and sinks from '{sns_path}'")

        # Create the flowdroid call for the given apk file
        command = f"java -jar {fd_path} -a {apk_path} -p {android_path} -s {sns_path}"

        # Execute command and get the output
        logging.info(f"Analyzing '{apk_path}'")
        logs = _run_command(command)

        # Save logs if save_logs is True
        if save_logs:
            log_path = apk_path.with_suffix(".log")
            logging.info(f"Flowdroid logs saved in {log_path}")
            _save_logs(logs, log_path)

        # Return the logs
        return logs

    # Raise execption for invalid paths
    else:
        raise ValueError(f"Address {path} does not point to a valid apk file")


def analyze_apk_folder(
    path: str = DEFAULT_APK_FOLDER_NAME,
    sources_and_sinks: str = "",
    save_logs: bool = True,
) -> dict:
    """
    Execute FlowDroid analysis in all APK files contained in a folder.

    Parameters
    ----------
    path : str, optional
        Path to the folder. By default, the default folder is 'apks'.
    sources_and_sinks : path, optional
        Defines the path to the sources and sinks file. As part of this
        library there are two sources_and_sinks files: 'large.txt' and
        'small.txt'. Both can be passed as valid values of this param.
        If not specified, the default sources and sinks file is 'small.txt'.
        A path to a custom sources and sinks file can be passed as a string too.
    save_logs : bool, optional
        Defines whether or not save raw logs from FlowDroid, by default True

    Returns
    -------
    dict
        Pairs of APK file name and its raw output of FlowDroid analyzer.

    Raises
    ------
    ValueError
        If `path` does not exist or does not point to a folder.
    ValueError
        If `sources_and_sinks` is passed and does not point to a existing file
        or is not one of default values ('small.txt' or 'large.txt').
    """

    # Create apk folder if it does not exist
    if path == DEFAULT_APK_FOLDER_NAME:
        Path(path).mkdir(parents=True, exist_ok=True)

    # Create the path object with the folder
    folder_path = Path(path)
    logging.info(f"Analyzing '{folder_path}'")

    # Check if path exists and is a folder
    if folder_path.exists() and folder_path.is_dir():

        # Retreive all apk files in the folder
        apk_paths = [
            str(apk_path)
            for apk_path in folder_path.glob("**/*.apk")
            if apk_path.is_file()
        ]
        logging.info(f"Found {len(apk_paths)} apks in '{folder_path}'")

        # Analize all apks and store their logs
        return {
            str(apk_path): analyze_apk(apk_path, sources_and_sinks, save_logs)
            for apk_path in apk_paths
        }

    # Raise execption for invalid paths
    raise ValueError(f"Address {path} does not point to a valid folder")


def analyze(
    path: str = DEFAULT_APK_FOLDER_NAME,
    sources_and_sinks: str = "",
    save_logs: bool = True,
) -> tuple[int, int, list]:
    """
    Execute FlowDroid analysis in the given path.

    Parameters
    ----------
    path : str, optional
        Path pointing the target of the analysis. If path points to an apk file,
        it returns the results of its analysis. If path points to a folder, it
        returns the overal results of analysing all apk files in that folder.
        By default, 'apks'.
    sources_and_sinks : path, optional
        Defines the path to the sources and sinks file. As part of this
        library there are two sources_and_sinks files: 'large.txt' and
        'small.txt'. Both can be passed as valid values of this param.
        If not specified, the default sources and sinks file is 'small.txt'.
        A path to a custom sources and sinks file can be passed as a string too.
    save_logs : bool, optional
        Defines whether or not save raw logs from FlowDroid, by default True

    Returns
    -------
    tuple[int, int, list]
        Tuple containing the total number of apks analized, the total number of
        leaks found and a list of the leaky apks.

    Raises
    ------
    ValueError
        If `path` does not exist.
    ValueError
        If `sources_and_sinks` is passed and does not point to a existing file
        or is not one of default values ('small.txt' or 'large.txt').
    """

    # Create the path object with the folder
    path = Path(path)

    # Check if path exists and is a folder
    if path.exists():
        if path.is_dir():
            logs = analyze_apk_folder(path, sources_and_sinks, save_logs)
        else:
            logs = {path: analyze_apk(path, sources_and_sinks, save_logs)}
        return quantify_leaks(logs)

    # Raise execption for invalid paths
    raise ValueError(f"Address {path} does not point to an existing location")


def quantify_leaks(logs: dict) -> tuple[int, int, list]:
    """
    Quantify the number of leaks in all the analyzed APK.

    Parameters
    ----------
    logs : dict
        Pairs of APK file name and its raw output of FlowDroid analyzer.

    Returns
    -------
    tuple[int, int, list]
        Tuple containing the total number of apks analized, the total number of
        leaks found and a list of the leaky apks.

    Raises
    ------
    ValueError
        If `logs` is not a dictionary.
    """

    # Check if logs is a dictionary
    if not isinstance(logs, dict):
        raise ValueError("logs must be a dictionary")

    leaky_apks = []
    total_leaks = 0
    total_apps = len(logs.keys())
    for apk, log in logs.items():
        leak_count = count_leaks_in_log_file(log)
        if leak_count != 0:
            total_leaks += leak_count
            leaky_apks.append(apk)

    return total_apps, total_leaks, leaky_apks


def count_leaks_in_log_file(log: str) -> int:
    """
    Count the number of leaks in the given logs.

    Parameters
    ----------
    logs : str
        Raw Flowdroid output

    Returns
    -------
    int
        Total number of leaks found by Flowdroid
    """

    # Parse the total count of leaks found in the logs
    # TODO: Improve this with regex
    last_line = log.split("\n")[-1]
    leaks = last_line.split()[-2]
    return int(leaks) if leaks.isdigit() else 0


def generate_report(total_apps, total_leaks, leaky_apks) -> str:
    """
    Generate a report of the analysis giving quantitative parameters.

    Parameters
    ----------
    total_apps : _type_
        Total number of apks analized
    total_leaks : _type_
        Total number of leaks found by Flowdroid
    leaky_apks : _type_
        List of the leaky apks.

    Returns
    -------
    str
        Comprehensive report of the analysis conducted
    """

    # Generate the report
    report = cli_header("PYFLOWDROID REPORT")
    report += f"Analized: {total_apps}\n"
    report += f"Leaks found: {total_leaks}\n\n"

    if len(leaky_apks):
        report += f"Leaky apks:\n"

        for lap in leaky_apks:
            report += f" - {lap}\n"
    else:
        report += "No leaky apks found\n"

    return report
