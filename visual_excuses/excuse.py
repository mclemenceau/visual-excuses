from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Excuse:
    """Represents an excuse for a package migration in Debian/Ubuntu UDD.

    Attributes:
        item_name (str): The name of the package.
        component (str): The repository component (e.g., 'universe').
        new_version (str): The new version of the package.
        missing_builds (List[str]): list of missing architectures builds
        reason (str): The reason migration has failed
    """

    item_name: str
    component: str
    new_version: str
    missing_builds: List[str]
    reason: List[str] = field(default_factory=list)
    age: Optional[int] = 0

    def ftbfs(self) -> bool:
        """Check if excuse is an FTBFS excuse

        Returns:
            bool: True is the excuse is an FTBFS
        """
        return len(self.missing_builds) > 0
