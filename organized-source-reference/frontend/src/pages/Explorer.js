import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import Reveal from "@/components/Reveal";
import StatusBadge, { StatusDot } from "@/components/StatusBadge";
import ComponentDrawer from "@/components/ComponentDrawer";
import { apiGet } from "@/lib/api";

const STATUS_VOCAB = ["IMPLEMENTED", "INTEGRATION_REQUIRED", "TEST_REQUIRED", "VERIFICATION_REQUIRED", "QUALIFICATION_REQUIRED", "NOT_MEASURED", "BLOCKED"];
const DEPLOYMENT_VOCAB = ["DEVELOPMENT", "STAGING", "PRODUCTION", "NOT_DEPLOYED"];
const EVIDENCE_VOCAB = ["NOT_MEASURED", "E0", "E1", "E2", "E3", "E4", "E5"];

function Select({ label, value, onChange, options, testid }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="font-mono text-[10px] tracking-[0.2em] text-mut">{label}</span>
      <select className="field-input !py-2.5" value={value} onChange={(e) => onChange(e.target.value)} data-testid={testid}>
        <option value="">ALL</option>
        {options.map((o) => (
          <option key={o} value={o}>{o.replace(/_/g, " ")}</option>
        ))}
      </select>
    </label>
  );
}

export default function Explorer() {
  const [params, setParams] = useSearchParams();
  const [data, setData] = useState(null);
  const [system, setSystem] = useState(null);
  const [selected, setSelected] = useState(null);
  const [q, setQ] = useState(params.get("q") || "");

  const section = params.get("section") || "";
  const status = params.get("status") || "";
  const deployment = params.get("deployment") || "";
  const evidence = params.get("evidence") || "";

  const setParam = (key, value) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next, { replace: true });
  };

  useEffect(() => {
    apiGet("/system").then(setSystem).catch(() => setSystem(null));
  }, []);

  useEffect(() => {
    const qs = new URLSearchParams();
    if (section) qs.set("section", section);
    if (status) qs.set("status", status);
    if (deployment) qs.set("deployment", deployment);
    if (evidence) qs.set("evidence", evidence);
    if (q) qs.set("q", q);
    const t = setTimeout(() => {
      apiGet(`/components?${qs.toString()}`).then(setData).catch(() => setData(null));
    }, 200);
    return () => clearTimeout(t);
  }, [section, status, deployment, evidence, q]);

  const sectionName = useMemo(() => {
    if (!section || !system) return null;
    return system.sections.find((s) => s.id === section)?.name || section;
  }, [section, system]);

  return (
    <main className="pt-28 pb-24">
      <div className="max-w-7xl mx-auto px-5 lg:px-12">
        <Reveal>
          <p className="eyebrow">SYSTEM EXPLORER</p>
          <h1 className="mt-4 font-display font-bold tracking-tight text-4xl sm:text-6xl">The registry.</h1>
          <p className="mt-4 max-w-2xl text-dim leading-relaxed">
            Every component of the public infrastructure layer, with its honest lifecycle and evidence status.
            Click any row to inspect purpose, dependencies, source, capabilities, and limitations.
          </p>
        </Reveal>

        <div className="mt-10 panel rounded-[3px] p-5 grid grid-cols-2 md:grid-cols-5 gap-4" data-testid="explorer-filters">
          <Select label="SECTION" value={section} onChange={(v) => setParam("section", v)} options={(system?.sections || []).map((s) => [s.id, s.name]).map(([id]) => id)} testid="explorer-filter-section" />
          <Select label="STATUS" value={status} onChange={(v) => setParam("status", v)} options={STATUS_VOCAB} testid="explorer-filter-status" />
          <Select label="EVIDENCE" value={evidence} onChange={(v) => setParam("evidence", v)} options={EVIDENCE_VOCAB} testid="explorer-filter-evidence" />
          <Select label="DEPLOYMENT" value={deployment} onChange={(v) => setParam("deployment", v)} options={DEPLOYMENT_VOCAB} testid="explorer-filter-deployment" />
          <label className="flex flex-col gap-1.5 col-span-2 md:col-span-1">
            <span className="font-mono text-[10px] tracking-[0.2em] text-mut">SEARCH</span>
            <input className="field-input !py-2.5" placeholder="name or purpose…" value={q} onChange={(e) => setQ(e.target.value)} data-testid="explorer-filter-search" />
          </label>
        </div>

        <div className="mt-6 flex items-center justify-between">
          <p className="font-mono text-[11px] tracking-[0.16em] text-mut" data-testid="explorer-count">
            {data ? `${data.total} COMPONENT${data.total === 1 ? "" : "S"} SHOWN${sectionName ? ` · SECTION ${section} ${sectionName}` : ""}` : "LOADING REGISTRY…"}
          </p>
          {(section || status || deployment || evidence || q) && (
            <button className="font-mono text-[10px] tracking-[0.16em] text-mut hover:text-accent transition-colors duration-200" onClick={() => { setParams({}, { replace: true }); setQ(""); }} data-testid="explorer-clear-filters">
              CLEAR FILTERS ✕
            </button>
          )}
        </div>

        <div className="mt-4 space-y-2" data-testid="explorer-list">
          {data?.components.map((c, i) => (
            <Reveal key={c.id} delay={Math.min(i * 0.02, 0.2)} y={12}>
              <button
                data-testid={`component-row-${c.id}`}
                onClick={() => setSelected(c)}
                className="w-full text-left panel panel-hover rounded-[3px] px-5 py-4 grid grid-cols-[auto_1fr_auto] sm:grid-cols-[auto_110px_1fr_auto_auto_auto] items-center gap-4 group"
              >
                <StatusDot state={c.status} />
                <span className="hidden sm:block font-mono text-[11px] text-mut">{c.id}</span>
                <span className="min-w-0">
                  <span className="block font-display font-semibold text-[15px] truncate group-hover:text-accent transition-colors duration-200">{c.name}</span>
                  <span className="block font-mono text-[10px] text-mut tracking-[0.1em] mt-0.5 sm:hidden">{c.id} · {c.section_name}</span>
                </span>
                <span className="hidden sm:block font-mono text-[10px] text-mut tracking-[0.12em]">{c.section_name}</span>
                <span className="hidden sm:block"><StatusBadge state={c.status} /></span>
                <span className="font-mono text-[10px] text-mut group-hover:text-accent transition-colors duration-200">→</span>
              </button>
            </Reveal>
          ))}

          {data && data.total === 0 && (
            <div className="panel rounded-[3px] p-10 text-center" data-testid="explorer-empty-state">
              <p className="font-mono text-xs text-warn tracking-[0.16em]">NO COMPONENTS MATCH THESE FILTERS</p>
              <p className="mt-2 text-sm text-mut">Clear a filter — the registry contains 61 tracked components across 8 sections.</p>
            </div>
          )}

          {!data && (
            <div className="panel rounded-[3px] p-10 text-center font-mono text-xs text-warn tracking-[0.16em]" data-testid="explorer-error-state">
              REGISTRY UNREACHABLE — no cached or fabricated data is displayed.
            </div>
          )}
        </div>
      </div>

      <AnimatePresence>
        {selected && <ComponentDrawer component={selected} onClose={() => setSelected(null)} />}
      </AnimatePresence>
    </main>
  );
}
