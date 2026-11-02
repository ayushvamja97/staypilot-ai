"""StayPilot AI chat service with read-only inventory tools."""

import json
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field

from copilot_tools import search_rooms


load_dotenv(Path(__file__).with_name(".env"))

router = APIRouter(prefix="/api/copilot", tags=["Copilot"])


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatTurn] = Field(default_factory=list, max_length=10)


SYSTEM_INSTRUCTIONS = """
You are StayPilot, a hotel operations assistant for a demo property.

Rules:
- Use search_rooms for factual questions about the room inventory.
- Never invent room numbers, room attributes, or inventory totals.
- Never claim that a room is available for booking.
- Housekeeping and maintenance statuses are not live.
- Only synthetic demonstration data is connected.
- No verified hotel policy documents are connected yet.
- If asked about an unverified policy, explain that you cannot
  confirm the property's policy.
- The connected tools are read-only.
- Be concise, accurate, and clear about limitations.
"""

ROOM_PROPERTIES = {
    "floor": {"type": ["integer", "null"]},
    "room_type": {"type": ["string", "null"]},
    "view": {
        "type": ["string", "null"],
        "enum": ["city", "river", "not_specified", None],
    },
    "accessible": {"type": ["boolean", "null"]},
    "sofa_bed": {"type": ["boolean", "null"]},
    "suite": {"type": ["boolean", "null"]},
    "limit": {"type": ["integer", "null"]},
}

ROOM_TOOL = {
    "type": "function",
    "name": "search_rooms",
    "description": (
        "Search the demo property's 290-room inventory by floor, "
        "category, view and room features. This is not a live "
        "availability or reservation search."
    ),
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": ROOM_PROPERTIES,
        "required": list(ROOM_PROPERTIES),
        "additionalProperties": False,
    },
}


@router.post("/chat")
def chat(request: ChatRequest):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key is not configured.",
        )

    client = OpenAI(
        api_key=api_key,
        timeout=30.0,
        max_retries=1,
    )

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    messages = [
        {"role": turn.role, "content": turn.content}
        for turn in request.history
    ]
    messages.append({
        "role": "user",
        "content": request.message,
    })

    try:
        response = client.responses.create(
            model=model,
            instructions=SYSTEM_INSTRUCTIONS,
            input=messages,
            tools=[ROOM_TOOL],
            parallel_tool_calls=False,
            store=False,
        )

        if response.status != "completed":
            raise HTTPException(
                status_code=502,
                detail="AI response did not complete.",
            )

        tool_calls = [
            item for item in response.output
            if item.type == "function_call"
        ]

        sources = []

        if tool_calls:
            if len(tool_calls) > 3:
                raise HTTPException(
                    status_code=502,
                    detail="Too many tool calls.",
                )

            messages.extend(response.output)

            for call in tool_calls:
                if call.name != "search_rooms":
                    raise HTTPException(
                        status_code=502,
                        detail="Unexpected AI tool request.",
                    )

                try:
                    arguments = json.loads(call.arguments)

                    if not isinstance(arguments, dict):
                        raise ValueError("Expected object arguments")

                    arguments = {
                        key: value
                        for key, value in arguments.items()
                        if value is not None
                    }

                    result = search_rooms(**arguments)

                    sources = ["StayPilot demo room inventory"]

                except (ValueError, TypeError) as exc:
                    result = {"error": str(exc)}

                messages.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result),
                })

            response = client.responses.create(
                model=model,
                instructions=SYSTEM_INSTRUCTIONS,
                input=messages,
                tools=[ROOM_TOOL],
                tool_choice="none",
                store=False,
            )

            if response.status != "completed":
                raise HTTPException(
                    status_code=502,
                    detail="AI response did not complete.",
                )

        answer = (response.output_text or "").strip()

        if not answer:
            raise HTTPException(
                status_code=502,
                detail="AI returned no answer.",
            )

        return {
            "answer": answer,
            "sources": sources,
        }

    except OpenAIError as exc:
        raise HTTPException(
            status_code=502,
            detail="AI provider request failed.",
        ) from exc
