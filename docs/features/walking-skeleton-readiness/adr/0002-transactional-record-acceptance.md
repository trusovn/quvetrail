---
status: Accepted
owner: "Architect / Tech Lead"
reviewers: ["Tech Lead"]
updated_at: "2026-10-05"
feature_size: "M"
ticket: "walking-skeleton-readiness"
---

# 0002 — Accept each record in a synchronous request-scoped transaction

- **Status:** Accepted
- **Date:** 2026-10-03
- **Deciders:** Architect + owner (Socratic walk)

## Context

The skeleton's core invariant (SAD §4, QG-2, AC-16/16a/17) is that `SAVED` requires known durable acceptance, retry-safe `SAVE_FAILED` requires known non-acceptance, and unknown acceptance claims neither. Previously accepted data remains intact; no submitted record feeds Evidence Status until acceptance is known. The request-scoped transaction preserves atomicity, while its acknowledgement determines what the API can claim.

## Decision drivers

- QG-2 — durability under failed saves: only known non-acceptance permits retry-safe failure; preserve prior data.
- AC-16 / AC-16a / AC-17 — distinguish known non-acceptance from unknown acceptance; no `SAVED` or pending-record status use before durable acceptance is known.
- One-record walking-skeleton scope (spec §3) — no need for async or outbox machinery.

## Considered options

1. **Synchronous request-scoped transaction** — wrap each record-accept in one PostgreSQL transaction; `SAVED` only after confirmed commit; known non-acceptance returns `SAVE_FAILED`, unknown acceptance requires authoritative recovery.
2. **Optimistic UI with server reconciliation** — show `SAVED` before durable acceptance and reconcile later.
3. **Event-sourced append log with a projection** — persist events and derive state from a projection.

## Decision outcome

**Chosen:** Option 1 — a single request-scoped transaction per accept; `SAVED` is returned only after confirmed durable commit, `SAVE_FAILED` only after known non-acceptance, and unknown acceptance requires authoritative recovery. Option 2 is excluded as a strawman (it directly violates AC-17). Option 3 adds a projection layer far beyond one-record scope.

**Transaction-outcome clarification (2026-10-05):** a COMMIT exception can mean its acknowledgement was lost after PostgreSQL committed. The persistence adapter owns a three-way result: confirmed committed, confirmed not accepted, or acceptance unknown. It may establish non-acceptance when its controlled transaction lifecycle never dispatched COMMIT, or from a definitive rollback/non-commit response for that transaction. Generic database/connection exceptions, timeouts, cancellation requests, and a cleanup ROLLBACK after an unacknowledged COMMIT do not establish non-acceptance. If proof is unavailable, classify unknown. The application preserves this result and the HTTP layer maps it to `201 SAVED`, `503 *.save_failed`, or `503 *.save_outcome_unknown` using the existing error envelope. No automatic transaction/POST replay is introduced. See SAD §6 for the evidence rules and GET recovery.

## Consequences

**Positive**
- Directly satisfies AC-16/16a/17 and QG-2 with the weakest machinery (one transaction plus explicit outcome classification).
- Confirmed commit = accepted; confirmed non-commit = nothing accepted; lost commit acknowledgement = unknown. Both server-side uncertainty and browser response loss recover authoritative workspace state before another explicit create (SAD §6 / ADR-0004).

**Negative**
- A slow commit blocks the request; acceptable at one-record scale.
- GET recovery restores current state without proving whether an uncertain attempt committed or guaranteeing duplicate-free re-submission; repeated creates remain allowed without idempotency machinery.

**Neutral**
- If the product later needs cross-record atomicity or async work, the transactional boundary moves but the "nothing before durable acceptance" invariant stays.

## Links

- Spec: [[../spec.md]]
- SAD: [[../sad.md]] §4, §5
- Related ADR: [[0003-derive-evidence-status-at-read-time]]
