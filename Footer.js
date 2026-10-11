import { Link } from "react-router-dom";
import Logo from "./Logo";

const SECTIONS = [
  ["01", "PUBLIC APPLICATION"],
  ["02", "APPLICATION API"],
  ["03", "SYSTEM CONNECTORS"],
  ["04", "EVIDENCE SYSTEM"],
  ["05", "AUTHORITY"],
  ["06", "TEVV"],
  ["07", "SECURITY"],
  ["08", "DEPLOYMENT"],
];

export default function Footer() {
  return (
    <footer className="border-t border-line bg-panel/40" data-testid="footer">
      <div className="max-w-7xl mx-auto px-5 lg:px-12 py-16 grid gap-12 md:grid-cols-3">
        <div>
          <Logo />
          <p className="mt-4 text-sm text-dim leading-relaxed max-w-xs">
            Human-Governed Intelligence Infrastructure. A public, inspectable interface layer over real systems.
          </p>
          <p className="mt-4 font-mono text-[11px] tracking-[0.14em] text-mut">
            CAPABILITY ≠ EVIDENCE ≠ VERIFICATION ≠ QUALIFICATION ≠ AUTHORITY
          </p>
        </div>

        <div>
          <p className="eyebrow">System Map</p>
          <ul className="mt-4 grid grid-cols-2 gap-2">
            {SECTIONS.map(([id, name]) => (
              <li key={id}>
                <Link
                  to={`/explorer?section=${id}`}
                  data-testid={`footer-section-${id}`}
                  className="font-mono text-[11px] text-dim hover:text-accent transition-colors duration-200"
                >
                  {id} · {name}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <p className="eyebrow">Application</p>
          <ul className="mt-4 space-y-2 font-mono text-[11px]">
            <li><Link to="/explorer" data-testid="footer-link-explorer" className="text-dim hover:text-accent transition-colors duration-200">SYSTEM EXPLORER</Link></li>
            <li><Link to="/test" data-testid="footer-link-test" className="text-dim hover:text-accent transition-colors duration-200">LIVE TEST</Link></li>
            <li><Link to="/evidence" data-testid="footer-link-evidence" className="text-dim hover:text-accent transition-colors duration-200">EVIDENCE EXPLORER</Link></li>
            <li><Link to="/docs" data-testid="footer-link-docs" className="text-dim hover:text-accent transition-colors duration-200">DOCUMENTATION</Link></li>
            <li><Link to="/ask" data-testid="footer-link-ask" className="text-dim hover:text-accent transition-colors duration-200">ASK THE SYSTEM</Link></li>
            <li><a href={`${process.env.REACT_APP_BACKEND_URL}/api/system`} target="_blank" rel="noreferrer" data-testid="footer-link-api" className="text-dim hover:text-accent transition-colors duration-200">RAW API · /api/system</a></li>
          </ul>
        </div>
      </div>

      <div className="border-t border-line">
        <div className="max-w-7xl mx-auto px-5 lg:px-12 py-6 flex flex-col sm:flex-row justify-between gap-3 font-mono text-[10px] tracking-[0.12em] text-mut">
          <span data-testid="footer-version">KETCHUM-SOS · v0.1.0 · DEVELOPMENT CHANNEL</span>
          <span data-testid="footer-disclaimer">
            EVERY UNFINISHED COMPONENT IS MARKED. NOTHING HERE CLAIMS VERIFICATION, QUALIFICATION, OR AUTHORITY WITHOUT EVIDENCE.
          </span>
        </div>
      </div>
    </footer>
  );
}
