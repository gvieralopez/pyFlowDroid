import logging
import subprocess
from pathlib import Path

from pyflowdroid.errors import AnalysisTimeoutError
from pyflowdroid.models import Installation, JavaRuntime

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 900


def run_flowdroid(java: JavaRuntime, installation: Installation, apk: Path, output: Path) -> str:
    command = flowdroid_command(java, installation, apk, output)
    logger.debug("Running %s", command)
    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise AnalysisTimeoutError(
            apk, f"no result after {TIMEOUT_SECONDS} seconds", _partial_log(error.output)
        ) from error
    return completed.stdout


def flowdroid_command(
    java: JavaRuntime, installation: Installation, apk: Path, output: Path
) -> list[str]:
    return [
        str(java.executable),
        "-jar",
        str(installation.flowdroid_jar),
        "-a",
        str(apk),
        "-p",
        str(installation.android_jar),
        "-s",
        str(installation.sources_sinks),
        "-o",
        str(output),
        "-ol",
    ]


def _partial_log(output: str | bytes | None) -> str:
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return output or ""
