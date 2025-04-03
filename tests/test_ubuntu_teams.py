import pytest
from unittest.mock import patch, Mock

from visual_excuses.ubuntu_teams import UbuntuTeamMapping

FAKE_MAPPING = {
    "team-a": ["bash", "glibc", "dbus"],
    "team-b": ["gnome", "dbus", "ptyxis"],
    "team-c": ["kernel"]
}


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        yield mock_get


def test_init_succes_with_mapping(mock_requests_get):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = FAKE_MAPPING
    mock_requests_get.return_value = mock_response

    team_mapping = UbuntuTeamMapping()

    assert (team_mapping.mapping == FAKE_MAPPING)


def test_init_failure_without_connection(mock_requests_get):

    mock_response = Mock()
    mock_response.status_code = 404
    mock_requests_get.return_value = mock_response

    with pytest.raises(RuntimeError, match="Failed to load Ubuntu team "):
        UbuntuTeamMapping()


def test_get_teams_returns_correct_teams_for_package(mock_requests_get):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = FAKE_MAPPING
    mock_requests_get.return_value = mock_response

    team_mapping = UbuntuTeamMapping()

    assert team_mapping.get_teams("bash") == ["team-a"]
    assert team_mapping.get_teams("gnome") == ["team-b"]
    assert team_mapping.get_teams("dbus") == ["team-a", "team-b"]


def test_get_teams_returns_empty_list_teams_for_unknown_package(
        mock_requests_get):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = FAKE_MAPPING
    mock_requests_get.return_value = mock_response

    team_mapping = UbuntuTeamMapping()

    assert team_mapping.get_teams("vim") == []


def test_default_team_returns_first_team(mock_requests_get):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = FAKE_MAPPING
    mock_requests_get.return_value = mock_response

    team_mapping = UbuntuTeamMapping()

    assert team_mapping.default_team("bash") == "team-a"
    assert team_mapping.default_team("gnome") == "team-b"
    assert team_mapping.default_team("dbus") == "team-a"


def test_default_team_returns_empty_string_if_no_teams(mock_requests_get):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = FAKE_MAPPING
    mock_requests_get.return_value = mock_response

    team_mapping = UbuntuTeamMapping()

    assert team_mapping.default_team("vim") == ""
