"""HTTP integration tests for the Copilot inventory API."""

import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import app


class CopilotApiTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_search_river_view_on_floor_19(self):
        response = self.client.get(
            "/api/copilot/rooms/search",
            params={"floor": 19, "view": "river"},
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["total"], 4)
        self.assertEqual(
            [room["room_number"] for room in data["rooms"]],
            ["1905", "1906", "1907", "1920"],
        )

    def test_accessible_room_search(self):
        response = self.client.get(
            "/api/copilot/rooms/search",
            params={"accessible": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 4)

    def test_invalid_floor_returns_422(self):
        response = self.client.get(
            "/api/copilot/rooms/search",
            params={"floor": -1},
        )

        self.assertEqual(response.status_code, 422)

    def test_invalid_view_returns_422(self):
        response = self.client.get(
            "/api/copilot/rooms/search",
            params={"view": "ocean"},
        )

        self.assertEqual(response.status_code, 422)

    def test_invalid_limit_returns_422(self):
        response = self.client.get(
            "/api/copilot/rooms/search",
            params={"limit": 101},
        )

        self.assertEqual(response.status_code, 422)

    def test_no_live_availability_claim(self):
        response = self.client.get(
            "/api/copilot/rooms/search",
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            response.json()["availability_verified"]
        )


if __name__ == "__main__":
    unittest.main()
