import logging

from pyflowdroid.analysis import analyze, find_apks
from pyflowdroid.apk_sources import download
from pyflowdroid.discovery import environment
from pyflowdroid.errors import (
    AnalysisFailedError,
    AnalysisTimeoutError,
    ChecksumMismatchError,
    DownloadError,
    FlowDroidNotInstalledError,
    InvalidApkError,
    JavaNotFoundError,
    PyFlowDroidError,
    UnknownApkSourceError,
    UnsupportedJavaError,
)
from pyflowdroid.installer import install
from pyflowdroid.models import (
    AnalysisResult,
    ApkRef,
    Environment,
    Installation,
    JavaRuntime,
    Leak,
    Statement,
)

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = [
    "AnalysisFailedError",
    "AnalysisResult",
    "AnalysisTimeoutError",
    "ApkRef",
    "ChecksumMismatchError",
    "DownloadError",
    "Environment",
    "FlowDroidNotInstalledError",
    "Installation",
    "InvalidApkError",
    "JavaNotFoundError",
    "JavaRuntime",
    "Leak",
    "PyFlowDroidError",
    "Statement",
    "UnknownApkSourceError",
    "UnsupportedJavaError",
    "analyze",
    "download",
    "environment",
    "find_apks",
    "install",
]

__version__ = "0.9.0-beta0"
