
from ..const.command import FAILURE, SUCCESS, PENDING


def status_update_prefix(msg: str, state=FAILURE) -> str:
    _d = {
        FAILURE: "error",
        SUCCESS: "success",
        PENDING: "pending",
    }
    return f"`{_d[state]}`: {msg}."   # exception handling not required: param not dependent on user input