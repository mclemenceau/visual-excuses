import sys
import lzma
from pathlib import Path
from typing import List, Optional
from email.utils import formatdate
from shutil import copyfileobj

import requests

from .const import DEFAULT_CACHE_DIR, UBUNTU_EXCUSES_URL
from .excuse import Excuse
from .yaml_parser import load_excuses


class CachedExcuses:
    """
    CachedExcuses will facilitae the download, decompression and storage for
    the Ubuntu Excuses file.
    CachedExcuses will only download new excuses if the version in the cached
    folder is outdated
    """
    def __init__(self, url: str, cache_dir: Path = DEFAULT_CACHE_DIR):
        self.url = url
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.etag = cache_dir / "excuse.yaml.etag"
        self.yaml = cache_dir / "excuse.yaml"

    def update(self):
        """
        Check of the local cache need to be updated based on the ETag value
        """
        headers = {}
        if self.etag.exists() and self.yaml.exists():
            headers['If-None-Match'] = self.etag.read_text()
            headers['If-Modified-Since'] = formatdate(
                self.yaml.stat().st_mtime, usegmt=True)
        response = requests.head(self.url, timeout=10, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(
                "Error accessing excuses yaml data from server: "
                f"{e.response.status_code} - {e.response.reason}",
                file=sys.stderr)
            return

        if response.status_code == 200:
            if response.headers['ETag'] != headers.get('If-None-Match', ''):
                print(f"Downloading {self.url}", file=sys.stderr)
                response = requests.get(
                    self.url, timeout=10, stream=True, headers=headers)
                response.raise_for_status()
                with (
                    lzma.LZMAFile(response.raw) as source,
                    self.yaml.open('wb') as target
                ):
                    copyfileobj(source, target)
                self.etag.write_text(response.headers['ETag'])
        elif response.status_code == 304:
            # Not changed according to ETag/If-Modified-Since
            pass
        else:
            raise ValueError(
                f'Unexpected HTTP response status {response.status_code}')


def load_ubuntu_excuses(
    url: str = UBUNTU_EXCUSES_URL,
    cache_dir: Optional[Path] = DEFAULT_CACHE_DIR
) -> List[Excuse]:
    """Fetches Ubuntu excuses YAML and parses it into Excuse objects.

    Args:
        url (str, optional): The URL to fetch the excuses file from.
        Defaults to ubuntu_excuses_url.

    Returns:
        List[Excuse]: A list of parsed Excuse objects.
    """
    cache = CachedExcuses(url, cache_dir)
    cache.update()
    try:
        return load_excuses(cache.yaml)
    except FileNotFoundError:
        print("No excuse data to consume", file=sys.stderr)
        return []
