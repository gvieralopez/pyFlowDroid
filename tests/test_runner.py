import subprocess
from pathlib import Path

import pytest

from pyflowdroid import runner
from pyflowdroid.errors import AnalysisTimeoutError
from pyflowdroid.models import Installation, JavaRuntime

JAVA = JavaRuntime(executable=Path("/jdk/bin/java"), version=17)


def test_command_passes_every_path_as_its_own_argument(installation: Installation) -> None:
    apk = Path("/apks/with space/app.apk")

    command = runner.flowdroid_command(JAVA, installation, apk, Path("/out/results.xml"))

    assert command == [
        "/jdk/bin/java",
        "-jar",
        str(installation.flowdroid_jar),
        "-a",
        "/apks/with space/app.apk",
        "-p",
        str(installation.android_jar),
        "-s",
        str(installation.sources_sinks),
        "-o",
        "/out/results.xml",
        "-ol",
    ]


def test_run_returns_the_merged_log(
    installation: Installation, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: dict[str, object] = {}

    def run(command: list[str], **options: object) -> subprocess.CompletedProcess[str]:
        seen.update(options, command=command)
        return subprocess.CompletedProcess(command, 0, stdout="Found 0 leaks from 0 sources")

    monkeypatch.setattr(subprocess, "run", run)

    log = runner.run_flowdroid(JAVA, installation, Path("app.apk"), Path("out.xml"))

    assert log == "Found 0 leaks from 0 sources"
    assert seen["stderr"] == subprocess.STDOUT
    assert seen["timeout"] == runner.TIMEOUT_SECONDS
    assert "shell" not in seen


@pytest.mark.parametrize(("partial", "log"), [(b"half a log", "half a log"), (None, "")])
def test_run_turns_a_timeout_into_an_analysis_error(
    installation: Installation, monkeypatch: pytest.MonkeyPatch, partial: bytes | None, log: str
) -> None:
    def run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(command, runner.TIMEOUT_SECONDS, output=partial)

    monkeypatch.setattr(subprocess, "run", run)

    with pytest.raises(AnalysisTimeoutError, match="no result after") as raised:
        runner.run_flowdroid(JAVA, installation, Path("app.apk"), Path("out.xml"))

    assert raised.value.log == log
