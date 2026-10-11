const MAP = {
  IMPLEMENTED: { c: "#10B981" },
  INTEGRATION_REQUIRED: { c: "#F59E0B" },
  TEST_REQUIRED: { c: "#38BDF8" },
  VERIFICATION_REQUIRED: { c: "#60A5FA" },
  QUALIFICATION_REQUIRED: { c: "#94A3B8" },
  NOT_MEASURED: { c: "#64748B", dashed: true },
  BLOCKED: { c: "#EF4444" },
  NOT_CONFIGURED: { c: "#F59E0B" },
  CONFIGURED: { c: "#10B981" },
  UNAVAILABLE: { c: "#EF4444" },
  PASS: { c: "#10B981" },
  FAIL: { c: "#EF4444" },
  NOT_VERIFIED: { c: "#64748B" },
  NOT_QUALIFIED: { c: "#64748B" },
  DEVELOPMENT: { c: "#38BDF8" },
  STAGING: { c: "#F59E0B" },
  PRODUCTION: { c: "#10B981" },
  NOT_DEPLOYED: { c: "#64748B" },
  LIVE: { c: "#10B981" },
};

export function statusColor(state) {
  return (MAP[state] || { c: "#64748B" }).c;
}

export function StatusDot({ state, size = 7 }) {
  const { c, dashed } = MAP[state] || {};
  return (
    <span
      aria-hidden="true"
      className={state === "LIVE" || state === "PASS" ? "pulse-dot" : ""}
      style={{
        display: "inline-block",
        width: size,
        height: size,
        borderRadius: 9999,
        flexShrink: 0,
        background: dashed ? "transparent" : c,
        border: dashed ? `1.5px dashed ${c}` : "none",
        boxShadow: dashed ? "none" : `0 0 8px ${c}66`,
      }}
    />
  );
}

export default function StatusBadge({ state, className = "" }) {
  const meta = MAP[state] || { c: "#64748B" };
  return (
    <span
      data-testid={`status-badge-${state.toLowerCase()}`}
      className={`inline-flex items-center gap-2 font-mono uppercase tracking-[0.12em] text-[10px] px-2 py-1 rounded-[2px] border ${className}`}
      style={{
        color: meta.c,
        borderColor: `${meta.c}55`,
        background: `${meta.c}12`,
        borderStyle: meta.dashed ? "dashed" : "solid",
      }}
    >
      <StatusDot state={state} size={6} />
      {state.replace(/_/g, " ")}
    </span>
  );
}
