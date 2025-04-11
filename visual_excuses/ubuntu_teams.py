import requests
from typing import List

UBUNTU_TEAMS_MAPPING_URL = (
    "http://reqorts.qa.ubuntu.com/reports/m-r-package-team-mapping.json"
)


class UbuntuTeamMapping:
    def __init__(self):
        # retrieve distro teams and packages information
        response = requests.get(UBUNTU_TEAMS_MAPPING_URL)
        if response.status_code == 200:
            self.mapping = response.json()
        else:
            raise RuntimeError("Failed to load Ubuntu team mapping.")

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
