
import yaml

from typing import List
from visual_excuses.excuse import Excuse


def load_excuses(file_path: str) -> List[Excuse]:
    """Loads excuses from a YAML file and returns a list of Excuse objects.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
        List[Excuse]: A list of parsed Excuse objects.

    Raises:
    ValueError: If 'sources' key is missing or not a list.
    """
    with open(file_path, "r") as file:
        data = yaml.load(file, Loader=yaml.CSafeLoader)

    excuses_list = []

    for entry in data["sources"]:
        raw_age = (
            entry.get('policy_info', {})
            .get('age', {})
            .get('current-age')
        )
        bug = ""
        for key in entry.get('policy_info', {}).get('update-excuse', {}).keys():
            if key and key != "verdict":
                bug = "LP: #" + key
        excuses_list.append(
            Excuse(
                item_name=entry.get("item-name", ""),
                component=entry.get("component", "main"),
                old_version=str(entry.get("old-version", "")),
                new_version=str(entry.get("new-version", "")),
                missing_builds=(
                    entry.get("missing-builds", {}).get("on-architectures", [])
                ),
                reasons=entry.get("reason", []),
                age=int(raw_age) if raw_age is not None else 0,
                excuse_bug=bug,
                blocked_by=(
                    entry.get("dependencies", {}).get("blocked-by", [])[0]
                    if entry.get("dependencies", {}).get("blocked-by")
                    else ""
                ),
                migrate_after=(
                    entry.get('dependencies', {}).get('migrate-after', [])
                ),
                excuses=entry.get("excuses", [])
            )
        )

    return excuses_list
