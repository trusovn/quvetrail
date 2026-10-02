---
id: "T1"
title: "Promote the staged hierarchy schema into Drizzle history"
layer: "migration"
deps: []
blocks: ["T3"]
acs: ["AC-01", "AC-06", "AC-10", "AC-18"]
files_hint: ["apps/api/src/schema.ts", "apps/api/drizzle/**", "docs/features/walking-skeleton-readiness/migrations/**"]
owner: "<TBD lead>"
estimate: "6h"
context_budget: "L" # justified: Five FK-linked tables and both staged migration directions form one reviewed schema promotion and rollback gate.
status: "todo"
---

# T1 — Promote the staged hierarchy schema into Drizzle history

## Place in the sequence

- **Blocked by:** none.
- **Blocks:** T3 — Implement transactional hierarchy persistence and reliable reads. **Wave:** 1 (after the named prerequisites).
- **Lane:** own lane. No standalone compile-breaking interface task.

## Why (user story)

> **As a** QA engineer
> **I want** the complete Project, Environment, Verification Target, and optional Verification Run context restored after refresh or restart
> **So that** the same Evidence Status can be reproduced from the complete persisted hierarchy
>
> — `spec.md §4, US-08, verbatim` · full text: [spec.md](../spec.md)

Extend the existing editable schema with the five entities; preserve foundation_probe.

## Inlined context

> The Walking Skeleton uses a progressive evidence-applicability workspace that exposes the persisted hierarchy, external-run context, operation outcomes, and current Evidence Status.
>
> — `spec.md §1, committed approach, verbatim` · full text: [spec.md](../spec.md)

> - Invalid or failed submissions do not alter previously accepted data.
> - Missing hierarchy prerequisites prevent dependent records from being accepted.
> - Unreadable authoritative data produces `UNAVAILABLE`, not an inferred applicability conclusion.
>
> — `spec.md §6.1, limited trust-boundary behavior, abridged` · full text: [spec.md](../spec.md)

> | The one-record restriction is temporary scope, not a domain singleton/immutability rule | Medium | Record in code + docs that single-record is this slice only; do not encode singleton assumptions in the schema beyond what this slice needs | Tech Lead |
>
> — `sad.md §11, one-record scope, verbatim` · full text: [sad.md](../sad.md)

> The API is a layered (hexagonal-leaning) service: transport (Fastify handlers) → application (use-cases) → domain (pure deterministic rules: Evidence Status derivation, trimming/comparison); application → repository abstraction ← infrastructure implementation (Drizzle over node-postgres). Deterministic domain logic has no I/O and no dependency on outer layers, per the repo convention (`docs/project-map.md`). The web client is a thin SPA that calls the API and holds no business rules. Chosen because durability and derivation correctness (QG-1/QG-2) must be provable without the UI. The current architecture gate protects foundation paths; T3 extends it to the planned application/domain boundaries below.
>
> — `sad.md §5, module boundaries, verbatim` · full text: [sad.md](../sad.md)

> QA->>Web: submits run reference + Observed Run State
> Web->>API: send run context
> API->>API: validate + trim (reject if empty)
> API->>DB: accept record in one transaction
> API->>API: derive Evidence Status from readable hierarchy
> API-->>Web: SAVED + MATCH/MISMATCH
> Web-->>QA: show SAVED and Evidence Status
>
> — `sad.md §6, Critical flow 1, abridged` · full text: [sad.md](../sad.md)

> QA->>Web: refresh / reopen after restart
> Web->>API: request current workspace
> API->>DB: read authoritative hierarchy
> DB-->>API: accepted records
> DB-->>API: read failure
> API-->>Web: UNAVAILABLE, no applicability conclusion
> Web-->>QA: explain context cannot be relied upon
>
> — `sad.md §6, Critical flow 2, abridged` · full text: [sad.md](../sad.md)

> **Chosen:** Option 1 — a single request-scoped transaction per accept; `SAVED` is returned only after confirmed durable commit, `SAVE_FAILED` only after known non-acceptance, and unknown acceptance requires authoritative recovery.
>
> — `adr/0002-transactional-record-acceptance.md §Decision outcome, ADR-0002, abridged` · full text: [0002-transactional-record-acceptance.md](../adr/0002-transactional-record-acceptance.md)

