import requests
import lzma
import tempfile

from typing import List

from visual_excuses.excuse import Excuse
from visual_excuses.yaml_parser import load_excuses

ubuntu_excuses_url = (
    "https://people.canonical.com/~ubuntu-archive/proposed-migration/"
    "/update_excuses.yaml.xz"
)


def load_ubuntu_excuses(url: str = ubuntu_excuses_url) -> List[Excuse]:
    """Fetches Ubuntu excuses YAML and parses it into Excuse objects.

    Args:
        url (str, optional): The URL to fetch the excuses file from.
        Defaults to ubuntu_excuses_url.

    Returns:
        List[Excuse]: A list of parsed Excuse objects.
    """
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        raise ConnectionError(
            f"Failed to fetch excuses from {url}.\
                Status code: {response.status_code}")

    try:
        # Decompress XZ content
        decompressed_yaml = lzma.decompress(response.content)

        # Write decompressed YAML to a temporary file and use load_excuses()
        with tempfile.NamedTemporaryFile(
                delete=False,
                mode="wb",
                suffix=".yaml") as temp_file:
            temp_file.write(decompressed_yaml)

        # Use existing YAML parser
        return load_excuses(temp_file.name)

    except Exception as e:
        raise RuntimeError(f"Couldn't process excuses.yaml.xz. Exception: {e}")
