import os
from pathlib import Path

UBUNTU_EXCUSES_URL = (
    "https://ubuntu-archive-team.ubuntu.com/proposed-migration/"
    "update_excuses.yaml.xz"
)

UBUNTU_TEAMS_MAPPING_URL = (
    "http://reqorts.qa.ubuntu.com/reports/m-r-package-team-mapping.json"
)

CACHE_HOME = os.environ.get('XDG_CACHE_HOME', '~/.cache')
DEFAULT_CACHE_DIR = Path(CACHE_HOME).expanduser() / 'visual-excuses'
del CACHE_HOME
