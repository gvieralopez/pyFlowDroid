import json
from pathlib import Path

import httpx
import pytest

from pyflowdroid.apk_sources.droidbench import RAW_URL, TREE_URL, DroidBench
from pyflowdroid.errors import DownloadError
from pyflowdroid.models import ApkRef

TREE = {
    "tree": [
        {"path": "apk", "type": "tree"},
        {"path": "apk/AndroidSpecific/DirectLeak1.apk", "type": "blob"},
        {"path": "apk/Callbacks/Button1.apk", "type": "blob"},
        {"path": "projects/AndroidSpecific/DirectLeak1/app.apk", "type": "blob"},
        {"path": "apk/README.md", "type": "blob"},
    ]
}
DIRECT_LEAK = ApkRef(
    source="droidbench",
    name="AndroidSpecific/DirectLeak1",
    url=f"{RAW_URL}/apk/AndroidSpecific/DirectLeak1.apk",
)


def _client(routes: dict[str, bytes]) -> httpx.Client:
    def handle(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        return httpx.Response(200, content=routes[url]) if url in routes else httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(handle))


def test_lists_only_the_benchmark_apks() -> None:
    source = DroidBench(_client({TREE_URL: json.dumps(TREE).encode()}))

    assert [apk.name for apk in source.list_apks()] == [
        "AndroidSpecific/DirectLeak1",
        "Callbacks/Button1",
    ]
    assert next(source.list_apks()) == DIRECT_LEAK


def test_fetch_names_the_file_after_category_and_app(tmp_path: Path) -> None:
    source = DroidBench(_client({DIRECT_LEAK.url: b"apk bytes"}))

    path = source.fetch(DIRECT_LEAK, tmp_path)

    assert path == tmp_path / "AndroidSpecific-DirectLeak1.apk"
    assert path.read_bytes() == b"apk bytes"


def test_fetch_keeps_a_file_that_is_already_there(tmp_path: Path) -> None:
    existing = tmp_path / "AndroidSpecific-DirectLeak1.apk"
    existing.write_bytes(b"old")
    source = DroidBench(_client({}))

    assert source.fetch(DIRECT_LEAK, tmp_path).read_bytes() == b"old"


def test_listing_reports_http_errors() -> None:
    with pytest.raises(DownloadError, match="HTTP 404"):
        list(DroidBench(_client({})).list_apks())
