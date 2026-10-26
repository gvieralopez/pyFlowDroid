import json
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path

import platformdirs

from pyflowdroid.errors import FlowDroidNotInstalledError, JavaNotFoundError, UnsupportedJavaError
from pyflowdroid.models import Environment, Installation, JavaRuntime

logger = logging.getLogger(__name__)

HOME_VARIABLE = "PYFLOWDROID_HOME"
MINIMUM_JAVA_VERSION = 17
MANIFEST_NAME = "installation.json"
JAVA_VERSION_TIMEOUT_SECONDS = 30

_JAVA_VERSION = re.compile(r'version "(?P<major>\d+)(?:\.(?P<minor>\d+))?')


def environment() -> Environment:
    location = home()
    return Environment(
        home=location, java=_java_or_none(), installation=_installation_or_none(location)
    )


def home() -> Path:
    configured = os.environ.get(HOME_VARIABLE)
    return Path(configured) if configured else platformdirs.user_data_path("pyflowdroid")


def find_java() -> JavaRuntime:
    executable = _java_executable()
    version = java_version(executable)
    if version < MINIMUM_JAVA_VERSION:
        raise UnsupportedJavaError(
            f"FlowDroid needs Java {MINIMUM_JAVA_VERSION} or newer, but {executable} is Java {version}"
        )
    return JavaRuntime(executable=executable, version=version)


def java_version(executable: Path) -> int:
    completed = subprocess.run(
        [str(executable), "-version"],
        capture_output=True,
        text=True,
        check=False,
        timeout=JAVA_VERSION_TIMEOUT_SECONDS,
    )
    match = _JAVA_VERSION.search(completed.stderr + completed.stdout)
    if match is None:
        raise JavaNotFoundError(f"Could not read the Java version reported by {executable}")
    major = int(match["major"])
    return int(match["minor"]) if major == 1 and match["minor"] else major


def load_installation(location: Path) -> Installation:
    manifest = location / MANIFEST_NAME
    if not manifest.is_file():
        raise FlowDroidNotInstalledError(
            f"FlowDroid is not installed in {location}; run `pyflowdroid install`"
        )
    data = json.loads(manifest.read_text())
    installation = Installation(
        flowdroid_version=data["flowdroid_version"],
        flowdroid_jar=location / data["flowdroid_jar"],
        sources_sinks=location / data["sources_sinks"],
        android_platform=data["android_platform"],
        android_jar=location / data["android_jar"],
    )
    missing = [
        path.name
        for path in (
            installation.flowdroid_jar,
            installation.sources_sinks,
            installation.android_jar,
        )
        if not path.is_file()
    ]
    if missing:
        raise FlowDroidNotInstalledError(
            f"The installation in {location} is missing {', '.join(missing)}; run `pyflowdroid install`"
        )
    return installation


def save_installation(location: Path, installation: Installation) -> None:
    data = {
        "flowdroid_version": installation.flowdroid_version,
        "flowdroid_jar": installation.flowdroid_jar.relative_to(location).as_posix(),
        "sources_sinks": installation.sources_sinks.relative_to(location).as_posix(),
        "android_platform": installation.android_platform,
        "android_jar": installation.android_jar.relative_to(location).as_posix(),
    }
    (location / MANIFEST_NAME).write_text(json.dumps(data, indent=2))


def _java_executable() -> Path:
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        found = shutil.which("java", path=str(Path(java_home) / "bin"))
        if found:
            return Path(found)
        logger.warning("JAVA_HOME (%s) has no java executable; looking on PATH", java_home)
    found = shutil.which("java")
    if found is None:
        raise JavaNotFoundError(
            f"Java was not found. Install Java {MINIMUM_JAVA_VERSION} or newer and put it on PATH "
            "or point JAVA_HOME at it"
        )
    return Path(found)


def _java_or_none() -> JavaRuntime | None:
    try:
        return find_java()
    except (JavaNotFoundError, UnsupportedJavaError):
        return None


def _installation_or_none(location: Path) -> Installation | None:
    try:
        return load_installation(location)
    except FlowDroidNotInstalledError:
        return None
