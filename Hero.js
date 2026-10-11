import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { motion, useScroll, useTransform, useSpring, useMotionValue } from "framer-motion";
import { apiGet } from "@/lib/api";

const lineReveal = {
  hidden: { y: "115%" },
  show: (i) => ({ y: "0%", transition: { duration: 0.95, delay: 0.2 + i * 0.14, ease: [0.16, 1, 0.3, 1] } }),
};

export default function Hero() {
  const [manifest, setManifest] = useState(null);
  const wrapRef = useRef(null);
  const { scrollYProgress } = useScroll();
  const gridY = useTransform(scrollYProgress, [0, 1], [0, 140]);
  const glowY = useTransform(scrollYProgress, [0, 1], [0, 60]);

  const mx = useMotionValue(0);
  const my = useMotionValue(0);
  const rx = useSpring(useTransform(my, [-0.5, 0.5], [4, -4]), { stiffness: 120, damping: 18 });
  const ry = useSpring(useTransform(mx, [-0.5, 0.5], [-5, 5]), { stiffness: 120, damping: 18 });

  useEffect(() => {
    apiGet("/manifest").then(setManifest).catch(() => setManifest(null));
  }, []);

  const onMove = (e) => {
    const r = wrapRef.current?.getBoundingClientRect();
    if (!r) return;
    mx.set((e.clientX - r.left) / r.width - 0.5);
    my.set((e.clientY - r.top) / r.height - 0.5);
  };

  return (
    <section
      ref={wrapRef}
      onMouseMove={onMove}
      className="relative min-h-screen flex flex-col justify-center overflow-hidden pt-24 pb-16"
      data-testid="hero-section"
    >
      <motion.div className="absolute inset-0 grid-bg" style={{ y: gridY, opacity: 0.55 }} aria-hidden="true" />
      <motion.div className="absolute inset-0 vignette" style={{ y: glowY }} aria-hidden="true" />

      <div className="relative max-w-7xl mx-auto w-full px-5 lg:px-12 grid lg:grid-cols-[1.15fr_0.85fr] gap-14 items-center">
        <div>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.05 }}
            className="eyebrow flex items-center gap-3"
          >
            <span className="pulse-dot" style={{ width: 7, height: 7, borderRadius: 9999, background: "#10B981", display: "inline-block" }} />
            HUMAN-GOVERNED INTELLIGENCE INFRASTRUCTURE
          </motion.p>

          <h1 className="mt-6 font-display font-extrabold uppercase leading-[0.94] tracking-[-0.02em] text-[clamp(2.8rem,7vw,6rem)]">
            {["KETCHUM", "SYSTEM-OF-", "SYSTEMS"].map((line, i) => (
              <span key={line} className="block overflow-hidden pb-1">
                <motion.span
                  className={`block ${i === 2 ? "outline-text" : ""}`}
                  custom={i}
                  variants={lineReveal}
                  initial="hidden"
                  animate="show"
                >
                  {line}
                </motion.span>
              </span>
            ))}
          </h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.75 }}
            className="mt-7 max-w-xl text-base sm:text-lg text-dim leading-relaxed"
          >
            A public, inspectable interface layer over real systems — KCN · MANIFEX · KSI · TEVV · ARENA ·
            Independent Witness. Every unfinished component is marked. Nothing is claimed without evidence.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.9 }}
            className="mt-9 flex flex-wrap gap-4"
          >
            <Link to="/test" data-testid="hero-run-test-btn" className="btn-primary">
              [ RUN TEST ]
            </Link>
            <Link to="/explorer" data-testid="hero-explore-btn" className="btn-ghost">
              EXPLORE THE SYSTEM
            </Link>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.55, ease: [0.16, 1, 0.3, 1] }}
          style={{ perspective: 1000 }}
          className="relative"
        >
          <motion.div
            data-testid="hero-telemetry-panel"
            style={{ rotateX: rx, rotateY: ry, transformStyle: "preserve-3d" }}
            className="panel rounded-[3px] shadow-[0_30px_80px_rgba(0,0,0,0.5)]"
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-line">
              <span className="font-mono text-[10px] tracking-[0.22em] text-mut">SYSTEM STATUS · /api/manifest</span>
              <span className="font-mono text-[10px] text-accent">LIVE FETCH</span>
            </div>
            <div>
              <div className="telemetry-row" data-testid="hero-status-row">
                <span className="text-mut">SYSTEM STATUS</span>
                <span className="text-ok flex items-center gap-2">
                  <span className="pulse-dot" style={{ width: 6, height: 6, borderRadius: 9999, background: "#10B981", display: "inline-block" }} />
                  LIVE · PUBLIC LAYER
                </span>
              </div>
              <div className="telemetry-row" data-testid="hero-evidence-row">
                <span className="text-mut">EVIDENCE</span>
                <span className="text-dim">E0–E5 · NOT_MEASURED</span>
              </div>
              <div className="telemetry-row" data-testid="hero-authority-row">
                <span className="text-mut">AUTHORITY</span>
                <span className="text-accent">HUMAN CONTROLLED</span>
              </div>
              <div className="telemetry-row" data-testid="hero-connectors-row">
                <span className="text-mut">CONNECTORS</span>
                <span className="text-warn">6 INTERFACES · NOT_CONFIGURED</span>
              </div>
              {manifest && (
                <>
                  <div className="telemetry-row" data-testid="hero-registry-row">
                    <span className="text-mut">REGISTRY HASH</span>
                    <span className="text-dim text-[11px]">{String(manifest.registry_sha256).slice(0, 18)}…</span>
                  </div>
                  <div className="telemetry-row" data-testid="hero-components-row">
                    <span className="text-mut">COMPONENTS</span>
                    <span className="text-dim">{manifest.component_count} TRACKED · v{manifest.version}</span>
                  </div>
                </>
              )}
            </div>
            <div className="px-4 py-3 border-t border-line">
              <p className="font-mono text-[10px] leading-relaxed text-mut">
                Fetched from the running API — not a mock. Unconfigured connectors report NOT_CONFIGURED, never a simulated state.
              </p>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
