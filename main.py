###############################################################################
# 1) Launchpad team information
# package by team content is built from the page
# http://reqorts.qa.ubuntu.com/reports/m-r-package-team-mapping.html
# then turned into a python dictionnary imported below
# This is done rigth now by the script ./update-data.sh
# TODO: maybe find a better more reliable way to get updated team/packages
from packages_by_team import packages_by_team

def search_teams(package):
    teams=[]
    for k in packages_by_team:
        for v in packages_by_team[k]:
            if package == v:
                teams.append(k)
    return teams

###############################################################################
# 2) excuses data
# https://people.canonical.com/~ubuntu-archive/proposed-migration/update_excuses.yaml.xz
# This data is download using the script ./update-data.sh as well
# TODO: data could be downloaded directly in python, cached or something
import yaml
import json
# we will load the excuse data into a simpler dictionnary that we will then
# draw using pyvis toolkit, that way we can always change toolkit later
excuses_data = {}

all_excuses = None

with open("update_excuses.yaml",'r') as file:
    print("Loading update_excuses.yaml. (this could take a while)")
    all_excuses = yaml.load(file, Loader=yaml.CSafeLoader)
    print("%d packages found" % len(all_excuses['sources']))


for item in all_excuses['sources']:
    # We assume some of these keys are always present which won't be always
    # the case and may need to be checked for
    package = item['item-name']
    new = item['new-version']
    old = item['old-version']

    age = 0
    if 'policy_info' in item \
        and 'age' in item['policy_info'] \
        and 'current-age' in item['policy_info']['age']:
        age = int(item['policy_info']['age']['current-age'])

    excuses = []
    for excuse in item['excuses']:
        if excuse.startswith("autopkgtest") and "Regression" in excuse:
            autopkg = excuse[excuse.index("for")+4:excuse.index("/")]
            excuses.append({'pkg':autopkg, 'dsc':excuse})

    missing_builds = ""
    if 'missing-builds' in item:
        missing_builds = item['missing-builds']["on-architectures"]

    # This is for dependencies
    blocked_by=""
    if 'dependencies' in item and 'blocked-by' in item['dependencies']:
        blocked_by=item['dependencies']['blocked-by'][0]

    excuses_data[package] = {
        "name":package,
        "new-version":new,
        "old-version":old,
        "age":age,
        "autopkg-regression":excuses,
        "missing-builds":missing_builds,
        "blocked-by":blocked_by
    }

    #TODO: what is item['dependencies']

with open("excuses_data.json", 'w') as fp:
    json.dump(excuses_data, fp, indent=2)

# exit(0)

###############################################################################
# 3) network graph drawing
from pyvis.network import Network

# https://htmlcolorcodes.com/color-chart/
def age_color(old):
    if old < 5:
        return "#2ECC71"
    if old < 15:
        return "#F9E79F"
    if old < 30:
        return "#F5B041"
    if old < 60:
        return "#E74C3C"
    if old < 90:
        return "#922B21"

    return "#641E16"

teams = list(packages_by_team.keys())

default_color = '#FFFFFF'

visual_excuses = Network(height="768px", width="1024px")

autopkg_list = []

team_choice = ''

for item in excuses_data.values():
    current_package = item['name']
    if current_package == 'rust-rustc-version':
        print("debug")

    # When should we display a package on the map?
    # Issues preventing migration
    # [DONE] When it has failing autopkgtest?
    # [DONE] Missing builds
    # Blocked-by
    # - Depends / RDepends
    teams = search_teams(current_package)

    # We only display this package if it belong to a specif team
    # or if we want all the teams (team_choice empty)
    blocked_by = item['blocked-by']


    if not team_choice or team_choice in teams:
        if  item['autopkg-regression'] \
            or item['missing-builds'] \
            or blocked_by:

            if item['autopkg-regression']:
                color = "#2E86C1"
                details = "failing autopkgtest"
            elif item['missing-builds']:
                color = "#CD6155"
                details = "<b>Missing builds: </b> " + str(item['missing-builds'])
            elif blocked_by:
                color = "#FAD7A0"
                details = "Depends on " + blocked_by
            else:
                color = default_color

            # if the node already exist we only update the title
            if current_package in visual_excuses.get_nodes():
                visual_excuses.get_node(current_package)['title'] = details
            else:
                visual_excuses.add_node(
                    current_package,
                    label=current_package,
                    color=color,
                    title=details
                )

            for team in teams:
                if not team_choice or team == team_choice:
                    visual_excuses.add_node(team,title=team, color="#8B8985", size=20)
                    visual_excuses.add_edge(team, current_package)

            for excuse in item['autopkg-regression']:
                if excuse['pkg'] != current_package:
                    visual_excuses.add_node(excuse['pkg'],
                        label=excuse['pkg'],
                        title=excuse['dsc'])
                else:
                    # self failing autopkgtest here, node already exists
                    visual_excuses.get_node(current_package)['title'] = excuse['dsc']

                visual_excuses.add_edge(
                    current_package,
                    excuse['pkg'],
                    color='#2E86C1')

            if blocked_by:
                visual_excuses.add_node(
                    blocked_by,
                    label=blocked_by,
                    title='Unknown Cause (for now)',
                    color="#FAD7A0")
                visual_excuses.add_edge(
                    current_package,
                    blocked_by,
                    color="#FAD7A0")


        else:
            print(current_package)

print(len(visual_excuses.get_nodes()))
visual_excuses.show("excuses.html")
###############################################################################
