import io
import lzma
from unittest.mock import patch, Mock

import pytest

from visual_excuses.ubuntu_excuses_loader \
    import CachedExcuses, load_ubuntu_excuses


@pytest.fixture(scope='session')
def excuses_yaml():
    data = b"""
sources:
- component: universe
  item-name: example-package
  old-version: 1.0
  new-version: 1.1
  missing-builds: {}
"""
    return lzma.compress(data), data


def test_cache_uncached(tmp_path, excuses_yaml):
    compressed, uncompressed = excuses_yaml

    with patch('visual_excuses.ubuntu_excuses_loader.requests.get') as get:
        response = Mock()
        response.status_code = 200
        response.headers = {'ETag': 'foo'}
        response.raw = io.BytesIO(compressed)
        response.raise_for_status.return_value = None
        get.return_value = response

        cache = CachedExcuses(
            'http://example.com/excuses.yaml.xz', cache_dir=tmp_path)
        assert not cache.etag.exists()
        assert not cache.yaml.exists()
        cache.update()
        assert cache.etag.exists()
        assert cache.etag.read_text() == 'foo'
        assert cache.yaml.exists()
        assert cache.yaml.read_bytes() == uncompressed


def test_cache_cached(tmp_path, excuses_yaml):
    compressed, uncompressed = excuses_yaml

    with patch('visual_excuses.ubuntu_excuses_loader.requests.get') as get:
        response = Mock()
        response.status_code = 304
        response.headers = {'ETag': 'foo'}
        response.raw = io.BytesIO(b'')
        response.raise_for_status.return_value = None
        get.return_value = response

        cache = CachedExcuses(
            'http://example.com/excuses.yaml.xz', cache_dir=tmp_path)
        cache.etag.write_text('foo')
        cache.yaml.write_bytes(uncompressed)
        cache.update()
        assert cache.etag.exists()
        assert cache.etag.read_text() == 'foo'
        assert cache.yaml.exists()
        assert cache.yaml.read_bytes() == uncompressed


def test_cache_unexpected(tmp_path, excuses_yaml):
    compressed, uncompressed = excuses_yaml

    with patch('visual_excuses.ubuntu_excuses_loader.requests.get') as get:
        response = Mock()
        response.status_code = 201
        response.headers = {'ETag': 'foo'}
        response.raw = io.BytesIO(b'')
        response.raise_for_status.return_value = None
        get.return_value = response

        cache = CachedExcuses(
            'http://example.com/excuses.yaml.xz', cache_dir=tmp_path)
        with pytest.raises(ValueError):
            cache.update()


def test_load_ubuntu_excuses(tmp_path, excuses_yaml):
    compressed, uncompressed = excuses_yaml

    with patch('visual_excuses.ubuntu_excuses_loader.requests.get') as get:
        response = Mock()
        response.status_code = 200
        response.headers = {'ETag': 'foo'}
        response.raw = io.BytesIO(compressed)
        response.raise_for_status.return_value = None
        get.return_value = response

        excuses = load_ubuntu_excuses(
            'http://example.com/excuses.yaml.xz', cache_dir=tmp_path)
        assert len(excuses) == 1
        assert excuses[0].component == 'universe'
        assert excuses[0].new_version == '1.1'
