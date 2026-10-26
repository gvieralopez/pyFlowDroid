from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

from pyflowdroid.models import ApkRef


class ApkSource(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def description(self) -> str: ...

    def list_apks(self) -> Iterator[ApkRef]: ...

    def fetch(self, apk: ApkRef, folder: Path) -> Path: ...
