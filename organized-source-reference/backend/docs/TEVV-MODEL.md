# TEVV-MODEL

Test, Evaluation, Verification & Validation — the pipeline that turns "it works" into "it was shown to work, independently."

## Pipeline stages

```
1. TEST EXECUTION        → implemented here (basic): /api/executions runs real tasks
2. VERIFICATION          → VERIFICATION_REQUIRED: needs an external verifier
3. REPRODUCTION          → INTEGRATION_REQUIRED: harness not attached to records yet
4. INDEPENDENT WITNESS   → INTEGRATION_REQUIRED: cannot be self-issued
5. QUALIFICATION         → QUALIFICATION_REQUIRED: formal gates, not yet defined or run
```

## What exists today (honestly)

- **Test execution:** the Live Test page + `POST /api/executions`. Real dispatch, real states, measured latencies, hashed records.
- **Self-test:** one genuinely reproducible measurement — this deployment's own datastore round-trip.

## What cannot exist yet (and is not faked)

- **Verification:** nothing in this package is verified. There is no witness.
- **Reproduction:** execution records are persisted, but a third party cannot yet re-run them from the record alone.
- **Qualification:** no qualification gates have been defined or run by anyone, independent or otherwise.

## Gate rules

- A gate opens only on evidence produced by a party independent of the thing being gated.
- `TEST_REQUIRED`, `VERIFICATION_REQUIRED`, `QUALIFICATION_REQUIRED` are statuses, not aspirations: they name the *next* real-world action required.
- The acceptance suite (`/app/tests/run_acceptance.py`) is a floor, not a verdict: it checks invariants of this package, not quality of the external systems.
