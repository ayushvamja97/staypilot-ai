import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = `${(process.env.STAYPILOT_BACKEND_ORIGIN || "http://127.0.0.1:8002").replace(/\/$/, "")}/api/copilot/demo-chat`;

export async function POST(request: NextRequest) {
  let payload: unknown;

  try {
    payload = await request.json();
  } catch {
    return NextResponse.json(
      { error: "Invalid JSON request." },
      { status: 400 }
    );
  }

  if (
    !payload ||
    typeof payload !== "object" ||
    Array.isArray(payload)
  ) {
    return NextResponse.json(
      { error: "Invalid chat request." },
      { status: 400 }
    );
  }

  const data = payload as Record<string, unknown>;
  const message = data.message;
  const history = data.history ?? [];

  if (
    typeof message !== "string" ||
    !message.trim() ||
    message.length > 2000
  ) {
    return NextResponse.json(
      { error: "Message must contain 1 to 2000 characters." },
      { status: 400 }
    );
  }

  if (
    !Array.isArray(history) ||
    history.length > 10 ||
    !history.every((turn: unknown) => {
      if (
        !turn ||
        typeof turn !== "object" ||
        Array.isArray(turn)
      ) {
        return false;
      }

      const item = turn as Record<string, unknown>;

      return (
        (item.role === "user" || item.role === "assistant") &&
        typeof item.content === "string" &&
        item.content.length > 0 &&
        item.content.length <= 2000
      );
    })
  ) {
    return NextResponse.json(
      { error: "Invalid conversation history." },
      { status: 400 }
    );
  }

  try {
    const upstream = await fetch(BACKEND_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message.trim(),
        history,
      }),
      cache: "no-store",
      signal: AbortSignal.timeout(75000),
    });

    if (!upstream.ok) {
      const status =
        upstream.status === 503 ? 503 :
        upstream.status === 422 ? 422 : 502;

      return NextResponse.json(
        {
          error:
            status === 503
              ? "The AI service is not configured yet."
              : "The AI backend could not complete this request.",
        },
        { status }
      );
    }

    const result: unknown = await upstream.json();

    if (
      !result ||
      typeof result !== "object" ||
      !("answer" in result) ||
      typeof result.answer !== "string" ||
      !result.answer.trim()
    ) {
      return NextResponse.json(
        { error: "Invalid response from the AI backend." },
        { status: 502 }
      );
    }

    const sources =
      "sources" in result && Array.isArray(result.sources)
        ? result.sources.filter(
            (source): source is string =>
              typeof source === "string"
          )
        : [];

    return NextResponse.json(
      { answer: result.answer, sources },
      {
        status: 200,
        headers: { "Cache-Control": "no-store" },
      }
    );
  } catch {
    return NextResponse.json(
      { error: "The AI backend is unreachable." },
      { status: 502 }
    );
  }
}
