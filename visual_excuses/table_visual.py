from visual_excuses.excuse import Excuse
from typing import List
from tabulate import tabulate


def render_excuses_table(excuses: List[Excuse], args) -> str:
    """Render a list of Excuse objects as a table."""

    headers = [
            "Days",
            "Package",
            "Component",
            "New Version",
            "FTBFS",
            "Excuse Bug"]
    rows = []

    for e in excuses:
        ftbfs_str = ""
        if e.ftbfs():
            if args.missing_builds:
                ftbfs_str = e.missing_builds
            else:
                ftbfs_str = "✅"

        rows.append(
            [
                e.age,
                e.item_name,
                e.component,
                e.new_version,
                ftbfs_str,
                e.excuse_bug
            ]
        )

    return tabulate(rows, headers=headers, tablefmt="fancy_outline")
