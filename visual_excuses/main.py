#!/usr/bin/env python3

import sys
from typing import Optional

from argparser import Options, get_arg_parser
from config import excuses_root_url, teampkgs
from errors import VisualExcusesError
from utils import (
    generate_graph,
    get_packages_by_team,
    list_teams,
)


def main(args: Optional[list[str]] = None) -> int:
    opt_parser = get_arg_parser()
    opts = opt_parser.parse_args(args, namespace=Options())

    try:
        packages_by_team = get_packages_by_team(teampkgs)
    except VisualExcusesError:
        print("Couldn't access team package information")
        return 1

    if opts.list_team:
        list_teams(packages_by_team)
        return 0

    generate_graph(excuses_root_url, packages_by_team, opts.team, opts.age, opts.save)
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
