import lzma
import re
from typing import Optional
from urllib.request import urlopen

import requests
import yaml
from custom_types import ExcusesData, PackagesByTeam, UnprocessedExcusesData
from errors import AccessError
from pyvis.network import Network


def search_teams(package: str, packages_by_team: PackagesByTeam) -> list[str]:
    teams = []
    for k, v in packages_by_team.items():
        if package in v:
            teams.append(k)
    return teams


def load_yaml_excuses(excuses_root_url: str) -> Optional[UnprocessedExcusesData]:
    # we will load the excuse data into a simpler dictionnary that we will then
    # draw using pyvis toolkit, that way we can always change toolkit later
    all_excuses = None
    try:
        yaml_excuses = lzma.open(urlopen(excuses_root_url + "/update_excuses.yaml.xz"))
    except:
        print("Couldn't download excuses.yaml")
        return 1
    print("Loading update_excuses.yaml. (this could take a while)")
    all_excuses = yaml.load(yaml_excuses, Loader=yaml.CSafeLoader)
    print(f"{len(all_excuses['sources'])} packages found")
    return all_excuses


def consume_yaml_excuses(unprocessed_excuses: UnprocessedExcusesData) -> ExcusesData:
    data = {}
    for item in unprocessed_excuses["sources"]:
        # We assume some of these keys are always present which won't be always
        # the case and may need to be checked for
        package = item["item-name"]

        # current known reasons for excuses
        # [x] 'autopkgtest',
        # [ ] 'source-ppa',
        # [x] 'missingbuild'
        # [ ] 'block',
        # [ ] 'cruft',
        # [ ] 'depends',
        # [ ] 'implicit-dependency',
        # [ ] 'linux-meta-not-ready',
        # [ ] 'no-binaries'

        reasons = item["reason"]
        new = item["new-version"]
        old = item["old-version"]

        age = item.get("policy_info", {}).get("age", {}).get("current-age", 0.0)
        age = int(age)

        excuses = []
        missing_builds = ""
        blocked_by = ""
        migrate_after = ""
        update_excuse_keys = item.get("policy_info", {}).get("update-excuse", {})
        update_excuse_bugs = [
            int(s) for s in update_excuse_keys if re.match(r"^\d+$", s)
        ]

        best_reason = ""

        for reason in reasons:
            if reason == "autopkgtest":
                test_progress = False
                for excuse in item["excuses"]:
                    if excuse.startswith("autopkgtest"):
                        if "Regression" in excuse:
                            autopkg = excuse[
                                excuse.index("for") + 4 : excuse.index("/")
                            ]
                            excuses.append({"pkg": autopkg, "dsc": excuse})
                        else:
                            test_progress = True
                # Only if there's actual failing autokpgtest
                if excuses:
                    best_reason = "autopkgtest"
                    break
                if test_progress:
                    best_reason = "waiting"
                    break

            if reason == "missingbuild":
                missing_builds = item["missing-builds"]["on-architectures"]
                best_reason = "missingbuild"
                break

            if reason == "no-binaries":
                missing_builds = ["no binaries on any arch"]
                best_reason = "missingbuild"
                break

            if "depends" in reasons or "implicit-dependency" in reasons:
                if "dependencies" in item:
                    if "blocked-by" in item["dependencies"]:
                        blocked_by = item["dependencies"]["blocked-by"][0]
                        best_reason = "depends"
                else:
                    best_reason = "unknown"
                break

            # # At this point we might be able to catch the migrate_after
            # if 'dependencies' in item and 'migrate-after' in item['dependencies']:
            #     print(package)
            # migrate_after=item['dependencies']['migrate-after']
            # best_reason = 'migrate_after

        data[package] = {
            "name": package,
            "reason": best_reason,
            "new-version": new,
            "old-version": old,
            "age": age,
            "autopkg-regression": excuses,
            "missing-builds": missing_builds,
            "blocked-by": blocked_by,
            "migrate-after": migrate_after,
            "update-excuse-bugs": update_excuse_bugs,
        }
    return data


