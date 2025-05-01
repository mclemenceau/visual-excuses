from visual_excuses.excuse import Excuse
from visual_excuses.ubuntu_teams import UbuntuTeamMapping
from visual_excuses.table_visual import render_excuses_table

from typing import List

import json
import re


def filter_excuses(excuses: List[Excuse], args, teams: UbuntuTeamMapping):
    if args.inspect:
        excuse = next(
            (e for e in excuses if e.item_name == args.inspect), None
        )
        if excuse:
            print(render_excuses_table([excuse]))
            print(json.dumps(excuse.__dict__, indent=2))
            return []
        else:
            print(f"Excuse {args.inspect} can't be found in excuses list")
            return []

    if args.ftbfs:
        excuses = [e for e in excuses if e.ftbfs()]

    if args.with_bugs:
        excuses = [e for e in excuses if e.excuse_bug]

    if args.min_age is not None:
        excuses = [
            e for e in excuses if e.age is not None and e.age >= args.min_age
        ]

    if args.max_age is not None:
        excuses = [
            e for e in excuses if e.age is not None and e.age <= args.max_age
        ]

    if args.team:
        if args.team in teams.mapping:
            excuses = [
                e for e in excuses
                if teams.default_team(e.item_name) == args.team
            ]
        else:
            print(f"Team {args.team} is not a valid Ubuntu Team")
            return []

    if args.component:
        excuses = [
            e for e in excuses if e.component == args.component
        ]

    if args.name:
        try:
            pattern = re.compile(args.name, re.IGNORECASE)
            excuses = [e for e in excuses if pattern.search(e.item_name)]
        except re.error as e:
            print(f"Invalid regex pattern: {e}")
            return []

    if args.limit:
        excuses = excuses[:args.limit]

    if args.reverse:
        excuses.reverse()

    # Visualization json / visual / cli
    if args.json:
        print(json.dumps([e.__dict__ for e in excuses], indent=2))
        return []

    return excuses
