import hashlib
from pathlib import Path

import httpx
import pytest

from pyflowdroid import installer
from pyflowdroid.discovery import load_installation
from pyflowdroid.errors import ChecksumMismatchError, DownloadError
from pyflowdroid.models import Installation

JAR = b"flowdroid jar bytes"
ANDROID = b"android jar bytes"
SOURCES_SINKS = b"<a: void b()> -> _SOURCE_\n"


def _metadata(release: str) -> bytes:
    return f"<metadata><versioning><release>{release}</release></versioning></metadata>".encode()


def _routes(version: str, tag: str) -> dict[str, tuple[int, bytes]]:
    jar_url = (
        f"{installer.MAVEN_URL}/{version}/soot-infoflow-cmd-{version}-jar-with-dependencies.jar"
    )
    return {
        f"{installer.MAVEN_URL}/maven-metadata.xml": (200, _metadata(version)),
        jar_url: (200, JAR),
        f"{jar_url}.sha1": (200, hashlib.sha1(JAR, usedforsecurity=False).hexdigest().encode()),
        f"{installer.FLOWDROID_RAW_URL}/{tag}/{installer.SOURCES_SINKS_PATH}": (200, SOURCES_SINKS),
        f"{installer.ANDROID_PLATFORMS_RAW_URL}/android-36/android.jar": (200, ANDROID),
    }


class _Recorder:
    def __init__(self, routes: dict[str, tuple[int, bytes]]) -> None:
        self.routes = routes
        self.requested: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        self.requested.append(url)
        status, content = self.routes.get(url, (404, b""))
        return httpx.Response(status, content=content)

    def client(self) -> httpx.Client:
        return httpx.Client(transport=httpx.MockTransport(self))


def test_install_downloads_everything_and_records_it(home: Path) -> None:
    recorder = _Recorder(_routes("2.15.1", "v2.15.1"))
    progress: list[tuple[str, int, int | None]] = []

    installation = installer.install_using(
        recorder.client(), home, lambda *update: progress.append(update)
    )

    assert installation == load_installation(home)
    assert installation.flowdroid_version == "2.15.1"
    assert installation.flowdroid_jar.read_bytes() == JAR
    assert installation.sources_sinks.read_bytes() == SOURCES_SINKS
    assert installation.android_jar.read_bytes() == ANDROID
    assert ("FlowDroid 2.15.1", len(JAR), len(JAR)) in progress


def test_install_skips_what_is_already_there(home: Path) -> None:
    routes = _routes("2.15.1", "v2.15.1")
    installer.install_using(_Recorder(routes).client(), home, lambda *_: None)
    again = _Recorder(routes)

    installer.install_using(again.client(), home, lambda *_: None)

    assert again.requested == [f"{installer.MAVEN_URL}/maven-metadata.xml"]


def test_install_finds_the_short_tag_of_a_dot_zero_release(home: Path) -> None:
    recorder = _Recorder(_routes("2.15.0", "v2.15"))

    installation = installer.install_using(recorder.client(), home, lambda *_: None)

    assert installation.sources_sinks.read_bytes() == SOURCES_SINKS


def test_install_rejects_a_jar_with_the_wrong_checksum(home: Path) -> None:
    routes = _routes("2.15.1", "v2.15.1")
    sha1_url = next(url for url in routes if url.endswith(".sha1"))
    routes[sha1_url] = (200, b"0" * 40)

    with pytest.raises(ChecksumMismatchError, match="SHA-1"):
        installer.install_using(_Recorder(routes).client(), home, lambda *_: None)

    assert not list(home.rglob("*.jar"))


def test_install_without_a_sources_sinks_list(home: Path) -> None:
    routes = _routes("2.15.1", "v9.9.9")

    with pytest.raises(DownloadError, match="No sources and sinks list"):
        installer.install_using(_Recorder(routes).client(), home, lambda *_: None)


def test_install_reports_http_errors(home: Path) -> None:
    routes = _routes("2.15.1", "v2.15.1")
    android_url = next(url for url in routes if url.endswith("android.jar"))
    routes[android_url] = (503, b"")

    with pytest.raises(DownloadError, match="HTTP 503"):
        installer.install_using(_Recorder(routes).client(), home, lambda *_: None)


def test_install_reports_network_errors(home: Path) -> None:
    def unreachable(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no network", request=request)

    client = httpx.Client(transport=httpx.MockTransport(unreachable))

    with pytest.raises(DownloadError, match="no network"):
        installer.install_using(client, home, lambda *_: None)


def test_install_reports_network_errors_while_downloading(home: Path) -> None:
    routes = _routes("2.15.1", "v2.15.1")
    recorder = _Recorder(routes)

    def flaky(request: httpx.Request) -> httpx.Response:
        if str(request.url).endswith("android.jar"):
            raise httpx.ReadTimeout("too slow", request=request)
        return recorder(request)

    client = httpx.Client(transport=httpx.MockTransport(flaky))

    with pytest.raises(DownloadError, match="too slow"):
        installer.install_using(client, home, lambda *_: None)


@pytest.mark.parametrize("metadata", [b"<metadata/>", b"<metadata><versioning/></metadata>"])
def test_latest_version_needs_a_release(metadata: bytes) -> None:
    routes = {f"{installer.MAVEN_URL}/maven-metadata.xml": (200, metadata)}

    with pytest.raises(DownloadError, match="did not report"):
        installer.latest_flowdroid_version(_Recorder(routes).client())


def test_install_uses_the_home_folder(
    home: Path, installation: Installation, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[Path] = []

    def install_using(
        client: httpx.Client, location: Path, progress: installer.Progress
    ) -> Installation:
        progress("label", 1, None)
        calls.append(location)
        return installation

    monkeypatch.setattr(installer, "install_using", install_using)

    assert installer.install() == installation
    assert calls == [home]


def test_latest_version_reports_http_errors() -> None:
    with pytest.raises(DownloadError, match="HTTP 404"):
        installer.latest_flowdroid_version(_Recorder({}).client())
