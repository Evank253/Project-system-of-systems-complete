# TEST-MATRIX

Test status: all boxes below are open. The matrix names what must be true, by whom, and with what evidence. Nothing is checked off until real evidence exists.

## Layer 1 — Package invariants (automated, this build)

| # | Check | Method | Status |
|---|---|---|---|
| 1.1 | Health responds with measured datastore latency | `run_acceptance.py` | TEST_REQUIRED |
| 1.2 | Registry: 8 sections, >50 components | `run_acceptance.py` | TEST_REQUIRED |
| 1.3 | No component claims VERIFIED/QUALIFIED | `run_acceptance.py` | TEST_REQUIRED |
| 1.4 | Unconfigured KCN returns NOT_CONFIGURED (no fake success) | `run_acceptance.py` | TEST_REQUIRED |
| 1.5 | Self-test returns measured result + 64-hex evidence hash | `run_acceptance.py` | TEST_REQUIRED |
| 1.6 | No-upgrade rules present in `/api/evidence` | `run_acceptance.py` | TEST_REQUIRED |
| 1.7 | Verification/qualification endpoints report zero | `run_acceptance.py` | TEST_REQUIRED |
| 1.8 | Docs index + content served | `run_acceptance.py` | TEST_REQUIRED |
| 1.9 | AI models endpoint lists sol + luna with server-configured ids | `run_acceptance.py` | TEST_REQUIRED |
| 1.10 | AI /ask grounded (reports registry status, never fabricates) | `run_acceptance.py` + live LLM | TEST_REQUIRED |
| 1.11 | AI explain streams grounded answer with grounding metadata | `run_acceptance.py` + live LLM | TEST_REQUIRED |
| 1.12 | AI health endpoint: configured state + measured ping latency | `run_acceptance.py` (ping run manually: `/api/ai/health?ping=true`) | TEST_REQUIRED |

## Layer 2 — Integration (needs real runtimes)

| # | Check | Requires | Status |
|---|---|---|---|
| 2.1 | KCN connector forwards task, returns real state | `KCN_RUNTIME_ENDPOINT` | INTEGRATION_REQUIRED |
| 2.2 | MANIFEX connector | `MANIFEX_RUNTIME_ENDPOINT` | INTEGRATION_REQUIRED |
| 2.3 | KSI connector | `KSI_RUNTIME_ENDPOINT` | INTEGRATION_REQUIRED |
| 2.4 | TEVV connector | `TEVV_RUNTIME_ENDPOINT` | INTEGRATION_REQUIRED |
| 2.5 | ARENA connector + benchmark run | `ARENA_RUNTIME_ENDPOINT` | INTEGRATION_REQUIRED |
| 2.6 | Connector timeout → UNAVAILABLE, evidence records the attempt | configured endpoint | TEST_REQUIRED |

## Layer 3 — Independent (needs external parties)

| # | Check | Requires | Status |
|---|---|---|---|
| 3.1 | Verification of any claim | independent witness | VERIFICATION_REQUIRED |
| 3.2 | Reproduction of a recorded execution from its record | reproduction harness + witness | INTEGRATION_REQUIRED |
| 3.3 | Qualification gates defined & passed | TEVV + witness | QUALIFICATION_REQUIRED |

Rule: a check moves out of TEST_REQUIRED only when its evidence record exists — with hash, provenance, and an executor independent of the thing tested.
