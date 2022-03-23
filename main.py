
from pyvis.network import Network
import yaml

from packages import static_packages

component_colors= { 'main': '#EB7D7D',
                    'restricted': '#FBCD77',
                    'universe': '#63E38C',
                    'multiverse': '#90D2F0'}

default_color = '#B1B6C1'

excuses = None

with open("update_excuses.yaml",'r') as file:
    print("Loading update_excuses.yaml. (this could take a while)")
    excuses = yaml.load(file, Loader=yaml.CSafeLoader)

print("%d packages found" % len(excuses['sources']))

visual_excuses = Network(height="768px", width="1024px")

# Single package for test
# for item in excuses['sources']:
#     package = item['item-name']
#     if package == "gh":
#         visual_excuses.add_node(package, label=package)
#         break
# visual_excuses.show("gh.html")

for item in excuses['sources']:
    package = item['item-name']

    visual_excuses.add_node(
        package,
        label=package,
        color=component_colors.get(item.get('component', 'main'),
            default_color)
        )

for item in excuses['sources']:
    package = item['item-name']
    if 'dependencies' in item and 'blocked-by' in item['dependencies']:
        visual_excuses.add_edge(package, item['dependencies']['blocked-by'][0])

visual_excuses.show("excuses.html")

###############################################################################
