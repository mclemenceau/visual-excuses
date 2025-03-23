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
        reasons (str): The reason migration has failed
        age (int): How many days have this package been blocked
        excuse_bug (str) : LaunchPad bug relevant to that excuse
        blocked_by (str) : excuse blocking this excuse to migrate
        migrate_after (List) : excuses that need to migrate before this excuse
        excuses (List) : Text List of all excuses (autopkgtest and dependencies)
    """

    item_name: str
    component: str
    new_version: str
    missing_builds: List[str]
    reasons: List[str] = field(default_factory=list)
    age: Optional[int] = 0
    excuse_bug: Optional[str] = ""
    blocked_by: Optional[str] = ""
    migrate_after: List[str] = field(default_factory=list)
    excuses: List[str] = field(default_factory=list)

    def ftbfs(self) -> bool:
        """Check if excuse is an FTBFS excuse

        Returns:
            bool: True is the excuse is an FTBFS
        """
        return len(self.missing_builds) > 0
