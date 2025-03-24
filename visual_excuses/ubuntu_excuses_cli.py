# excuses: simple command line tool allowing to manipulate current list of
# packages stuck in the proposed pocket and not migrating to Ubuntu Devel

from visual_excuses.ubuntu_excuses_loader import load_ubuntu_excuses
from visual_excuses.table_visual import render_excuses_table
from visual_excuses.excuses_parser import ExcusesParser
from visual_excuses.ubuntu_teams import UbuntuTeamMapping

import json
import re


def main():
    """
    For now the main function will simply list all the excuses on Ubuntu Devel
    """
    parser = ExcusesParser()
    args = parser.parse_args()

    excuses = load_ubuntu_excuses()

    if args.inspect:
        excuse = next(
            (e for e in excuses if e.item_name == args.inspect), None
        )
        if excuse:
            print(render_excuses_table([excuse]))
            print(json.dumps(excuse.__dict__, indent=2))
            return
        else:
            print(f"Excuse {args.inspect} can't be found in excuses list")
            return

    if args.ftbfs:
        excuses = [e for e in excuses if e.ftbfs()]

    if args.min_age is not None:
        excuses = [
            e for e in excuses if e.age is not None and e.age >= args.min_age
        ]

    if args.max_age is not None:
        excuses = [
            e for e in excuses if e.age is not None and e.age <= args.max_age
        ]

    if args.team:
        ubuntu_teams = UbuntuTeamMapping()
        if args.team in ubuntu_teams.mapping:
            excuses = [
                e for e in excuses
                if ubuntu_teams.default_team(e.item_name) == args.team
            ]
        else:
            print(f"Team {args.team} is not a valid Ubuntu Team")
            return

    if args.name:
        try:
            pattern = re.compile(args.name, re.IGNORECASE)
            excuses = [e for e in excuses if pattern.search(e.item_name)]
        except re.error as e:
            print(f"Invalid regex pattern: {e}")
            return

    if args.limit:
        excuses = excuses[:args.limit]

    if args.json:
        print(json.dumps([e.__dict__ for e in excuses], indent=2))
    else:
        print(render_excuses_table(excuses))


if __name__ == "__main__":
    main()
