from pyvis.network import Network
from visual_excuses.excuse import Excuse
from visual_excuses.ubuntu_teams import UbuntuTeamMapping

from typing import List

EXCUSE_REASON_COLORS = {
    "default": "#FFFFFF",
    "unknown": "#FFFFFF",
    "autopkgtest": "#d4713b",
    "autopkgtest-depends": "#DBBF60",
    "missing-builds": "#CD6155",
    "depends": "#FAD7A0",
    "candidate": "#41AF25",
    "waiting": "#7C7B7B"
}


def lp_pkg_link(pkg: str) -> str:
    return f"<a href=https://pad.lv/u/{pkg}>{pkg} </a>"


def lp_bug_link(bug: str) -> str:
    return f"<a href=https://bugs.launchpad.net/bugs/{bug}>{bug}</a>"


def html_title(excuse: Excuse) -> str:
    """ libsepol (3.7-1 to 3.8-1) in proposed for 48 days """
    title = lp_pkg_link(excuse.item_name)
    usource = "https://launchpad.net/ubuntu/+source/" + excuse.item_name + "/"
    old = f"<a href={usource}{excuse.old_version}>{excuse.old_version}</a>"
    new = f"<a href={usource}{excuse.new_version}>{excuse.new_version}</a>"
    day = "days" if excuse.age > 1 else "day"
    title += f"({old} to {new}) in proposed for {excuse.age} {day}"

    return title


def visual_pyvis_excuses(excuses: List[Excuse], teams: UbuntuTeamMapping):
    if not excuses:
        return

    # Creating the Node network
    visual_excuses = Network(
        height="100vh",
        width="100vw",
        directed=True,
        filter_menu=True)

    # Creating teams Node, we will only display team with packages in proposed
    active_teams = set(
        [teams.default_team(excuse.item_name) for excuse in excuses]
    )

    for team in active_teams:
        if team:
            visual_excuses.add_node(
                team,
                title=team,
                color="#8B8985",
                size=20,
                shape='box')

    # Creating excuses Nodes
    for excuse in excuses:
        reason = "default"
        current = excuse.item_name

        # details will contain all the information we need to display
        details = html_title(excuse)

        # If there's an excuse bug, we display the excuse bug
        if excuse.excuse_bug:
            bug = excuse.excuse_bug[5:]
            details += f"<br/> - Excuses bug: #{lp_bug_link(bug)}"

        # If the excuse has missing builds, we display them
        if excuse.ftbfs():
            # TODO if missing-builgs is empty here it means missing on all arch
            details += f"<br/> - Missing builds : {excuse.missing_builds}"
            reason = "missing-builds"

        # If there's autopkgtest failures we will collect and add them later
        autopkg_failures = []
        if "autopkgtest" in excuse.reasons:
            for errors in excuse.excuses:
                if errors.startswith("autopkgtest") and "Regression" in errors:
                    autopkg = errors[errors.index("for")+4:errors.index("/")]
                    autopkg_failures.append([autopkg, errors])

        # If there's autopkgtest failures
        if autopkg_failures:
            details += "<br/> - Autopkgtest Regressions"
            reason = "autopkgtest-depends"

        if not excuse.reasons:
            details += "<br/> - <b>candidate</b>"
            reason = "candidate"

        if "autopkgtest" in excuse.reasons:
            if "Waiting for test results" in excuse.excuses[0]:
                details += "<br/> - Autopkgtests In Progress"
                reason = "waiting"

        # By now if the reason is still default, that means we are likely
        # facing packages blocked by another package, or that need to migrate
        # after another package or that have a block-bugs
        depends = []
        if reason == "default":
            reason = "depends"
            if excuse.blocked_by:
                details += f"<br/> - Depends on {excuse.blocked_by}"
                depends.append(excuse.blocked_by)
            elif excuse.migrate_after:
                for pkg in excuse.migrate_after:
                    details += f"<br/> - Requires {pkg} to migrate"
                    depends.append(pkg)
            else:
                reason = "unknown"

        # If there's an excuse bug, we display the excuse bug
        if excuse.block_bug:
            bug = excuse.block_bug[5:]
            details += f"<br/> - Block bug: #{lp_bug_link(bug)}"

        # Add the excuse to the graph
        # The Node might have already been created as a depends
        if current in visual_excuses.get_nodes():
            visual_excuses.get_node(current)['title'] = details
            visual_excuses.get_node(
                current
                )['color'] = EXCUSE_REASON_COLORS[reason]
        else:
            visual_excuses.add_node(
                current,
                label=current,
                color=EXCUSE_REASON_COLORS[reason],
                title=details
            )

        # Link the excuse to the team appropriate team
        if teams.default_team(current):
            visual_excuses.add_edge(teams.default_team(current), current)

        # If there's autopkgtest failure we will add them as well
        for failure in autopkg_failures:
            pkg = failure[0]
            errors = failure[1]
            reason = "autopkgtest"
            if pkg not in visual_excuses.get_nodes():
                visual_excuses.add_node(
                    pkg,
                    label=pkg,
                    color=EXCUSE_REASON_COLORS[reason],
                    title=errors
                )
                # We connect current package with its failed autopkgtest
                visual_excuses.add_edge(current, pkg)
            else:
                visual_excuses.get_node(pkg)['title'] += f"<br/>{errors}"
                visual_excuses.get_node(
                    pkg
                    )['color'] = EXCUSE_REASON_COLORS[reason]

        # Creating link to depends
        for dep_package in depends:
            if dep_package not in visual_excuses.get_nodes():
                visual_excuses.add_node(
                    dep_package,
                    label=dep_package,
                    color=EXCUSE_REASON_COLORS["default"],
                    title="Unknown"
                )
            visual_excuses.add_edge(current, dep_package)

    visual_excuses.show("excuses.html", notebook=False)
