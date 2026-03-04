import os

from flask import Blueprint, request, jsonify
import requests

from db_functionality import (
    get_spaces, get_pages, get_contents, get_page, get_space, get_content
)

from utils.schema_db_validation_management import (
    INVALID_INPUT, UNEXPECTED_ERROR, NOT_FOUND, DB_ERROR, err, ok
)

import logging
logger = logging.getLogger(__name__)

docmost_api = Blueprint("docmost_fetcher_api_route", __name__)

# MODE
MODE = os.getenv("MODE", "dev")

# ROUTE ENVS
SPACES_ALL_ENDPOINT = os.getenv("SPACES_ALL_ENDPOINT", "/docmost/api")

if MODE == "prod":
    SCHEMA_BASE_PATH = os.getenv("SCHEMA_BASE_PATH", "./schemas/")
else:
    SCHEMA_BASE_PATH = os.getenv(
        "SCHEMA_BASE_PATH_DEV",
        "/home/isakadmin/docmost-ai-standalone-software/schemas/"
    )


def _status_for(code: str) -> int:
    if code == INVALID_INPUT:
        return 400
    if code == NOT_FOUND:
        return 404
    if code in (DB_ERROR, UNEXPECTED_ERROR):
        return 500
    return 400


def respond(res):
    _ok, d = res
    if _ok:
        return jsonify(d), 200

    code = d.get("error", UNEXPECTED_ERROR)
    return jsonify(d), _status_for(code)


# ---------------------------------------- #
# ---------------- ROUTES ---------------- #
# ---------------------------------------- #

@docmost_api.get("/")
def http_home_list_spaces():
    return respond(get_spaces())


@docmost_api.get("/get-content")
def http_get_content_specific():
    payload = request.get_json(silent=True) or {}
    if not payload:
        return respond(err(INVALID_INPUT, {"reason": "missing_payload"}, "No payload"))

    page_id = (payload.get("page_id") or "").strip()
    if not page_id:
        return respond(err(INVALID_INPUT, {"reason": "missing_page_id"}, "No page id specified"))

    return respond(get_content(page_id))


@docmost_api.get("/get-content-single")
def http_get_content_single():
    page_id = (request.args.get("page_id") or "").strip()
    if not page_id:
        return respond(err(INVALID_INPUT, {"reason": "missing_page_id"}, "No page id specified"))

    return respond(get_content(page_id))


@docmost_api.get("/health")
def health():
    return jsonify({"ok": True})


@docmost_api.route(SPACES_ALL_ENDPOINT, methods=["GET"])
def spaces():
    payload = request.get_json(silent=True) or {}
    if not payload:
        return respond(err(INVALID_INPUT, {"reason": "missing_payload"}, "No payload"))

    spaces_id = (request.args.get("spaces_id") or "").strip()
    space_id = (payload.get("space_id") or "").strip()  # fixed None.strip

    if not space_id and not spaces_id:
        return respond(err(INVALID_INPUT, {"reason": "missing_space_id"}, "No space id specified"))

    return respond(get_spaces(space_id) if space_id else get_spaces(spaces_id))


# ---------------------------------------- #
# ------------- END OF ROUTES ------------ #
# ---------------------------------------- #