import sys
import json
import requests
from typing import List
from email.utils import formatdate
from shutil import copyfileobj
from pathlib import Path

from .const import DEFAULT_CACHE_DIR, UBUNTU_TEAMS_MAPPING_URL


class UbuntuTeamMapping:
    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR):
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.etag = cache_dir / "teams.json.etag"
        self.data = cache_dir / "teams.json"
        self.update()

    def update(self):
        """
        Check if the local cache requires refreshing
        """
        headers = {}
        if self.etag.exists() and self.data.exists():
            headers['If-None-Match'] = self.etag.read_text()
            headers['If-Modified-Since'] = formatdate(
                self.data.stat().st_mtime, usegmt=True)
        response = requests.get(
            UBUNTU_TEAMS_MAPPING_URL, timeout=10, stream=True,
            headers=headers)
        response.raise_for_status()

        if response.status_code == 200:
            print(f"Downloading {UBUNTU_TEAMS_MAPPING_URL}", file=sys.stderr)
            with self.data.open('wb') as target:
                copyfileobj(response.raw, target)
            self.etag.write_text(response.headers['ETag'])
        elif response.status_code == 304:
            # Not changed according to ETag/modified date
            pass
        else:
            raise ValueError(
                f'Unexpected HTTP response status {response.status_code}')

        with self.data.open('r') as source:
            self.mapping = json.load(source)

    def get_teams(self, package: str) -> List[str]:
        # return teams assigned to a single package
        teams = []
        for team, packages in self.mapping.items():
            if package in packages:
                teams.append(team)

        return teams

    def default_team(self, package: str) -> str:
        # This function will return the first team subscribed
        teams = self.get_teams(package)
        return teams[0] if teams else ""
