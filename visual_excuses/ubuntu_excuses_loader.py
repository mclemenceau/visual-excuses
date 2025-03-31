import requests
import lzma
import tempfile

from pathlib import Path
from typing import List

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
    def __init__(self, url: str):
        self.url = url
        self.directory = Path(f"{Path.home()}/.excuses")
        self.etag = Path(f"{self.directory}/ETag")
        self.yaml = Path(f"{self.directory}/excuse.yaml")

    def update(self):
        """
        Check of the local cache need to be updated based on the ETag value
        """
        # Check for the online tag version
        response = requests.head(self.url, allow_redirects=True)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch excuses from {url}.\
                Status code: {response.status_code}")

        tag = response.headers['etag']

        if not (
            self.etag.exists() and
            self.etag.read_text() == tag and
            self.yaml.exists()
        ):
            if not self.directory.is_dir():
                self.directory.mkdir()

            print(f"Downloading {self.url}")
            response = requests.get(self.url, timeout=10)

            if response.status_code != 200:
                raise ConnectionError(
                    f"Failed to fetch excuses from {url}.\
                        Status code: {response.status_code}")

            decompressed_yaml = lzma.decompress(response.content)

            self.yaml.write_bytes(decompressed_yaml)
            self.etag.write_text(tag)

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
        cache = CachedExcuses(UBUNTU_EXCUSES_URL)

        cache.update()

        return load_excuses(cache.yaml)

    except Exception as e:
        raise RuntimeError(f"Couldn't process excuses.yaml.xz. Exception: {e}")
