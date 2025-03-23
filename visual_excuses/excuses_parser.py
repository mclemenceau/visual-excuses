import argparse


class ExcusesParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Ubuntu Excuses (Proposed Migration) Viewer")

        self.parser.add_argument(
            "--ftbfs",
            action="store_true",
            help="Show only FTBFS packages"
        )

        self.parser.add_argument(
            "--json",
            action="store_true",
            help="Output in JSON format"
        )

        self.parser.add_argument(
            "--limit",
            type=int,
            help="Limit the number of results shown"
        )

        self.parser.add_argument(
            "--name",
            type=str,
            help="Regex to filter package names (case-insensitive)"
        )

    def parse_args(self, argv=None):
        self.args = self.parser.parse_args(argv)
        return self.args
