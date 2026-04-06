from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.docmost import SpaceNotFoundError, get_space as fetch_space, list_spaces as fetch_spaces
from app.models import SpaceOut

router = APIRouter(prefix="/spaces", tags=["spaces"])


@router.get(
    "",
    response_model=List[SpaceOut],
    summary="List all spaces",
    description="Returns all non-deleted spaces from the live Docmost database, ordered by creation date.",
)
def list_spaces():
    return fetch_spaces()


@router.get(
    "/{space_id}",
    response_model=SpaceOut,
    summary="Get a space",
    description="Returns a single space by its UUID. Returns 404 if the space does not exist or has been deleted.",
)
def get_space(space_id: UUID):
    try:
        return fetch_space(space_id)
    except SpaceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
