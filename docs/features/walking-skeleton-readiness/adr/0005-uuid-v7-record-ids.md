---
status: Accepted
owner: "Architect / Tech Lead"
reviewers: ["Tech Lead"]
updated_at: "2026-10-05"
feature_size: "M"
ticket: "walking-skeleton-readiness"
---

# 0005 — Use time-sortable uuid v7 generated at the application layer for record IDs

- **Status:** Accepted
- **Date:** 2026-10-03
- **Deciders:** Architect + owner (Socratic walk)

## Context

The repository has **no product ID convention** (`architecture-map.md`: the `foundation_probe` singleton integer is a technical smoke fixture and must not be generalized). This is the first real product schema, so the ID strategy must be fixed now; once rows exist, changing it requires a backfill (read-locking and rewriting every id).

## Decision drivers

- No product ID convention exists; the singleton integer must not be generalized (`architecture-map.md`).
- spec §3/§8 defer but do not rule out multiple-record selection, editing, and history → ordered listing will plausibly be wanted later.
- Single trusted QA engineer, a progressive current-record workspace this slice — repeated creates are allowed, but exact acceptance chronology is not a product requirement.

## Considered options

1. **Time-sortable uuid v7, app-layer** — 128-bit uuid with a timestamp prefix; sortable; generated in the application layer; single-column primary key.
2. **Random uuid v4, app-layer** — simplest uuid; no ordering.
3. **Postgres identity / auto-increment** — DB-generated integer per table.

## Decision outcome

**Chosen:** Option 1 — uuid v7 generated at the application layer. v4 would give no future ordering and would force a backfill when history/multi-record slices arrive; v7 provides ordered primary keys at the same uuid cost and format today. Option 3 leaks sequence semantics and conflicts with the map's warning against generalizing the singleton integer.

## Consequences

**Positive**
- UUID-ordered listing is available without an ID backfill; later history slices must define any stronger chronology requirement separately.
- Generation in the application layer keeps the domain independent of the datastore.

**Negative**
- Same-millisecond IDs can interleave; clock skew and differing transaction completion order also prevent UUID order from guaranteeing exact acceptance/commit chronology. Current selection is nevertheless deterministic: greatest visible accepted UUID, with each child scoped to the selected parent (`ORDER BY id DESC LIMIT 1`). Repeated creates and recovery use that rule; this slice adds no chronology column.

**Neutral**
- Format remains a standard uuid, so drivers/ORM tooling treat it uniformly; time-sortability does not establish commit order.

## Links

- Spec: [[../spec.md]]
- SAD: [[../sad.md]] §8
- Related ADR: —
