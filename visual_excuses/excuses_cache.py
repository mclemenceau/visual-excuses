import requests
import lzma

from pathlib import Path


if (
    Path(CACHE_ETAG).exists and
    Path(CACHE_ETAG).read_text() == etag and
    Path(CACHE_YAML).exists
):
    print("Everything is here and up to date!")
    print("yaml parser")
else:
    if not Path(CACHE_DIRECTORY).is_dir():
        print(f"{CACHE_DIRECTORY} local cache doesn't exist")
        Path(CACHE_DIRECTORY).mkdir()
        print(f" - Created {CACHE_DIRECTORY}")

    print("Downloading {url} in RAM")
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        raise ConnectionError(
            f"Failed to fetch excuses from {url}.\
                Status code: {response.status_code}")

    print("Decompressing ...")
    # Decompress XZ content
    decompressed_yaml = lzma.decompress(response.content)

    # Write decompressed YAML to a temporary file and use load_excuses()
    Path(CACHE_YAML).write_bytes(decompressed_yaml)
    print(f"Stored {CACHE_YAML}")
    Path(CACHE_ETAG).write_text(etag)
    print(f"Stored {CACHE_ETAG}")

    print("everything should be there now, opening yaml ")