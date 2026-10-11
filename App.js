import React, { useEffect, useRef } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import Lenis from "lenis";
import Nav from "@/components/Nav";
import Footer from "@/components/Footer";
import Home from "@/pages/Home";
import Explorer from "@/pages/Explorer";
import LiveTest from "@/pages/LiveTest";
import EvidencePage from "@/pages/EvidencePage";
import DocsPage from "@/pages/DocsPage";
import AskPage from "@/pages/AskPage";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { err: null };
  }
  static getDerivedStateFromError(err) {
    return { err };
  }
  render() {
    if (this.state.err) {
      return (
        <div style={{ padding: 48, fontFamily: "'JetBrains Mono', monospace", color: "#F1F5F9", background: "#070A0F", minHeight: "100vh" }}>
          <p style={{ color: "#EF4444" }}>SYSTEM ERROR — a component crashed.</p>
          <pre style={{ whiteSpace: "pre-wrap", color: "#94A3B8", fontSize: 12 }}>{String(this.state.err)}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
}

function App() {
  const lenisRef = useRef(null);
  useEffect(() => {
    const lenis = new Lenis({ duration: 1.15, smoothWheel: true });
    lenisRef.current = lenis;
    let rafId;
    const raf = (t) => {
      lenis.raf(t);
      rafId = requestAnimationFrame(raf);
    };
    rafId = requestAnimationFrame(raf);
    return () => {
      cancelAnimationFrame(rafId);
      lenis.destroy();
    };
  }, []);

  return (
    <ErrorBoundary>
      <BrowserRouter>
        <ScrollToTop />
        <div className="min-h-screen bg-ink text-[#F1F5F9]">
          <Nav />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/explorer" element={<Explorer />} />
            <Route path="/test" element={<LiveTest />} />
            <Route path="/evidence" element={<EvidencePage />} />
            <Route path="/docs" element={<DocsPage />} />
            <Route path="/ask" element={<AskPage />} />
            <Route path="*" element={<Home />} />
          </Routes>
          <Footer />
        </div>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
