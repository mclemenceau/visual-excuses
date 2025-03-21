
import yaml

from typing import List
from visual_excuses.excuse import Excuse


def load_excuses(file_path: str) -> List[Excuse]:
    """Loads excuses from a YAML file and returns a list of Excuse objects.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
        List[Excuse]: A list of parsed Excuse objects.
    """
    with open(file_path, "r") as file:
        data = yaml.load(file, Loader=yaml.CSafeLoader)

    excuses_list = []

    for entry in data["sources"]:
        excuses_list.append(
            Excuse(
                item_name=entry.get("item-name", ""),
                component=entry.get("component", ""),
                new_version=str(entry.get("new-version", "")),
                missing_builds=entry.get("missing-builds", []),
            )
        )

    return excuses_list
