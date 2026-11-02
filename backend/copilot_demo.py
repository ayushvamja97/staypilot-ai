"""Free, rule-based chat for synthetic hotel inventory."""

import re

from fastapi import APIRouter

from copilot_chat import ChatRequest
from copilot_tools import search_rooms
from hotel_config import HOTEL


router = APIRouter(prefix="/api/copilot", tags=["Copilot Demo"])

SOURCE = "StayPilot synthetic room inventory (not live availability)"


@router.post("/demo-chat")
def demo_chat(request: ChatRequest):
    question = request.message.strip()
    text = question.lower()

    if re.fullmatch(
        r"(?:what kinds?|which types?|what types?)"
        r"(?: of rooms?)?\??",
        text,
    ):
        previous = next(
            (
                turn.content.lower()
                for turn in reversed(request.history)
                if turn.role == "user"
            ),
            "",
        )

        previous_floor = re.search(
            r"\b(?:floor|level)\s*(\d{1,2})\b"
            r"|\b(\d{1,2})(?:st|nd|rd|th)\s+floor\b",
            previous,
        )

        floor = (
            int(previous_floor.group(1) or previous_floor.group(2))
            if previous_floor
            else None
        )

        view = (
            "river" if re.search(r"\briver\b", previous)
            else "city" if re.search(r"\bcity\b", previous)
            else None
        )

        categories = []

        for code, details in HOTEL["room_types"].items():
            count = search_rooms(
                floor=floor,
                view=view,
                room_type=code,
                limit=1,
            )["total"]

            if count:
                categories.append(
                    f"{code} - {details['name']}: {count}"
                )

        scope = (
            f"floor {floor}" if floor is not None
            else "the entire hotel"
        )

        if view is not None:
            scope += f", {view}-view"

        if categories:
            answer = (
                f"Room categories for {scope}:\n"
                + "\n".join(categories)
            )
        else:
            answer = f"No matching room categories for {scope}."

        answer += (
            "\nSynthetic inventory only. "
            "Booking availability is not verified."
        )

        return {"answer": answer, "sources": [SOURCE]}

    if re.search(
        r"\b(available|availability|vacant|booking|book|reserve)\b",
        text,
    ):
        return {
            "answer": (
                "Demo mode cannot check room availability or make "
                "reservations. I can search synthetic room features "
                "such as floor, view, room category and accessibility."
            ),
            "sources": [SOURCE],
        }

    inventory_words = bool(
        re.search(r"\b(rooms?|inventory|suites?)\b", text)
    )
    view_query = bool(
        re.search(r"\b(river|city)[\s-]*view\b", text)
        and re.search(
            r"\b(how many|which|show|find|list|any)\b",
            text,
        )
    )

    if not (inventory_words or view_query):
        return {
            "answer": (
                "Free demo mode supports room-inventory questions only. "
                "Try: How many river-view rooms are on floor 19? "
                "Hotel policy and operational advice are not connected."
            ),
            "sources": [],
        }

    floor_match = re.search(
        r"\b(?:floor|level)\s*(\d{1,2})\b"
        r"|\b(\d{1,2})(?:st|nd|rd|th)\s+floor\b",
        text,
    )

    floor = None

    if floor_match:
        floor = int(floor_match.group(1) or floor_match.group(2))

    view = None

    if re.search(r"\briver\b", text):
        view = "river"
    elif re.search(r"\bcity\b", text):
        view = "city"

    accessible = (
        True if re.search(r"\baccessible\b", text) else None
    )

    sofa_bed = (
        True if re.search(r"\bsofa[\s-]*bed\b", text) else None
    )

    suite = True if re.search(r"\bsuites?\b", text) else None

    room_type = None

    for code in HOTEL["room_types"]:
        if re.search(r"\b" + re.escape(code) + r"\b", question.upper()):
            room_type = code
            break

    result = search_rooms(
        floor=floor,
        view=view,
        accessible=accessible,
        sofa_bed=sofa_bed,
        suite=suite,
        room_type=room_type,
        limit=20,
    )

    total = result["total"]

    filters = []

    if floor is not None:
        filters.append(f"floor {floor}")

    if view is not None:
        filters.append(f"{view}-view")

    if accessible:
        filters.append("accessible")

    if sofa_bed:
        filters.append("sofa-bed")

    if suite:
        filters.append("suite")

    if room_type:
        filters.append(room_type)

    description = ", ".join(filters) if filters else "all"
    numbers = [
        room["room_number"] for room in result["rooms"]
    ]

    answer = (
        f"The synthetic hotel inventory contains {total} "
        f"matching rooms ({description})."
    )

    if numbers:
        prefix = (
            "Room numbers"
            if not result["has_more"]
            else "First 20 matching room numbers"
        )

        answer += f" {prefix}: {', '.join(numbers)}."

    answer += (
        " These are inventory matches only. "
        "Booking availability is not verified."
    )

    return {
        "answer": answer,
        "sources": [SOURCE],
    }
