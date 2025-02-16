import pytest

from visual_excuses.custom_types import PackagesByTeam
from visual_excuses.utils import search_teams


@pytest.fixture
def mock_packages_by_team() -> PackagesByTeam:
    return {
        "canonical-mainstream": [
            "oem-qemu-meta",
            "oem-somerville-aipom-adl-meta",
            "oem-somerville-arbok-meta",
            "oem-somerville-arcanine-14-meta",
            "oem-somerville-arcanine-meta",
            "oem-somerville-beedrill-meta",
            "oem-somerville-beric-amd-meta",
            "oem-somerville-beric-icl-meta",
            "oem-somerville-beric-tgl-meta",
            "oem-somerville-blastoise-meta",
            "oem-somerville-bowen-meta",
            "oem-somerville-bronn-meta",
        ],
        "canonical-support": [],
        "canonical-ubuntu-qa": [
            "autopkgtest",
            "openqa",
            "os-autoinst",
            "retry",
            "alsa-driver",  # added to have multiple teams with same package
        ],
        "desktop-packages": [
            "aalib",
            "abseil",
            "accountsservice",
            "adsys",
            "adwaita-icon-theme",
            "aisleriot",
            "alsa-driver",
            "alsa-plugins",
            "alsa-utils",
            "amtk",
            "apg",
            "appconfig",
            "appstream",
            "appstream-glib",
            "aspell",
            "aspell-en",
        ],
    }


def test_search_teams_multiple(mock_packages_by_team):
    current = search_teams("alsa-driver", mock_packages_by_team)
    expected = ["desktop-packages", "canonical-ubuntu-qa"]
    assert len(current) == 2
    assert set(current) == set(expected)


def test_search_teams_single(mock_packages_by_team):
    current = search_teams("oem-qemu-meta", mock_packages_by_team)
    expected = ["canonical-mainstream"]
    assert len(current) == 1
    assert current == expected


def test_search_teams_empty(mock_packages_by_team):
    current = search_teams("not-a-package", mock_packages_by_team)
    expected = []
    assert len(current) == 0
    assert current == expected
