# AI-INTERFACE

The AI layer of the KETCHUM public application: grounded reasoning over the registry, evidence model, documentation, and execution records.

## Prime rule

**The AI is not the source of truth.** It is an interface/reasoning component. System state, evidence, verification, qualification, and authority come only from the underlying authoritative records. An AI response is never authority, authorization, verification, or qualification.

## Placements

| Placement | Route | Grounded in |
|---|---|---|
| Health / runtime state | `GET /api/ai/health` | Key presence, model ids, limits; `?ping=true` performs a real measured micro-completion (OPERATIONAL / UNAVAILABLE + latency) — never a faked ping result |
| Ask the System | `POST /api/ai/ask` | Full component registry, evidence rules, docs index, recent executions |
| Component Explain | `POST /api/ai/explain/{component_id}` | That component's complete registry record + evidence rules |

Both stream Server-Sent Events: `start` → `delta`… → `done` (with a grounding object), or an honest `error` event. No simulated answers ever.

## Models

| Slug | Identifier source | Default |
|---|---|---|
| `sol` | env `AI_MODEL_SOL` | `gpt-6-sol` |
| `luna` | env `AI_MODEL_LUNA` | `gpt-6-luna` |

Model identifiers are server-configurable — never hard-coded in logic, never exposed decisions to the browser. The runtime key (`EMERGENT_LLM_KEY`) lives only in backend environment; if it is missing, endpoints return HTTP 503 with the factual reason.

## System-prompt contract (enforced in code)

1. Answer only from the GROUNDED CONTEXT provided per request.
2. Never invent or upgrade statuses, evidence levels, benchmarks, verification, qualification, capabilities, or execution results.
3. Unknown facts are reported as unavailable or NOT_MEASURED.
4. Inline citations required: `[registry:03-01]`, `[doc:evidence-model]`, `[evidence-rules]`.
5. Interpretation must be labeled as interpretation, separate from authoritative data.

## Security & privacy

- Per-IP rate limit, default 10/min (env `AI_RATE_LIMIT_PER_MIN`) — stricter than the execution limiter.
- No credentials or privileged operations reachable through AI endpoints.
- Conversation messages persisted in the application datastore for session continuity; audit entries contain metadata only (model, scope, size) — never content.
- Public users get read-only reasoning; they cannot modify authoritative records, evidence, qualification state, or governance rules through any AI path.

## Honest limits

- If the external LLM runtime is unreachable, the UI shows an honest error — never a fabricated answer.
- Streams carry a server-side timeout (env `AI_STREAM_TIMEOUT_S`, default 120 s) and a client-side 90 s abort; a timed-out stream is labeled PARTIAL, never presented as complete.
- Execution task strings embedded in context are treated as untrusted data, never instructions (injection hardening).
- AI interpretations may be wrong; the registry record displayed beside them is authoritative.
- Authentication does not exist yet; when accounts are added, per-user quotas attach at the same boundary without redesign.