> **Chosen:** Option 1 — a pure function in `apps/api/src/domain/` derives Evidence Status from the readable hierarchy on each read.
>
> — `adr/0003-derive-evidence-status-at-read-time.md §Decision outcome, ADR-0003, abridged` · full text: [0003-derive-evidence-status-at-read-time.md](../adr/0003-derive-evidence-status-at-read-time.md)

> **Chosen:** Option 1 — uuid v7 generated at the application layer.
>
> — `adr/0005-uuid-v7-record-ids.md §Decision outcome, ADR-0005, abridged` · full text: [0005-uuid-v7-record-ids.md](../adr/0005-uuid-v7-record-ids.md)

**Fallback:** If a signed slice is insufficient, ambiguous or contradicts the code, read its linked source in full; the source wins. Do not invent missing requirements.

## Data delta

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | uuid | PK, NOT NULL, app-generated (UUID v7) | Time-sortable (ADR-0005); "current Project" selection uses `ORDER BY id DESC LIMIT 1`. |
| `name` | text | NOT NULL | Non-empty after trimming, enforced at the application layer (AC-01/AC-02, AC-14a); stored already trimmed; case preserved. |
| `created_at` | timestamp with time zone | NOT NULL DEFAULT now() | Timestamp assigned during the acceptance transaction; not the commit instant. |

— `data-model.md §Entities, project, verbatim` · full text: [data-model.md](../data-model.md)

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | uuid | PK, NOT NULL, app-generated (UUID v7) | |
| `project_id` | uuid | NOT NULL, FK → `project(id)` | Indexed (`environment_project_id_idx`). |
| `name` | text | NOT NULL | Non-empty after trimming, application layer (AC-03/AC-05). |
| `created_at` | timestamp with time zone | NOT NULL DEFAULT now() | |

— `data-model.md §Entities, environment, verbatim` · full text: [data-model.md](../data-model.md)

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | uuid | PK, NOT NULL, app-generated (UUID v7) | |
| `environment_id` | uuid | NOT NULL, FK → `environment(id)` | Indexed (`verification_target_environment_id_idx`). |
| `key` | text | NOT NULL | Non-empty after trimming, application layer (AC-06/AC-08); stored trimmed, compared case-sensitively (AC-14a). |
| `value` | text | NOT NULL | Same validation and comparison rules as `key`. |
| `created_at` | timestamp with time zone | NOT NULL DEFAULT now() | |

— `data-model.md §Entities, verification_target, verbatim` · full text: [data-model.md](../data-model.md)

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | uuid | PK, NOT NULL, app-generated (UUID v7) | |
| `verification_target_id` | uuid | NOT NULL, FK → `verification_target(id)` | Indexed (`verification_run_verification_target_id_idx`). |
| `run_reference` | text | NOT NULL | External run identifier; non-empty after trimming, application layer (AC-10/AC-12); a trusted user assertion (spec §6.1). |
| `created_at` | timestamp with time zone | NOT NULL DEFAULT now() | |

— `data-model.md §Entities, verification_run, verbatim` · full text: [data-model.md](../data-model.md)

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | uuid | PK, NOT NULL, app-generated (UUID v7) | |
| `verification_run_id` | uuid | NOT NULL, FK → `verification_run(id)` | Indexed (`observed_run_state_verification_run_id_idx`). |
| `key` | text | NOT NULL | Non-empty after trimming, application layer (AC-10/AC-12); compared case-sensitively against `verification_target.key` (AC-14). |
| `value` | text | NOT NULL | Same rules as `key`. |
| `created_at` | timestamp with time zone | NOT NULL DEFAULT now() | |

— `data-model.md §Entities, observed_run_state, verbatim` · full text: [data-model.md](../data-model.md)

**Migration ownership:** `apps/api/src/schema.ts` is the editable schema authority. The staged SQL is planning/reference input. Generate and review the new live history using the existing `apps/api/drizzle.config.ts` / Drizzle Kit mechanism; assign the next sequence at implementation time. T1 owns `apps/api/drizzle/**`, including new SQL and generated metadata required by Drizzle. Generated journal/snapshot metadata may be updated as required by Drizzle, retaining applied-migration history; preserve all applied migration SQL, including `0000_foundation.sql`.

Staged inputs (promote reviewed forward SQL through `apps/api/drizzle/`, retaining generated journal/snapshot metadata):

