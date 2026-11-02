import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hotel_config import HOTEL
from main import reservations
from room_inventory import ROOMS


class HotelDataTests(unittest.TestCase):

    def test_room_inventory_count(self):
        self.assertEqual(len(ROOMS), HOTEL["total_rooms"])
        self.assertEqual(len(ROOMS), 290)

    def test_unique_room_numbers(self):
        numbers = [room["room_number"] for room in ROOMS]
        self.assertEqual(len(numbers), len(set(numbers)))

    def test_room_numbers_are_normalized(self):
        numbers = {room["room_number"] for room in ROOMS}
        self.assertIn("401", numbers)
        self.assertNotIn("0401", numbers)

    def test_reservation_rooms_exist(self):
        inventory = {
            room["room_number"]: room
            for room in ROOMS
        }

        for reservation in reservations:
            with self.subTest(reservation=reservation["id"]):
                self.assertIn(
                    reservation["room_number"],
                    inventory,
                )

    def test_reservation_categories_match_rooms(self):
        inventory = {
            room["room_number"]: room
            for room in ROOMS
        }

        for reservation in reservations:
            with self.subTest(reservation=reservation["id"]):
                room = inventory[reservation["room_number"]]
                self.assertEqual(
                    reservation["room_type"],
                    room["room_type"],
                )

    def test_no_duplicate_room_assignments(self):
        numbers = [
            reservation["room_number"]
            for reservation in reservations
        ]
        self.assertEqual(len(numbers), len(set(numbers)))


if __name__ == "__main__":
    unittest.main()
