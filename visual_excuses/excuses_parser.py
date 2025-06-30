import argparse
from pathlib import Path

from .ubuntu_excuses_loader import DEFAULT_CACHE_DIR


class ExcusesParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Ubuntu Excuses (Proposed Migration) Viewer")

        self.parser.add_argument(
            "--inspect",
            type=str,
            help="Get details about a specific package"
        )

        self.parser.add_argument(
            "--name",
            type=str,
            help="Regex to filter package names (case-insensitive)"
        )

        self.parser.add_argument(
            "--component",
            type=str,
            help="Archive component (main, restricted, universe, multivere)"
        )

        self.parser.add_argument(
            "--team",
            type=str,
            help="Show only packages subscribed by this Ubuntu team"
        )

        self.parser.add_argument(
            "--ftbfs",
            action="store_true",
            help="Show only FTBFS packages"
        )

        self.parser.add_argument(
            "--missing-builds",
            action="store_true",
            help="Show which architectures didn't build"
        )

        self.parser.add_argument(
            "--with-bugs",
            action="store_true",
            help="Show only pacakges with associated excuse bugs"
        )

        self.parser.add_argument(
            "--min-age",
            type=int,
            metavar="DAYS",
            help="Only include packages at least this many days old"
        )

        self.parser.add_argument(
            "--max-age",
            type=int,
            metavar="DAYS",
            help="Only include packages no older than this many days"
        )

        self.parser.add_argument(
            "--limit",
            type=int,
            help="Limit the number of results shown"
        )

        self.parser.add_argument(
            "--reverse",
            action="store_true",
            help="Show excuses from older to more recent"
        )

        self.parser.add_argument(
            "--json",
            action="store_true",
            help="Output in JSON format"
        )

        self.parser.add_argument(
            "--cache-dir",
            type=Path,
            default=DEFAULT_CACHE_DIR,
            metavar="DIR",
            help="The directory under which to cache the excuses data "
            "(default: %(default)s)"
        )

    def parse_args(self, argv=None):
        self.args = self.parser.parse_args(argv)
        return self.args
