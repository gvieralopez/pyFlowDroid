from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest

from pyflowdroid.apk_sources import registry
from pyflowdroid.apk_sources.droidbench import DroidBench
from pyflowdroid.errors import UnknownApkSourceError
from pyflowdroid.models import ApkRef

APKS = [ApkRef(source="fake", name=f"app{index}", url=f"https://x/{index}") for index in range(3)]


class _FakeSource:
    name = "fake"
    description = "a source for tests"

    def __init__(self, client: httpx.Client) -> None:
        self.client = client

    def list_apks(self) -> Iterator[ApkRef]:
        yield from APKS

    def fetch(self, apk: ApkRef, folder: Path) -> Path:
        path = folder / f"{apk.name}.apk"
        path.write_text(apk.url)
        return path


def test_download_from_fetches_the_first_apks(tmp_path: Path) -> None:
    folder = tmp_path / "new" / "apks"

    paths = registry.download_from(_FakeSource(httpx.Client()), 2, folder)

    assert paths == [folder / "app0.apk", folder / "app1.apk"]


def test_download_by_name(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(registry.SOURCES, "fake", _FakeSource)

    assert registry.download("fake", 5, tmp_path) == [tmp_path / f"app{i}.apk" for i in range(3)]


def test_get_source_builds_the_named_source() -> None:
    client = httpx.Client()

    source = registry.get_source("droidbench", client)

    assert isinstance(source, DroidBench)


def test_get_source_lists_the_known_names_when_unknown() -> None:
    with pytest.raises(UnknownApkSourceError, match="available: droidbench"):
        registry.get_source("cubapk.com", httpx.Client())


def test_source_names() -> None:
    assert registry.source_names() == ["droidbench"]
