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

    reasons = item['reason']
    new = item['new-version']
    old = item['old-version']

    age = 0
    if 'policy_info' in item \
        and 'age' in item['policy_info'] \
        and 'current-age' in item['policy_info']['age']:
        age = int(item['policy_info']['age']['current-age'])

    excuses = []
    missing_builds = ""
    blocked_by=""
    migrate_after=""

    best_reason=""

    for reason in reasons:
        if reason == 'autopkgtest':
            test_progress = False
            for excuse in item['excuses']:
                if excuse.startswith("autopkgtest"):
                    if "Regression" in excuse:
                        autopkg = excuse[excuse.index("for")+4:excuse.index("/")]
                        excuses.append({'pkg':autopkg, 'dsc':excuse})
                    else:
                        test_progress = True
            # Only if there's actual failing autokpgtest
            if excuses:
                best_reason = 'autopkgtest'
                break
            if test_progress:
                best_reason = 'waiting'
                break

        if reason == 'missingbuild':
            missing_builds = item['missing-builds']["on-architectures"]
            best_reason = 'missingbuild'
            break

        if reason == 'no-binaries':
            missing_builds = ['no binaries on any arch']
            best_reason = 'missingbuild'
            break

        if 'depends' in reasons or 'implicit-dependency' in reasons :
            if 'dependencies' in item:
                if 'blocked-by' in item['dependencies']:
                    blocked_by=item['dependencies']['blocked-by'][0]
                    best_reason = 'depends'
            else:
                best_reason = 'unknown'
            break

        # # At this point we might be able to catch the migrate_after
        # if 'dependencies' in item and 'migrate-after' in item['dependencies']:
        #     print(package)
                    # migrate_after=item['dependencies']['migrate-after']
                    # best_reason = 'migrate_after


    excuses_data[package] = {
        "name":package,
        "reason":best_reason,
        "new-version":new,
        "old-version":old,
        "age":age,
        "autopkg-regression":excuses,
        "missing-builds":missing_builds,
        "blocked-by":blocked_by,
        "migrate-after":migrate_after
    }


# with open("excuses_data.json", 'w') as fp:
#     json.dump(excuses_data, fp, indent=2)


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

visual_excuses = Network(height="768px", width="1024px", directed=True)

autopkg_list = []

team_choice = ''

for item in excuses_data.values():
    current_package = item['name']

    teams = search_teams(current_package)

    # We only display this package if it belong to a specif team
    # or if we want all the teams (team_choice empty)

    if not team_choice or team_choice in teams:
        # Only display the Node if there's an actual reason
        if  item['reason']:
            if item['reason'] == 'autopkgtest':
                color = "#AED6F1"
                details = "autopkgtest depends failures"
            elif item['reason'] == 'missingbuild':
                color = "#CD6155"
                details = "<b>Missing builds: </b> " + str(item['missing-builds'])
            elif item['reason'] == 'depends':
                color = "#FAD7A0"
                details = "Blocked by " + item['blocked-by']
            elif item['reason'] == 'migrate_after':
                color = "#7DCEA0"
                details = "Will migrate after" + item['migrate-after']
            elif item['reason'] == 'waiting':
                continue
            else:
                details = "Unknown at this time"
                color = default_color

            # if the node already exist now we know why
            if current_package in visual_excuses.get_nodes():
                visual_excuses.get_node(current_package)['title'] = details
                visual_excuses.get_node(current_package)['color'] = color
            else:
                visual_excuses.add_node(
                    current_package,
                    label=current_package,
                    color=color,
                    title=details
            )

            for team in teams:
                if not team_choice or team == team_choice:
                    visual_excuses.add_node(team,
                        title=team,
                        color="#8B8985",
                        size=20,
                        shape='box')
                    visual_excuses.add_edge(team, current_package)

            # Time to create dependencie autokgtest cards
            for excuse in item['autopkg-regression']:
                if excuse['pkg'] != current_package:
                    visual_excuses.add_node(excuse['pkg'],
                        label=excuse['pkg'],
                        title=excuse['dsc'],
                        color='#2E86C1')
                else:
                    # self failing autopkgtest here, node already exists
                    visual_excuses.get_node(current_package)\
                        ['title'] = excuse['dsc']
                    visual_excuses.get_node(current_package)\
                        ['color'] = '#2E86C1'

                visual_excuses.add_edge(
                    current_package,
                    excuse['pkg'],
                    color='#2E86C1')

            if item['reason'] == 'depends':
                visual_excuses.add_node(
                    item['blocked-by'],
                    label=item['blocked-by'],
                    title='Unknown Cause (for now)',
                    color="#DC7633")
                visual_excuses.add_edge(
                    current_package,
                    item['blocked-by'],
                    color="#FAD7A0")


print("%d packages with valid reason" % len(visual_excuses.get_nodes()))
visual_excuses.show("excuses.html")
###############################################################################
