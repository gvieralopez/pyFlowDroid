import logging
from collections.abc import Iterator
from pathlib import Path, PurePosixPath

import httpx

from pyflowdroid import net
from pyflowdroid.models import ApkRef

logger = logging.getLogger(__name__)

TREE_URL = (
    "https://api.github.com/repos/secure-software-engineering/DroidBench/git/trees/master"
    "?recursive=1"
)
RAW_URL = "https://raw.githubusercontent.com/secure-software-engineering/DroidBench/master"
APK_FOLDER = "apk"


class DroidBench:
    name = "droidbench"
    description = "FlowDroid's benchmark: small Android apps with documented leaks"

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_apks(self) -> Iterator[ApkRef]:
        tree = net.get(self._client, TREE_URL).json()["tree"]
        for entry in tree:
            path = PurePosixPath(entry["path"])
            if entry["type"] == "blob" and path.suffix == ".apk" and path.parts[0] == APK_FOLDER:
                name = path.relative_to(APK_FOLDER).with_suffix("").as_posix()
                yield ApkRef(source=self.name, name=name, url=f"{RAW_URL}/{path.as_posix()}")

    def fetch(self, apk: ApkRef, folder: Path) -> Path:
        destination = folder / f"{apk.name.replace('/', '-')}.apk"
        if destination.is_file():
            logger.info("%s is already downloaded", destination.name)
            return destination
        destination.write_bytes(net.get(self._client, apk.url).content)
        return destination
