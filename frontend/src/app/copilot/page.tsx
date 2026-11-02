"use client";

import Link from "next/link";
import { useRef, useState } from "react";

type Role = "user" | "assistant";

type ChatMessage = {
  id: number;
  role: Role;
  content: string;
  sources?: string[];
};

type CopilotResponse = {
  answer: string;
  sources?: string[];
};

const suggestions = [
  {
    title: "Room Inventory",
    description: "Search rooms using hotel attributes",
    prompt: "How many river-view rooms are on floor 19?",
  },
  {
    title: "Policy Assistant",
    description: "Find answers in hotel procedures",
    prompt: "Explain the credit card authorization policy.",
  },
  {
    title: "Shift Handover",
    description: "Summarize operational priorities",
    prompt: "Prepare a front desk shift handover.",
  },
  {
    title: "Operational Analysis",
    description: "Investigate issues and recommend actions",
    prompt: "What information should I review before resolving an oversold room?",
  },
];

export default function CopilotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLTextAreaElement>(null);

  function selectSuggestion(prompt: string) {
    setInput(prompt);
    setError("");
    inputRef.current?.focus();
  }

  async function sendMessage() {
    const question = input.trim();

    if (!question || loading || question.length > 2000) return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: "user",
      content: question,
    };

    const history = messages.map(({ role, content }) => ({
      role,
      content,
    }));

    setMessages((previous) => [...previous, userMessage]);
    setInput("");
    setError("");
    setLoading(true);

    try {
      const response = await fetch("/api/copilot/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: question,
          history: history.slice(-10),
        }),
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(
            "The AI service is not connected yet. We will build its backend next."
          );
        }

        throw new Error(
          `The AI service returned an error (${response.status}).`
        );
      }

      const data: CopilotResponse = await response.json();

      if (
        typeof data.answer !== "string" ||
        data.answer.trim().length === 0
      ) {
        throw new Error("The AI service returned an invalid response.");
      }

      const assistantMessage: ChatMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: data.answer,
        sources: Array.isArray(data.sources)
          ? data.sources.filter(
              (source): source is string =>
                typeof source === "string"
            )
          : [],
      };

      setMessages((previous) => [...previous, assistantMessage]);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to the AI service."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#f2f5f9] text-[#243247]">
      <header className="border-b border-[#0b2c50] bg-[#123d70] text-white">
        <div className="mx-auto flex max-w-[1600px] items-center justify-between px-6 py-4">
          <div>
            <div className="text-xl font-bold tracking-tight">
              StayPilot AI
            </div>
            <div className="text-[10px] uppercase tracking-[0.16em] text-blue-200">
              Property Management Intelligence
            </div>
          </div>
          <div className="rounded border border-white/25 bg-white/10 px-3 py-2 text-xs">
            Demo Property
          </div>
        </div>
      </header>

      <div className="mx-auto flex min-h-[calc(100vh-72px)] max-w-[1600px]">
        <aside className="hidden w-60 shrink-0 border-r border-slate-200 bg-white p-5 md:block">
          <div className="mb-5 text-xs font-semibold uppercase tracking-wider text-slate-400">
            Workspace
          </div>

          <nav className="space-y-1 text-sm">
            <Link
              href="/"
              className="block rounded px-3 py-3 text-slate-600 hover:bg-slate-100"
            >
              Dashboard
            </Link>

            <Link
              href="/rooms"
              className="block rounded px-3 py-3 text-slate-600 hover:bg-slate-100"
            >
              Room Management
            </Link>

            <Link
              href="/copilot"
              className="block rounded bg-blue-50 px-3 py-3 font-semibold text-blue-700"
              aria-current="page"
            >
              AI Operations Copilot
            </Link>
          </nav>

          <div className="mt-10 rounded-lg border border-slate-200 bg-slate-50 p-4">
            <div className="text-xs font-semibold text-slate-700">
              Development Status
            </div>
            <p className="mt-2 text-xs leading-5 text-slate-500">
              The conversation interface is being built. AI responses
              will only appear when the backend is connected.
            </p>
          </div>
        </aside>

        <main className="flex min-w-0 flex-1 flex-col">
          <div className="border-b border-slate-200 bg-white px-5 py-5 md:px-8">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="text-xs text-slate-400">
                  Hotel Operations / AI Copilot
                </div>
                <h1 className="mt-1 text-2xl font-semibold text-[#17385c]">
                  AI Operations Copilot
                </h1>
                <p className="mt-1 text-sm text-slate-500">
                  Ask questions, investigate issues, and work with hotel data.
                </p>
              </div>

              <span className="rounded-full border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-medium text-amber-800">
                AI Integration Pending
              </span>
            </div>

            <div className="mt-4 flex gap-4 text-xs md:hidden">
              <Link href="/" className="text-blue-700 underline">
                Dashboard
              </Link>
              <Link href="/rooms" className="text-blue-700 underline">
                Rooms
              </Link>
            </div>
          </div>

          <div
            className="flex-1 space-y-5 overflow-y-auto px-5 py-7 md:px-8"
            aria-label="Conversation"
            aria-live="polite"
          >
            {messages.length === 0 && (
              <div className="mx-auto max-w-3xl pt-6">
                <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-[#123d70] text-2xl font-bold text-white">
                  S
                </div>

                <h2 className="text-2xl font-semibold text-[#17385c]">
                  Your hotel operations assistant
                </h2>

                <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
                  StayPilot Copilot is being developed to combine hotel
                  inventory, operational tools, and documented procedures
                  into one intelligent workspace.
                </p>

                <div className="mt-8 grid gap-3 sm:grid-cols-2">
                  {suggestions.map((item) => (
                    <button
                      key={item.title}
                      type="button"
                      onClick={() => selectSuggestion(item.prompt)}
                      className="rounded-xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:border-blue-300 hover:shadow-md"
                    >
                      <div className="font-semibold text-[#17385c]">
                        {item.title}
                      </div>
                      <div className="mt-2 text-xs leading-5 text-slate-500">
                        {item.description}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.length > 0 && (
              <div className="mx-auto max-w-3xl space-y-5">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.role === "user"
                        ? "justify-end"
                        : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[90%] rounded-xl px-5 py-4 text-sm leading-7 shadow-sm ${
                        message.role === "user"
                          ? "bg-[#123d70] text-white"
                          : "border border-slate-200 bg-white text-slate-700"
                      }`}
                    >
                      <div className="mb-2 text-xs font-semibold opacity-70">
                        {message.role === "user"
                          ? "You"
                          : "StayPilot Copilot"}
                      </div>

                      <p className="whitespace-pre-wrap break-words">
                        {message.content}
                      </p>

                      {message.sources &&
                        message.sources.length > 0 && (
                          <div className="mt-4 border-t border-slate-200 pt-3">
                            <div className="text-xs font-semibold">
                              Sources
                            </div>
                            <ul className="mt-2 list-inside list-disc text-xs">
                              {message.sources.map((source, index) => (
                                <li key={index}>{source}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                    </div>
                  </div>
                ))}

                {loading && (
                  <div
                    className="text-sm text-slate-500"
                    role="status"
                  >
                    Processing your request...
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="border-t border-slate-200 bg-white px-5 py-5 md:px-8">
            <div className="mx-auto max-w-3xl">
              {error && (
                <div
                  role="alert"
                  className="mb-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
                >
                  {error}
                </div>
              )}

              <div className="rounded-xl border border-slate-300 bg-white p-3 shadow-sm focus-within:border-blue-500">
                <label htmlFor="copilot-input" className="sr-only">
                  Ask StayPilot Copilot
                </label>

                <textarea
                  id="copilot-input"
                  ref={inputRef}
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (
                      event.key === "Enter" &&
                      !event.shiftKey &&
                      !event.nativeEvent.isComposing
                    ) {
                      event.preventDefault();
                      void sendMessage();
                    }
                  }}
                  maxLength={2000}
                  rows={3}
                  placeholder="Ask about rooms, hotel policies, or operations..."
                  className="w-full resize-none bg-transparent px-2 py-2 text-sm outline-none placeholder:text-slate-400"
                />

                <div className="flex items-center justify-between gap-3 px-2">
                  <span className="text-xs text-slate-400">
                    {input.length}/2000 characters
                  </span>

                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        setMessages([]);
                        setInput("");
                        setError("");
                      }}
                      disabled={loading}
                      className="rounded-lg border border-slate-200 px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-50"
                    >
                      New Chat
                    </button>

                    <button
                      type="button"
                      onClick={() => void sendMessage()}
                      disabled={!input.trim() || loading}
                      className="rounded-lg bg-[#123d70] px-5 py-2 text-xs font-semibold text-white hover:bg-[#0d3159] disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {loading ? "Sending..." : "Send Message"}
                    </button>
                  </div>
                </div>
              </div>

              <p className="mt-3 text-center text-xs text-slate-400">
                Development environment. AI functionality is not connected yet.
                Verify operational decisions before acting.
              </p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
