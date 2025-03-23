from visual_excuses.excuse import Excuse
from typing import List
from tabulate import tabulate


def render_excuses_table(excuses: List[Excuse]) -> str:
    """Render a list of Excuse objects as a table."""

    headers = ["Days", "Package", "Component", "New Version", "FTBFS"]
    rows = [
        [
            e.age,
            e.item_name,
            e.component,
            e.new_version,
            "✅" if e.ftbfs() else ""
        ]
        for e in excuses
    ]

    return tabulate(rows, headers=headers, tablefmt="fancy_grid")
