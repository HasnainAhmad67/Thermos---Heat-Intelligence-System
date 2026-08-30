
import { useState } from "react";
import { api } from "../api/client";
import AgentGuidance from "./AgentGuidance";

interface Message {
  role: "user" | "agent";
  text: string;
}

interface Props {
  selectedAssetId: string | null;
}

function renderMarkdown(text: string) {
  const lines = text.split("\n");

  return lines.map((line, i) => {
    const trimmed = line.trim();

    if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      return <li key={i}>{boldify(trimmed.slice(2))}</li>;
    }

    if (!trimmed) {
      return <br key={i} />;
    }

    return <p key={i}>{boldify(trimmed)}</p>;
  });
}

function boldify(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);

  return parts.map((part, i) =>
    part.startsWith("**") && part.endsWith("**") ? (
      <strong key={i}>{part.slice(2, -2)}</strong>
    ) : (
      part
    )
  );
}

export default function AgentChat({ selectedAssetId }: Props) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const askQuestion = async () => {
    const trimmed = question.trim();

    if (!trimmed) return;

    setMessages((prev) => [
      ...prev,
      { role: "user", text: trimmed },
    ]);

    setQuestion("");
    setLoading(true);
    setError(null);

    try {
      const res = await api.askAgent(
        trimmed,
        selectedAssetId ?? undefined
      );

      setMessages((prev) => [
        ...prev,
        { role: "agent", text: res.answer },
      ]);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (
    e: React.KeyboardEvent<HTMLInputElement>
  ) => {
    if (e.key === "Enter") askQuestion();
  };

  return (
    <div className="panel panel--chat">
      <h2>THERMOS Decision Agent</h2>

      <AgentGuidance />

      <div className="chat-history">
        {messages.length === 0 && (
          <p className="muted">
            Ask e.g. "Which zone needs attention first?" or
            "Why is this asset critical?"
          </p>
        )}

        {messages.map((m, i) => (
          <div
            key={i}
            className={`chat-bubble chat-bubble--${m.role}`}
          >
            {m.role === "agent" ? (
              <div className="chat-bubble__content">
                {renderMarkdown(m.text)}
              </div>
            ) : (
              m.text
            )}
          </div>
        ))}

        {loading && (
          <div className="chat-bubble chat-bubble--agent">
            Thinking…
          </div>
        )}
      </div>

      {error && <p className="error-text">{error}</p>}

      <div className="chat-input-row">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask the agent…"
        />

        <button onClick={askQuestion} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}