def create_visual_excuses(
    data: ExcusesData,
    excuses_root_url: str,
    packages_by_team: PackagesByTeam,
    team_choice: str = "",
    age: int = 0,
) -> Network:
    if not data:
        return None

    teams = list(packages_by_team.keys())

    if team_choice not in teams:
        print("No team specified we will show all excuses")
    else:
        print(f"Showing excuses relevant to {team_choice} team")

    default_color = "#FFFFFF"  # white

    visual_excuses = Network(
        height="100vh", width="100vw", directed=True, filter_menu=True
    )

    for item in data.values():
        current_package = item["name"]

        teams = search_teams(current_package, packages_by_team)

        # We only display this package if it belong to a specif team
        # or if we want all the teams (team_choice empty)

        if not team_choice or team_choice in teams:
            # Don't display the node if it's younger than the --age flag
            if age and item["age"] < age:
                continue
            if item["update-excuse-bugs"]:
                bugs = ", ".join(
                    [
                        f'<a href="https://bugs.launchpad.net/bugs/{bug}">{bug}</a>'
                        for bug in item["update-excuse-bugs"]
                    ]
                )
                bugs = f"<br />More info in {bugs}."
            else:
                bugs = ""

            # Only display the Node if there's an actual reason
            if item["reason"]:
                unknown_reason = f'Unknown at this time <a href="{excuses_root_url}/update_excuses.html#{current_package}">see details</a>'

                if item["reason"] == "autopkgtest":
                    color = "#DBBF60"  # beige
                    reason_detail = "autopkgtest depends failures"
                elif item["reason"] == "missingbuild":
                    color = "#CD6155"  # light-red
                    reason_detail = f"<b>Missing builds: </b> {item['missing-builds']}"
                elif item["reason"] == "depends":
                    color = "#FAD7A0"  # light-yellow
                    reason_detail = f"Blocked by {item['blocked-by']}"
                elif item["reason"] == "migrate_after":
                    color = "#7DCEA0"  # light-green
                    reason_detail = f"Will migrate after {item['migrate-after']}"
                elif item["reason"] == "waiting":
                    continue
                else:
                    reason_detail = unknown_reason
                    color = default_color

                detail_age = f"<br />{item['age']} days old"
                detail_link = f'<br /><a href="https://launchpad.net/ubuntu/+source/{current_package}">{current_package}</a>'
                full_details = f"{reason_detail}{bugs}{detail_age}{detail_link}"

                # if the node already exist now we know why
                if current_package in visual_excuses.get_nodes():
                    visual_excuses.get_node(current_package)["title"] = full_details
                    visual_excuses.get_node(current_package)["color"] = color
                else:
                    visual_excuses.add_node(
                        current_package,
                        label=current_package,
                        color=color,
                        title=full_details,
                        age=item["age"],
                    )

                for team in teams:
                    if not team_choice or team == team_choice:
                        visual_excuses.add_node(
                            team,
                            title=team,
                            color="#8B8985",  # gray
                            size=20,
                            shape="box",
                        )
                        visual_excuses.add_edge(team, current_package)

                # Time to create dependencie autokgtest cards
                for excuse in item["autopkg-regression"]:
                    if excuse["pkg"] != current_package:
                        visual_excuses.add_node(
                            excuse["pkg"],
                            label=excuse["pkg"],
                            title=f"{excuse['dsc']}{bugs}",
                            color="#D4713B",  # orange
                        )
                    else:
                        # self failing autopkgtest here, node already exists
                        visual_excuses.get_node(current_package)["title"] = (
                            f"{excuse['dsc']}{bugs}"
                        )
                        visual_excuses.get_node(current_package)["color"] = (
                            "#D4713B"  # orange
                        )

                    visual_excuses.add_edge(
                        current_package,
                        excuse["pkg"],
                        color="#2E86C1",  # light-blue
                    )

                if item["reason"] == "depends":
                    visual_excuses.add_node(
                        item["blocked-by"],
                        label=item["blocked-by"],
                        title=unknown_reason,
                        color="#DC7633",  # orange
                    )
                    visual_excuses.add_edge(
                        current_package,
                        item["blocked-by"],
                        color="#FAD7A0",  # light-yellow
                    )
    return visual_excuses


def get_packages_by_team(teampkgs: str) -> PackagesByTeam:
    # retrieve distro teams and packages information
    print("refreshing distro teams and packages information")
    response = requests.get(teampkgs)
    if response.status_code == 200:
        return response.json()
    else:
        raise AccessError()


def list_teams(packages_by_team: PackagesByTeam):
    print("\n".join(packages_by_team))


def generate_graph(
    excuses_root_url: str,
    packages_by_team: PackagesByTeam,
    team: str,
    age: int,
    filepath: Optional[str],
):
    unprocessed_excuses_data = load_yaml_excuses(excuses_root_url)
    excuses_data = consume_yaml_excuses(unprocessed_excuses_data)
    graph = create_visual_excuses(
        excuses_data, excuses_root_url, packages_by_team, team, age
    )
    print("%d packages with valid excuse" % len(graph.get_nodes()))

    if filepath:
        graph.save_graph(filepath)
        return

    graph.show("excuses.html", notebook=False)
