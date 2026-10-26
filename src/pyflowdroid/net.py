from collections.abc import Iterator
from contextlib import contextmanager

import httpx

from pyflowdroid.errors import DownloadError

TIMEOUT_SECONDS = 60


def new_client() -> httpx.Client:
    return httpx.Client(follow_redirects=True, timeout=TIMEOUT_SECONDS)


def get(client: httpx.Client, url: str) -> httpx.Response:
    response = request(client, url)
    if not response.is_success:
        raise DownloadError(f"Could not download {url}: HTTP {response.status_code}")
    return response


def request(client: httpx.Client, url: str) -> httpx.Response:
    try:
        return client.get(url)
    except httpx.HTTPError as error:
        raise DownloadError(f"Could not download {url}: {error}") from error


@contextmanager
def stream(client: httpx.Client, url: str) -> Iterator[httpx.Response]:
    try:
        with client.stream("GET", url) as response:
            if not response.is_success:
                raise DownloadError(f"Could not download {url}: HTTP {response.status_code}")
            yield response
    except httpx.HTTPError as error:
        raise DownloadError(f"Could not download {url}: {error}") from error
