import { useEffect, useState } from "react";
import Reveal from "@/components/Reveal";
import StatusBadge from "@/components/StatusBadge";
import { statusColor } from "@/components/StatusBadge";
import { apiGet, apiPost } from "@/lib/api";

export default function LiveTest() {
  const [catalog, setCatalog] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [task, setTask] = useState("ping");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [runError, setRunError] = useState(null);
  const [history, setHistory] = useState(null);

  const loadHistory = () => apiGet("/executions?limit=10").then(setHistory).catch(() => setHistory(null));

  useEffect(() => {
    apiGet("/tasks").then((d) => {
      setCatalog(d);
      const selftest = d.connectors.find((c) => c.connector_id === "app-selftest");
      if (selftest) setSelectedId(selftest.connector_id);
    }).catch(() => setCatalog(null));
    loadHistory();
  }, []);

  const selected = catalog?.connectors.find((c) => c.connector_id === selectedId);

  const run = async () => {
    if (!selectedId || running) return;
    setRunning(true);
    setRunError(null);
    setResult(null);
    try {
      const d = await apiPost("/executions", { connector_id: selectedId, task });
      setResult(d);
      loadHistory();
    } catch (e) {
      setRunError(String(e.message || e));
    } finally {
      setRunning(false);
    }
  };

  return (
    <main className="pt-28 pb-24">
      <div className="max-w-7xl mx-auto px-5 lg:px-12">
        <Reveal>
          <p className="eyebrow">LIVE TEST</p>
          <h1 className="mt-4 font-display font-bold tracking-tight text-4xl sm:text-6xl">Real execution. Real states.</h1>
          <p className="mt-4 max-w-2xl text-dim leading-relaxed">
            This interface invokes the running backend for real. An unconfigured connector returns
            <span className="font-mono text-warn"> NOT_CONFIGURED</span> — never a simulated success. Every attempt is recorded
            as a hashed evidence record.
          </p>
        </Reveal>

        <div className="mt-12 grid lg:grid-cols-[0.9fr_1.1fr] gap-6">
          <div>
            <p className="font-mono text-[10px] tracking-[0.22em] text-mut mb-4">SELECT CONNECTOR · {catalog ? `${catalog.connectors.length} REGISTERED` : "…"}</p>
            <div className="space-y-3" data-testid="connector-catalog">
              {catalog?.connectors.map((c) => (
                <button
                  key={c.connector_id}
                  data-testid={`connector-card-${c.connector_id}`}
                  onClick={() => { setSelectedId(c.connector_id); setResult(null); setRunError(null); }}
                  className={`w-full text-left panel rounded-[3px] p-5 transition-colors duration-200 border ${
                    selectedId === c.connector_id ? "border-accent/70 bg-hov" : "border-line hover:border-linestrong"
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-display font-semibold text-[15px]">{c.name}</span>
                    <StatusBadge state={c.configured ? "CONFIGURED" : "NOT_CONFIGURED"} />
                  </div>
                  <p className="mt-2 text-[12px] text-mut leading-relaxed">{c.role}</p>
                  <p className="mt-2 font-mono text-[10px] text-mut">ENDPOINT ENV: <span className="text-dim">{c.endpoint_env || "—"}</span></p>
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col">
            <div className="panel rounded-[3px] p-6 sm:p-8" data-testid="live-test-console">
              <p className="font-mono text-[10px] tracking-[0.22em] text-mut">EXECUTION CONSOLE</p>
              <label className="block mt-5">
                <span className="font-mono text-[10px] tracking-[0.2em] text-mut">TASK</span>
                <input
                  className="field-input mt-1.5"
                  value={task}
                  onChange={(e) => setTask(e.target.value)}
                  placeholder="e.g. ping, status, datastore-ping"
                  data-testid="live-test-task-input"
                />
              </label>
              {selected?.suggested_tasks?.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {selected.suggested_tasks.map((t) => (
                    <button
                      key={t}
                      onClick={() => setTask(t)}
                      data-testid={`task-suggestion-${t}`}
                      className="font-mono text-[10px] text-dim border border-line px-2.5 py-1.5 rounded-[2px] hover:border-accent hover:text-accent transition-colors duration-200"
                    >
                      {t}
                    </button>
                  ))}
                </div>
              )}
              <button onClick={run} disabled={running || !selectedId} className="btn-primary mt-6 w-full justify-center" data-testid="live-test-run-btn">
                {running ? "EXECUTING…" : "[ RUN TEST ]"}
              </button>

              {runError && (
                <div className="mt-6 border border-bad/50 bg-bad/10 rounded-[2px] p-4" data-testid="live-test-error">
                  <p className="font-mono text-[11px] text-bad tracking-[0.14em]">REQUEST FAILED — REPORTED HONESTLY</p>
                  <p className="mt-1 font-mono text-[11px] text-dim">{runError}</p>
                </div>
              )}

              {result && (
                <div className="mt-6 border border-line rounded-[2px] overflow-hidden" data-testid="live-test-result">
                  <div className="flex items-center justify-between px-4 py-3 border-b border-line" style={{ background: `${statusColor(result.execution.state)}14` }}>
                    <span className="font-mono text-[11px] tracking-[0.18em]" style={{ color: statusColor(result.execution.state) }}>
                      STATE: {result.execution.state.replace(/_/g, " ")}
                    </span>
                    <span className="font-mono text-[10px] text-mut">{new Date(result.execution.created_at).toLocaleTimeString()}</span>
                  </div>
                  <div className="p-4 space-y-3">
                    <p className="text-sm text-[#F1F5F9]" data-testid="result-summary">{result.execution.summary}</p>
                    {result.execution.details && <p className="text-[12px] text-dim leading-relaxed" data-testid="result-details">{result.execution.details}</p>}
                    {Object.keys(result.execution.measured || {}).length > 0 && (
                      <div className="border border-line rounded-[2px] p-3" data-testid="result-measured">
                        <p className="font-mono text-[9px] tracking-[0.2em] text-mut mb-2">MEASURED — REAL VALUES ONLY</p>
                        {Object.entries(result.execution.measured).map(([k, v]) => (
                          <div key={k} className="flex justify-between font-mono text-[11px] py-0.5">
                            <span className="text-mut">{k}</span>
                            <span className="text-accent">{String(v)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    <div className="border border-line rounded-[2px] p-3" data-testid="result-evidence">
                      <p className="font-mono text-[9px] tracking-[0.2em] text-mut mb-1">EVIDENCE RECORD</p>
                      <p className="font-mono text-[11px] text-dim">LEVEL: <span style={{ color: statusColor(result.evidence_record.level) }}>{result.evidence_record.level}</span> · HASH: <span className="text-mut">{String(result.evidence_record.hash).slice(0, 26)}…</span></p>
                      <p className="mt-1 text-[11px] text-mut leading-relaxed">{result.evidence_record.note}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="panel rounded-[3px] mt-6 p-6 sm:p-8 flex-1" data-testid="execution-history">
              <div className="flex items-center justify-between">
                <p className="font-mono text-[10px] tracking-[0.22em] text-mut">EXECUTION HISTORY · PERSISTED RECORDS</p>
                <span className="font-mono text-[10px] text-mut">{history ? `${history.total} SHOWN` : "…"}</span>
              </div>
              {history?.executions?.length > 0 ? (
                <div className="mt-4 space-y-0">
                  {history.executions.map((e) => (
                    <div key={e.id} className="flex items-center gap-3 py-2.5 border-b border-line/50 last:border-0" data-testid="history-row">
                      <span className="font-mono text-[10px] text-mut w-20 shrink-0">{new Date(e.created_at).toLocaleTimeString()}</span>
                      <span className="font-mono text-[11px] text-dim truncate flex-1">{e.connector_id} · {e.task}</span>
                      <span className="font-mono text-[10px] tracking-[0.12em]" style={{ color: statusColor(e.state) }}>{e.state.replace(/_/g, " ")}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="mt-4 text-sm text-mut" data-testid="history-empty-state">No executions recorded yet. Run a test — the first factual record will appear here.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
