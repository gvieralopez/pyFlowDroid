from pathlib import Path


class PyFlowDroidError(Exception):
    pass


class JavaNotFoundError(PyFlowDroidError):
    pass


class UnsupportedJavaError(PyFlowDroidError):
    pass


class FlowDroidNotInstalledError(PyFlowDroidError):
    pass


class DownloadError(PyFlowDroidError):
    pass


class ChecksumMismatchError(DownloadError):
    pass


class InvalidApkError(PyFlowDroidError):
    pass


class UnknownApkSourceError(PyFlowDroidError):
    pass


class AnalysisFailedError(PyFlowDroidError):
    def __init__(self, apk: Path, reason: str, log: str) -> None:
        super().__init__(f"FlowDroid could not analyze {apk}: {reason}")
        self.apk = apk
        self.reason = reason
        self.log = log


class AnalysisTimeoutError(AnalysisFailedError):
    pass
