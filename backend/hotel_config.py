HOTEL = {
    "name": "StayPilot Demo Property",
    "total_rooms": 290,
    "room_types": {
        "QNBX": {
            "name": "Corner Queen - City View"
        },
        "QNDW": {
            "name": "Corner Queen - River View"
        },
        "QNDA": {
            "name": "Accessible Queen",
            "features": [
                "Roll-in shower",
                "Wider entryways",
                "Lower beds"
            ]
        },
        "QND2": {
            "name": "Two Queen Beds",
            "max_floor": 12
        },
        "KNPX": {
            "name": "King - City View"
        },
        "KNPW": {
            "name": "King - River View"
        },
        "QNXH": {
            "name": "Junior Queen Studio Suite",
            "rooms": ["1801", "1802", "1812", "1902", "1912"]
        },
        "QNEJ": {
            "name": "Queen Executive Suite",
            "rooms": ["1804", "1815", "1820", "1904", "1915"]
        },
        "KNEJ": {
            "name": "King Presidential Suite",
            "rooms": ["1809", "1909"]
        },
        "QNEX": {
            "name": "Queen River Suite",
            "rooms": ["1920"]
        }
    },
    "loyalty_levels": {
        "Y1": "Base",
        "M1": "Silver",
        "X1": "Gold",
        "P6": "Platinum Elite",
        "X4": "Titanium Elite",
        "X5": "Ambassador Elite"
    }
}

# Verified room-number mapping - StayPilot
# Source: Hotel floor plans and bed distribution matrix.
# Colors on the plans are NOT live housekeeping statuses.

def add_verified_rooms(room_type, floor, suffixes):
    numbers = HOTEL["room_types"][room_type].setdefault("rooms", [])

    for suffix in suffixes:
        number = str(floor * 100 + suffix)
        if number not in numbers:
            numbers.append(number)


TWO_QUEEN_STANDARD = [1, 2, 3, 6, 7, 10, 11, 12, 14, 17, 18, 21]
CORNER_STANDARD = [4, 5, 8, 9, 15, 16, 19, 20]

# Floors 4 and 5: two accessible rooms per floor.
for floor in [4, 5]:
    add_verified_rooms("QNDA", floor, [1, 2])
    add_verified_rooms(
        "QND2", floor,
        [3, 6, 7, 10, 11, 12, 14, 17, 18, 21]
    )
    add_verified_rooms("QNBX", floor, CORNER_STANDARD)

# Floors 6 through 9.
for floor in range(6, 10):
    add_verified_rooms("QND2", floor, TWO_QUEEN_STANDARD)
    add_verified_rooms("QNBX", floor, CORNER_STANDARD)

# Floors 10 through 12.
for floor in range(10, 13):
    add_verified_rooms("QND2", floor, TWO_QUEEN_STANDARD)
    add_verified_rooms("QNBX", floor, [15, 16])
    add_verified_rooms("QNDW", floor, [4, 5, 8, 9, 19, 20])

# Floors 14 through 17.
for floor in range(14, 18):
    add_verified_rooms("QNBX", floor, [15, 16])
    add_verified_rooms("QNDW", floor, [4, 5, 8, 9, 19, 20])
    add_verified_rooms("KNPW", floor, [1, 2, 3, 6, 7, 21])
    add_verified_rooms("KNPX", floor, [10, 11, 12, 14, 17, 18])

# Floor 18: standard rooms alongside existing suites.
add_verified_rooms("QNDW", 18, [5, 19])
add_verified_rooms("QNBX", 18, [16])
add_verified_rooms("KNPW", 18, [6, 7])
add_verified_rooms("KNPX", 18, [10, 11, 17, 18])

# Floor 19: standard rooms alongside existing suites.
add_verified_rooms("QNDW", 19, [5])
add_verified_rooms("QNBX", 19, [16])
add_verified_rooms("KNPW", 19, [6, 7])
add_verified_rooms("KNPX", 19, [10, 11, 17, 18])

# Verify category quantities against the source documents.
EXPECTED_COUNTS = {
    "QNBX": 64,
    "QNDW": 45,
    "QNDA": 4,
    "QND2": 104,
    "KNPX": 32,
    "KNPW": 28,
    "QNXH": 5,
    "QNEJ": 5,
    "KNEJ": 2,
    "QNEX": 1,
}

all_room_numbers = []

for room_type, expected in EXPECTED_COUNTS.items():
    numbers = HOTEL["room_types"][room_type]["rooms"]
    assert len(numbers) == expected, (
        f"{room_type}: expected {expected}, got {len(numbers)}"
    )
    all_room_numbers.extend(numbers)

assert len(all_room_numbers) == HOTEL["total_rooms"]
assert len(set(all_room_numbers)) == 290

EXPECTED_FLOORS = set(range(4, 13)) | set(range(14, 20))
actual_floors = {int(number) // 100 for number in all_room_numbers}

assert actual_floors == EXPECTED_FLOORS

