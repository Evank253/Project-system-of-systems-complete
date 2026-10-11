import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Reveal from "@/components/Reveal";
import { StatusDot } from "@/components/StatusBadge";
import { apiGet } from "@/lib/api";

export default function ArchitectureMap() {
  const [system, setSystem] = useState(null);

  useEffect(() => {
    apiGet("/system").then(setSystem).catch(() => setSystem(null));
  }, []);

  return (
    <section className="section-pad" id="architecture" data-testid="architecture-section">
      <div className="max-w-7xl mx-auto">
        <Reveal>
          <p className="eyebrow">01–08 / SYSTEM MAP</p>
          <h2 className="mt-4 font-display font-bold tracking-tight text-3xl sm:text-5xl leading-[1.05]">
            Eight subsystems.
            <br />
            <span className="text-dim">One invariant.</span>
          </h2>
          <p className="mt-5 max-w-2xl text-dim leading-relaxed">
            The public application is an interface layer around existing authoritative systems — never their
            replacement. Each section below is live-tracked in the registry with an honest status.
          </p>
        </Reveal>

        <div className="mt-14 grid md:grid-cols-2 xl:grid-cols-4 gap-5">
          {(system?.sections || []).map((s, i) => (
            <Reveal key={s.id} delay={i * 0.05}>
              <Link
                to={`/explorer?section=${s.id}`}
                data-testid={`arch-section-${s.id}`}
                className="panel panel-hover rounded-[3px] h-full flex flex-col p-6 group"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs text-accent tracking-[0.2em]">{s.id}</span>
                  <span className="font-mono text-[10px] text-mut">{s.components.length} COMPONENTS</span>
                </div>
                <h3 className="mt-4 font-display font-semibold text-lg tracking-wide group-hover:text-accent transition-colors duration-200">
                  {s.name}
                </h3>
                <p className="mt-2 text-[13px] text-mut leading-relaxed">{s.blurb}</p>
                <div className="mt-5 space-y-2 flex-1">
                  {s.components.map((c) => (
                    <div key={c.id} className="flex items-center gap-2.5 font-mono text-[11px]">
                      <StatusDot state={c.status} size={6} />
                      <span className="text-dim truncate">{c.name}</span>
                      <span className="ml-auto text-mut text-[9px] tracking-[0.14em]">{c.status.split("_")[0]}</span>
                    </div>
                  ))}
                </div>
                <span className="mt-5 font-mono text-[10px] tracking-[0.2em] text-mut group-hover:text-accent transition-colors duration-200">
                  INSPECT IN EXPLORER →
                </span>
              </Link>
            </Reveal>
          ))}
          {!system && (
            <div className="col-span-full panel rounded-[3px] p-8 font-mono text-sm text-warn" data-testid="architecture-loading-state">
              REGISTRY UNREACHABLE — statuses shown when /api/system responds. No cached or fabricated data is displayed.
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
