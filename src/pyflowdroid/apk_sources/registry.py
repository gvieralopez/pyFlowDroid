from collections.abc import Callable
from itertools import islice
from pathlib import Path

import httpx

from pyflowdroid import net
from pyflowdroid.apk_sources.base import ApkSource
from pyflowdroid.apk_sources.droidbench import DroidBench
from pyflowdroid.errors import UnknownApkSourceError

SOURCES: dict[str, Callable[[httpx.Client], ApkSource]] = {DroidBench.name: DroidBench}


def download(source: str, count: int, folder: Path) -> list[Path]:
    with net.new_client() as client:
        return download_from(get_source(source, client), count, folder)


def download_from(source: ApkSource, count: int, folder: Path) -> list[Path]:
    folder.mkdir(parents=True, exist_ok=True)
    return [source.fetch(apk, folder) for apk in islice(source.list_apks(), count)]


def get_source(name: str, client: httpx.Client) -> ApkSource:
    try:
        return SOURCES[name](client)
    except KeyError:
        known = ", ".join(sorted(SOURCES))
        raise UnknownApkSourceError(f"Unknown APK source {name!r}; available: {known}") from None


def source_names() -> list[str]:
    return sorted(SOURCES)
