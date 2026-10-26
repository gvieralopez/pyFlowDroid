import shutil
import subprocess
from pathlib import Path

import platformdirs
import pytest

from pyflowdroid import discovery as env
from pyflowdroid.errors import FlowDroidNotInstalledError, JavaNotFoundError, UnsupportedJavaError
from pyflowdroid.models import Installation, JavaRuntime


def test_home_comes_from_the_environment_variable(home: Path) -> None:
    assert env.home() == home


def test_home_defaults_to_the_user_data_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(env.HOME_VARIABLE, raising=False)
    monkeypatch.setattr(platformdirs, "user_data_path", lambda name: tmp_path / name)

    assert env.home() == tmp_path / "pyflowdroid"


@pytest.mark.parametrize(
    ("output", "version"),
    [
        ('openjdk version "17.0.21" 2026-10-20', 17),
        ('openjdk version "21" 2023-09-19', 21),
        ('java version "1.8.0_402"', 8),
    ],
)
def test_java_version_reads_the_major_version(
    monkeypatch: pytest.MonkeyPatch, output: str, version: int
) -> None:
    _fake_java_output(monkeypatch, output)

    assert env.java_version(Path("java")) == version


def test_java_version_rejects_unreadable_output(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_java_output(monkeypatch, "command not found")

    with pytest.raises(JavaNotFoundError, match="Could not read the Java version"):
        env.java_version(Path("java"))


def test_find_java_prefers_java_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    java_home = tmp_path / "jdk"
    monkeypatch.setenv("JAVA_HOME", str(java_home))
    monkeypatch.setattr(shutil, "which", _which({str(java_home / "bin"): "/jdk/bin/java"}))
    _fake_java_output(monkeypatch, 'openjdk version "17.0.21"')

    assert env.find_java() == JavaRuntime(executable=Path("/jdk/bin/java"), version=17)


def test_find_java_falls_back_to_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv("JAVA_HOME", str(tmp_path / "empty"))
    monkeypatch.setattr(shutil, "which", _which({None: "/usr/bin/java"}))
    _fake_java_output(monkeypatch, 'openjdk version "21"')

    assert env.find_java() == JavaRuntime(executable=Path("/usr/bin/java"), version=21)
    assert "has no java executable" in caplog.text


def test_find_java_without_java(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JAVA_HOME", raising=False)
    monkeypatch.setattr(shutil, "which", _which({}))

    with pytest.raises(JavaNotFoundError, match="Java was not found"):
        env.find_java()


def test_find_java_rejects_old_java(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JAVA_HOME", raising=False)
    monkeypatch.setattr(shutil, "which", _which({None: "/usr/bin/java"}))
    _fake_java_output(monkeypatch, 'java version "1.8.0_402"')

    with pytest.raises(UnsupportedJavaError, match="needs Java 17 or newer"):
        env.find_java()


def test_installation_round_trips_through_the_manifest(
    home: Path, installation: Installation
) -> None:
    assert env.load_installation(home) == installation


def test_load_installation_without_manifest(home: Path) -> None:
    with pytest.raises(FlowDroidNotInstalledError, match="not installed"):
        env.load_installation(home)


def test_load_installation_with_a_missing_file(home: Path, installation: Installation) -> None:
    installation.android_jar.unlink()

    with pytest.raises(FlowDroidNotInstalledError, match=r"missing android\.jar"):
        env.load_installation(home)


def test_environment_reports_what_is_there(
    home: Path, installation: Installation, monkeypatch: pytest.MonkeyPatch
) -> None:
    java = JavaRuntime(executable=Path("java"), version=17)
    monkeypatch.setattr(env, "find_java", lambda: java)

    found = env.environment()

    assert (found.home, found.java, found.installation, found.ready) == (
        home,
        java,
        installation,
        True,
    )


def test_environment_reports_what_is_missing(home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(env, "find_java", _raise(JavaNotFoundError("no java")))

    found = env.environment()

    assert (found.java, found.installation, found.ready) == (None, None, False)


def _fake_java_output(monkeypatch: pytest.MonkeyPatch, stderr: str) -> None:
    def run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout="", stderr=stderr)

    monkeypatch.setattr(subprocess, "run", run)


def _which(found: dict[str | None, str]) -> object:
    def which(name: str, path: str | None = None) -> str | None:
        return found.get(path)

    return which


def _raise(error: Exception) -> object:
    def fail() -> None:
        raise error

    return fail
