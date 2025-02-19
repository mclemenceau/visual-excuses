import pytest

from visual_excuses.custom_types import (
    ExcusesData,
    PackagesByTeam,
    UnprocessedExcusesData,
)
from visual_excuses.utils import (
    consume_yaml_excuses,
    create_visual_excuses,
    search_teams,
)


@pytest.fixture
def mock_packages_by_team() -> PackagesByTeam:
    return {
        "team-0": [
            "package-name-5",
            "package-name-1",
            "package-name-7",
        ],
        "team-1": [],
        "team-2": [
            "package-name-1",  # added to have multiple teams with same package
            "package-name-2",
            "package-name-3",
        ],
        "team-3": [
            "package-name-4",
            "package-name-0",
            "package-name-6",
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
    current = search_teams("package-name-1", mock_packages_by_team)
    expected = ["team-0", "team-2"]
    assert len(current) == 2
    assert set(current) == set(expected)


def test_search_teams_single(mock_packages_by_team):
    current = search_teams("package-name-0", mock_packages_by_team)
    expected = ["team-3"]
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


def test_create_visual_excuses_all_teams_and_any_age(
    mock_excuses_data, mock_packages_by_team
):
    graph = create_visual_excuses(
        mock_excuses_data, "mock_url.com/tests", mock_packages_by_team
    )
    current_nodes = graph.nodes
    current_edges = graph.edges
    expected_nodes = [
        {
            "color": "#DBBF60",
            "title": 'autopkgtest depends failures<br />More info in <a href="https://bugs.launchpad.net/bugs/101010">101010</a>.<br />42 days old<br /><a href="https://launchpad.net/ubuntu/+source/package-name-0">package-name-0</a>',
            "age": 42,
            "id": "package-name-0",
            "label": "package-name-0",
            "shape": "dot",
        },
        {
            "color": "#8B8985",
            "title": "team-3",
            "size": 20,
            "id": "team-3",
            "label": "team-3",
            "shape": "box",
        },
        {
            "color": "#d4713b",
            "title": "autopkgtest for some-package/0.42: very long description that includes the word 'Regression'.<br />More info in <a href=\"https://bugs.launchpad.net/bugs/101010\">101010</a>.",
            "id": "some-package",
            "label": "some-package",
            "shape": "dot",
        },
        {
            "color": "#CD6155",
            "title": "<b>Missing builds: </b> ['amd64', 'arm64']<br />5 days old<br /><a href=\"https://launchpad.net/ubuntu/+source/package-name-2\">package-name-2</a>",
            "age": 5,
            "id": "package-name-2",
            "label": "package-name-2",
            "shape": "dot",
        },
        {
            "color": "#8B8985",
            "title": "team-2",
            "size": 20,
            "id": "team-2",
            "label": "team-2",
            "shape": "box",
        },
        {
            "color": "#CD6155",
            "title": '<b>Missing builds: </b> [\'no binaries on any arch\']<br />More info in <a href="https://bugs.launchpad.net/bugs/123456">123456</a>.<br />0 days old<br /><a href="https://launchpad.net/ubuntu/+source/package-name-3">package-name-3</a>',
            "age": 0,
            "id": "package-name-3",
            "label": "package-name-3",
            "shape": "dot",
        },
        {
            "color": "#FAD7A0",
            "title": 'Blocked by ocaml<br />0 days old<br /><a href="https://launchpad.net/ubuntu/+source/package-name-4">package-name-4</a>',
            "age": 0,
            "id": "package-name-4",
            "label": "package-name-4",
            "shape": "dot",
        },
        {
            "color": "#DC7633",
            "title": "Unknown at this time <a href=mock_url.com/tests/update_excuses.html#package-name-4>see details</a>",
            "id": "ocaml",
            "label": "ocaml",
            "shape": "dot",
        },
        {
            "color": "#FFFFFF",
            "title": 'Unknown at this time <a href=mock_url.com/tests/update_excuses.html#package-name-5>see details</a><br />0 days old<br /><a href="https://launchpad.net/ubuntu/+source/package-name-5">package-name-5</a>',
            "age": 0,
            "id": "package-name-5",
            "label": "package-name-5",
            "shape": "dot",
        },
        {
            "color": "#8B8985",
            "title": "team-0",
            "size": 20,
            "id": "team-0",
            "label": "team-0",
            "shape": "box",
        },
        {
            "color": "#FAD7A0",
            "title": 'Blocked by coq<br />0 days old<br /><a href="https://launchpad.net/ubuntu/+source/package-name-6">package-name-6</a>',
            "age": 0,
            "id": "package-name-6",
            "label": "package-name-6",
            "shape": "dot",
        },
        {
            "color": "#DC7633",
            "title": "Unknown at this time <a href=mock_url.com/tests/update_excuses.html#package-name-6>see details</a>",
            "id": "coq",
            "label": "coq",
            "shape": "dot",
        },
        {
            "color": "#FFFFFF",
            "title": 'Unknown at this time <a href=mock_url.com/tests/update_excuses.html#package-name-7>see details</a><br />0 days old<br /><a href="https://launchpad.net/ubuntu/+source/package-name-7">package-name-7</a>',
            "age": 0,
            "id": "package-name-7",
            "label": "package-name-7",
            "shape": "dot",
        },
    ]
    expected_edges = [
        {"from": "team-3", "to": "package-name-0", "arrows": "to"},
        {
            "color": "#2E86C1",
            "from": "package-name-0",
            "to": "some-package",
            "arrows": "to",
        },
        {"from": "team-2", "to": "package-name-2", "arrows": "to"},
        {"from": "team-2", "to": "package-name-3", "arrows": "to"},
        {"from": "team-3", "to": "package-name-4", "arrows": "to"},
        {"color": "#FAD7A0", "from": "package-name-4", "to": "ocaml", "arrows": "to"},
        {"from": "team-0", "to": "package-name-5", "arrows": "to"},
        {"from": "team-3", "to": "package-name-6", "arrows": "to"},
        {"color": "#FAD7A0", "from": "package-name-6", "to": "coq", "arrows": "to"},
        {"from": "team-0", "to": "package-name-7", "arrows": "to"},
    ]
    assert len(current_nodes) == 13
    assert current_nodes == expected_nodes
    assert len(current_edges) == 10
    assert current_edges == expected_edges


def test_create_visual_excuses_single_team_and_any_age(
    mock_excuses_data, mock_packages_by_team
):
    graph = create_visual_excuses(
        mock_excuses_data, "mock_url.com/tests", mock_packages_by_team, "team-0"
    )
    current_nodes = graph.nodes
    current_edges = graph.edges
    expected_nodes = [
        {
            "color": "#FFFFFF",
            "title": 'Unknown at this time <a href=mock_url.com/tests/update_excuses.html#package-name-5>see details</a><br />0 days old<br /><a href="https://launchpad.net/ubuntu/+source/package-name-5">package-name-5</a>',
            "age": 0,
            "id": "package-name-5",
            "label": "package-name-5",
            "shape": "dot",
        },
        {
            "color": "#8B8985",
            "title": "team-0",
            "size": 20,
            "id": "team-0",
            "label": "team-0",
            "shape": "box",
        },
        {
            "color": "#FFFFFF",
            "title": 'Unknown at this time <a href=mock_url.com/tests/update_excuses.html#package-name-7>see details</a><br />0 days old<br /><a href="https://launchpad.net/ubuntu/+source/package-name-7">package-name-7</a>',
            "age": 0,
            "id": "package-name-7",
            "label": "package-name-7",
            "shape": "dot",
        },
    ]
    expected_edges = [
        {"from": "team-0", "to": "package-name-5", "arrows": "to"},
        {"from": "team-0", "to": "package-name-7", "arrows": "to"},
    ]
    assert len(current_nodes) == 3
    assert current_nodes == expected_nodes
    assert len(current_edges) == 2
    assert current_edges == expected_edges


def test_create_visual_excuses_all_teams_and_older_than_1(
    mock_excuses_data, mock_packages_by_team
):
    graph = create_visual_excuses(
        mock_excuses_data, "mock_url.com/tests", mock_packages_by_team, age=1
    )
    current_nodes = graph.nodes
    current_edges = graph.edges
    expected_nodes = [
        {
            "color": "#DBBF60",
            "title": 'autopkgtest depends failures<br />More info in <a href="https://bugs.launchpad.net/bugs/101010">101010</a>.<br />42 days old<br /><a href="https://launchpad.net/ubuntu/+source/package-name-0">package-name-0</a>',
            "age": 42,
            "id": "package-name-0",
            "label": "package-name-0",
            "shape": "dot",
        },
        {
            "color": "#8B8985",
            "title": "team-3",
            "size": 20,
            "id": "team-3",
            "label": "team-3",
            "shape": "box",
        },
        {
            "color": "#d4713b",
            "title": "autopkgtest for some-package/0.42: very long description that includes the word 'Regression'.<br />More info in <a href=\"https://bugs.launchpad.net/bugs/101010\">101010</a>.",
            "id": "some-package",
            "label": "some-package",
            "shape": "dot",
        },
        {
            "color": "#CD6155",
            "title": "<b>Missing builds: </b> ['amd64', 'arm64']<br />5 days old<br /><a href=\"https://launchpad.net/ubuntu/+source/package-name-2\">package-name-2</a>",
            "age": 5,
            "id": "package-name-2",
            "label": "package-name-2",
            "shape": "dot",
        },
        {
            "color": "#8B8985",
            "title": "team-2",
            "size": 20,
            "id": "team-2",
            "label": "team-2",
            "shape": "box",
        },
    ]
    expected_edges = [
        {"from": "team-3", "to": "package-name-0", "arrows": "to"},
        {
            "color": "#2E86C1",
            "from": "package-name-0",
            "to": "some-package",
            "arrows": "to",
        },
        {"from": "team-2", "to": "package-name-2", "arrows": "to"},
    ]
    assert len(current_nodes) == 5
    assert current_nodes == expected_nodes
    assert len(current_edges) == 3
    assert current_edges == expected_edges
