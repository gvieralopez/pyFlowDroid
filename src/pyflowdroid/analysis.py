import time
import zipfile
from os import PathLike
from pathlib import Path
from tempfile import TemporaryDirectory

from pyflowdroid.discovery import find_java, home, load_installation
from pyflowdroid.errors import InvalidApkError
from pyflowdroid.models import AnalysisResult, Installation, JavaRuntime
from pyflowdroid.results import read_outcome
from pyflowdroid.runner import run_flowdroid


def analyze(apk: str | PathLike[str]) -> AnalysisResult:
    return analyze_with(find_java(), load_installation(home()), Path(apk))


def analyze_with(java: JavaRuntime, installation: Installation, apk: Path) -> AnalysisResult:
    _check_apk(apk)
    with TemporaryDirectory() as temporary:
        output = Path(temporary) / "results.xml"
        started = time.monotonic()
        log = run_flowdroid(java, installation, apk, output)
        leaks = read_outcome(apk, log, output)
        seconds = time.monotonic() - started
    return AnalysisResult(
        apk=apk,
        leaks=leaks,
        flowdroid_version=installation.flowdroid_version,
        seconds=seconds,
        log=log,
    )


def find_apks(folder: str | PathLike[str]) -> list[Path]:
    root = Path(folder)
    if not root.is_dir():
        raise NotADirectoryError(f"{root} is not a folder")
    return sorted(path for path in root.rglob("*.apk") if path.is_file())


def _check_apk(apk: Path) -> None:
    if not apk.is_file():
        raise InvalidApkError(f"{apk} is not a file")
    if not zipfile.is_zipfile(apk):
        raise InvalidApkError(f"{apk} is not an APK (it is not a zip archive)")
