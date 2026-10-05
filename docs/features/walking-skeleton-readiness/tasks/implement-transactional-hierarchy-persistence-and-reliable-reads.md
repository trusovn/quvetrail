---
id: "T3"
title: "Implement transactional hierarchy persistence and reliable reads"
layer: "infra"
deps: ["T1", "T2"]
blocks: ["T4", "T6"]
acs: ["AC-16", "AC-16a", "AC-17", "AC-18", "AC-19a", "AC-20"]
files_hint: ["apps/api/src/app/workspace-repository.ts", "apps/api/src/infra/**", "apps/api/test/unit/workspace-repository.spec.ts", ".dependency-cruiser.cjs", "tools/test-architecture-gate.mjs"]
owner: "<TBD lead>"
estimate: "8h"
context_budget: "M"
status: "todo"
---

# T3 — Implement transactional hierarchy persistence and reliable reads

## Place in the sequence

- **Blocked by:** T1 — Promote the staged hierarchy schema into Drizzle history; T2 — Implement pure input and evidence-applicability rules.
- **Blocks:** T4 — Implement Project and Environment acceptance use cases; T6 — Implement authoritative workspace loading and recovery states. **Wave:** 2 (after the named prerequisites).
- **Lane:** own lane. No standalone compile-breaking interface task.

## Why (user story)

> **As a** QA engineer
> **I want** the complete Project, Environment, Verification Target, and optional Verification Run context restored after refresh or restart
> **So that** the same Evidence Status can be reproduced from the complete persisted hierarchy
>
> — `spec.md §4, US-08, verbatim` · full text: [spec.md](../spec.md)

Implement the application-facing repository contract and its first Drizzle implementation together, plus the narrow dependency gate correction protecting that seam.

## Repository boundary ownership

- Own `apps/api/src/app/workspace-repository.ts`, despite this task's `infra` lane: it is the application-facing contract, not an infrastructure export. Define only the current hierarchy reads, four acceptance operations (Run/State together), plain input/record types, and three-way acceptance results and reliable/unreliable read results needed by T4/T5/T6. Reuse T2 domain types where useful; no Drizzle-derived types, database clients, Fastify/Zod types or HTTP status codes belong here.
- Own the concrete factory/implementation in `apps/api/src/infra/workspace-repository.ts`; any focused transaction-lifecycle helpers remain under `infra/**`. Implement/import the application contract, never re-export it from infrastructure for consumers. Database/schema handles remain adapter inputs and implementation details.
- T4/T5/T6 consume the contract read-only through injection and typed structural doubles. T5 reaches T3 through T4; no new repository-contract task is needed. If a consumer needs a missing capability, return that change to T3's bounded scope before continuing rather than editing infrastructure or inventing a second contract.
- T9 alone binds the concrete product adapter in `server.ts` and passes its application contract into `buildApp`; T3 must not edit composition or `database.ts`. Application imports domain/the contract; infrastructure imports the contract; HTTP imports use cases; domain imports none of these outer layers.

## Planned architecture gate correction

