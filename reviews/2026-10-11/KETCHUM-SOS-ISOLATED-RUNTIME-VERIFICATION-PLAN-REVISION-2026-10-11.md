# Ketchum SoS Isolated Runtime Verification Plan — Revision

**Plan date:** 2026-10-11  
**Assessment ID:** KETCHUM-SOS-STATIC-ADV-2026-10-11  
**Repository:** `Evank253/Project-system-of-systems-complete`  
**Branch:** `Python-3`  
**Execution status:** NOT EXECUTED  
**Authorization status:** PLAN ONLY — no runtime execution is authorized by this document.

## 1. Objective

Define a controlled, evidence-producing runtime verification sequence for selected static-review findings while protecting the original repository, canonical export, data, and authority boundary.

This plan does not assert that any test has run or passed. Every planned check begins as NOT_MEASURED. Execution requires a separately approved scope and completed preflight.

## 2. Non-negotiable constraints

- Preserve repository history, the existing branch, and the canonical source export.
- Do not edit application code, commit fixes, push changes, deploy, contact external systems, or enable external connectors as part of this plan.
- Do not run against production, a shared database, or an environment with unknown data ownership.
- Use a disposable isolated environment and a disposable database with explicit connection-target verification.
- Do not enable delegation while signature verification and trusted-key management are absent or unverified.
- Do not treat an HTTP denial, UI label, model assertion, test name, or self-reported flag as proof that privileged state did not change.
- Preserve logs, request/response records, state snapshots, test parameters, timestamps, and hashes of evidence artifacts.
- Stop immediately if the environment is not the approved isolated target, unexpected external traffic occurs, production/shared credentials are detected, protected state changes unexpectedly, or cleanup cannot be verified.

## 3. Mandatory preflight checklist

All P-items must be recorded before running any runtime test.

| ID | Preflight requirement | Required evidence | Gate |
|---|---|---|---|
| P-01 | Identify exact source under test | Repository, branch, commit SHA, working-tree state, and source/archive hash where applicable | BLOCK until recorded |
| P-02 | Preserve baseline | Confirm original history and canonical export are retained and unmodified | BLOCK if not confirmed |
| P-03 | Confirm disposable database | Explicit DB name/URI target, environment identity, and proof it is not production/shared | BLOCK if uncertain |
| P-04 | Capture initial state | Snapshot relevant authority, delegation, evidence, authorization, and ledger/anchor state | BLOCK until retained |
| P-05 | Confirm isolation | Record local network/listening configuration and evidence that tests cannot reach external services | BLOCK if uncertain |
| P-06 | Record dependencies | Runtime, database, package, and test-runner versions; relevant configuration | BLOCK until recorded |
| P-07 | Handle secrets safely | No secrets in artifacts; use isolated test credentials; document secret source without exposing values | BLOCK if unsafe |
| P-08 | Define cleanup | Disposable-instance teardown or reliable finally-based cleanup and post-cleanup verification | BLOCK until proven workable |
| P-09 | Define stop conditions | Name operator, abort triggers, and procedure for preserving partial evidence | BLOCK until recorded |
| P-10 | Explicitly approve batch | Written approval identifying exact batch, target environment, duration, and permitted side effects | BLOCK until approved |

No preflight result is implied by the existence of this checklist.

## 4. Workstream A — Authority-boundary enforcement

**Purpose:** Verify that invalid, unauthorized, or untrusted inputs cannot create privileged state changes.

For every test, capture initial and final snapshots of relevant authoritative state, authority transition records, delegation records/status, evidence records, and authorization state. Capture request, response, timestamp, and logs. If a route does not touch a category, record NOT_APPLICABLE with rationale.

| ID | Proposed case | Evidence and pass criteria |
|---|---|---|
| A-01 | Caller supplies forged `verified=true`, `human_approved=true`, `qualified=true`, or equivalent flags | Request is rejected or flags are ignored; no unauthorized privileged state changes; state diff retained |
| A-02 | Caller attempts to self-ratify or redefine human authority | Request is rejected; no authority/ratification record is created; before/after state comparison retained |
| A-03 | Untrusted model/tool output requests privileged mutation | No privileged mutation occurs without the required authorization path; state and decision evidence retained |
| A-04 | Invalid, missing, or malformed delegation data | Denial or safe failure; no delegation activation or authority-state mutation |
| A-05 | Valid-looking delegation signature under current disabled/empty policy configuration | Delegation remains unavailable; no signature is treated as cryptographically verified merely because it is present |
| A-06 | Direct route/alternate path survey for privileged mutations | All discovered paths are classified; unauthorized paths are denied or explicitly recorded as findings |

**Pass discipline:** A-01 through A-06 cannot pass solely from HTTP status. Any unexpected privileged-state delta is a stop condition and potential finding.

## 5. Workstream B — Evidence and ledger integrity

**Purpose:** Characterize tamper detection and the actual trust boundary.

Only execute against disposable data. Use synthetic records; never alter canonical historical evidence.

| ID | Proposed case | Evidence and pass criteria |
|---|---|---|
| B-01 | Validate an unchanged baseline chain | Recompute expected chain and anchor; preserve input/output and implementation/version details |
| B-02 | Modify a ledger record while leaving any anchor unchanged | Record whether verification detects the alteration and where the mismatch appears |
| B-03 | Rewrite ledger plus an anchor stored within the same DB trust boundary | Determine whether application-level verification detects coordinated rewrite; do not assume it will |
| B-04 | If and only if an independently controlled anchor/witness exists, compare rewritten DB state to it | Independent witness must reject or expose divergence; document its separate control boundary |
| B-05 | Exercise partial write/failure and recovery on disposable state | Verify chain continuity, acknowledged-write durability, and explicit handling of incomplete records |

