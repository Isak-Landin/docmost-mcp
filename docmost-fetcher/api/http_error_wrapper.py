# docmost-fetcher/api/http_error_wrapper.py
from __future__ import annotations

from functools import wraps
from flask import jsonify
from errors import ApiError, err, UNEXPECTED_ERROR

def http_errors(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ApiError as e:
            return jsonify(e.to_dict()), e.http_status
        except Exception as e:
            ok_flag, d = err(UNEXPECTED_ERROR, {"exception": repr(e)})
            return jsonify(d), 500
    return wrapper