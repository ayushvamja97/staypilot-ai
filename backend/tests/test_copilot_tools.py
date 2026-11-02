import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from copilot_tools import search_rooms


class CopilotToolsTests(unittest.TestCase):

    def test_total_inventory(self):
        result = search_rooms()
        self.assertEqual(result["total"], 290)
        self.assertTrue(result["has_more"])

    def test_floor_19_river_view(self):
        result = search_rooms(floor=19, view="river")

        self.assertEqual(result["total"], 4)

        numbers = [
            room["room_number"]
            for room in result["rooms"]
        ]

        self.assertEqual(
            numbers,
            ["1905", "1906", "1907", "1920"],
        )

    def test_accessible_rooms(self):
        result = search_rooms(accessible=True)
        self.assertEqual(result["total"], 4)

    def test_room_category(self):
        result = search_rooms(room_type="qnd2")
        self.assertEqual(result["total"], 104)

    def test_result_limit(self):
        result = search_rooms(floor=19, limit=2)

        self.assertEqual(result["total"], 14)
        self.assertEqual(len(result["rooms"]), 2)
        self.assertTrue(result["has_more"])

    def test_invalid_view(self):
        with self.assertRaises(ValueError):
            search_rooms(view="ocean")

    def test_invalid_limit(self):
        with self.assertRaises(ValueError):
            search_rooms(limit=0)

    def test_no_live_availability_claim(self):
        result = search_rooms()
        self.assertFalse(result["availability_verified"])

    def test_no_matching_rooms(self):
        result = search_rooms(floor=4, view="river")
        self.assertEqual(result["total"], 0)


if __name__ == "__main__":
    unittest.main()
