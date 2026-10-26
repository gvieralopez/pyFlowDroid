from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Statement:
    method: str
    statement: str
    definition: str
    line: int | None


@dataclass(frozen=True, slots=True)
class Leak:
    source: Statement
    sink: Statement


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    apk: Path
    leaks: tuple[Leak, ...]
    flowdroid_version: str
    seconds: float
    log: str = field(repr=False)

    @property
    def leaky(self) -> bool:
        return bool(self.leaks)


@dataclass(frozen=True, slots=True)
class JavaRuntime:
    executable: Path
    version: int


@dataclass(frozen=True, slots=True)
class Installation:
    flowdroid_version: str
    flowdroid_jar: Path
    sources_sinks: Path
    android_platform: int
    android_jar: Path


@dataclass(frozen=True, slots=True)
class Environment:
    home: Path
    java: JavaRuntime | None
    installation: Installation | None

    @property
    def ready(self) -> bool:
        return self.java is not None and self.installation is not None


@dataclass(frozen=True, slots=True)
class ApkRef:
    source: str
    name: str
    url: str
