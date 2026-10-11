import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Reveal from "@/components/Reveal";
import { apiGet } from "@/lib/api";

const TERMS = ["CAPABILITY", "EVIDENCE", "VERIFICATION", "QUALIFICATION", "AUTHORITY"];

const CARDS = [
  {
    title: "EVIDENCE — E0–E5",
    to: "/evidence",
    testid: "model-card-evidence",
    body: "Six evidence levels, each defined only by authoritative documentation once supplied. NOT_MEASURED is a first-class status: displayed honestly, never rendered as a pass, never upgraded without a real measurement.",
    meta: "EVERY RECORD: SHA-256 + PROVENANCE",
  },
  {
    title: "AUTHORITY — H0–H3",
    to: "/docs/authority-model",
    testid: "model-card-authority",
    body: "Authority belongs to humans. A system's ability to act is capability, never authority. Delegation, authorization, and revocation are auditable lifecycles — enforced by KSI and human operators, not by this website.",
    meta: "ENFORCEMENT: KSI · HUMAN OPERATORS",
  },
  {
    title: "TEVV — THE GATES",
    to: "/docs/tevv-model",
    testid: "model-card-tevv",
    body: "Test execution runs here for real. Verification requires an independent witness. Reproduction requires a harness. Qualification requires formal gates. None of those exist yet — so nothing is verified or qualified.",
    meta: "VERIFIED: 0 · QUALIFIED: 0",
  },
];

export default function InvariantModels() {
  const [evidence, setEvidence] = useState(null);
  useEffect(() => {
    apiGet("/evidence").then((d) => setEvidence(d)).catch(() => setEvidence(null));
  }, []);

  return (
    <section className="section-pad border-t border-line bg-panel/30" data-testid="invariant-section">
      <div className="max-w-7xl mx-auto">
        <Reveal>
          <p className="eyebrow">THE INVARIANT</p>
          <h2 className="mt-6 font-display font-bold tracking-tight text-2xl sm:text-4xl md:text-5xl leading-snug max-w-5xl">
            {TERMS.map((t, i) => (
              <span key={t}>
                <span className="text-[#F1F5F9]">{t}</span>
                {i < TERMS.length - 1 && <span className="text-accent mx-3 sm:mx-5">≠</span>}
              </span>
            ))}
          </h2>
          <p className="mt-6 max-w-2xl text-dim leading-relaxed">
            Five different claims. The most common failure in AI products is collapsing them into one. This
            system is built so that collapsing them is structurally impossible — the API has no code path that
            does it.
          </p>
        </Reveal>

        <div className="mt-14 grid md:grid-cols-3 gap-5">
          {CARDS.map((c, i) => (
            <Reveal key={c.title} delay={i * 0.06}>
              <Link to={c.to} data-testid={c.testid} className="panel panel-hover rounded-[3px] h-full flex flex-col p-7 group">
                <h3 className="font-mono text-[13px] tracking-[0.18em] text-accent">{c.title}</h3>
                <p className="mt-4 text-sm text-dim leading-relaxed flex-1">{c.body}</p>
                <div className="mt-6 flex items-center justify-between font-mono text-[10px] tracking-[0.16em]">
                  <span className="text-mut">{c.meta}</span>
                  <span className="text-mut group-hover:text-accent transition-colors duration-200">→</span>
                </div>
              </Link>
            </Reveal>
          ))}
        </div>

        {evidence && (
          <Reveal delay={0.1}>
            <div className="mt-10 panel rounded-[3px] p-6 sm:p-8" data-testid="no-upgrade-rules">
              <p className="font-mono text-[10px] tracking-[0.22em] text-warn">NEVER-UPGRADE RULES · ENFORCED IN CODE</p>
              <ul className="mt-4 grid md:grid-cols-2 gap-x-8 gap-y-2">
                {evidence.rules.slice(0, 4).map((r) => (
                  <li key={r} className="font-mono text-[11px] leading-relaxed text-dim before:text-bad before:content-['✕_']">
                    {r}
                  </li>
                ))}
              </ul>
            </div>
          </Reveal>
        )}
      </div>
    </section>
  );
}
