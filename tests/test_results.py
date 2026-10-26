from pathlib import Path

import pytest

from conftest import DATA
from pyflowdroid.errors import AnalysisFailedError, AnalysisTimeoutError
from pyflowdroid.models import Leak, Statement
from pyflowdroid.results import parse_results, read_outcome

APK = Path("app.apk")


def test_parses_a_leak_with_its_line_numbers() -> None:
    xml = (DATA / "private-data-leak.xml").read_text()

    assert parse_results(APK, xml, "log") == (
        Leak(
            source=Statement(
                method="<de.ecspride.PrivateDateLeakage: void onRestart()>",
                statement=(
                    "$r0 = virtualinvoke this.<de.ecspride.PrivateDateLeakage: "
                    "android.view.View findViewById(int)>(2130771970)"
                ),
                definition="",
                line=36,
            ),
            sink=Statement(
                method="<de.ecspride.PrivateDateLeakage: void sendMessage(android.view.View)>",
                statement=(
                    "virtualinvoke $r6.<android.telephony.SmsManager: void sendTextMessage("
                    "java.lang.String,java.lang.String,java.lang.String,android.app.PendingIntent,"
                    'android.app.PendingIntent)>("+49 1234", null, $r5, null, null)'
                ),
                definition=(
                    "<android.telephony.SmsManager: void sendTextMessage(java.lang.String,"
                    "java.lang.String,java.lang.String,android.app.PendingIntent,"
                    "android.app.PendingIntent)>"
                ),
                line=54,
            ),
        ),
    )


def test_one_leak_per_source_and_sink_pair() -> None:
    xml = """<DataFlowResults TerminationState="Success"><Results>
        <Result><Sink Method="m" Statement="sink"/>
            <Sources><Source Statement="a"/><Source Statement="b"/></Sources></Result>
    </Results></DataFlowResults>"""

    leaks = parse_results(APK, xml, "log")

    assert [(leak.source.statement, leak.sink.statement) for leak in leaks] == [
        ("a", "sink"),
        ("b", "sink"),
    ]
    assert leaks[0].source.line is None


def test_a_result_without_a_sink_is_malformed() -> None:
    xml = '<DataFlowResults TerminationState="Success"><Results><Result><Sources>'
    xml += '<Source Statement="a"/></Sources></Result></Results></DataFlowResults>'

    with pytest.raises(ValueError, match="without a <Sink>"):
        parse_results(APK, xml, "log")


@pytest.mark.parametrize(
    ("state", "error_type"),
    [
        ("DataFlowTimeout", AnalysisTimeoutError),
        ("DataFlowOutOfMemory", AnalysisFailedError),
        ("", AnalysisFailedError),
    ],
)
def test_an_unsuccessful_termination_is_an_error(
    state: str, error_type: type[AnalysisFailedError]
) -> None:
    xml = f'<DataFlowResults TerminationState="{state}"><Results/></DataFlowResults>'

    with pytest.raises(error_type, match="FlowDroid stopped with state"):
        parse_results(APK, xml, "log")


def test_outcome_reads_the_results_file(tmp_path: Path) -> None:
    output = tmp_path / "results.xml"
    output.write_text((DATA / "direct-leak.xml").read_text())

    leaks = read_outcome(APK, "log", output)

    assert [leak.sink.line for leak in leaks] == [27]


def test_outcome_without_results_file_and_no_leaks(tmp_path: Path) -> None:
    log = (DATA / "no-leaks.log").read_text()

    assert read_outcome(APK, log, tmp_path / "missing.xml") == ()


@pytest.mark.parametrize(
    ("fixture", "reason"),
    [
        ("missing-apk.log", "Target APK file /nonexistent.apk does not exist"),
        ("crash.log", "The data flow analysis has failed."),
    ],
)
def test_outcome_without_results_file_is_a_failure(
    tmp_path: Path, fixture: str, reason: str
) -> None:
    log = (DATA / fixture).read_text()

    with pytest.raises(AnalysisFailedError) as raised:
        read_outcome(APK, log, tmp_path / "missing.xml")

    assert raised.value.reason.startswith(reason)
    assert raised.value.log == log


@pytest.mark.parametrize(
    ("log", "reason"), [("", "FlowDroid produced no output"), ("first\nlast line\n", "last line")]
)
def test_failure_reason_falls_back_to_the_last_line(tmp_path: Path, log: str, reason: str) -> None:
    with pytest.raises(AnalysisFailedError) as raised:
        read_outcome(APK, log, tmp_path / "missing.xml")

    assert raised.value.reason == reason
