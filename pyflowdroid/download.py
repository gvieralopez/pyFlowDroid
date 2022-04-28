import abc
import shutil
import urllib
import logging
import functools
from pathlib import Path
from urllib.request import urlopen
from bs4 import BeautifulSoup
from pyflowdroid import DEFAULT_APK_PROVIDER


class ApkProvider(metaclass=abc.ABCMeta):
    """
    Abstract class to define the structure of an APK provider.

    Parameters
    ----------
    force_redownload : bool, optional
        Defines wheter or not the provider will overwrite existing apk files
        when is trying to download a file with a name already existing in the
        give folder, by default False.
    """

    def __init__(self, force_redownload: bool = False):
        self.force_redownload = force_redownload

    @abc.abstractmethod
    def avialable_apks(self) -> dict:
        """
        Abstract method to be implemented by each apk provider. In classes
        inheriting from ApkProvider, this method is expected to return a
        dictionary with the data from the apks the provider has avialable.

        The expected format of the dictionary is:
        {
            'apk1.apk': 'http://url/to/apk1.apk',
            'another.apk': 'http://url/to/another.apk',
            'verynice.apk': 'http://url/to/verynice.apk'
        }

        Returns
        -------
        dict
            Dictionary with the data of the apks avialable.
        """
        ...

    def download_apk(self, apk_name: str, apk_url: str, path: str) -> None:
        """
        Download an apk from a given url.

        Parameters
        ----------
        apk_name : str
            Name of the apk to be downloaded.
        apk_url : str
            Url of the apk to be downloaded.
        path : str
            Path where the apk will be downloaded.

        Raises
        ------
        ValueError
            If path does not points to a folder
        """

        # Check if path is a folder and exists
        folder_path = Path(path)
        if not folder_path.exists() or folder_path.is_file():
            raise ValueError(f"{path} does not points to a folder")

        # Generate the path to the apk file that is going to be downloaded
        apk_path = folder_path / apk_name

        # Check if the apk file already exists and if force_redownload is False
        if apk_path.exists() and not self.force_redownload:

            # If the apk file already exists and force_redownload is False skips
            # the download
            logging.info(f"{apk_name} already exists")
            return

        # Download the apk file from the given url
        try:
            logging.info(f"Downloading {apk_name} from {apk_url}")
            hdr = {"User-Agent": "Mozilla/5.0"}
            req = urllib.request.Request(apk_url, headers=hdr)
            with urllib.request.urlopen(req) as response, open(
                apk_path, "wb"
            ) as out_file:
                shutil.copyfileobj(response, out_file)
        # Notify if the apk file could not be downloaded
        except urllib.error.HTTPError:
            logging.error(f"Error downloading {apk_name} from {apk_url}")

    def download_apks(self, amount: int, path: str, create_path: bool = True) -> None:
        """
        Download a given amount of apks from the provider.

        Parameters
        ----------
        amount : int
            Amount of apks to be downloaded.
        path : str
            Path where the apks will be downloaded.
        create_path : bool, optional
            Defines wheter or not the path will be created if it does not exists.
        """

        # Create the path if it does not exists
        if create_path:
            Path(path).mkdir(parents=True, exist_ok=True)

        # Fetch the dictionary with all the apks from the provider
        avialable_apks = self.avialable_apks()

        # Download each apk until reaching the amount of apks to be downloaded
        for i, apk_name in enumerate(avialable_apks):
            if i == amount:
                logging.info(f"Downloaded {i} apks")
                return
            apk_url = avialable_apks[apk_name]
            self.download_apk(apk_name, apk_url, path)

        # Download each apk until reaching the amount of apks to be downloaded
        logging.error(
            f"Downloaded {i} apks instead of {amount}. No more apks to download"
        )


class CubapkProvider(ApkProvider):
    """
    CubapkProvider class to download apks from the cubapk.com website.
    """

    def __init__(self, force_redownload: bool = False):
        super().__init__(force_redownload)
        self.base_url = "https://cubapk.com"

    @functools.lru_cache(maxsize=None)
    def avialable_apks(self) -> dict:
        """
        Generates a dictionary with the avialable apks from cubapk.com website.
        """

        # Empty dictionary to store the avialable apks
        apk_dict = {}

        # Interation variable to control the page we are parsing in the website
        page = 1

        # If there is another page to be parsed
        while True:
            page_url = f"{self.base_url}/store/?page={page}"

            # Fetches the website raw HTML
            try:
                request = urllib.request.Request(
                    page_url, headers={"User-Agent": "Mozilla/5.0"}
                )
                text = urlopen(request).read()
            except urllib.error.HTTPError:
                logging.info(f"Index of {self.base_url} has {page-1} pages")
                break

            # Parses the website
            soup = BeautifulSoup(text, features="lxml")
            data = soup.findAll("div", attrs={"class": "app-data"})
            for div in data:

                # Parse the apk name
                raw_name = div.find("div", attrs={"class": "app-title"}).text
                apk_name = "".join(filter(str.isalnum, raw_name))
                apk_name += ".apk"

                # Parse the apk url
                download_div = div.find("div", attrs={"class": "app-meta"})
                raw_link = download_div.a["href"]
                link = f"{self.base_url}{raw_link}"

                # Apend the data from the apk to the dictionary
                apk_dict[apk_name] = link

            # Updates the page number
            page += 1
        return apk_dict


# Dictionary with all the available providers
_providers = {"cubapk.com": CubapkProvider}


def get_provider(name: str) -> ApkProvider:
    """
    Returns an ApkProvider instance with the given name. If there are no
    matches with the given name, the default provider is returned.

    Parameters
    ----------
    name : str
        Name of the provider to be returned.

    Returns
    -------
    ApkProvider
        Provider with the given name.
    """

    if name not in _providers.keys():
        logging.warning(f"Provider '{name}' not found, using '{DEFAULT_APK_PROVIDER}'")
        return _providers[DEFAULT_APK_PROVIDER]()
    return _providers[name]()
