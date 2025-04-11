# ubuntu-excuses: simple command line tool allowing to manipulate current list
# of packages stuck in the proposed pocket and not migrating to Ubuntu Devel

from visual_excuses.ubuntu_excuses_loader import load_ubuntu_excuses
from visual_excuses.table_visual import render_excuses_table
from visual_excuses.excuses_parser import ExcusesParser
from visual_excuses.ubuntu_teams import UbuntuTeamMapping
from visual_excuses.excuses_filter import filter_excuses


def main():

    parser = ExcusesParser()
    args = parser.parse_args()

    excuses = load_ubuntu_excuses(cache_dir=args.cache_dir)
    ubuntu_teams = UbuntuTeamMapping()

    excuses = filter_excuses(excuses, args, ubuntu_teams)
    if excuses:
        print(render_excuses_table(excuses))


if __name__ == "__main__":
    main()
