"""Read-only hotel inventory tools for StayPilot Copilot."""

from hotel_config import HOTEL
from room_inventory import ROOMS


def search_rooms(
    *,
    floor: int | None = None,
    room_type: str | None = None,
    view: str | None = None,
    accessible: bool | None = None,
    sofa_bed: bool | None = None,
    suite: bool | None = None,
    limit: int = 50,
) -> dict:
    """Search verified room attributes, not live availability.

    Returns the total number of matches and a limited room list.
    All supplied filters must match.
    """

    if floor is not None:
        if type(floor) is not int or floor < 1:
            raise ValueError("floor must be a positive integer")

    if room_type is not None:
        if not isinstance(room_type, str):
            raise ValueError("room_type must be a string")

        room_type = room_type.upper()

        if room_type not in HOTEL["room_types"]:
            raise ValueError("Unknown room type")

    if view is not None:
        if view not in {"city", "river", "not_specified"}:
            raise ValueError("Invalid view")

    for name, value in {
        "accessible": accessible,
        "sofa_bed": sofa_bed,
        "suite": suite,
    }.items():
        if value is not None and type(value) is not bool:
            raise ValueError(f"{name} must be a boolean")

    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")

    filters = {
        "floor": floor,
        "room_type": room_type,
        "view": view,
        "accessible": accessible,
        "sofa_bed": sofa_bed,
        "suite": suite,
    }

    active_filters = {
        key: value
        for key, value in filters.items()
        if value is not None
    }

    matches = [
        room
        for room in ROOMS
        if all(
            room[key] == value
            for key, value in active_filters.items()
        )
    ]

    return {
        "filters": active_filters,
        "total": len(matches),
        "rooms": matches[:limit],
        "has_more": len(matches) > limit,
        "data_source": "StayPilot demo room inventory",
        "availability_verified": False,
    }
