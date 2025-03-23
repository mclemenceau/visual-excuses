# excuses: simple command line tool allowing to manipulate current list of
# packages stuck in the proposed pocket and not migrating to Ubuntu Devel

from visual_excuses.ubuntu_excuses_loader import load_ubuntu_excuses
from visual_excuses.table_visual import render_excuses_table
from visual_excuses.excuses_parser import ExcusesParser

import json


def main():
    """
    For now the main function will simply list all the excuses on Ubuntu Devel
    """
    parser = ExcusesParser()
    args = parser.parse_args()

    excuses = load_ubuntu_excuses()

    if args.ftbfs:
        excuses = [e for e in excuses if e.ftbfs()]

    if args.limit:
        excuses = excuses[:args.limit]

    if args.json:
        print(json.dumps([e.__dict__ for e in excuses], indent=2))
    else:
        print(render_excuses_table(excuses))


if __name__ == "__main__":
    main()
