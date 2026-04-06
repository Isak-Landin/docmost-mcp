from __future__ import annotations

from typing import Any
from uuid import UUID

from app.db import get_conn
from app.models import PageOut, SpaceOut
from app.text_utils import reformat_text


class SpaceNotFoundError(Exception):
    pass


class PageNotFoundError(Exception):
    pass


def _assert_space_exists(cur, space_id: UUID) -> dict[str, Any]:
    cur.execute(
        """
        SELECT id, name, description, slug, visibility, default_role,
               creator_id, workspace_id, created_at, updated_at
        FROM public.spaces
        WHERE id = %s AND deleted_at IS NULL
        LIMIT 1
        """,
        (str(space_id),),
    )
    row = cur.fetchone()
    if not row:
        raise SpaceNotFoundError("Space not found")
    return dict(row)


def _assert_page_in_space(cur, page_id: UUID, space_id: UUID) -> dict[str, Any]:
    cur.execute(
        """
        SELECT id, slug_id, title, icon, position, parent_page_id, creator_id,
               last_updated_by_id, space_id, workspace_id, is_locked,
               text_content, created_at, updated_at
        FROM public.pages
        WHERE id = %s AND space_id = %s AND deleted_at IS NULL
        LIMIT 1
        """,
        (str(page_id), str(space_id)),
    )
    row = cur.fetchone()
    if not row:
        raise PageNotFoundError("Page not found in this space")
    return dict(row)


def _format_page(row: dict[str, Any]) -> PageOut:
    formatted = dict(row)
    if formatted.get("text_content"):
        formatted["text_content"] = reformat_text(formatted["text_content"])
    return PageOut(**formatted)


def list_spaces() -> list[SpaceOut]:
    sql = """
        SELECT id, name, description, slug, visibility, default_role,
               creator_id, workspace_id, created_at, updated_at
        FROM public.spaces
        WHERE deleted_at IS NULL
        ORDER BY created_at ASC
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    return [SpaceOut(**dict(row)) for row in rows]


def get_space(space_id: UUID) -> SpaceOut:
    with get_conn() as conn:
        with conn.cursor() as cur:
            return SpaceOut(**_assert_space_exists(cur, space_id))


def list_pages(space_id: UUID) -> list[PageOut]:
    sql = """
        SELECT id, slug_id, title, icon, position, parent_page_id, creator_id,
               last_updated_by_id, space_id, workspace_id, is_locked,
               text_content, created_at, updated_at
        FROM public.pages
        WHERE space_id = %s AND deleted_at IS NULL
        ORDER BY created_at ASC
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            _assert_space_exists(cur, space_id)
            cur.execute(sql, (str(space_id),))
            rows = cur.fetchall()
    return [_format_page(dict(row)) for row in rows]


def get_page(space_id: UUID, page_id: UUID) -> PageOut:
    with get_conn() as conn:
        with conn.cursor() as cur:
            _assert_space_exists(cur, space_id)
            row = _assert_page_in_space(cur, page_id, space_id)
    return _format_page(row)
