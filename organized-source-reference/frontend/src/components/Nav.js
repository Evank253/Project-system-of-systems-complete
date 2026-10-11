import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import Logo from "./Logo";

const LINKS = [
  { to: "/explorer", label: "SYSTEM EXPLORER", id: "explorer" },
  { to: "/test", label: "LIVE TEST", id: "test" },
  { to: "/evidence", label: "EVIDENCE", id: "evidence" },
  { to: "/docs", label: "DOCS", id: "docs" },
  { to: "/ask", label: "ASK", id: "ask" },
];

export default function Nav() {
  const [open, setOpen] = useState(false);

  return (
    <header className="fixed top-0 inset-x-0 z-50 bg-ink/85 backdrop-blur-xl border-b border-line">
      <nav className="max-w-7xl mx-auto flex items-center justify-between h-16 px-5 lg:px-12">
        <Link to="/" data-testid="nav-link-home" className="shrink-0">
          <Logo />
        </Link>

        <div className="hidden md:flex items-center gap-8">
          {LINKS.map((l) => (
            <NavLink
              key={l.id}
              to={l.to}
              data-testid={`nav-link-${l.id}`}
              className={({ isActive }) =>
                `font-mono text-[11px] tracking-[0.18em] transition-colors duration-200 hover:text-[#F1F5F9] ${
                  isActive ? "text-accent" : "text-dim"
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </div>

        <div className="flex items-center gap-4">
          <span
            data-testid="nav-live-chip"
            className="hidden sm:inline-flex items-center gap-2 font-mono text-[10px] tracking-[0.16em] text-ok border border-ok/40 bg-ok/10 px-2.5 py-1 rounded-[2px]"
          >
            <span className="pulse-dot" style={{ width: 6, height: 6, borderRadius: 9999, background: "#10B981", display: "inline-block" }} />
            PUBLIC LAYER · LIVE
          </span>
          <button
            data-testid="nav-mobile-toggle"
            className="md:hidden font-mono text-[11px] tracking-[0.2em] text-dim border border-line px-3 py-2 rounded-[2px]"
            onClick={() => setOpen(!open)}
            aria-label="Toggle navigation menu"
          >
            {open ? "CLOSE" : "MENU"}
          </button>
        </div>
      </nav>

      {open && (
        <div className="md:hidden border-t border-line bg-ink/95 backdrop-blur-xl" data-testid="nav-mobile-menu">
          <div className="px-5 py-4 flex flex-col gap-4">
            {LINKS.map((l) => (
              <NavLink
                key={l.id}
                to={l.to}
                data-testid={`nav-mobile-link-${l.id}`}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  `font-mono text-xs tracking-[0.18em] ${isActive ? "text-accent" : "text-dim"}`
                }
              >
                {l.label}
              </NavLink>
            ))}
          </div>
        </div>
      )}
    </header>
  );
}
