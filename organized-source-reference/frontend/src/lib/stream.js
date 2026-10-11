const BASE = process.env.REACT_APP_BACKEND_URL;
const STREAM_TIMEOUT_MS = 90000;

export async function streamAI(path, body, { onStart, onDelta, onDone, onError } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), STREAM_TIMEOUT_MS);
  let r;
  try {
    r = await fetch(`${BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
  } catch (e) {
    clearTimeout(timer);
    if (e.name === "AbortError") throw new Error("AI stream timed out after 90 s — reported honestly. Try a shorter question or the LUNA model.");
    throw e;
  }
  if (!r.ok) {
    clearTimeout(timer);
    let detail = `HTTP ${r.status}`;
    try {
      const d = await r.json();
      detail = d.detail || detail;
    } catch (e) {}
    throw new Error(detail);
  }
  try {
    const reader = r.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const parts = buf.split("\n\n");
      buf = parts.pop();
      for (const part of parts) {
        const line = part.trim();
        if (!line.startsWith("data:")) continue;
        let ev;
        try {
          ev = JSON.parse(line.slice(5));
        } catch (e) {
          continue;
        }
        if (ev.type === "delta") onDelta && onDelta(ev.content);
        else if (ev.type === "start") onStart && onStart(ev);
        else if (ev.type === "done") onDone && onDone(ev);
        else if (ev.type === "error") onError && onError(ev.content);
      }
    }
  } catch (e) {
    if (e.name === "AbortError") throw new Error("AI stream timed out after 90 s — reported honestly. Try a shorter question or the LUNA model.");
    throw e;
  } finally {
    clearTimeout(timer);
  }
}
