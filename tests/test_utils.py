import pytest

from visual_excuses.custom_types import (
    ExcusesData,
    PackagesByTeam,
    UnprocessedExcusesData,
)
from visual_excuses.utils import (
    consume_yaml_excuses,
    search_teams,
)


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


@pytest.fixture
def mock_unprocessed_excuses() -> UnprocessedExcusesData:
    """You can check how the unprocessed data is in visual_excuses/custom_types
    Even though the data has a lot of information, some of them are not used;
    therefore, in the mock below we will ignore:
        generated-date
        sources/component
        sources/is-candidate
        sources/maintainer
        sources/migration-policy-verdict
        sources/policy_info/*
            except sources/policy_info/age/current-age
                   sources/policy_info/update-excuse
        sources/source
    """

    return {
        "sources": [
            # complete
            # reason: autopkgtest -> autopkgtest
            {
                "item-name": "package-name-0",
                "reason": ["autopkgtest", "doesn't matter"],
                "new-version": "0.1.1",
                "old-version": "0.1.0",
                "policy_info": {
                    "age": {"current-age": 42.42},
                    "update-excuse": {
                        "101010": 42,
                        "verdict": "PASS",
                    },
                },
                "excuses": [
                    "whatever",
                    "some string that doesn't matter because it doesn't starts with 'autopkgtest'.",
                    "autopkgtest for some-package/0.42: very long description that includes the word 'Regression'.",
                    "another string that will be ignored",
                ],
            },
            # missing sources/policy_info/
            # reason: autopkgtest -> waiting
            {
                "item-name": "package-name-1",
                "reason": ["will be ignored", "autopkgtest"],
                "new-version": "0.2.3",
                "old-version": "0.2.2",
                "excuses": [
                    "some string that doesn't matter because it doesn't starts with 'autopkgtest'.",
                    "autopkgtest for some-package/0.42: very long description that does not includes the word trigger word.",
                    "another string that will be ignored",
                ],
            },
            # missing sources/policy_info/update-excuse
            # reason: missingbuild -> missingbuild
            {
                "item-name": "package-name-2",
                "reason": ["missingbuild"],
                "new-version": "0.5.0",
                "old-version": "0.4.24",
                "policy_info": {
                    "age": {"current-age": 5.43},
                },
                "missing-builds": {
                    "on-architectures": [
                        "amd64",
                        "arm64",
                    ],
                    "on-unimportant-architectures": [],
                },
            },
            # missing sources/policy_info/age
            # reason: no-binaries -> missingbuild
            {
                "item-name": "package-name-3",
                "reason": ["no-binaries"],
                "new-version": "0.4.2",
                "old-version": "0.4.1",
                "policy_info": {
                    "update-excuse": {"123456": 654321},
                },
            },
            # from now on it is missing sources/policy_info/
            # because it is shorter and it won't increase coverage
            # reason: depends -> depends
            {
                "item-name": "package-name-4",
                "reason": ["will be ignored", "depends", "another one"],
                "new-version": "1.2.3",
                "old-version": "1.2.2",
                "dependencies": {"blocked-by": ["ocaml", "something"]},
            },
            # reason: depends -> unknown
            {
                "item-name": "package-name-5",
                "reason": ["depends"],
                "new-version": "3.2.1",
                "old-version": "3.2.0",
            },
            # reason: implicit-dependency -> depends
            {
                "item-name": "package-name-6",
                "reason": ["will be ignored", "implicit-dependency", "another one"],
                "new-version": "1.2.3",
                "old-version": "1.2.2",
                "dependencies": {"blocked-by": ["coq"]},
            },
            # reason: implicit-dependency -> unknown
            {
                "item-name": "package-name-7",
                "reason": ["implicit-dependency"],
                "new-version": "3.2.1",
                "old-version": "3.2.0",
            },
        ]
    }


@pytest.fixture
def mock_excuses_data() -> ExcusesData:
    return {
        "package-name-0": {
            "name": "package-name-0",
            "reason": "autopkgtest",
            "new-version": "0.1.1",
            "old-version": "0.1.0",
            "age": 42,
            "autopkg-regression": [
                {
                    "pkg": "some-package",
                    "dsc": "autopkgtest for some-package/0.42: very long description that includes the word 'Regression'.",
                }
            ],
            "missing-builds": "",
            "blocked-by": "",
            "migrate-after": "",
            "update-excuse-bugs": [101010],
        },
        "package-name-1": {
            "name": "package-name-1",
            "reason": "waiting",
            "new-version": "0.2.3",
            "old-version": "0.2.2",
            "age": 0,
            "autopkg-regression": [],
            "missing-builds": "",
            "blocked-by": "",
            "migrate-after": "",
            "update-excuse-bugs": [],
        },
        "package-name-2": {
            "name": "package-name-2",
            "reason": "missingbuild",
            "new-version": "0.5.0",
            "old-version": "0.4.24",
            "age": 5,
            "autopkg-regression": [],
            "missing-builds": ["amd64", "arm64"],
            "blocked-by": "",
            "migrate-after": "",
            "update-excuse-bugs": [],
        },
        "package-name-3": {
            "name": "package-name-3",
            "reason": "missingbuild",
            "new-version": "0.4.2",
            "old-version": "0.4.1",
            "age": 0,
            "autopkg-regression": [],
            "missing-builds": ["no binaries on any arch"],
            "blocked-by": "",
            "migrate-after": "",
            "update-excuse-bugs": [123456],
        },
        "package-name-4": {
            "name": "package-name-4",
            "reason": "depends",
            "new-version": "1.2.3",
            "old-version": "1.2.2",
            "age": 0,
            "autopkg-regression": [],
            "missing-builds": "",
            "blocked-by": "ocaml",
            "migrate-after": "",
            "update-excuse-bugs": [],
        },
        "package-name-5": {
            "name": "package-name-5",
            "reason": "unknown",
            "new-version": "3.2.1",
            "old-version": "3.2.0",
            "age": 0,
            "autopkg-regression": [],
            "missing-builds": "",
            "blocked-by": "",
            "migrate-after": "",
            "update-excuse-bugs": [],
        },
        "package-name-6": {
            "name": "package-name-6",
            "reason": "depends",
            "new-version": "1.2.3",
            "old-version": "1.2.2",
            "age": 0,
            "autopkg-regression": [],
            "missing-builds": "",
            "blocked-by": "coq",
            "migrate-after": "",
            "update-excuse-bugs": [],
        },
        "package-name-7": {
            "name": "package-name-7",
            "reason": "unknown",
            "new-version": "3.2.1",
            "old-version": "3.2.0",
            "age": 0,
            "autopkg-regression": [],
            "missing-builds": "",
            "blocked-by": "",
            "migrate-after": "",
            "update-excuse-bugs": [],
        },
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


def test_consume_yaml_excuses(mock_unprocessed_excuses, mock_excuses_data):
    current = consume_yaml_excuses(mock_unprocessed_excuses)
    expected = mock_excuses_data
    assert current == expected
