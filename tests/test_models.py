from pathlib import Path

import pytest

from pyflowdroid.errors import AnalysisFailedError, AnalysisTimeoutError
from pyflowdroid.models import (
    AnalysisResult,
    Environment,
    Installation,
    JavaRuntime,
    Leak,
    Statement,
)

STATEMENT = Statement(method="<A: void m()>", statement="x = y", definition="<B: int f()>", line=3)
INSTALLATION = Installation(
    flowdroid_version="2.15.1",
    flowdroid_jar=Path("fd.jar"),
    sources_sinks=Path("SourcesAndSinks.txt"),
    android_platform=36,
    android_jar=Path("android.jar"),
)
JAVA = JavaRuntime(executable=Path("java"), version=17)


@pytest.mark.parametrize(
    ("leaks", "leaky"), [((), False), ((Leak(source=STATEMENT, sink=STATEMENT),), True)]
)
def test_result_is_leaky_when_it_has_leaks(leaks: tuple[Leak, ...], leaky: bool) -> None:
    result = AnalysisResult(
        apk=Path("a.apk"), leaks=leaks, flowdroid_version="2.15.1", seconds=1.0, log="log"
    )

    assert result.leaky is leaky


def test_result_repr_leaves_out_the_log() -> None:
    result = AnalysisResult(
        apk=Path("a.apk"), leaks=(), flowdroid_version="2.15.1", seconds=1.0, log="secret log"
    )

    assert "secret log" not in repr(result)


@pytest.mark.parametrize(
    ("java", "installation", "ready"),
    [(JAVA, INSTALLATION, True), (None, INSTALLATION, False), (JAVA, None, False)],
)
def test_environment_is_ready_with_java_and_flowdroid(
    java: JavaRuntime | None, installation: Installation | None, ready: bool
) -> None:
    environment = Environment(home=Path("home"), java=java, installation=installation)

    assert environment.ready is ready


@pytest.mark.parametrize("error_type", [AnalysisFailedError, AnalysisTimeoutError])
def test_analysis_errors_keep_the_apk_reason_and_log(error_type: type[AnalysisFailedError]) -> None:
    error = error_type(Path("a.apk"), "it broke", "the log")

    assert (error.apk, error.reason, error.log) == (Path("a.apk"), "it broke", "the log")
    assert str(error) == "FlowDroid could not analyze a.apk: it broke"
