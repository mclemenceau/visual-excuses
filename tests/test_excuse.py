import pytest
# from unittest.mock import patch, Mock

from visual_excuses.excuse import Excuse


def test_excuse_is_ftbfs_with_missing_builds():
    excuse = Excuse(
        item_name="example",
        component="universe",
        new_version="1.2",
        missing_builds=["arm64", "ppc64el"]
    )
    assert excuse.ftbfs() is True


def test_excuse_is_not_ftbfs_with_no_missing_builds():
    excuse = Excuse(
        item_name="example",
        component="universe",
        new_version="1.2",
        missing_builds=[]
    )
    assert not excuse.ftbfs()
