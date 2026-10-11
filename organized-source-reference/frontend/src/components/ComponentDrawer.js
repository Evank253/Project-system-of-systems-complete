import { useEffect } from "react";
import { motion } from "framer-motion";
import StatusBadge, { statusColor } from "./StatusBadge";
import ExplainSection from "./ExplainSection";

const Row = ({ label, children, testid }) => (
  <div data-testid={testid} className="flex flex-col sm:flex-row sm:items-start gap-1 sm:gap-4 py-3 border-b border-line/60">
    <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-mut w-40 shrink-0 pt-1">{label}</span>
    <span className="text-sm text-[#F1F5F9] flex-1">{children}</span>
  </div>
);

export default function ComponentDrawer({ component, onClose }) {
  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  if (!component) return null;

  return (
    <motion.div
      className="fixed inset-0 z-[100] flex justify-end"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} data-testid="drawer-overlay" />
      <motion.aside
        data-testid="component-detail-drawer"
        initial={{ x: "100%" }}
        animate={{ x: 0 }}
        exit={{ x: "100%" }}
        transition={{ type: "spring", damping: 30, stiffness: 260 }}
        className="relative h-full w-full max-w-xl overflow-y-auto border-l border-line bg-panel p-6 sm:p-8"
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="font-mono text-[11px] tracking-[0.2em] text-mut">{component.id} · SECTION {component.section}</p>
            <h3 className="font-display text-2xl font-bold mt-1">{component.name}</h3>
          </div>
          <button
            data-testid="drawer-close-btn"
            onClick={onClose}
            className="btn-ghost !px-4 !py-2 shrink-0"
            aria-label="Close component detail"
          >
            ESC
          </button>
        </div>

        <div className="mt-4"><StatusBadge state={component.status} /></div>

        <p className="mt-5 text-sm leading-relaxed text-dim">{component.purpose}</p>

        <div className="mt-6 border-t border-line">
          <Row label="Evidence level" testid="drawer-field-evidence">
            <span className="font-mono" style={{ color: statusColor(component.evidence_level) }}>{component.evidence_level}</span>
            {component.evidence_level === "NOT_MEASURED" && (
              <span className="ml-2 placeholder-chip">no measurement exists</span>
            )}
          </Row>
          <Row label="Verification" testid="drawer-field-verification">
            <span className="font-mono" style={{ color: statusColor(component.verification) }}>{component.verification}</span>
          </Row>
          <Row label="Qualification" testid="drawer-field-qualification">
            <span className="font-mono" style={{ color: statusColor(component.qualification) }}>{component.qualification}</span>
          </Row>
          <Row label="Deployment" testid="drawer-field-deployment">
            <StatusBadge state={component.deployment} />
          </Row>
          <Row label="Source" testid="drawer-field-source">
            <span className="font-mono text-[13px] text-warn">{component.source}</span>
            <span className="ml-2 placeholder-chip">placeholder</span>
          </Row>
          <Row label="Version / commit" testid="drawer-field-version">
            <span className="font-mono text-[13px] text-warn">{component.version}</span>
            <span className="ml-2 placeholder-chip">placeholder</span>
          </Row>
          <Row label="Dependencies" testid="drawer-field-dependencies">
            {component.dependencies?.length
              ? component.dependencies.map((d) => (
                  <span key={d} className="inline-block font-mono text-[11px] text-dim border border-line rounded-[2px] px-2 py-1 mr-2 mb-2">{d}</span>
                ))
              : <span className="text-mut">none recorded</span>}
          </Row>
          <Row label="Capabilities" testid="drawer-field-capabilities">
            {component.capabilities?.length
              ? <ul className="list-none space-y-1">{component.capabilities.map((c) => <li key={c} className="text-sm text-dim before:text-accent before:content-['▸_'] before:mr-1">{c}</li>)}</ul>
              : <span className="text-mut">none recorded</span>}
          </Row>
          <Row label="Limitations" testid="drawer-field-limitations">
            {component.limitations?.length
              ? <ul className="list-none space-y-1">{component.limitations.map((l) => <li key={l} className="text-sm text-[#FCA5A5]/90">{l}</li>)}</ul>
              : <span className="text-mut">none recorded</span>}
          </Row>
        </div>

        <p className="mt-6 text-[11px] leading-relaxed text-mut font-mono">
          Fields in [BRACKETS] are explicit placeholders awaiting authoritative data. This panel never presents a component as verified or qualified without supporting evidence.
        </p>

        <ExplainSection component={component} />
      </motion.aside>
    </motion.div>
  );
}
