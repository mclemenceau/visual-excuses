from visual_excuses.excuse import Excuse
from typing import List
from tabulate import tabulate


def render_excuses_table(excuses: List[Excuse], args=None) -> str:
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
            if args and args.missing_builds:
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


def render_excuses_markdown(excuses: List[Excuse], args=None) -> str:
    """Render a list of Excuse objects as a Markdown table."""

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
            if args and args.missing_builds:
                ftbfs_str = e.missing_builds
            else:
                ftbfs_str = "yes"

        pkg_url = (
            "https://ubuntu-archive-team.ubuntu.com/proposed-migration/"
            f"update_excuses.html#{e.item_name}"
        )
        bug_str = (
            f"[{e.excuse_bug}](https://bugs.launchpad.net/bugs/{e.excuse_bug})"
            if e.excuse_bug else ""
        )
        rows.append(
            [
                e.age,
                f"[{e.item_name}]({pkg_url})",
                e.component,
                e.new_version,
                ftbfs_str,
                bug_str
            ]
        )

    return tabulate(rows, headers=headers, tablefmt="github")
