<div align="center">

<img src="assets/logo.svg" alt="" width="96">

# pyFlowDroid

**Run FlowDroid taint analysis on Android APKs from Python**

[![QA](https://github.com/gvieralopez/pyFlowDroid/actions/workflows/qa.yml/badge.svg)](https://github.com/gvieralopez/pyFlowDroid/actions/workflows/qa.yml)
[![Release](https://img.shields.io/github/v/release/gvieralopez/pyFlowDroid?label=release)](https://github.com/gvieralopez/pyFlowDroid/releases/latest)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pyflowdroid)](https://pypi.org/project/pyflowdroid/)
<br>
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

<!-- Badges to move into the rows above once they apply:
[![Docker image](https://img.shields.io/badge/docker-ghcr.io-2496ED?logo=docker&logoColor=white)](https://github.com/gvieralopez/pyFlowDroid/pkgs/container/pyFlowDroid)
[![Docs](https://readthedocs.org/projects/pyFlowDroid/badge/?version=latest)](https://pyFlowDroid.readthedocs.io)
-->

[Quick start](#quick-start) · [Command line](#command-line) · [Python](#python) · [Coming from 0.2](#coming-from-02) · [Development](#development)

</div>

---

Run [FlowDroid](https://github.com/secure-software-engineering/FlowDroid)'s taint analysis on Android
APKs from Python or the command line. One command sets FlowDroid up; every analysis returns typed
results: which data leaks, from which call to which, with line numbers.

## Features

- **FlowDroid out of the box.** `pyflowdroid install` fetches the latest FlowDroid release, the
  sources and sinks list from that same release, and an Android platform: about 54 MB, in seconds.
- **Typed results.** `analyze()` returns an `AnalysisResult` with `Leak` objects (source, sink,
  method, statement, line), not a log to grep.
- **Honest failures.** When FlowDroid fails, you get an `AnalysisFailedError` with the reason and the
  log, never a silent "0 leaks".
- **Sample APKs.** `pyflowdroid download` fetches apps from
  [DroidBench](https://github.com/secure-software-engineering/DroidBench), FlowDroid's benchmark with
  documented leaks, to try things out.

## Quick start

You need **Java 17 or newer** on your `PATH` (or in `JAVA_HOME`) and Python 3.11 or newer.

```bash
pip install pyflowdroid
pyflowdroid install
pyflowdroid analyze path/to/app.apk
```

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┓
┃ APK                       ┃ Leaks ┃ Seconds ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━┩
│ apks/DirectLeak1.apk      │ 1     │ 0.8     │
│ apks/LogNoLeak.apk        │ 0     │ 0.6     │
└───────────────────────────┴───────┴─────────┘
apks/DirectLeak1.apk
  from TelephonyManager.getDeviceId() in MainActivity.onCreate(), line 27
  to   SmsManager.sendTextMessage() in MainActivity.onCreate(), line 27
```

`pyflowdroid doctor` tells you what is missing if something doesn't work.

## Command line

| Command | What it does |
|---|---|
| `pyflowdroid install` | Download FlowDroid, its sources and sinks list and the Android 36 platform; files already there are kept |
| `pyflowdroid analyze PATH...` | Analyze APK files and folders (searched recursively); `--json` prints the results as JSON. Exits 1 if any APK failed |
| `pyflowdroid download FOLDER` | Download sample APKs (`--source droidbench`, `--count 10`) |
| `pyflowdroid sources` | List where sample APKs can come from |
| `pyflowdroid doctor` | Check Java and the FlowDroid installation |

`python -m pyflowdroid` works the same. `--verbose` shows what happens; `--version` prints the version.

## Python

```python
from pathlib import Path

import pyflowdroid

pyflowdroid.install()  # once; skips what is already there

result = pyflowdroid.analyze("app.apk")  # -> AnalysisResult
for leak in result.leaks:
    print(leak.source.definition, "->", leak.sink.definition, "line", leak.sink.line)

for apk in pyflowdroid.find_apks("apks/"):
    try:
        print(apk, pyflowdroid.analyze(apk).leaky)
    except pyflowdroid.AnalysisFailedError as error:
        print(apk, "failed:", error.reason)

pyflowdroid.download("droidbench", 5, Path("apks"))  # sample apps
```

- `AnalysisResult`: `apk`, `leaks` (a tuple of `Leak`), `leaky`, `flowdroid_version`, `seconds`, `log`.
- `Leak`: `source` and `sink`, each a `Statement` with `method`, `statement`, `definition` (the
  source or sink signature from the list) and `line`.
- `pyflowdroid.environment()` reports what is installed without raising.
- Every error derives from `PyFlowDroidError`: `JavaNotFoundError`, `UnsupportedJavaError`,
  `FlowDroidNotInstalledError`, `DownloadError` (and `ChecksumMismatchError`), `InvalidApkError`,
  `AnalysisFailedError` (and `AnalysisTimeoutError`), `UnknownApkSourceError`.

The library doesn't configure logging or print; it logs through the `pyflowdroid` logger.

## How it works

- **FlowDroid** comes from Maven Central (`de.fraunhofer.sit.sse.flowdroid:soot-infoflow-cmd`, the
  `jar-with-dependencies`), checked against its published SHA-1. The latest release is used.
- **Sources and sinks**: `SourcesAndSinks.txt` from the same FlowDroid release, so the list always
  matches the analysis.
- **Android platform**: one `android.jar` (API 36) from
  [Sable/android-platforms](https://github.com/Sable/android-platforms), used for every APK.
- Everything lives in your user data folder (for example `~/.local/share/pyflowdroid` on Linux);
  set `PYFLOWDROID_HOME` to use another folder.
- FlowDroid runs as `java -jar … -o results.xml -ol` with each argument passed separately (no shell),
  so paths with spaces work. Each analysis has a 15 minute timeout.

## Coming from 0.2

0.9.0 is a rewrite and breaks the old API on purpose.

| 0.2 | 0.9 |
|---|---|
| `install_deps()` downloaded FlowDroid 2.9 and ~1 GB of Android platforms into the installed package | `install()`: latest FlowDroid, one platform, in the user data folder |
| `analyze_apk(path)` returned FlowDroid's log as a string | `analyze(path)` returns an `AnalysisResult` |
| `analyze(folder)` returned `(count, leaks, leaky_apps)` | `find_apks(folder)` + `analyze()` per APK |
| `fetch(n, "cubapk.com", folder)` | `download("droidbench", n, folder)`; cubapk.com no longer serves APKs |
| bundled `small.txt` / `large.txt` | the sources and sinks list of the installed FlowDroid release |
| `python -m pyflowdroid …` | `pyflowdroid …` (`python -m pyflowdroid` still works) |

0.2 no longer works on current Java: FlowDroid 2.9 fails on Java 17 updates and 0.2 reported that as
"0 leaks".

## Development

Setup, QA and releases: [DEVELOPMENT.md](DEVELOPMENT.md). `make qa` runs the unit tests;
`uv run pytest -m e2e --no-cov` runs real FlowDroid on DroidBench apps (needs Java 17+ and the network).

## Contributing

Issues and pull requests are welcome; `make qa` must pass.

## Acknowledgements

[FlowDroid](https://github.com/secure-software-engineering/FlowDroid) and
[DroidBench](https://github.com/secure-software-engineering/DroidBench) by the Secure Software
Engineering group, and [Sable/android-platforms](https://github.com/Sable/android-platforms).
pyflowdroid downloads them; it doesn't redistribute them.

## License

MIT: see [LICENSE](LICENSE).

---

<sub>🚀 Project starter provided by [Cookie Pyrate v1.0.0](https://github.com/gvieralopez/cookie-pyrate/tree/v1.0.0)</sub>
