from hotel_config import HOTEL


SOFA_KING_CITY_SUFFIXES = {10, 11, 12, 15, 17, 18}
SOFA_KING_RIVER_SUFFIXES = {1, 2, 3, 6, 7, 21}
SUITE_TYPES = {"QNXH", "QNEJ", "KNEJ", "QNEX"}


def get_room_attributes(room_type, room_number):
    floor = int(room_number) // 100
    suffix = int(room_number) % 100

    king_beds = 1 if room_type in {"KNPX", "KNPW", "KNEJ"} else 0
    queen_beds = 2 if room_type == "QND2" else (0 if king_beds else 1)

    if room_type in {"KNPW", "QNDW", "QNEX"}:
        view = "river"
    elif room_type in {"KNPX", "QNBX"}:
        view = "city"
    else:
        view = "not_specified"

    sofa_bed = room_type in SUITE_TYPES

    if room_type == "KNPX" and floor in {14, 15, 16}:
        sofa_bed = suffix in SOFA_KING_CITY_SUFFIXES

    if room_type == "KNPW" and floor in {14, 15, 16}:
        sofa_bed = suffix in SOFA_KING_RIVER_SUFFIXES

    return {
        "king_beds": king_beds,
        "queen_beds": queen_beds,
        "sofa_bed": sofa_bed,
        "view": view,
        "accessible": room_type == "QNDA",
        "suite": room_type in SUITE_TYPES,
        "skylight": room_number in {"1905", "1920"},
    }


def build_room_inventory():
    rooms = []

    for room_type, details in HOTEL["room_types"].items():
        for room_number in details.get("rooms", []):
            rooms.append({
                "room_number": room_number,
                "floor": int(room_number) // 100,
                "room_type": room_type,
                "room_type_name": details["name"],
                **get_room_attributes(room_type, room_number),
                "housekeeping_status": "unknown",
                "maintenance_status": "unknown",
            })

    return sorted(rooms, key=lambda room: int(room["room_number"]))


ROOMS = build_room_inventory()

assert len(ROOMS) == HOTEL["total_rooms"]
assert len({r["room_number"] for r in ROOMS}) == len(ROOMS)