Own only the seam-related edits in `.dependency-cruiser.cjs` and `tools/test-architecture-gate.mjs` described by [SAD §5](../sad.md#5-building-block-view). Extend the existing domain rule to `app/`, `infra/`, and `ports/`; add `no-application-to-outer-layers` from `apps/api/src/app/` to `infra/`, `ports/`, and existing root transport/persistence/composition files (`app.ts`, `database.ts`, `foundation-probe.ts`, `migrate.ts`, `schema.ts`, `server.ts`). Both rules reject direct `fastify`, `@fastify/*`, `drizzle-orm`, and `pg` imports/subpaths, including type-only imports. Do not forbid infrastructure → application contract, application → domain, or composition-root wiring, and do not add unrelated policy.

The current gate and its web-only sentinel cannot prove this seam. Add resolvable, cleaned-up negative fixtures for application → infrastructure (including a type-only import), application → transport/root persistence/direct persistence package, and domain → each new outer directory/direct outer package. Add allowed-direction checks for infrastructure → application contract, application → domain and server composition; retain the web sentinel. Run `pnpm check:architecture` and focused repository tests/typecheck. These rule changes are implementation work owned by T3, not changes already made during planning.

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

> QA->>Web: refresh / reopen after restart
> Web->>API: request current workspace
> API->>DB: read authoritative hierarchy
> DB-->>API: accepted records
> DB-->>API: read failure
> API-->>Web: UNAVAILABLE, no applicability conclusion
> Web-->>QA: explain context cannot be relied upon
>
> — `sad.md §6, Critical flow 2, abridged` · full text: [sad.md](../sad.md)

> QA->>Web: submits next valid record
> Web->>API: send record
> API->>DB: accept record in one transaction
> DB-->>API: confirmed rollback / no commit dispatched
> API-->>Web: SAVE_FAILED (nothing accepted, prior data preserved)
> Web-->>QA: show SAVE_FAILED and allow retry
>
> — `sad.md §6, Critical flow 3, abridged` · full text: [sad.md](../sad.md)

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

Read/write persisted records through the adapter; schema and migration source ownership remains T1 and is read-only here.

## API contract

Internal — no API surface.

## Acceptance criteria

### AC-16 — contribution verified by this task

> **Given** previously accepted Walking Skeleton data exists
> **When** saving the next valid record fails and non-acceptance is known (COMMIT was not dispatched and cannot follow, or rollback/non-commit of that transaction is confirmed)
> **Then** QuVeTrail shows `SAVE_FAILED`, accepts none of that attempted record, preserves all previously accepted data, and allows retry
>
> — `spec.md §5, AC-16, verbatim` · full text: [spec.md](../spec.md)

### AC-16a — contribution verified by this task

> **Given** the QA engineer has submitted a valid record
> **When** acceptance cannot be established, including loss of the API's PostgreSQL COMMIT acknowledgement or loss of the POST response
> **Then** QuVeTrail claims neither `SAVED` nor retry-safe `SAVE_FAILED`, explains that the save outcome could not be confirmed, blocks creates, and reloads the authoritative workspace before continuing; reliable recovery replaces the displayed hierarchy without replaying the POST or inventing a `SAVED` outcome for that attempt, while failed recovery shows `UNAVAILABLE` and allows GET retry only
>
> — `spec.md §5, AC-16a, verbatim` · full text: [spec.md](../spec.md)

### AC-17 — contribution verified by this task

> **Given** the QA engineer has submitted a valid record
> **When** durable acceptance is not known
> **Then** QuVeTrail does not show `SAVED` or derive Evidence Status using the submitted record; a reliable authoritative recovery may subsequently show persisted records and derive status from them without claiming `SAVED` for the uncertain attempt
>
> — `spec.md §5, AC-17, verbatim` · full text: [spec.md](../spec.md)

### AC-18 — contribution verified by this task

> **Given** a Project, Environment, Verification Target, Verification Run, and Observed Run State have been accepted
> **When** QuVeTrail is refreshed or restarted
> **Then** it restores the complete Project → Environment → Verification Target → Verification Run and Observed Run State hierarchy and derives the same `MATCH` or `MISMATCH` Evidence Status
>
> — `spec.md §5, AC-18, verbatim` · full text: [spec.md](../spec.md)

### AC-19a — contribution verified by this task

> **Given** only a Project, or only a Project and Environment, have been accepted
> **When** QuVeTrail is refreshed or restarted within the recovery boundary defined in §1
> **Then** it restores and shows only the accepted hierarchy levels, shows no unaccepted dependent record, and presents no Evidence Status until a Verification Target has been accepted
>
> — `spec.md §5, AC-19a, verbatim` · full text: [spec.md](../spec.md)

### AC-20 — contribution verified by this task

> **Given** any authoritative persisted record required to restore the current Project → Environment → Verification Target → optional Verification Run and Observed Run State hierarchy cannot be read reliably
> **When** QuVeTrail attempts recovery or status derivation
> **Then** an explicit read failure or malformed or inconsistent accepted relationships produce Evidence Status `UNAVAILABLE`, no `MATCH` or `MISMATCH` applicability conclusion, and an explanation that the evidence context cannot currently be relied upon; a successful read with no accepted Verification Run follows AC-09 instead
>
> — `spec.md §5, AC-20, verbatim` · full text: [spec.md](../spec.md)

Use [data-model.md §Current hierarchy validity](../data-model.md#current-hierarchy-validity-ac-20) as the exact AC-20 predicate. Test empty/Project-only/Project+Environment/Target-without-Run as reliable; a full parent-linked chain with one state as complete; selected-parent mismatch, zero/multiple states for the selected Run, wrong-run returned state, and query failure as unreliable. Older branch rows alone remain reliable. Do not add persisted empty/untrimmed-string corruption detection.

## Coherent workspace-read obligation and evidence

Own the [SAD §6 coherent workspace read](../sad.md#6-runtime-view) in the application-facing repository contract and adapter: one workspace result uses one database visibility snapshot for Project, each selected descendant or absence, and the selected Run's state/count. Independently changing visibility points cannot form a reliable result, even when parent links pass AC-20 checks. Keep the PostgreSQL/Drizzle mechanism open; a transaction whose statements see different snapshots is insufficient. T6 consumes this coherent result rather than assembling separate level reads.

Retain a deterministic lower-level oracle at the actual adapter query/transaction boundary that proves the chosen mechanism shares visibility across the entire read and rejects an implementation using independently advancing snapshots. The oracle must distinguish those implementations, including when concurrent acceptance changes the current selection; canned hierarchy doubles or parent-link checks alone do not prove coherence. Document the PostgreSQL snapshot guarantee the oracle relies on. A controlled real-PostgreSQL interleaving may supply the proof if needed; do not require a timing-sensitive concurrency test when the lower-level oracle establishes the same property. T13 checks this evidence against the real database mechanism.

## Save-outcome obligations

Own the [SAD §6 transaction-outcome boundary](../sad.md#6-runtime-view): control BEGIN/COMMIT/ROLLBACK on one leased node-postgres client with Drizzle statements bound to it, and expose confirmed committed / known not accepted / acceptance unknown. Track whether COMMIT may have been dispatched and require an actual commit acknowledgement for success; a transaction callback or INSERT result is not acceptance. Before-COMMIT failure must prevent any later commit and roll back or discard the client. Discard uncertain/broken clients; do not convert cleanup errors or a ROLLBACK after uncertain COMMIT into rollback proof. Never automatically retry acceptance.

Adapter tests must distinguish: pending commit; acknowledged commit; failure before COMMIT with no possible later dispatch (including rollback failure with client disposal); definite rollback/non-commit; COMMIT returning a rollback command result; and lost COMMIT acknowledgement with either committed or uncommitted fixture ground truth. Both uncertain cases return unknown. A cleanup ROLLBACK acknowledgement after uncertain COMMIT must remain unknown, and cleanup failure after known commit must not turn it into non-acceptance. Assertions at this layer prove classification, not real durability; T13 owns real PostgreSQL rows.

## Checklist

- [ ] Establish `app/workspace-repository.ts` with its `infra/workspace-repository.ts` implementation, and extend/test only the dependency rules protecting this seam. (owned paths below).
- [ ] Read current records by UUID order within the selected parent context, with one coherent workspace view as defined above. (owned paths below).
- [ ] Accept run plus observed state atomically; detect malformed/inconsistent accepted relationships and distinguish failed reads from successful absence. (owned paths below).
- [ ] Consume T1's schema at `apps/api/src/schema.ts` read-only; do not move or modify schema/migration source.
- [ ] Implement focused verification in the owned test paths; use the plan-tests allocation before execution.
- [ ] Keep changes within: `apps/api/src/app/workspace-repository.ts`, `apps/api/src/infra/**`, `apps/api/test/unit/workspace-repository.spec.ts`, `.dependency-cruiser.cjs`, `tools/test-architecture-gate.mjs`.

## Edge cases

| Case | Behaviour |
|---|---|
| Pending commit | No SAVED or status from the submitted record. |
| Known non-acceptance | SAVE_FAILED preserves prior rows/input and permits user-initiated POST retry. |
| Unknown acceptance / lost COMMIT acknowledgement | No SAVED or SAVE_FAILED; preserve uncertainty and recover authoritative workspace via GET before explicit continuation. |
| Target/run absent on successful authoritative read | Only accepted levels; no status before target; NO_EVIDENCE is workflow guidance when run absent. |
| Read failure or malformed/inconsistent accepted relationship | UNAVAILABLE explanation; no MATCH/MISMATCH or inferred recovery. |

— `spec.md §5, AC-16, AC-17, AC-18, AC-19a, AC-20, abridged` · full text: [spec.md](../spec.md)
— `sad.md §6, Critical flow 2, Critical flow 3, abridged` · full text: [sad.md](../sad.md)

## Definition of Done

- [ ] Adapter tests demonstrate confirmed commit, known non-acceptance and unknown acceptance, commit-awaited success, rollback of both run rows and preservation of earlier rows when non-acceptance is known. Cover in-flight COMMIT acknowledgement loss, cleanup rollback/error that cannot erase uncertainty, and no automatic transaction retry; real PostgreSQL evidence is completed by T13. Parent-scoped current reads include selected-parent/wrong-run mismatch, zero/multiple current-Run states and query failure; valid partial states and older branches remain reliable per data-model AC-20. The adapter implements the application-owned workspace-repository contract without outer-layer types leaking into it; focused gate sentinels reject application/domain outer imports (including type-only) and permit the intended inward imports/composition. Current-read fixtures with same-millisecond UUIDs and insertion/commit order differing from UUID order select the greatest visible UUID within each selected parent; a larger UUID on an older branch cannot win. Retained coherent-read evidence at the actual adapter boundary distinguishes one shared snapshot from independently changing visibility points and documents the PostgreSQL guarantee; T13 validates that mechanism.
- [ ] All inlined hard rules remain true; no unaccepted data used for conclusions.
- [ ] `pnpm check:architecture` and relevant focused tests/typecheck pass. No dedicated lint command exists; do not invent lint/vet commands.
- [ ] Follow [AGENTS.md verification execution policy](../../../../AGENTS.md#verification-execution-policy) and [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff); report retained evidence and actual contract impact.
