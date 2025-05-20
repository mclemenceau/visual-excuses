# visual-excuses: Show the list of excuses, packages stuck in proposed using
# pyvis visualization

from visual_excuses.ubuntu_excuses_loader import load_ubuntu_excuses
from visual_excuses.pyvis_visual import visual_pyvis_excuses
from visual_excuses.excuses_parser import ExcusesParser
from visual_excuses.ubuntu_teams import UbuntuTeamMapping
from visual_excuses.excuses_filter import filter_excuses


def main():

    parser = ExcusesParser()
    args = parser.parse_args()

    excuses = load_ubuntu_excuses()
    ubuntu_teams = UbuntuTeamMapping(cache_dir=args.cache_dir)

    excuses = filter_excuses(excuses, args, ubuntu_teams)
    if excuses:
        visual_pyvis_excuses(excuses, ubuntu_teams)


if __name__ == "__main__":
    main()
