"""Tests for free demo mode. No OpenAI requests."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import app


class DemoChatTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_floor_19_river_view(self):
        response = self.client.post(
            "/api/copilot/demo-chat",
            json={
                "message":
                    "How many river-view rooms are on floor 19?"
            },
        )

        self.assertEqual(response.status_code, 200)
        answer = response.json()["answer"]

        self.assertIn("4 matching rooms", answer)
        self.assertIn("1905", answer)
        self.assertIn("1906", answer)
        self.assertIn("1907", answer)
        self.assertIn("1920", answer)
        self.assertIn("not verified", answer)

    def test_booking_availability_not_claimed(self):
        response = self.client.post(
            "/api/copilot/demo-chat",
            json={"message": "Which rooms are available?"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "cannot check room availability",
            response.json()["answer"],
        )

    def test_policy_question_not_invented(self):
        response = self.client.post(
            "/api/copilot/demo-chat",
            json={"message": "Explain the hotel cancellation policy."},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "room-inventory questions only",
            response.json()["answer"],
        )

    def test_invalid_message_rejected(self):
        response = self.client.post(
            "/api/copilot/demo-chat",
            json={"message": ""},
        )

        self.assertEqual(response.status_code, 422)

    def test_openai_not_called(self):
        with patch("copilot_chat.OpenAI") as mock_openai:
            response = self.client.post(
                "/api/copilot/demo-chat",
                json={"message": "How many accessible rooms?"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("4 matching rooms", response.json()["answer"])
        mock_openai.assert_not_called()


if __name__ == "__main__":
    unittest.main()
