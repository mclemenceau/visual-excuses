import pytest
import lzma
from unittest.mock import patch, Mock

from visual_excuses.excuse import Excuse
from visual_excuses.ubuntu_excuses_loader \
    import CachedExcuses, load_ubuntu_excuses


@pytest.fixture
def mocker():
    pass


def test_is_cache_valid_returns_true_if_both_files_exist_and_match(tmp_path):
    etag = "1234"

    etag_path = tmp_path / "ETag"
    yaml_path = tmp_path / "excuse.yaml"

    etag_path.write_text(etag)
    yaml_path.write_text("mock: yaml")

    cache = CachedExcuses(url="http://notneeded.com", cache_dir=tmp_path)

    assert cache._is_cache_valid(etag) is True


def test_is_cache_valid_returns_false_if_etag_file_missing(tmp_path):

    etag = "1234"
    yaml_path = tmp_path / "excuse.yaml"
    yaml_path.write_text("mock: yaml")

    cache = CachedExcuses(url="http://notneeded.com", cache_dir=tmp_path)

    assert cache._is_cache_valid(etag) is False


def test_is_cache_valid_returns_false_if_yaml_missing(tmp_path):
    etag = "1234"

    etag_path = tmp_path / "ETag"
    etag_path.write_text(etag)

    cache = CachedExcuses(url="http://notneeded.com", cache_dir=tmp_path)

    assert cache._is_cache_valid(etag) is False


@pytest.fixture
def mock_requests_head():
    with patch("requests.head") as mock_head:
        yield mock_head


def test_fetch_remote_etag_returns_etag_on_success(
        tmp_path, mock_requests_head):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {"etag": "1234"}
    mock_requests_head.return_value = mock_response

    cache = CachedExcuses(url="http://notneeded.com", cache_dir=tmp_path)

    assert cache._fetch_remote_etag() == "1234"


def test_fetch_remote_etag_raises_on_missing_etag(
        tmp_path, mock_requests_head):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {"tag": "wrong"}
    mock_requests_head.return_value = mock_response

    cache = CachedExcuses(url="http://notneeded.com", cache_dir=tmp_path)

    with pytest.raises(ValueError, match="ETag header missing from"):
        cache._fetch_remote_etag()    


def test_fetch_remote_etag_raises_on_http_error(
        tmp_path, mock_requests_head):

    mock_response = Mock()
    mock_response.status_code = 404
    mock_requests_head.return_value = mock_response

    cache = CachedExcuses(url="http://notneeded.com", cache_dir=tmp_path)

    with pytest.raises(ConnectionError, match="Failed to fetch etag from"):
        cache._fetch_remote_etag()    


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        yield mock_get


# Sample valid YAML content (as bytes)
VALID_YAML = b"""
sources:
- component: universe
  item-name: example-package
  old-version: 1.0
  new-version: 1.1
  missing-builds: []
"""

# Compressed version of the YAML in .xz format
COMPRESSED_YAML = lzma.compress(VALID_YAML)


def test_fetch_and_cache_downloads_and_writes_files(
        tmp_path, mock_requests_get):

    etag = "1234"

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = COMPRESSED_YAML
    mock_requests_get.return_value = mock_response

    cache = CachedExcuses(url="http://notneeded.com", cache_dir=tmp_path)

    cache._fetch_and_cache(etag)

    assert cache.etag.read_text() == etag
    assert cache.yaml.read_bytes() == VALID_YAML


def test_fetch_and_cache_fails_without_connection(
        tmp_path, mock_requests_get):

    etag = "1234"

    mock_response = Mock()
    mock_response.status_code = 404
    mock_requests_get.return_value = mock_response

    cache = CachedExcuses(url="http://notneeded.com", cache_dir=tmp_path)

    with pytest.raises(ConnectionError, match="Failed to fetch excuses from "):
        cache._fetch_and_cache(etag)


def test_update_skips_download_if_cache_is_valid(tmp_path):

    cache = CachedExcuses(url="http://notneeded.com", cache_dir=tmp_path)

    with (
        patch.object(
            cache, "_fetch_remote_etag", return_value="1234"
        ) as mock_etag,
        patch.object(
            cache, "_is_cache_valid", return_value=True
        ) as mock_valid,
        patch.object(cache, "_fetch_and_cache") as mock_fetch
    ):
        cache.update()

        mock_etag.assert_called_once()
        mock_valid.assert_called_once_with("1234")
        mock_fetch.assert_not_called()


def test_update_downloads_if_cache_invalid(tmp_path):
    cache = CachedExcuses(url="http://notneeded.com", cache_dir=tmp_path)

    with (
        patch.object(
            cache, "_fetch_remote_etag", return_value="1234"
        ) as mock_etag,
        patch.object(
            cache, "_is_cache_valid", return_value=False
        ) as mock_valid,
        patch.object(cache, "_fetch_and_cache") as mock_fetch,
        patch.object(cache, "directory") as mock_directory
    ):
        cache.update()

        mock_etag.assert_called_once()
        mock_valid.assert_called_once_with("1234")
        mock_directory.mkdir.assert_called_once_with(
            parents=True, exist_ok=True)
        mock_fetch.assert_called_once_with("1234")


def test_load_ubuntu_excuses_returns_parsed_objects(tmp_path):
    with (
        patch(
            "visual_excuses.ubuntu_excuses_loader.CachedExcuses"
        ) as mock_class,
        patch(
            "visual_excuses.ubuntu_excuses_loader.load_excuses"
            ) as mock_loader
    ):
        mock_instance = mock_class.return_value
        mock_instance.yaml = tmp_path / "excuse.yaml"
        mock_instance.update.return_value = None
        mock_loader.return_value = ["excuse"]

        excuses = load_ubuntu_excuses("url")

        mock_instance.update.assert_called_once()
        mock_loader.assert_called_once_with(mock_instance.yaml)
        assert len(excuses) == 1
        assert excuses[0] == "excuse"


def test_load_ubuntu_excuses_raises_runtime_error_on_failure():
    with (
        patch(
            "visual_excuses.ubuntu_excuses_loader.CachedExcuses"
        ) as mock_class
    ):
        mock_instance = mock_class.return_value
        mock_instance.update.side_effect = Exception("Failure!")

        with pytest.raises(RuntimeError, match="Couldn't process excuses.yaml.xz"):
            load_ubuntu_excuses("url")
