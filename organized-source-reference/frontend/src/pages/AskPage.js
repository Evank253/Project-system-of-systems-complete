import { useEffect, useRef, useState } from "react";
import Reveal from "@/components/Reveal";
import { streamAI } from "@/lib/stream";
import { apiGet } from "@/lib/api";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

const MODELS = [
  { slug: "sol", label: "GPT-6 SOL", hint: "most capable" },
  { slug: "luna", label: "GPT-6 LUNA", hint: "faster" },
];

const SUGGESTIONS = [
  "What is actually implemented right now?",
  "Why does the system show zero verified components?",
  "What does NOT_MEASURED mean in this system?",
  "What is blocking production deployment?",
];

const mdChat = {
  p: (p) => <span className="block my-1.5" {...p} />,
  strong: (p) => <strong className="text-[#F1F5F9] font-semibold" {...p} />,
  h1: (p) => <span className="block font-mono text-[11px] tracking-[0.16em] text-accent mt-3 mb-1 uppercase" {...p} />,
  h2: (p) => <span className="block font-mono text-[11px] tracking-[0.16em] text-accent mt-3 mb-1 uppercase" {...p} />,
  h3: (p) => <span className="block font-mono text-[11px] tracking-[0.16em] text-accent mt-3 mb-1 uppercase" {...p} />,
  ul: (p) => <ul className="list-disc pl-4 my-1.5 space-y-1" {...p} />,
  ol: (p) => <ol className="list-decimal pl-4 my-1.5 space-y-1" {...p} />,
  li: (p) => <li className="leading-relaxed" {...p} />,
  code: (p) => <code className="font-mono text-[12px] text-accent bg-ink border border-line rounded-[2px] px-1" {...p} />,
};

