import io
import json
from unittest.mock import patch, Mock

import pytest

from visual_excuses.ubuntu_teams import UbuntuTeamMapping

FAKE_MAPPING = {
    "team-a": ["bash", "glibc", "dbus"],
    "team-b": ["gnome", "dbus", "ptyxis"],
    "team-c": ["kernel"]
}
FAKE_MAPPING_RAW = json.dumps(FAKE_MAPPING).encode('utf-8')


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        yield mock_get


def test_init_succes_with_mapping(tmp_path, mock_requests_get):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {'ETag': 'foo'}
    mock_response.raw = io.BytesIO(FAKE_MAPPING_RAW)
    mock_requests_get.return_value = mock_response

    team_mapping = UbuntuTeamMapping(cache_dir=tmp_path)

    assert (team_mapping.mapping == FAKE_MAPPING)


def test_init_failure_without_connection(tmp_path, mock_requests_get):

    mock_response = Mock()
    mock_response.status_code = 404
    mock_requests_get.return_value = mock_response

    with pytest.raises(ValueError, match="Unexpected HTTP response "):
        UbuntuTeamMapping(cache_dir=tmp_path)


def test_get_teams_returns_correct_teams_for_package(
        tmp_path, mock_requests_get):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {'ETag': 'foo'}
    mock_response.raw = io.BytesIO(FAKE_MAPPING_RAW)
    mock_requests_get.return_value = mock_response

    team_mapping = UbuntuTeamMapping(cache_dir=tmp_path)

    assert team_mapping.get_teams("bash") == ["team-a"]
    assert team_mapping.get_teams("gnome") == ["team-b"]
    assert team_mapping.get_teams("dbus") == ["team-a", "team-b"]


def test_get_teams_returns_empty_list_teams_for_unknown_package(
        tmp_path, mock_requests_get):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {'ETag': 'foo'}
    mock_response.raw = io.BytesIO(FAKE_MAPPING_RAW)
    mock_requests_get.return_value = mock_response

    team_mapping = UbuntuTeamMapping(cache_dir=tmp_path)

    assert team_mapping.get_teams("vim") == []


def test_default_team_returns_first_team(tmp_path, mock_requests_get):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {'ETag': 'foo'}
    mock_response.raw = io.BytesIO(FAKE_MAPPING_RAW)
    mock_requests_get.return_value = mock_response

    team_mapping = UbuntuTeamMapping(cache_dir=tmp_path)

    assert team_mapping.default_team("bash") == "team-a"
    assert team_mapping.default_team("gnome") == "team-b"
    assert team_mapping.default_team("dbus") == "team-a"


def test_default_team_returns_empty_string_if_no_teams(
        tmp_path, mock_requests_get):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {'ETag': 'foo'}
    mock_response.raw = io.BytesIO(FAKE_MAPPING_RAW)
    mock_requests_get.return_value = mock_response

    team_mapping = UbuntuTeamMapping(cache_dir=tmp_path)

    assert team_mapping.default_team("vim") == ""
