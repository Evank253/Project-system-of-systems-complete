export function LogoMark({ size = 26 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <rect x="1" y="1" width="30" height="30" rx="5" fill="#0B0F17" stroke="#2A364F" strokeWidth="1.5" />
      <path d="M9.5 7.5v17" stroke="#F1F5F9" strokeWidth="2.4" strokeLinecap="round" />
      <path d="M22.5 7.5l-8.5 8.5 8.5 8.5" stroke="#F1F5F9" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="22.5" cy="7.5" r="2.3" fill="#38BDF8" />
      <circle cx="22.5" cy="24.5" r="2.3" fill="#38BDF8" />
      <circle cx="14" cy="16" r="2" fill="#F59E0B" />
    </svg>
  );
}

export default function Logo({ compact = false }) {
  return (
    <div className="flex items-center gap-3">
      <LogoMark />
      {!compact && (
        <span className="font-display font-bold tracking-[0.08em] text-[15px] text-[#F1F5F9]">
          KETCHUM <span className="text-dim font-medium">SYSTEMS</span>
        </span>
      )}
    </div>
  );
}
