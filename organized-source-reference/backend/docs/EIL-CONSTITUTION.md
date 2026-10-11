# EIL CONSTITUTION — Emergent Intelligence Layer

**Frozen doctrine, stored verbatim from the owner-provided external architecture work. Machine-readable artifact: `/app/backend/data/eil/constitution.json` (SHA-256 anchored; modification is detectable). Status: HUMAN_RATIFICATION_PENDING inside this application.**

## Core principle

**MAKE INTELLIGENCE EXTENSIBLE. MAKE AUTHORITY CONSTITUTIONAL.**

EIL (Emergent Intelligence Layer) is engineered to permit intelligence and capability to expand without permitting intelligence or capability to become an independent source of authority.

**Fundamental invariant:** No increase in intelligence, capability, composition, knowledge, evidence, verification, or qualification shall, by itself, create, inherit, expand, or transfer authority.

## Constitutional invariants

- **EIL-01 — NON-TRANSITIVE AUTHORITY.** No increase in intelligence, capability, composition, knowledge, evidence, verification, or qualification shall, by itself, create, inherit, expand, or transfer authority.
- **EIL-02 — VALID DELEGATION.** Machine authority may change only through an explicitly permitted constitutional delegation or transition.
- **EIL-03 — NO SELF-ELEVATION.** EIL and its constituent systems cannot manufacture, approve, or confer authority upon themselves.
- **EIL-04 — EVIDENCE DOES NOT AUTHORIZE.** Evidence, verification, and qualification establish claims about capability; they do not independently grant permission to exercise that capability.
- **EIL-05 — RESERVED HUMAN AUTHORITY.** Authority designated as reserved remains outside machine delegation unless the governing constitution explicitly permits otherwise.

## State-domain separation

```
CAPABILITY_STATE ≠ EVIDENCE_STATE ≠ VERIFICATION_STATE ≠ QUALIFICATION_STATE ≠ AUTHORITY_STATE
```

A transition in one state domain may trigger evaluation in another domain, but MUST NOT implicitly mutate AUTHORITY_STATE.

## Core assurance requirement — EIL-ASSURE-001

An EIL capability-state transition MUST NOT produce an authority-state transition unless the authority transition is independently authorized through a valid constitutional delegation.

Machine-testable invariant: **authority_after == authority_before unless valid_constitutional_delegation == TRUE** — executed live at `GET /api/eil/invariant-check`.

## Authoritative authority transition

```
REQUESTED_AUTHORITY_CHANGE → CONSTITUTIONAL_POLICY → VALID_DELEGATION_VERIFICATION → DENY OR AUTHORITY_TRANSITION → AUDIT_RECORD
```

Every authority mutation preserves: requester, requested, transition, constitutional rule, prerequisite evidence, authorized approver, anti-forgery validation, actual state mutation, audit record.

## Delegation (v1)

**NO CONSTITUTIONALLY AUTHORIZED DELEGATION TYPE EXISTS** in v1 → VALID_DELEGATION_VERIFICATION = FALSE → AUTHORITY TRANSITION = **DENY**. The enforcement architecture recognizes a future delegation type if and only if it is added to a human-ratified constitutional version. No delegation types are invented.

## Untrusted inputs

`verified=True`, `human_approved=True`, `policy_allows=True`, `qualified=True`, `authorize=True` — from any caller, model, router, agent, API payload, serialized state, database record, or tool — are untrusted claims and can never independently establish authority.

## Forbidden authority paths

confidence, capability, composition, consensus, evidence, verification, qualification, successful execution, model assertion, router assertion, agent authority claim, serialization/API/database mutation, self-authorization, authority inheritance — **none of these lead to authority.**

## Evidence vocabulary

`PASS` = the specific test condition passed. `VERIFIED` = a defined verification activity established the result. `QUALIFIED` = applicable qualification criteria were satisfied. `AUTHORIZED` = a valid authority transition exists. `NOT_MEASURED` = the property has not been established by the required measurement. **These labels are NOT interchangeable.** A passing test does not itself create authority. Qualification does not itself create human authorization.

## Assurance chain

```
ARCHITECTURE → IMPLEMENTATION → TEVV → QUALIFICATION → HUMAN RATIFICATION
```

Do not collapse these stages.
