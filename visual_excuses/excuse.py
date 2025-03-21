from dataclasses import dataclass
from typing import List


@dataclass
class Excuse:
    """Represents an excuse for a package migration in Debian/Ubuntu UDD.

    Attributes:
        item_name (str): The name of the package.
        component (str): The repository component (e.g., 'universe').
        new_version (str): The new version of the package.
        missing_builds (List[str]): listof missing architectures build for that
            package
    """

    item_name: str
    component: str
    new_version: str
    missing_builds: List[str]

    def ftbfs(self) -> bool:
        """Check if excuse is an FTBFS excuse

        Returns:
            bool: True is the excuse is an FTBFS
        """
        return len(self.missing_builds) > 0
