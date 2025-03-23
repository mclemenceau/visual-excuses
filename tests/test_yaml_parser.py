import pytest
import tempfile
import os
from visual_excuses.yaml_parser import load_excuses
from visual_excuses.excuse import Excuse
import yaml

VALID_YAML = {
    "sources": [
        {
            "item-name": "example",
            "component": "universe",
            "new-version": "1.0",
            "missing-builds": {
                "on-architectures": ["amd64"],
                "on-unimportant-architectures": []
            }
        }
    ]
}


INVALID_YAML_CONTENT = """
sources:
  - item-name: test
    new-version: [not valid YAML  # missing closing bracket and structure
"""


def test_load_excuses_valid_file():
    """Test loading valid YAML with expected structure."""
    with tempfile.NamedTemporaryFile("w+", suffix=".yaml", delete=False) as f:
        yaml.dump(VALID_YAML, f)
        f.flush()
        path = f.name

    excuses = load_excuses(path)

    assert len(excuses) == 1
    assert isinstance(excuses[0], Excuse)
    assert excuses[0].item_name == "example"
    assert excuses[0].component == "universe"
    assert excuses[0].new_version == "1.0"
    assert excuses[0].missing_builds == ["amd64"]

    os.remove(path)


def test_load_excuses_missing_file():
    """Test behavior when the YAML file does not exist."""
    with pytest.raises(FileNotFoundError):
        load_excuses("non_existent_file.yaml")


def test_load_excuses_invalid_yaml():
    """Test behavior when the YAML content is invalid."""
    with tempfile.NamedTemporaryFile("w+", suffix=".yaml", delete=False) as f:
        f.write(INVALID_YAML_CONTENT)
        f.flush()
        path = f.name

    with pytest.raises(yaml.YAMLError):
        load_excuses(path)

    os.remove(path)
