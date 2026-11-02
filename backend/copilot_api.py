"""Read-only API routes for StayPilot Copilot tools."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from copilot_tools import search_rooms


router = APIRouter(prefix="/api/copilot", tags=["Copilot"])


@router.get("/rooms/search")
def search_room_inventory(
    floor: Annotated[int | None, Query(ge=1)] = None,
    room_type: str | None = None,
    view: str | None = None,
    accessible: bool | None = None,
    sofa_bed: bool | None = None,
    suite: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """Return inventory matches without asserting live availability."""

    try:
        return search_rooms(
            floor=floor,
            room_type=room_type,
            view=view,
            accessible=accessible,
            sofa_bed=sofa_bed,
            suite=suite,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
