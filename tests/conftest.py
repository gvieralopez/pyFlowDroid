from pathlib import Path

import pytest

from pyflowdroid.discovery import HOME_VARIABLE, save_installation
from pyflowdroid.models import Installation

DATA = Path(__file__).parent / "data"


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    location = tmp_path / "home"
    location.mkdir()
    monkeypatch.setenv(HOME_VARIABLE, str(location))
    return location


@pytest.fixture
def installation(home: Path) -> Installation:
    installed = Installation(
        flowdroid_version="2.15.1",
        flowdroid_jar=home / "flowdroid" / "2.15.1" / "soot-infoflow-cmd.jar",
        sources_sinks=home / "flowdroid" / "2.15.1" / "SourcesAndSinks.txt",
        android_platform=36,
        android_jar=home / "android" / "android-36" / "android.jar",
    )
    for path in (installed.flowdroid_jar, installed.sources_sinks, installed.android_jar):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(path.name)
    save_installation(home, installed)
    return installed