**Required interpretation:** If B-03 is not detected because the ledger and anchor share the same trust boundary, report that limitation plainly. Do not call an application-stored hash chain independently tamper-proof.

## 6. Workstream C — Concurrent ledger append

**Purpose:** Measure append atomicity, ordering, continuity, durability, and recovery under concurrent writes.

Predefine concurrency levels, repetition count, duration, seed/input set, and failure-injection approach. Use disposable isolated storage.

| ID | Proposed case | Evidence and pass criteria |
|---|---|---|
| C-01 | Concurrent append at a low concurrency level | No duplicate sequence IDs, gaps, broken previous-hash links, or lost acknowledged writes |
| C-02 | Repeat at progressively higher concurrency levels | Same integrity criteria; publish level-by-level counts and any failures |
| C-03 | Inject controlled interruption or partial failure, then recover | Explicit, consistent recovery behavior; no silent orphan/gap; chain and anchor validation after recovery |

Record every attempted write, acknowledged write, stored record, sequence identifier, predecessor hash, resulting chain verification, errors, and recovery action. Report concurrency and repetitions; a single successful run is insufficient. Any integrity violation is a stop condition.

## 7. Workstream D — API exposure and route classification

**Purpose:** Establish route-level expectations and identify exposure questions without implying production security certification.

| ID | Proposed case | Evidence and pass criteria |
|---|---|---|
| D-01 | Inventory API routes | Route, method, side effect, auth requirement, privilege level, and data classification recorded |
| D-02 | Classify routes | Each route classified public read-only, public non-privileged write, privileged/authority-sensitive, or administrative/operational |
| D-03 | Inspect authentication and authorization expectations | Route behavior matches explicit policy; missing policy is recorded as a finding |
| D-04 | Inspect CORS behavior in the isolated environment | Observed headers/config recorded and compared with intended client origins |
| D-05 | Inspect rate-limit scope | Determine whether enforcement is in-process or shared across instances; test only in isolated environment |
| D-06 | Document deployment boundary assumptions | Record what cannot be established locally, including TLS, reverse proxy, firewall/network controls, production secrets, deployed configuration, and external identity services |

Do not infer production readiness from localhost results. Do not contact external systems or test public production endpoints under this plan.

## 8. Workstream E — UI status, adversarial-test hygiene, prompt injection, connectors

| ID | Proposed case | Evidence and pass criteria |
|---|---|---|
| E-01 | Inspect TEVV UI stage status, including any hardcoded `IMPLEMENTED` label | Determine whether status derives from evidence-bearing runtime state or is static/presentational; record exact source reference |
| E-02 | Inspect adversarial tests that directly mutate MongoDB | Identify all mutation paths, cleanup guarantees, and failure behavior; prove cleanup on assertion failure in a disposable test instance before wider use |
| E-03 | Probe prompt-injection boundaries using non-privileged synthetic inputs | Verify untrusted content cannot directly mutate authority/privileged state; preserve before/after snapshots; scope result narrowly |
| E-04 | Inspect connector status handling | Confirm unconfigured connectors remain NOT_CONFIGURED and are not represented as successful external verification |

Prompt-injection testing is not a proof of universal resistance. Any result applies only to the tested source version, inputs, model/configuration, and execution environment.

## 9. Evidence package requirements

For each executed case, preserve:
- unique test ID and run ID;
- exact source commit and environment identifier;
- date/time, runtime/dependency versions, configuration reference;
- test inputs and commands or request details, excluding secrets;
- raw response and relevant logs;
- initial and final state snapshots/diff;
- ledger/anchor verification output where applicable;
- result status: PASS, FAIL, BLOCKED, NOT_APPLICABLE, or NOT_MEASURED;
- reviewer notes and limitations;
- hashes for retained evidence artifacts.

Do not edit raw evidence after capture. Corrections or interpretations belong in a separate append-only review record. PASS must identify the criterion and supporting evidence. Unknown or untested behavior remains NOT_MEASURED.

## 10. Execution sequence and approval gates

1. Preserve baseline and record source identity.
2. Complete P-01 through P-10; do not proceed if any gate is incomplete.
3. Obtain separate explicit authorization for a narrow initial batch, preferably A-01 through A-04, after environment review.
4. Review evidence and state diffs before deciding whether to continue.
5. Authorize B, C, D, or E as separate batches; do not automatically proceed from one batch to the next.
6. Preserve all failures and unexpected state changes; do not clean away evidence.
7. Record remediation decisions separately. This plan itself makes no remediation and closes no findings.

## 11. Stop conditions

Immediately stop the current batch if:
- the target is production, shared, or cannot be conclusively identified;
- the source version differs from the approved baseline;
- any unexpected authority, delegation, evidence, or authorization state changes;
- the test emits unexpected external network traffic;
- data loss, chain corruption, unexplained sequence gaps, or irrecoverable cleanup failure occurs;
- secrets or sensitive user data appear in artifacts;
- test effects exceed the approved scope.

Preserve partial results and document why the run stopped. Do not automatically retry a destructive or integrity-sensitive test.

## 12. Current status

- Plan authored: YES
- Preflight completed: NOT MEASURED
- Runtime tests executed: NO
- PASS results established: NO
- Findings closed: NO
- Repository code modified: NO
- Deployment performed: NO
- External systems contacted by this plan: NO

This document is a proposed plan only. Runtime execution requires separate explicit authorization after preflight review.
