import hashlib
import logging
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

import httpx
from defusedxml import ElementTree

from pyflowdroid import net
from pyflowdroid.discovery import home, save_installation
from pyflowdroid.errors import ChecksumMismatchError, DownloadError
from pyflowdroid.models import Installation

logger = logging.getLogger(__name__)

MAVEN_URL = "https://repo1.maven.org/maven2/de/fraunhofer/sit/sse/flowdroid/soot-infoflow-cmd"
FLOWDROID_RAW_URL = "https://raw.githubusercontent.com/secure-software-engineering/FlowDroid"
SOURCES_SINKS_PATH = "soot-infoflow-android/SourcesAndSinks.txt"
ANDROID_PLATFORMS_RAW_URL = "https://raw.githubusercontent.com/Sable/android-platforms/master"
ANDROID_PLATFORM = 36
CHUNK_BYTES = 1 << 16

Progress = Callable[[str, int, int | None], None]


def install() -> Installation:
    return install_with_progress(_no_progress)


def install_with_progress(progress: Progress) -> Installation:
    with net.new_client() as client:
        return install_using(client, home(), progress)


def install_using(client: httpx.Client, location: Path, progress: Progress) -> Installation:
    version = latest_flowdroid_version(client)
    folder = location / "flowdroid" / version
    installation = Installation(
        flowdroid_version=version,
        flowdroid_jar=folder / f"soot-infoflow-cmd-{version}-jar-with-dependencies.jar",
        sources_sinks=folder / "SourcesAndSinks.txt",
        android_platform=ANDROID_PLATFORM,
        android_jar=location / "android" / f"android-{ANDROID_PLATFORM}" / "android.jar",
    )
    _fetch_flowdroid(client, installation, progress)
    _fetch_sources_sinks(client, installation, progress)
    _fetch_android_platform(client, installation, progress)
    save_installation(location, installation)
    logger.info("FlowDroid %s is ready in %s", version, location)
    return installation


def latest_flowdroid_version(client: httpx.Client) -> str:
    metadata = net.get(client, f"{MAVEN_URL}/maven-metadata.xml")
    release = ElementTree.fromstring(metadata.content).findtext("versioning/release")
    if not release:
        raise DownloadError("Maven Central did not report a FlowDroid release")
    return release.strip()


def _fetch_flowdroid(client: httpx.Client, installation: Installation, progress: Progress) -> None:
    jar = installation.flowdroid_jar
    if jar.is_file():
        logger.info("FlowDroid %s is already downloaded", installation.flowdroid_version)
        return
    url = f"{MAVEN_URL}/{installation.flowdroid_version}/{jar.name}"
    expected = net.get(client, f"{url}.sha1").text.split()[0]
    label = f"FlowDroid {installation.flowdroid_version}"
    if _download(client, url, jar, label, progress) != expected:
        jar.unlink()
        raise ChecksumMismatchError(f"{url} does not match its published SHA-1 checksum")


def _fetch_sources_sinks(
    client: httpx.Client, installation: Installation, progress: Progress
) -> None:
    destination = installation.sources_sinks
    if destination.is_file():
        return
    for tag in _release_tags(installation.flowdroid_version):
        response = net.request(client, f"{FLOWDROID_RAW_URL}/{tag}/{SOURCES_SINKS_PATH}")
        if response.is_success:
            destination.write_bytes(response.content)
            progress(destination.name, len(response.content), len(response.content))
            return
    raise DownloadError(
        f"No sources and sinks list found for FlowDroid {installation.flowdroid_version}"
    )


def _fetch_android_platform(
    client: httpx.Client, installation: Installation, progress: Progress
) -> None:
    jar = installation.android_jar
    if jar.is_file():
        logger.info("Android platform %s is already downloaded", installation.android_platform)
        return
    url = f"{ANDROID_PLATFORMS_RAW_URL}/android-{installation.android_platform}/android.jar"
    _download(client, url, jar, f"Android {installation.android_platform} platform", progress)


def _download(
    client: httpx.Client, url: str, destination: Path, label: str, progress: Progress
) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(usedforsecurity=False)
    with TemporaryDirectory(dir=destination.parent) as temporary:
        partial = Path(temporary) / destination.name
        with net.stream(client, url) as response, partial.open("wb") as file:
            total = (
                int(response.headers["Content-Length"])
                if "Content-Length" in response.headers
                else None
            )
            done = 0
            for chunk in response.iter_bytes(CHUNK_BYTES):
                file.write(chunk)
                digest.update(chunk)
                done += len(chunk)
                progress(label, done, total)
        partial.replace(destination)
    return digest.hexdigest()


def _release_tags(version: str) -> list[str]:
    tags = [f"v{version}"]
    if version.endswith(".0"):
        tags.append(f"v{version.removesuffix('.0')}")
    return tags


def _no_progress(_label: str, _done: int, _total: int | None) -> None:
    pass
