import { useEffect, useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Reveal from "@/components/Reveal";
import StatusBadge from "@/components/StatusBadge";
import { apiGet } from "@/lib/api";

const mdComponents = {
  h1: (p) => <h1 className="font-display font-bold text-2xl sm:text-3xl mt-8 mb-4 tracking-tight" {...p} />,
  h2: (p) => <h2 className="font-display font-bold text-xl sm:text-2xl mt-8 mb-3 tracking-tight text-[#F1F5F9]" {...p} />,
  h3: (p) => <h3 className="font-mono text-[13px] tracking-[0.18em] uppercase text-accent mt-6 mb-3" {...p} />,
  p: (p) => <p className="text-sm leading-relaxed text-dim my-3" {...p} />,
  ul: (p) => <ul className="list-disc pl-5 my-3 space-y-1.5 text-sm text-dim" {...p} />,
  ol: (p) => <ol className="list-decimal pl-5 my-3 space-y-1.5 text-sm text-dim" {...p} />,
  li: (p) => <li className="leading-relaxed" {...p} />,
  strong: (p) => <strong className="text-[#F1F5F9] font-semibold" {...p} />,
  a: (p) => <a className="text-accent hover:underline" target="_blank" rel="noreferrer" {...p} />,
  code: (p) => <code className="font-mono text-[12px] text-accent bg-ink border border-line rounded-[2px] px-1.5 py-0.5" {...p} />,
  pre: (p) => <pre className="panel rounded-[3px] p-4 overflow-x-auto my-4 text-[12px] font-mono text-[#CBD5E1] leading-relaxed" {...p} />,
  table: (p) => <div className="overflow-x-auto my-4 border border-line rounded-[2px]"><table className="w-full text-[12px]" {...p} /></div>,
  thead: (p) => <thead className="bg-panel" {...p} />,
  th: (p) => <th className="text-left font-mono text-[10px] tracking-[0.14em] text-mut uppercase px-3 py-2.5 border-b border-line" {...p} />,
  td: (p) => <td className="px-3 py-2.5 border-b border-line/50 text-dim align-top" {...p} />,
  blockquote: (p) => <blockquote className="border-l-2 border-accent/60 pl-4 my-4 text-sm text-dim italic" {...p} />,
  hr: () => <hr className="my-6 border-line" />,
};

export default function DocsPage() {
  const [index, setIndex] = useState(null);
  const [slug, setSlug] = useState(null);
  const [doc, setDoc] = useState(null);

  useEffect(() => {
    apiGet("/docs").then((d) => {
      setIndex(d);
      if (d.docs?.length) setSlug(d.docs[0].slug);
    }).catch(() => setIndex(null));
  }, []);

  useEffect(() => {
    if (!slug) return;
    setDoc(null);
    apiGet(`/docs/${slug}`).then(setDoc).catch(() => setDoc(null));
  }, [slug]);

  return (
    <main className="pt-28 pb-24">
      <div className="max-w-7xl mx-auto px-5 lg:px-12">
        <Reveal>
          <p className="eyebrow">DOCUMENTATION</p>
          <h1 className="mt-4 font-display font-bold tracking-tight text-4xl sm:text-6xl">The build specification.</h1>
          <p className="mt-4 max-w-2xl text-dim leading-relaxed">
            The complete master infrastructure package — architecture, API, models, gates, and the master build
            prompt — served directly from the running backend. Status reflects build state, not product claims.
          </p>
        </Reveal>

        <div className="mt-12 grid lg:grid-cols-[300px_1fr] gap-8">
          <aside className="lg:sticky lg:top-24 h-fit" data-testid="docs-nav">
            <div className="panel rounded-[3px] p-3">
              {(index?.docs || []).map((d) => (
                <button
                  key={d.slug}
                  data-testid={`docs-nav-${d.slug}`}
                  onClick={() => setSlug(d.slug)}
                  className={`w-full text-left px-3.5 py-3 rounded-[2px] transition-colors duration-200 border ${
                    slug === d.slug ? "border-accent/50 bg-hov" : "border-transparent hover:bg-hov/60"
                  }`}
                >
                  <span className={`block font-mono text-[11px] leading-snug ${slug === d.slug ? "text-accent" : "text-dim"}`}>{d.title}</span>
                  <span className="block font-mono text-[9px] tracking-[0.14em] text-mut mt-1">{d.status.replace(/_/g, " ")}</span>
                </button>
              ))}
              {!index && <p className="p-4 font-mono text-[11px] text-warn">DOC INDEX UNREACHABLE</p>}
            </div>
          </aside>

          <article className="panel rounded-[3px] p-6 sm:p-10 min-h-[500px]" data-testid="docs-content">
            {doc ? (
              <>
                <div className="flex flex-wrap items-center justify-between gap-3 pb-5 border-b border-line">
                  <span className="font-mono text-[10px] tracking-[0.2em] text-mut">/api/docs/{doc.slug}</span>
                  <StatusBadge state={doc.status} />
                </div>
                <Markdown remarkPlugins={[remarkGfm]} components={mdComponents}>
                  {doc.content}
                </Markdown>
              </>
            ) : (
              <p className="font-mono text-xs text-mut tracking-[0.16em]" data-testid="docs-loading-state">
                {slug ? "LOADING DOCUMENT…" : "SELECT A DOCUMENT"}
              </p>
            )}
          </article>
        </div>
      </div>
    </main>
  );
}
