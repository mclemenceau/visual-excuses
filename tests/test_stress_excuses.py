# test against a large excuse file to make sure all corner cases are covered

import pytest
from visual_excuses.yaml_parser import load_excuses


EXCUSES_YAML = "tests/data/update_excuses.yaml"


@pytest.mark.parametrize("excuse", load_excuses(EXCUSES_YAML))
def test_excuse_consistency(excuse):
    """Stress test ftbfs using real data."""
    result = excuse.ftbfs()

    # Check the ftbfs property matches the state of missing_builds
    assert isinstance(result, bool)
    assert result == (len(excuse.missing_builds) > 0)
