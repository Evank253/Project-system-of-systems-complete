import { Link } from "react-router-dom";
import Reveal from "@/components/Reveal";

const STAGES = [
  ["TEST EXECUTION", "IMPLEMENTED", "Real runner — /api/executions"],
  ["VERIFICATION", "VERIFICATION_REQUIRED", "Needs an independent witness"],
  ["REPRODUCTION", "INTEGRATION_REQUIRED", "Harness not attached yet"],
  ["INDEPENDENT WITNESS", "INTEGRATION_REQUIRED", "Cannot be self-issued"],
  ["QUALIFICATION", "QUALIFICATION_REQUIRED", "Formal gates not yet run"],
];

const STATES = [
  ["NOT_CONFIGURED", "A connector has no runtime endpoint. Set its env var — until then, nothing is pretended."],
  ["UNAVAILABLE", "A real call was attempted and failed. The actual error is recorded and shown."],
  ["NOT_MEASURED", "No measurement exists. First-class, honest, never rendered as PASS."],
  ["BLOCKED", "A gate is closed for a named reason — e.g. production requires domain, secrets, review."],
];

export default function TevvLive() {
  return (
    <section className="section-pad border-t border-line" data-testid="tevv-section">
      <div className="max-w-7xl mx-auto">
        <Reveal>
          <p className="eyebrow">TEVV / LIVE STATES</p>
          <h2 className="mt-4 font-display font-bold tracking-tight text-3xl sm:text-5xl leading-[1.05]">
            Run a real test.
            <br />
            <span className="text-dim">See the real state — whatever it is.</span>
          </h2>
        </Reveal>

        <div className="mt-14 grid lg:grid-cols-[1.1fr_0.9fr] gap-5">
          <Reveal>
            <div className="panel rounded-[3px] h-full p-6 sm:p-8" data-testid="tevv-pipeline">
              <p className="font-mono text-[10px] tracking-[0.22em] text-mut">TEVV PIPELINE · CURRENT STATE OF EACH GATE</p>
              <div className="mt-6 space-y-0">
                {STAGES.map(([name, status, note], i) => (
                  <div key={name} className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-5 py-4 border-b border-line/60 last:border-0" data-testid={`tevv-stage-${i}`}>
                    <span className="font-mono text-[11px] text-mut w-8 shrink-0">{String(i + 1).padStart(2, "0")}</span>
                    <span className="font-display font-semibold text-base tracking-wide w-56 shrink-0">{name}</span>
                    <span className={`font-mono text-[10px] tracking-[0.14em] px-2 py-1 rounded-[2px] border w-fit ${
                      status === "IMPLEMENTED" ? "text-ok border-ok/40 bg-ok/10" : "text-warn border-warn/40 bg-warn/10"
                    }`}>
                      {status.replace(/_/g, " ")}
                    </span>
                    <span className="text-[12px] text-mut sm:ml-auto">{note}</span>
                  </div>
                ))}
              </div>
            </div>
          </Reveal>

          <Reveal delay={0.08}>
            <div className="panel rounded-[3px] h-full p-6 sm:p-8" data-testid="live-states-panel">
              <p className="font-mono text-[10px] tracking-[0.22em] text-mut">STATES THIS SYSTEM REPORTS — NEVER A FAKE SUCCESS</p>
              <div className="mt-6 space-y-5">
                {STATES.map(([s, d]) => (
                  <div key={s} data-testid={`live-state-${s.toLowerCase()}`}>
                    <p className="font-mono text-xs tracking-[0.16em]" style={{ color: s === "NOT_MEASURED" ? "#64748B" : s === "BLOCKED" || s === "UNAVAILABLE" ? "#EF4444" : "#F59E0B" }}>
                      {s.replace(/_/g, " ")}
                    </p>
                    <p className="mt-1 text-[13px] text-dim leading-relaxed">{d}</p>
                  </div>
                ))}
              </div>
              <div className="mt-8 flex flex-wrap gap-4">
                <Link to="/test" data-testid="tevv-run-test-btn" className="btn-primary">[ RUN TEST ]</Link>
                <Link to="/docs" data-testid="tevv-docs-btn" className="btn-ghost">READ THE SPECS</Link>
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
