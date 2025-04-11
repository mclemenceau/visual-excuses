import requests
import lzma

from pathlib import Path
from typing import List, Optional

from visual_excuses.excuse import Excuse
from visual_excuses.yaml_parser import load_excuses

UBUNTU_EXCUSES_URL = (
    "https://people.canonical.com/~ubuntu-archive/proposed-migration/"
    "/update_excuses.yaml.xz"
)


class CachedExcuses:
    """
    CachedExcuses will facilitae the download, decompression and storage for
    the Ubuntu Excuses file.
    CachedExcuses will only download new excuses if the version in the cached
    folder is outdated
    """
    def __init__(self, url: str, cache_dir: Optional[Path] = None):
        self.url = url
        self.directory = cache_dir or Path.home() / ".excuses"
        self.etag = self.directory / "ETag"
        self.yaml = self.directory / "excuse.yaml"

    def _fetch_remote_etag(self) -> str:
        # Grab the latest online etag
        response = requests.head(self.url, allow_redirects=True)
        if response.status_code != 200:
            raise ConnectionError(
                f"Failed to fetch etag from {self.url}. "
                f"Status code: {response.status_code}"
            )

        etag = None
        if "etag" in response.headers:
            etag = response.headers['etag']

        if not etag:
            raise ValueError(f"ETag header missing from {self.url}")
        return etag

    def _is_cache_valid(self, etag: str) -> bool:
        """
        Check if the local cache is valid and if an excuse file is present
        """
        if not self.etag.exists() or not self.yaml.exists():
            return False

        return self.etag.read_text() == etag

    def _fetch_and_cache(self, etag: str):
        """
        Download the latest excuse and cache them
        """

        print(f"Downloading {self.url}")
        response = requests.get(self.url, timeout=10)

        if response.status_code != 200:
            raise ConnectionError(
                f"Failed to fetch excuses from {self.url}. "
                f"Status code: {response.status_code}"
            )

        decompressed_yaml = lzma.decompress(response.content)

        self.yaml.write_bytes(decompressed_yaml)
        self.etag.write_text(etag)

    def update(self):
        """
        Check of the local cache need to be updated based on the ETag value
        """
        tag = self._fetch_remote_etag()

        if not self._is_cache_valid(tag):
            self.directory.mkdir(parents=True, exist_ok=True)
            self._fetch_and_cache(tag)

        print("Excuses Cache up to date!")


def load_ubuntu_excuses(url: str = UBUNTU_EXCUSES_URL) -> List[Excuse]:
    """Fetches Ubuntu excuses YAML and parses it into Excuse objects.

    Args:
        url (str, optional): The URL to fetch the excuses file from.
        Defaults to ubuntu_excuses_url.

    Returns:
        List[Excuse]: A list of parsed Excuse objects.
    """
    try:
        cache = CachedExcuses(url)

        cache.update()

        return load_excuses(cache.yaml)

    except Exception as e:
        raise RuntimeError(f"Couldn't process excuses.yaml.xz. Exception: {e}")
