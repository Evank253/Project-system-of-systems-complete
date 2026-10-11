import { useState } from "react";
import { streamAI } from "@/lib/stream";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

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

const DEFAULT_Q = "Explain this component: purpose, current status, evidence, verification, qualification, deployment, dependencies, and limitations.";

export default function ExplainSection({ component }) {
  const [model, setModel] = useState("luna");
  const [question, setQuestion] = useState("");
  const [output, setOutput] = useState("");
  const [grounding, setGrounding] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const run = async () => {
    if (busy) return;
    setBusy(true);
    setOutput("");
    setGrounding(null);
    setError(null);
    try {
      await streamAI(`/api/ai/explain/${component.id}`, { question: question.trim() || undefined, model }, {
        onDelta: (d) => setOutput((o) => o + d),
        onDone: (e) => setGrounding(e.grounding),
        onError: (m) => setError(m),
      });
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mt-8 border-t border-line pt-6" data-testid="explain-section">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="font-mono text-[10px] tracking-[0.22em] text-accent">EXPLAIN · AI REASONING OVER THIS RECORD</p>
        <div className="flex gap-1.5">
          {["sol", "luna"].map((s) => (
            <button
              key={s}
              data-testid={`explain-model-${s}`}
              onClick={() => setModel(s)}
              className={`font-mono text-[9px] tracking-[0.14em] px-2 py-1 rounded-[2px] border transition-colors duration-200 ${
                model === s ? "text-accent border-accent/60 bg-accent/10" : "text-mut border-line hover:border-linestrong"
              }`}
            >
              {s.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-3 flex gap-2">
        <input
          className="field-input !py-2"
          placeholder={`${DEFAULT_Q.slice(0, 58)}…`}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run()}
          maxLength={2000}
          data-testid="explain-question-input"
        />
        <button onClick={run} disabled={busy} className="btn-primary !px-4 !py-2 shrink-0" data-testid="drawer-explain-btn">
          {busy ? "…" : "EXPLAIN"}
        </button>
      </div>

      {(output || busy || error) && (
        <div className="mt-3 border border-line rounded-[2px] p-4 bg-ink/60">
          {error ? (
            <p className="font-mono text-[11px] text-bad leading-relaxed" data-testid="explain-error">{error}</p>
          ) : (
            <div className="text-[13px] leading-relaxed text-dim" data-testid="drawer-explain-output">
              <Markdown remarkPlugins={[remarkGfm]} components={mdChat}>{output}</Markdown>
              {busy && <span className="text-accent animate-pulse">▍</span>}
            </div>
          )}
          {grounding && (
            <p className="mt-3 font-mono text-[9px] tracking-[0.14em] text-mut" data-testid="explain-grounding">
              GROUNDED IN: COMPONENT {grounding.component_id} RECORD ({grounding.component_status}) · EVIDENCE {grounding.evidence_level}
            </p>
          )}
          <p className="mt-2 font-mono text-[9px] text-mut leading-relaxed">
            AI interpretation — the registry record above remains the authoritative source. This explanation is never verification or qualification.
          </p>
        </div>
      )}
    </div>
  );
}
