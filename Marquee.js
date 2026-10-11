const TERMS = ["CAPABILITY", "EVIDENCE", "VERIFICATION", "QUALIFICATION", "AUTHORITY"];

function Sequence({ ariaHidden }) {
  return (
    <div aria-hidden={ariaHidden || undefined} className="flex shrink-0 items-center">
      {TERMS.map((t) => (
        <span key={t} className="flex items-center font-mono text-base md:text-lg tracking-[0.22em] text-dim">
          <span>{t}</span>
          <span className="mx-10 text-accent/70" aria-hidden="true">≠</span>
        </span>
      ))}
    </div>
  );
}

export default function Marquee() {
  return (
    <div
      data-testid="invariant-marquee"
      className="marquee overflow-hidden border-y border-line bg-panel/60 py-5"
    >
      <div className="marquee-track">
        <Sequence />
        <Sequence ariaHidden />
      </div>
    </div>
  );
}
