---
status: Accepted
owner: "Architect / Tech Lead"
reviewers: ["Tech Lead"]
updated_at: "2026-10-03"
feature_size: "M"
ticket: "walking-skeleton-readiness"
---

# 0003 — Derive Evidence Status at read time in a pure domain module; do not store it

- **Status:** Accepted
- **Date:** 2026-10-03
- **Deciders:** Architect + owner (Socratic walk)

## Context

Evidence Status (`NO_EVIDENCE` / `MATCH` / `MISMATCH` / `UNAVAILABLE`) must be reproducible after refresh or restart from the same readable hierarchy (AC-18/19) and never confusable with a test outcome (QG-1). The decision is *where* and *when* the status is produced: stored on save, or computed from the persisted hierarchy at read time.

## Decision drivers

- AC-14 / AC-14a — `MATCH` iff trimmed target and observed keys/values are case-sensitively equal; a pure total function of the current hierarchy.
- AC-18 / AC-19 — the same readable hierarchy must yield the same status after refresh/restart.
- AC-20 — `UNAVAILABLE` is a read failure (unreadable/inconsistent authoritative data), not a persistable state.
- repo convention (`docs/project-map.md`): deterministic domain logic has no I/O and does not depend on outer layers.

## Considered options

1. **Derive at read time in a pure domain module** — compute status from the readable hierarchy on each read; never store it; `UNAVAILABLE` from read failure.
2. **Persist the status on save** — write a status column at record-accept time.

## Decision outcome

**Chosen:** Option 1 — a pure function in `apps/api/src/domain/` derives Evidence Status from the readable hierarchy on each read. Because the status is a deterministic function of the stored inputs, persisting it would create a second source of truth that could drift (the exact failure AC-18/19 guard against), and `UNAVAILABLE` (a read failure) cannot be a stored state at all. A future Readiness/audit slice may add a **persisted decision-record (with reasoning)** as a separate concept layered on top of this derived status — that evaluation is deferred (sad.md §11), not ruled out.

## Consequences

**Positive**
- Single source of truth: persisted inputs (target, observed state) always reproduce the same status — the skeleton's recovery proof (AC-18/19).
- `UNAVAILABLE` falls out naturally from a read failure, with no special-case stored value.
- Pure function with no I/O is trivially unit-testable under `apps/api/test/unit`.

**Negative**
- No historical record of "what the system concluded at time T" — acceptable this slice (no audit scope), revisited for the Readiness/audit slice.

**Neutral**
- When the Readiness/audit slice arrives, a persisted decision-record is added as a separate concept; this slice's derived status remains the basis, not the obstacle.

## Links

- Spec: [[../spec.md]]
- SAD: [[../sad.md]] §4, §5, §10
- Related ADR: [[0002-transactional-record-acceptance]]
