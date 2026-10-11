# ACCEPTANCE-GATES

Gates for the public infrastructure package. A gate is **OPEN** only when its evidence exists. Self-grading is not evidence; the acceptance script is a floor.

## Gate A — Package integrity (this build)

- A1: `/api/health` answers with real measured latency.
- A2: Registry serves 8 sections; every component carries an honest status.
- A3: No component is displayed as VERIFIED or QUALIFIED anywhere in UI or API.
- A4: Every unconfigured connector returns `NOT_CONFIGURED` — never simulated success.
- A5: Every execution attempt produces: execution record + evidence record (SHA-256 hash, provenance, level NOT_MEASURED) + audit entry.
- A6: `/api/evidence` lists the no-upgrade rules; `/api/verification` and `/api/qualification` report zero.
- A7: Documentation is served from real markdown at `/api/docs/{slug}`.
- A8: Acceptance script passes end-to-end: `python /app/tests/run_acceptance.py <BASE_URL>`.

**Status: OPEN FOR REVIEW — run the script; the gate is reviewable, not self-certified.**

## Gate B — Runtime integration (blocked on external runtimes)

- B1–B5: KCN / MANIFEX / KSI / TEVV / ARENA endpoints configured and answering.
- B6: A live test against a real runtime records measured values (latency, runtime identifier) — never invented ones.

**Status: CLOSED — INTEGRATION_REQUIRED.**

## Gate C — Independent evidence (blocked on external parties)

- C1: An independent witness re-runs at least one recorded execution and signs the record.
- C2: Reproduction harness attached to execution records.
- C3: First real evidence level assigned per authoritative E0–E5 definitions.

**Status: CLOSED — VERIFICATION_REQUIRED.**

## Gate D — Qualification (blocked on TEVV + witness)

- D1: Qualification gates defined by authoritative documentation.
- D2: Gates executed independently; results published with evidence records.

**Status: CLOSED — QUALIFICATION_REQUIRED.**

## Gate E — Production

- E1: Acceptance suite green on target host. E2: Production CORS + secrets. E3: Custom domain + TLS. E4: Security review.

**Status: CLOSED — BLOCKED (development channel only).**
