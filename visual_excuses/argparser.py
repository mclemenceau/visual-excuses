import argparse
import textwrap


class Options:
    list_team: bool
    team: str
    save: str
    age: int


def get_arg_parser() -> argparse.ArgumentParser:
    opt_parser = argparse.ArgumentParser(
        description="Propposed Migration excuses Visualizer",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent("""\
        Examples:
            visual-excuses
            visual-excuses --team foundations-bugs
        """),
    )
    opt_parser.add_argument(
        "-l",
        "--list-team",
        dest="list_team",
        action="store_true",
        help="List Ubuntu Distro teams",
    )

    opt_parser.add_argument(
        "-t", "--team", dest="team", help="Only shows specific team proposed migration"
    )

    opt_parser.add_argument(
        "-s", "--save", dest="save", help="save graph to a html file"
    )

    opt_parser.add_argument(
        "-a",
        "--age",
        dest="age",
        type=int,
        help="Only shows packages that have been in proposed for more than x days",
    )

    return opt_parser
