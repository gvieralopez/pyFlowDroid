import zipfile
from pathlib import Path

import pytest

from conftest import DATA
from pyflowdroid import analysis
from pyflowdroid.errors import AnalysisFailedError, InvalidApkError
from pyflowdroid.models import Installation, JavaRuntime

JAVA = JavaRuntime(executable=Path("java"), version=17)


@pytest.fixture
def apk(tmp_path: Path) -> Path:
    path = tmp_path / "apps" / "with space" / "app.apk"
    path.parent.mkdir(parents=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("AndroidManifest.xml", "<manifest/>")
    return path


def _fake_flowdroid(monkeypatch: pytest.MonkeyPatch, results: str | None, log: str) -> None:
    def run_flowdroid(
        java: JavaRuntime, installation: Installation, apk: Path, output: Path
    ) -> str:
        if results is not None:
            output.write_text((DATA / results).read_text())
        return log

    monkeypatch.setattr(analysis, "run_flowdroid", run_flowdroid)


def test_analyze_returns_the_leaks(
    apk: Path, installation: Installation, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(analysis, "find_java", lambda: JAVA)
    _fake_flowdroid(monkeypatch, "direct-leak.xml", "the log")

    result = analysis.analyze(str(apk))

    assert result.apk == apk
    assert result.leaky
    assert [leak.sink.line for leak in result.leaks] == [27]
    assert result.flowdroid_version == installation.flowdroid_version
    assert result.log == "the log"
    assert result.seconds >= 0


def test_analyze_an_app_without_leaks(
    apk: Path, installation: Installation, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_flowdroid(monkeypatch, None, (DATA / "no-leaks.log").read_text())

    result = analysis.analyze_with(JAVA, installation, apk)

    assert result.leaks == ()
    assert not result.leaky


def test_analyze_raises_when_flowdroid_fails(
    apk: Path, installation: Installation, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_flowdroid(monkeypatch, None, (DATA / "crash.log").read_text())

    with pytest.raises(AnalysisFailedError, match="analysis has failed"):
        analysis.analyze_with(JAVA, installation, apk)


def test_analyze_rejects_a_missing_file(tmp_path: Path, installation: Installation) -> None:
    with pytest.raises(InvalidApkError, match="is not a file"):
        analysis.analyze_with(JAVA, installation, tmp_path / "missing.apk")


def test_analyze_rejects_a_file_that_is_not_an_apk(
    tmp_path: Path, installation: Installation
) -> None:
    text = tmp_path / "notes.apk"
    text.write_text("not a zip")

    with pytest.raises(InvalidApkError, match="not a zip archive"):
        analysis.analyze_with(JAVA, installation, text)


def test_find_apks_searches_subfolders(tmp_path: Path) -> None:
    for name in ("b.apk", "nested/a.apk", "readme.txt"):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(name)
    (tmp_path / "folder.apk").mkdir()

    assert analysis.find_apks(tmp_path) == [tmp_path / "b.apk", tmp_path / "nested" / "a.apk"]


def test_find_apks_needs_a_folder(tmp_path: Path) -> None:
    with pytest.raises(NotADirectoryError):
        analysis.find_apks(tmp_path / "missing")
