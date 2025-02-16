from datetime import datetime
from typing import Optional

UnprocessedExcusesDataDeneratedDate = datetime
# {
#     "component": str,
#     "excuses": list[str],
#     "is-candidate": bool,
#     "item-name": str,
#     "maintainer": str,
#     "migration-policy-verdict": str,
#     "new-version": str,
#     "old-version": str,
#     "policy_info": {
#         "age": {
#             "age-requirement": int,
#             "current-age": float,
#             "verdict": str,
#         },
#         "autopkgtest": {
#             str: dict[
#                 str, list[Optional[str]]
#             ],  # {<package>?: {<architecture>: <list of 5 items> (result, link, link, ?, ?)}}
#             "verdict": str,
#         },
#         "block": {
#             "verdict": str,
#         },
#         "block-bugs": {
#             str: int,  # '<some number>': <another number>
#             "verdict": str,
#         },
#         "depends": {
#             "skip_dep_check": list[str],  # list of architectures
#             "verdict": str,
#         },
#         "email": {
#             "verdict": str,
#         },
#         "rc-bugs": {
#             "shared-bugs": list,
#             "unique-source-bugs": list,
#             "unique-target-bugs": list,
#             "verdict": str,
#         },
#         "source-ppa": {
#             str: str,  # idk
#             "verdict": str,
#         },
#         "update-excuse": {
#             str: int,  # '<some number>': <another number>
#             "verdict": str,
#         },
#     },
#     "reason": list[str],
#     "source": str,
# }
UnprocessedExcusesDataSourcePolicyInfo = dict[
    str, dict[str, int | float | str | list[Optional[str]] | list]
]
UnprocessedExcusesDataSource = list[
    dict[str, str | list[str] | bool | UnprocessedExcusesDataSourcePolicyInfo]
]

UnprocessedExcusesData = dict[
    str, UnprocessedExcusesDataDeneratedDate | UnprocessedExcusesDataSource
]
ExcusesData = dict[str, dict[str, str | int | list[str] | list[int]]]
PackagesByTeam = dict[str, list[str]]
