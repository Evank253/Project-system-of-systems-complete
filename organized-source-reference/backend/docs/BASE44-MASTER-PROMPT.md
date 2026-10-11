# BASE44 MASTER BUILD PROMPT

Give this document to an AI builder alongside the package. It is written as an instruction, because an instruction is what it is.

---

You are implementing the **product layer** of the KETCHUM SYSTEM-OF-SYSTEMS from a complete infrastructure specification. The systems below already exist and remain authoritative.

## Ground rules — read first

1. **Do not replace the existing systems. Connect to them.** KCN, MANIFEX, KSI, TEVV, ARENA, and Independent Witness are external and authoritative.
2. **Complete every component marked IMPLEMENTATION-READY** in the component registry.
3. **For anything requiring an external runtime, credential, physical resource, independent witness, or empirical measurement:** build the interface and test harness, mark it `INTEGRATION_REQUIRED` / `TEST_REQUIRED` / `VERIFICATION_REQUIRED`, and **do not fabricate completion**.
4. **Do not fabricate evidence.** No invented benchmark numbers, verification stamps, qualification certificates, or execution logs.
5. **Do not change historical evidence.** Records are append-only by convention.
6. **Do not promote statuses.** Never: NOT_MEASURED → PASS, E0 → E2, E2 → E3, E3 → E4, E4 → E5, or any evidence level → QUALIFIED.
7. **Preserve the invariant:** CAPABILITY ≠ EVIDENCE ≠ VERIFICATION ≠ QUALIFICATION ≠ AUTHORITY.
8. **Run the acceptance tests after implementation** (`/app/tests/run_acceptance.py`) and report the results honestly.

## Implementation order

1. Public application pages (Home, System Explorer, Architecture, Live Test, Evidence Explorer, Benchmarks, Research, Documentation).
2. Application API routes (`/api/system`, `/api/capabilities`, `/api/tasks`, `/api/executions`, `/api/evidence`, `/api/verification`, `/api/qualification`, `/api/authority`, `/api/docs`, `/api/health`, `/api/manifest`).
3. Connector interfaces against `*_RUNTIME_ENDPOINT` environment variables. If unset: return `NOT_CONFIGURED`.
4. Evidence records with SHA-256 hash + provenance on every execution attempt.
5. Security: environment-driven secrets, per-IP rate limits on executions, audit logging.
6. Deployment configuration per `DEPLOYMENT-SPEC.md`.

## Definition of done

A stranger can go **UNDERSTAND → EXPLORE → RUN TEST → INSPECT RESULT → INSPECT EVIDENCE → UNDERSTAND LIMITATIONS** — and every gate that remains closed is shown as closed, with the reason.
