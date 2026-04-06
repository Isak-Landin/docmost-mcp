from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.docmost import (
    PageNotFoundError,
    SpaceNotFoundError,
    get_page as fetch_page,
    list_pages as fetch_pages,
)
from app.models import PageOut

router = APIRouter(prefix="/spaces/{space_id}/pages", tags=["pages"])


@router.get(
    "",
    response_model=List[PageOut],
    summary="List pages in a space",
    description=(
        "Returns all non-deleted pages belonging to the given space, ordered by creation date. "
        "`text_content` is returned normalized: repeated newline runs and repeated `+` storage "
        "noise are collapsed."
    ),
)
def list_pages(space_id: UUID):
    try:
        return fetch_pages(space_id)
    except SpaceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/{page_id}",
    response_model=PageOut,
    summary="Get a page",
    description=(
        "Returns a single page by its UUID, scoped to the given space. "
        "Returns 404 if the page does not exist, is deleted, or belongs to a different space."
    ),
)
def get_page(space_id: UUID, page_id: UUID):
    try:
        return fetch_page(space_id, page_id)
    except SpaceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PageNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