- `docs/features/walking-skeleton-readiness/migrations/01_create_project.up.sql`
- `docs/features/walking-skeleton-readiness/migrations/01_create_project.down.sql`
- `docs/features/walking-skeleton-readiness/migrations/02_create_environment.up.sql`
- `docs/features/walking-skeleton-readiness/migrations/02_create_environment.down.sql`
- `docs/features/walking-skeleton-readiness/migrations/03_create_verification_target.up.sql`
- `docs/features/walking-skeleton-readiness/migrations/03_create_verification_target.down.sql`
- `docs/features/walking-skeleton-readiness/migrations/04_create_verification_run.up.sql`
- `docs/features/walking-skeleton-readiness/migrations/04_create_verification_run.down.sql`
- `docs/features/walking-skeleton-readiness/migrations/05_create_observed_run_state.up.sql`
- `docs/features/walking-skeleton-readiness/migrations/05_create_observed_run_state.down.sql`

## API contract

Internal — no API surface.

## Acceptance criteria

### AC-01 — contribution verified by this task

> **Given** no Project has been recorded
> **When** the QA engineer submits a Project name that is non-empty after trimming
> **Then** QuVeTrail durably records the Project and shows `SAVED`
>
> — `spec.md §5, AC-01, verbatim` · full text: [spec.md](../spec.md)

### AC-06 — contribution verified by this task

> **Given** the current Environment exists
> **When** the QA engineer submits a Verification Target key and value that are both non-empty after trimming
> **Then** QuVeTrail durably records them as the configuration comparison context and shows `SAVED`
>
> — `spec.md §5, AC-06, verbatim` · full text: [spec.md](../spec.md)

### AC-10 — contribution verified by this task

> **Given** a readable Verification Target exists and no Verification Run has been recorded
> **When** the QA engineer submits a non-empty run reference and a non-empty Observed Run State whose key and value exactly equal the Verification Target key and value
> **Then** QuVeTrail durably records the Verification Run and its Observed Run State, shows `SAVED`, and derives Evidence Status `MATCH`
>
> — `spec.md §5, AC-10, verbatim` · full text: [spec.md](../spec.md)

### AC-18 — contribution verified by this task

> **Given** a Project, Environment, Verification Target, Verification Run, and Observed Run State have been accepted
> **When** QuVeTrail is refreshed or restarted
> **Then** it restores the complete Project → Environment → Verification Target → Verification Run and Observed Run State hierarchy and derives the same `MATCH` or `MISMATCH` Evidence Status
>
> — `spec.md §5, AC-18, verbatim` · full text: [spec.md](../spec.md)

## Checklist

- [ ] Extend the existing editable schema with the five entities; preserve foundation_probe. (owned paths below).
- [ ] Generate and review new Drizzle forward history and metadata against the staged SQL in numeric order. (owned paths below).
- [ ] Retain the staged reverse-order rollback pairs as controlled test artifacts; do not invent a production rollback runner. (owned paths below).
- [ ] Implement focused verification in the owned test paths; use the plan-tests allocation before execution.
- [ ] Keep changes within: `apps/api/src/schema.ts`, `apps/api/drizzle/**`, `docs/features/walking-skeleton-readiness/migrations/**`. Own the new generated forward migration and required Drizzle journal/snapshot updates; never rewrite applied SQL such as `0000_foundation.sql`; metadata updates must retain applied-migration history.

## Edge cases

| Case | Behaviour |
|---|---|
| Key/value/case mismatch | MISMATCH; exact trimmed equality alone yields MATCH, applicability only. |

— `spec.md §5, AC-01, AC-06, AC-10, AC-18, abridged` · full text: [spec.md](../spec.md)
— `sad.md §6, Critical flow 1, Critical flow 2, abridged` · full text: [sad.md](../sad.md)

## Definition of Done

- [ ] On an isolated disposable database, the new history applies, reapplies without changes, and the staged down pairs reverse only the new tables in reverse dependency order; all FK indexes and prior foundation data survive the forward migration. New forward SQL and required generated Drizzle metadata are committed; applied history including 0000_foundation.sql is unchanged.
- [ ] All inlined hard rules remain true; no unaccepted data used for conclusions.
- [ ] `pnpm check:architecture` and relevant focused tests/typecheck pass. No dedicated lint command exists; do not invent lint/vet commands.
- [ ] Follow [AGENTS.md verification execution policy](../../../../AGENTS.md#verification-execution-policy) and [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff); report retained evidence and actual contract impact.
