import json
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

import pyflowdroid
from pyflowdroid.apk_sources.droidbench import RAW_URL
from pyflowdroid.cli import app
from pyflowdroid.discovery import HOME_VARIABLE

pytestmark = pytest.mark.e2e

APPS = [
    "AndroidSpecific/DirectLeak1",
    "AndroidSpecific/LogNoLeak",
    "AndroidSpecific/PrivateDataLeak1",
]


@pytest.fixture(scope="module")
def installed(tmp_path_factory: pytest.TempPathFactory) -> Path:
    location = tmp_path_factory.mktemp("home")
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv(HOME_VARIABLE, str(location))
        pyflowdroid.install()
    return location


@pytest.fixture
def home(installed: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv(HOME_VARIABLE, str(installed))
    return installed


@pytest.mark.parametrize("app_name", APPS)
def test_finds_the_documented_leaks(home: Path, tmp_path: Path, app_name: str) -> None:
    apk, expected = _download_app(app_name, tmp_path)

    result = pyflowdroid.analyze(apk)

    assert len(result.leaks) == len([flow for flow in expected if "Source" in flow])
    assert {leak.source.line for leak in result.leaks} == _lines(expected, "Source")
    assert {leak.sink.line for leak in result.leaks} == _lines(expected, "Sink")


def test_cli_reports_the_leaks_as_json(home: Path, tmp_path: Path) -> None:
    apk, _ = _download_app("AndroidSpecific/DirectLeak1", tmp_path)

    result = CliRunner().invoke(app, ["analyze", str(apk), "--json"])

    assert result.exit_code == 0
    assert json.loads(result.stdout)[0]["leaky"] is True


def test_doctor_is_happy(home: Path) -> None:
    assert pyflowdroid.environment().ready


def _download_app(name: str, folder: Path) -> tuple[Path, list[dict[str, object]]]:
    apk = folder / f"{name.rsplit('/', 1)[-1]}.apk"
    apk.write_bytes(httpx.get(f"{RAW_URL}/apk/{name}.apk", follow_redirects=True).content)
    expected = httpx.get(
        f"{RAW_URL}/projects/{name}/expected-info-flows.json", follow_redirects=True
    ).json()
    return apk, expected["expected-info-flows"]


def _lines(expected: list[dict[str, object]], kind: str) -> set[object]:
    return {flow["Line"] for flow in expected if kind in flow}
