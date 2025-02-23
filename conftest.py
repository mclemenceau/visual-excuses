import sys
from pathlib import Path


def pytest_configure(config):
    project_root = Path(__file__).parent
    src_dir = project_root / "visual_excuses"
    sys.path.insert(0, str(src_dir))