export default function AskPage() {
  const [model, setModel] = useState("luna");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [aiConfig, setAiConfig] = useState(null);
  const sessionRef = useRef(`web-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`);

  useEffect(() => {
    apiGet("/ai/models").then(setAiConfig).catch(() => setAiConfig(null));
  }, []);

  const modelId = (slug) => aiConfig?.models?.find((m) => m.slug === slug)?.model || null;

  const newSession = () => {
    if (busy) return;
    setMessages([]);
    sessionRef.current = `web-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
  };

  const send = async (text) => {
    const q = (text ?? input).trim();
    if (!q || busy) return;
    setInput("");
    setBusy(true);
    setMessages((m) => [...m, { role: "user", content: q }, { role: "assistant", content: "", model: null, grounding: null, error: null, aborted: false }]);
    try {
      await streamAI("/api/ai/ask", { question: q, model, session_id: sessionRef.current }, {
        onStart: (e) => setMessages((m) => { const c = [...m]; c[c.length - 1] = { ...c[c.length - 1], model: e.model }; return c; }),
        onDelta: (d) => setMessages((m) => { const c = [...m]; const last = c[c.length - 1]; c[c.length - 1] = { ...last, content: last.content + d }; return c; }),
        onDone: (e) => setMessages((m) => { const c = [...m]; c[c.length - 1] = { ...c[c.length - 1], grounding: e.grounding, aborted: !!e.aborted }; return c; }),
        onError: (msg) => setMessages((m) => { const c = [...m]; c[c.length - 1] = { ...c[c.length - 1], error: msg }; return c; }),
      });
    } catch (e) {
      setMessages((m) => { const c = [...m]; c[c.length - 1] = { ...c[c.length - 1], error: String(e.message || e) }; return c; });
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="pt-28 pb-24" data-testid="ask-page">
      <div className="max-w-4xl mx-auto px-5 lg:px-12">
        <Reveal>
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="eyebrow">ASK THE SYSTEM</p>
              <h1 className="mt-4 font-display font-bold tracking-tight text-4xl sm:text-6xl">Reasoning over the registry.</h1>
            </div>
            {messages.length > 0 && (
              <button onClick={newSession} data-testid="ai-new-session-btn" className="btn-ghost !px-4 !py-2 !text-[11px]">
                NEW SESSION
              </button>
            )}
          </div>
          <p className="mt-4 text-dim leading-relaxed">
            The assistant answers only from the live component registry, evidence rules, documentation, and execution
            records — with inline citations like <span className="font-mono text-accent text-[13px]">[registry:03-01]</span>.
          </p>
        </Reveal>

        {aiConfig && !aiConfig.models?.[0]?.configured && (
          <div className="mt-6 border border-bad/50 bg-bad/5 rounded-[2px] p-4" data-testid="ai-not-configured">
            <p className="font-mono text-[11px] leading-relaxed text-bad">
              AI RUNTIME NOT CONFIGURED — the server reports the LLM key is missing. No simulated answers will be shown; this is the honest state.
            </p>
          </div>
        )}

        <div className="mt-6 border border-warn/40 bg-warn/5 border-l-2 border-l-warn rounded-[2px] p-4" data-testid="ai-disclaimer">
          <p className="font-mono text-[11px] leading-relaxed text-warn">
            THE ASSISTANT IS A REASONING INTERFACE — NEVER THE SOURCE OF TRUTH, AUTHORITY, VERIFICATION, OR QUALIFICATION. System state comes from the registry and evidence records. It cannot invent statuses and will report NOT_MEASURED when data does not exist.
          </p>
        </div>

        <div className="mt-6 flex flex-wrap items-center gap-3" data-testid="ai-model-selector">
          <span className="font-mono text-[10px] tracking-[0.2em] text-mut">MODEL · SERVER-CONFIGURED IDS</span>
          {MODELS.map((m) => (
            <button
              key={m.slug}
              data-testid={`ai-model-${m.slug}`}
              onClick={() => setModel(m.slug)}
              title={modelId(m.slug) ? `configured id: ${modelId(m.slug)}` : undefined}
              className={`font-mono text-[11px] tracking-[0.12em] px-3 py-1.5 rounded-[2px] border transition-colors duration-200 ${
                model === m.slug ? "text-accent border-accent/60 bg-accent/10" : "text-mut border-line hover:border-linestrong"
              }`}
            >
              {m.label} <span className="text-[9px] opacity-70">· {m.hint}</span>
            </button>
          ))}
          {modelId(model) && (
            <span className="font-mono text-[9px] text-mut" data-testid="ai-configured-id">RUNTIME ID: {modelId(model)}</span>
          )}
        </div>

        <div className="mt-8 space-y-5" data-testid="ai-chat">
          {messages.map((msg, i) =>
            msg.role === "user" ? (
              <div key={i} className="border-l-2 border-linestrong pl-4" data-testid={`ai-message-${i}`}>
                <p className="font-mono text-[10px] tracking-[0.2em] text-mut">YOU</p>
                <p className="mt-1.5 text-sm text-[#F1F5F9] leading-relaxed">{msg.content}</p>
              </div>
            ) : (
              <div key={i} className="border-l-2 border-accent/60 pl-4" data-testid={`ai-message-${i}`}>
                <p className="font-mono text-[10px] tracking-[0.2em] text-accent">
                  SYSTEM ASSISTANT{msg.model ? ` · ${msg.model.toUpperCase()}` : ""}
                </p>
                {msg.error ? (
                  <p className="mt-2 font-mono text-[11px] text-bad leading-relaxed" data-testid="ai-error">{msg.error}</p>
                ) : (
                  <div className="mt-1.5 text-sm text-dim leading-relaxed" data-testid="ai-answer">
                    <Markdown remarkPlugins={[remarkGfm]} components={mdChat}>{msg.content}</Markdown>
                    {busy && i === messages.length - 1 && <span className="text-accent animate-pulse">▍</span>}
                  </div>
                )}
                {msg.aborted && (
                  <p className="mt-2 font-mono text-[10px] text-warn" data-testid="ai-aborted-note">STREAM ABORTED ON TIMEOUT — PARTIAL OUTPUT, PRESENTED AS PARTIAL.</p>
                )}
                {msg.grounding && (
                  <div className="mt-3 flex flex-wrap items-center gap-2" data-testid="ai-grounding">
                    <span className="font-mono text-[9px] tracking-[0.14em] text-mut border border-line rounded-[2px] px-2 py-1">
                      GROUNDED IN: {msg.grounding.components_total} REGISTRY COMPONENTS · {msg.grounding.evidence_rules} EVIDENCE RULES · {msg.grounding.docs?.length || 0} DOCS
                    </span>
                    <span className="font-mono text-[9px] text-mut">AI interpretation — not the source of truth.</span>
                  </div>
                )}
              </div>
            )
          )}

          {messages.length === 0 && (
            <div className="space-y-3" data-testid="ai-suggestions">
              <p className="font-mono text-[10px] tracking-[0.2em] text-mut">TRY ASKING</p>
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  disabled={busy}
                  data-testid={`ai-suggestion-${i}`}
                  className="block w-full text-left panel panel-hover rounded-[3px] px-5 py-4 font-mono text-[12px] text-dim hover:text-accent transition-colors duration-200"
                >
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="mt-8 flex gap-3 sticky bottom-4">
          <input
            className="field-input"
            placeholder="Ask about components, statuses, evidence rules, docs…"
            value={input}
            maxLength={2000}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            data-testid="ai-chat-input"
          />
          <button onClick={() => send()} disabled={busy || !input.trim()} className="btn-primary shrink-0" data-testid="ai-send-btn">
            {busy ? "…" : "SEND"}
          </button>
        </div>
        <p className="mt-2 font-mono text-[9px] text-mut">MAX 2000 CHARACTERS PER QUESTION · {aiConfig?.rate_limit_note || "PER-IP RATE LIMIT APPLIES"}</p>
      </div>
    </main>
  );
}
