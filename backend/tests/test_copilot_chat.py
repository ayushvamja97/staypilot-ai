"""Mocked integration tests for StayPilot AI chat.

These tests make no external OpenAI API requests.
"""

import json
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import app


class CopilotChatTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_missing_api_key_returns_503(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            response = self.client.post(
                "/api/copilot/chat",
                json={"message": "Hello"},
            )

        self.assertEqual(response.status_code, 503)
        self.assertIn(
            "not configured",
            response.json()["detail"],
        )

    def test_empty_message_returns_422(self):
        response = self.client.post(
            "/api/copilot/chat",
            json={"message": ""},
        )

        self.assertEqual(response.status_code, 422)

    def test_plain_ai_answer(self):
        fake_response = SimpleNamespace(
            status="completed",
            output=[],
            output_text="Hello! I am StayPilot.",
        )

        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "test-key-not-real"},
        ):
            with patch("copilot_chat.OpenAI") as mock_openai:
                mock_client = mock_openai.return_value
                mock_client.responses.create.return_value = (
                    fake_response
                )

                response = self.client.post(
                    "/api/copilot/chat",
                    json={"message": "Hello"},
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["answer"],
            "Hello! I am StayPilot.",
        )
        self.assertEqual(response.json()["sources"], [])
        mock_client.responses.create.assert_called_once()

    def test_inventory_tool_call(self):
        fake_call = SimpleNamespace(
            type="function_call",
            name="search_rooms",
            call_id="call_test_123",
            arguments=json.dumps({
                "floor": 19,
                "room_type": None,
                "view": "river",
                "accessible": None,
                "sofa_bed": None,
                "suite": None,
                "limit": 50,
            }),
        )

        first_response = SimpleNamespace(
            status="completed",
            output=[fake_call],
            output_text="",
        )

        final_response = SimpleNamespace(
            status="completed",
            output=[],
            output_text="There are 4 river-view rooms on floor 19.",
        )

        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "test-key-not-real"},
        ):
            with patch("copilot_chat.OpenAI") as mock_openai:
                mock_client = mock_openai.return_value

                mock_client.responses.create.side_effect = [
                    first_response,
                    final_response,
                ]

                response = self.client.post(
                    "/api/copilot/chat",
                    json={
                        "message":
                            "How many river-view rooms are on floor 19?"
                    },
                )

                calls = (
                    mock_client.responses.create.call_args_list
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["sources"],
            ["StayPilot demo room inventory"],
        )
        self.assertEqual(len(calls), 2)

        tool_output = calls[1].kwargs["input"][-1]

        self.assertEqual(
            tool_output["type"],
            "function_call_output",
        )
        self.assertEqual(
            tool_output["call_id"],
            "call_test_123",
        )

        inventory = json.loads(tool_output["output"])

        self.assertEqual(inventory["total"], 4)
        self.assertEqual(
            [
                room["room_number"]
                for room in inventory["rooms"]
            ],
            ["1905", "1906", "1907", "1920"],
        )
        self.assertFalse(
            inventory["availability_verified"]
        )

    def test_unexpected_tool_is_rejected(self):
        fake_response = SimpleNamespace(
            status="completed",
            output=[
                SimpleNamespace(
                    type="function_call",
                    name="delete_reservation",
                    call_id="call_unexpected",
                    arguments="{}",
                )
            ],
            output_text="",
        )

        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "test-key-not-real"},
        ):
            with patch("copilot_chat.OpenAI") as mock_openai:
                mock_openai.return_value.responses.create.return_value = (
                    fake_response
                )

                response = self.client.post(
                    "/api/copilot/chat",
                    json={"message": "Delete a reservation"},
                )

        self.assertEqual(response.status_code, 502)
        self.assertIn(
            "Unexpected AI tool",
            response.json()["detail"],
        )

    def test_incomplete_model_response_returns_502(self):
        fake_response = SimpleNamespace(
            status="incomplete",
            output=[],
            output_text="",
        )

        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "test-key-not-real"},
        ):
            with patch("copilot_chat.OpenAI") as mock_openai:
                mock_openai.return_value.responses.create.return_value = (
                    fake_response
                )

                response = self.client.post(
                    "/api/copilot/chat",
                    json={"message": "Hello"},
                )

        self.assertEqual(response.status_code, 502)


if __name__ == "__main__":
    unittest.main()
