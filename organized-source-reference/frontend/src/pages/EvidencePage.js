import { useEffect, useState } from "react";
import Reveal from "@/components/Reveal";
import { apiGet } from "@/lib/api";

export default function EvidencePage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    apiGet("/evidence").then(setData).catch(() => setData(null));
  }, []);

  const levels = data?.levels || [];
  const ladder = levels.filter((l) => l.level !== "NOT_MEASURED").slice().reverse();
  const notMeasured = levels.find((l) => l.level === "NOT_MEASURED");

  return (
    <main className="pt-28 pb-24">
      <div className="max-w-7xl mx-auto px-5 lg:px-12">
        <Reveal>
          <p className="eyebrow">EVIDENCE EXPLORER</p>
          <h1 className="mt-4 font-display font-bold tracking-tight text-4xl sm:text-6xl">The ladder — and the truth about it.</h1>
          <p className="mt-4 max-w-2xl text-dim leading-relaxed">
            E0–E5 will be used exactly as the authoritative project documentation defines them. Until then, no
            interpretation is offered — and NOT_MEASURED is treated as a first-class status.
          </p>
        </Reveal>

        <div className="mt-12 grid lg:grid-cols-[1.05fr_0.95fr] gap-6">
          <div className="space-y-4" data-testid="evidence-ladder">
            {notMeasured && (
              <div className="border border-dashed border-[#64748B] bg-panel rounded-[3px] p-6" data-testid="not-measured-card">
                <div className="flex items-center justify-between">
                  <p className="font-mono text-sm tracking-[0.18em] text-[#94A3B8]">NOT_MEASURED</p>
                  <span className="placeholder-chip">FIRST-CLASS STATUS</span>
                </div>
                <p className="mt-3 text-sm text-dim leading-relaxed">{notMeasured.definition}</p>
              </div>
            )}
            {ladder.map((l) => (
              <div key={l.level} className="panel rounded-[3px] p-6" data-testid={`evidence-level-${l.level.toLowerCase()}`}>
                <div className="flex items-center justify-between">
                  <p className="font-mono text-sm tracking-[0.18em] text-[#F1F5F9]">{l.display_name}</p>
                  <span className="placeholder-chip">DEFINITION PENDING</span>
                </div>
                <p className="mt-3 text-[13px] text-mut leading-relaxed">{l.definition}</p>
              </div>
            ))}
            {!data && (
              <div className="panel rounded-[3px] p-10 font-mono text-xs text-warn tracking-[0.16em]" data-testid="evidence-error-state">
                EVIDENCE MODEL UNREACHABLE — no fabricated levels are displayed.
              </div>
            )}
          </div>

          <div className="space-y-6">
            <div className="panel rounded-[3px] p-6 sm:p-8" data-testid="evidence-rules">
              <p className="font-mono text-[10px] tracking-[0.22em] text-warn">UPGRADE RULES — ENFORCED IN CODE & TESTS</p>
              <ul className="mt-5 space-y-3">
                {(data?.rules || []).map((r, i) => (
                  <li key={i} className="font-mono text-[11px] leading-relaxed text-dim border-l-2 border-bad/60 pl-4">{r}</li>
                ))}
              </ul>
            </div>

            <div className="panel rounded-[3px] p-6 sm:p-8" data-testid="evidence-records">
              <div className="flex items-center justify-between">
                <p className="font-mono text-[10px] tracking-[0.22em] text-mut">EVIDENCE RECORDS · HASHED + PROVENANCE</p>
                <span className="font-mono text-[10px] text-mut">{data ? data.record_count : "…"}</span>
              </div>
              {data?.records?.length > 0 ? (
                <div className="mt-5 space-y-3">
                  {data.records.map((r) => (
                    <div key={r.id} className="border border-line rounded-[2px] p-3.5" data-testid="evidence-record-row">
                      <div className="flex items-center justify-between gap-3">
                        <span className="font-mono text-[10px] text-mut">{r.id.slice(0, 8)} · {r.type}</span>
                        <span className="font-mono text-[10px] tracking-[0.12em] text-[#94A3B8]">{r.level}</span>
                      </div>
                      <p className="mt-2 text-[12px] text-dim leading-relaxed">{r.claim}</p>
                      <p className="mt-2 hash-text truncate">SHA256 {r.hash}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="mt-4 text-sm text-mut" data-testid="records-empty-state">
                  No evidence records exist yet. Run a live test — each attempt creates the first factual, hashed records.
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="mt-16" data-testid="benchmarks-section">
          <Reveal>
            <p className="eyebrow">BENCHMARKS</p>
            <h2 className="mt-4 font-display font-bold tracking-tight text-3xl sm:text-4xl">No numbers is also an answer.</h2>
          </Reveal>
          <div className="mt-8 grid md:grid-cols-2 gap-5">
            <div className="panel rounded-[3px] p-7 min-h-[180px]" data-testid="benchmarks-historical">
              <p className="font-mono text-[10px] tracking-[0.22em] text-mut">HISTORICAL RESULTS</p>
              <p className="mt-4 text-sm text-mut leading-relaxed">
                No historical benchmark data has been supplied. Claims about past runs cannot be validated from
                this application yet — so none are shown.
              </p>
              <span className="placeholder-chip inline-block mt-4">[BENCHMARK_RESULTS]</span>
            </div>
            <div className="panel rounded-[3px] p-7 min-h-[180px]" data-testid="benchmarks-current">
              <p className="font-mono text-[10px] tracking-[0.22em] text-mut">CURRENT REPRODUCIBLE RESULTS</p>
              <p className="mt-4 text-sm text-mut leading-relaxed">
                Benchmark runs require the ARENA connector and a real evaluation environment. Until it is
                configured, this column stays honestly empty.
              </p>
              <span className="placeholder-chip inline-block mt-4">[BENCHMARK_RESULTS]</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
