import re
from pathlib import Path
from xml.etree.ElementTree import Element

from defusedxml import ElementTree

from pyflowdroid.errors import AnalysisFailedError, AnalysisTimeoutError
from pyflowdroid.models import Leak, Statement

SUCCESS = "Success"

_NO_LEAKS = re.compile(r"Found 0 leaks from \d+ sources")
_FAILURE_MARKERS = ("Exception", "ERROR", "failed", "does not exist")


def read_outcome(apk: Path, log: str, output: Path) -> tuple[Leak, ...]:
    if output.is_file():
        return parse_results(apk, output.read_text(encoding="utf-8"), log)
    if _NO_LEAKS.search(log):
        return ()
    raise AnalysisFailedError(apk, _failure_reason(log), log)


def parse_results(apk: Path, xml: str, log: str) -> tuple[Leak, ...]:
    root = ElementTree.fromstring(xml)
    state = root.get("TerminationState", "")
    if state != SUCCESS:
        error_type = AnalysisTimeoutError if "Timeout" in state else AnalysisFailedError
        raise error_type(apk, f"FlowDroid stopped with state {state or 'unknown'}", log)
    return tuple(
        Leak(source=_statement(source), sink=_statement(_child(result, "Sink")))
        for result in root.iterfind("Results/Result")
        for source in result.iterfind("Sources/Source")
    )


def _statement(element: Element) -> Statement:
    line = element.get("LineNumber")
    return Statement(
        method=element.get("Method", ""),
        statement=element.get("Statement", ""),
        definition=element.get("MethodSourceSinkDefinition", ""),
        line=int(line) if line else None,
    )


def _child(element: Element, tag: str) -> Element:
    child = element.find(tag)
    if child is None:
        raise ValueError(f"FlowDroid result without a <{tag}> element")
    return child


def _failure_reason(log: str) -> str:
    lines = [line.strip() for line in log.splitlines() if line.strip()]
    for line in lines:
        if any(marker in line for marker in _FAILURE_MARKERS):
            return line
    return lines[-1] if lines else "FlowDroid produced no output"
