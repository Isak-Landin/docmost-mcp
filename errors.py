# docmost-fetcher/api/errors.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple, Optional, Union

# Stable error codes
INVALID_INPUT = "invalid_input"
NOT_FOUND = "not_found"
DB_ERROR = "db_error"
UNEXPECTED_ERROR = "unexpected_error"
INVALID_SCHEMA = "invalid_schema"

ERROR_MESSAGES: Dict[str, str] = {
    INVALID_INPUT: "Invalid input.",
    NOT_FOUND: "Resource not found.",
    DB_ERROR: "Database error.",
    UNEXPECTED_ERROR: "Unexpected error took place during runtime.",
    INVALID_SCHEMA: "Invalid schema.",
}

Result = Tuple[bool, Dict[str, Any]]

@dataclass
class ApiError(Exception):
    code: str
    message: str
    value: Any = None
    http_status: int = 400

    def to_dict(self) -> Dict[str, Any]:
        return {"error": self.code, "message": self.message, "value": self.value}

def default_http_status(code: str) -> int:
    if code == INVALID_INPUT:
        return 400
    if code == NOT_FOUND:
        return 404
    if code in (DB_ERROR, UNEXPECTED_ERROR, INVALID_SCHEMA):
        return 500
    return 400

def ok(payload: Any) -> Result:
    return True, {"payload": payload}

def err(code: str, value=None, message=None, *, to_raise: bool = True):
    if message is None:
        message = ERROR_MESSAGES.get(code, "Unknown error.")
    if to_raise:
        raise ApiError(code=code, message=message, value=value, http_status=default_http_status(code))
    return False, {"error": code, "message": message, "value": value}

"""
def must(res: Result, *, to_raise: bool = True) -> Union[Any, Result]:
    '''
    If ok -> returns payload
    If err and to_raise -> raises ApiError
    If err and not to_raise -> returns the original (False, dict) unchanged
    '''
    ok_flag, d = res
    if ok_flag:
        return d["payload"]

    if not to_raise:
        return res

    code = d.get("error", UNEXPECTED_ERROR)
    msg = d.get("message", ERROR_MESSAGES.get(code, "Unknown error."))
    val = d.get("value", None)
    raise ApiError(code=code, message=msg, value=val, http_status=default_http_status(code))
"""