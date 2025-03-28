import pytest
import lzma
from unittest.mock import patch, Mock

from visual_excuses.excuse import Excuse
from visual_excuses.ubuntu_excuses_loader import load_ubuntu_excuses

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


@pytest.fixture
def mock_requests_get():
    """Fixture to mock requests.get() globally."""
    with patch("requests.get") as mock_get:
        yield mock_get


@pytest.fixture
def mock_load_excuses():
    """Fixture to mock load_excuses() instead of actually parsing YAML."""
    with patch(
        "visual_excuses.ubuntu_excuses_loader.load_excuses"
    ) as mock_parser:
        yield mock_parser


def test_load_ubuntu_excuses_success(mock_requests_get, mock_load_excuses):
    """Test successful fetch, decompress, and parse of Ubuntu excuses."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = COMPRESSED_YAML
    mock_requests_get.return_value = mock_response

    # Mock load_excuses to return a fake parsed output
    mock_load_excuses.return_value = [
        Excuse(
            item_name="example-package",
            component="universe",
            old_version="1.0",
            new_version="1.1",
            missing_builds=[]
        ),
    ]

    excuses = load_ubuntu_excuses()

    assert len(excuses) == 1
    assert excuses[0].item_name == "example-package"
    assert excuses[0].component == "universe"
    assert excuses[0].new_version == "1.1"

    # Ensure load_excuses was called correctly
    mock_load_excuses.assert_called_once()


def test_load_ubuntu_excuses_http_error(mock_requests_get):
    """Test handling of an HTTP error (e.g., 404)."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_requests_get.return_value = mock_response

    with pytest.raises(ConnectionError, match="Failed to fetch excuses from"):
        load_ubuntu_excuses()


def test_load_ubuntu_excuses_invalid_xz(mock_requests_get):
    """Test handling of invalid .xz file response."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"invalid compressed data"
    mock_requests_get.return_value = mock_response

    with pytest.raises(RuntimeError, match="Couldn't process excuses.yaml.xz"):
        load_ubuntu_excuses()
