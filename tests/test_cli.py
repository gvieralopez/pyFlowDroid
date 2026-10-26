import json
import runpy
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

import pyflowdroid
from pyflowdroid import cli
from pyflowdroid.errors import AnalysisFailedError, JavaNotFoundError, UnknownApkSourceError
from pyflowdroid.installer import Progress
from pyflowdroid.models import (
    AnalysisResult,
    Environment,
    Installation,
    JavaRuntime,
    Leak,
    Statement,
)

JAVA = JavaRuntime(executable=Path("/jdk/bin/java"), version=17)
SOURCE = Statement(
    method="<de.ecspride.MainActivity: void onCreate(android.os.Bundle)>",
    statement="$r4 = virtualinvoke $r2.<android.telephony.TelephonyManager: java.lang.String getDeviceId()>()",
    definition="<android.telephony.TelephonyManager: java.lang.String getDeviceId()>",
    line=27,
)
SINK = Statement(method="onCreate", statement="send", definition="", line=None)

runner = CliRunner()


def _result(apk: Path, leaks: tuple[Leak, ...]) -> AnalysisResult:
    return AnalysisResult(apk=apk, leaks=leaks, flowdroid_version="2.15.1", seconds=0.5, log="log")


@pytest.fixture
def ready(installation: Installation, monkeypatch: pytest.MonkeyPatch) -> Installation:
    monkeypatch.setattr(cli, "find_java", lambda: JAVA)
    return installation


def test_version() -> None:
    result = runner.invoke(cli.app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == f"pyflowdroid {pyflowdroid.__version__}"


def test_no_arguments_shows_the_help() -> None:
    result = runner.invoke(cli.app, [])

    assert "Usage" in result.output


def test_install_reports_progress_and_the_version(
    home: Path, installation: Installation, monkeypatch: pytest.MonkeyPatch
) -> None:
    def install_with_progress(progress: Progress) -> Installation:
        progress("FlowDroid 2.15.1", 5, 10)
        progress("FlowDroid 2.15.1", 10, 10)
        return installation

    monkeypatch.setattr(cli, "install_with_progress", install_with_progress)

    result = runner.invoke(cli.app, ["--verbose", "install"])

    assert result.exit_code == 0
    assert "FlowDroid 2.15.1 is ready" in result.stdout


def test_install_failure_exits_with_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def install_with_progress(progress: Progress) -> Installation:
        raise pyflowdroid.DownloadError("no network")

    monkeypatch.setattr(cli, "install_with_progress", install_with_progress)

    result = runner.invoke(cli.app, ["install"])

    assert result.exit_code == 1
    assert "no network" in result.stderr


def test_analyze_prints_a_report(
    tmp_path: Path, ready: Installation, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = tmp_path / "apks"
    folder.mkdir()
    (folder / "leaky.apk").write_text("x")
    clean = tmp_path / "clean.apk"
    monkeypatch.chdir(tmp_path)

    def analyze_with(java: JavaRuntime, installation: Installation, apk: Path) -> AnalysisResult:
        leaks = (Leak(source=SOURCE, sink=SINK),) if apk.name == "leaky.apk" else ()
        return _result(apk, leaks)

    monkeypatch.setattr(cli, "analyze_with", analyze_with)

    result = runner.invoke(cli.app, ["analyze", str(folder), str(clean)])

    assert result.exit_code == 0
    assert "apks/leaky.apk" in result.stdout
    assert (
        "from TelephonyManager.getDeviceId() in MainActivity.onCreate(), line 27" in result.stdout
    )
    assert "to   send in onCreate" in result.stdout


def test_analyze_prints_json(
    tmp_path: Path, ready: Installation, monkeypatch: pytest.MonkeyPatch
) -> None:
    apk = tmp_path / "app.apk"
    monkeypatch.setattr(
        cli, "analyze_with", lambda java, installation, path: _result(path, ((Leak(SOURCE, SINK),)))
    )

    result = runner.invoke(cli.app, ["analyze", str(apk), "--json"])

    data = json.loads(result.stdout)
    assert result.exit_code == 0
    assert data[0]["apk"] == str(apk)
    assert data[0]["leaky"] is True
    assert data[0]["leaks"][0]["source"]["line"] == 27
    assert "log" not in data[0]


def test_analyze_keeps_going_after_a_failure_and_exits_with_an_error(
    tmp_path: Path, ready: Installation, monkeypatch: pytest.MonkeyPatch
) -> None:
    def analyze_with(java: JavaRuntime, installation: Installation, apk: Path) -> AnalysisResult:
        if apk.name == "broken.apk":
            raise AnalysisFailedError(apk, "it broke", "log")
        return _result(apk, ())

    monkeypatch.setattr(cli, "analyze_with", analyze_with)

    result = runner.invoke(
        cli.app, ["analyze", str(tmp_path / "broken.apk"), str(tmp_path / "fine.apk")]
    )

    assert result.exit_code == 1
    assert "it broke" in result.stderr
    assert "fine.apk" in result.stdout


def test_analyze_needs_java(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def find_java() -> JavaRuntime:
        raise JavaNotFoundError("Java was not found")

    monkeypatch.setattr(cli, "find_java", find_java)

    result = runner.invoke(cli.app, ["analyze", str(tmp_path)])

    assert result.exit_code == 1
    assert "Java was not found" in result.stderr


def test_download(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, int, Path]] = []

    def download(source: str, count: int, folder: Path) -> list[Path]:
        calls.append((source, count, folder))
        return [folder / "a.apk", folder / "b.apk"]

    monkeypatch.setattr(cli, "download", download)

    result = runner.invoke(cli.app, ["download", str(tmp_path), "--count", "2"])

    assert result.exit_code == 0
    assert calls == [("droidbench", 2, tmp_path)]
    assert "2 APKs from droidbench" in result.stdout


def test_download_from_an_unknown_source(tmp_path: Path) -> None:
    result = runner.invoke(cli.app, ["download", str(tmp_path), "--source", "nowhere"])

    assert result.exit_code == 1
    assert str(UnknownApkSourceError.__name__) not in result.stderr
    assert "Unknown APK source 'nowhere'" in result.stderr


def test_sources() -> None:
    result = runner.invoke(cli.app, ["sources"])

    assert result.exit_code == 0
    assert "droidbench" in result.stdout


def test_doctor_when_ready(
    home: Path, ready: Installation, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        cli, "environment", lambda: Environment(home=home, java=JAVA, installation=ready)
    )

    result = runner.invoke(cli.app, ["doctor"])

    assert result.exit_code == 0
    assert "Java 17" in result.stdout
    assert "FlowDroid 2.15.1 with the Android 36 platform" in result.stdout


def test_doctor_when_nothing_is_there(home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def find_java() -> JavaRuntime:
        raise JavaNotFoundError("Java was not found")

    monkeypatch.setattr(cli, "find_java", find_java)
    monkeypatch.setattr(
        cli, "environment", lambda: Environment(home=home, java=None, installation=None)
    )

    result = runner.invoke(cli.app, ["doctor"])

    assert result.exit_code == 1
    assert "Java was not found" in result.stdout
    assert "not installed" in result.stdout


def test_module_entry_point(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["pyflowdroid", "--version"])

    with pytest.raises(SystemExit) as raised:
        runpy.run_module("pyflowdroid", run_name="__main__")

    assert raised.value.code == 0
