
from collections.abc import Mapping
from typing import Union

from ..const.command import FAILURE, SUCCESS, PENDING


def status_update_prefix(msg: str, state=FAILURE) -> str:
    _d = {
        FAILURE: "error",
        SUCCESS: "success",
        PENDING: "pending",
    }
    return f"**{_d[state]}**: {msg}."   # exception handling not required: param not dependent on user input

def incremental_response(msg: Mapping[str, Union[int, float]]):
    for (k, v) in msg.items():
        print(k, v)