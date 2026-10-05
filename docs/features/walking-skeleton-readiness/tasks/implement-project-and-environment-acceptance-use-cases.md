---
id: "T4"
title: "Implement Project and Environment acceptance use cases"
layer: "app"
deps: ["T2", "T3"]
blocks: ["T5", "T7"]
acs: ["AC-01", "AC-02", "AC-03", "AC-04", "AC-05", "AC-14a", "AC-16", "AC-16a", "AC-17"]
files_hint: ["apps/api/src/app/record-project.ts", "apps/api/src/app/record-environment.ts", "apps/api/src/app/record-id.ts", "apps/api/test/unit/record-context.spec.ts", "apps/api/package.json", "pnpm-lock.yaml"]
owner: "<TBD lead>"
estimate: "6h"
context_budget: "M"
status: "todo"
---

# T4 — Implement Project and Environment acceptance use cases

## Place in the sequence

- **Blocked by:** T2 — Implement pure input and evidence-applicability rules; T3 — Implement transactional hierarchy persistence and reliable reads.
- **Blocks:** T5 — Implement Target and atomic Run acceptance use cases; T7 — Expose Project and Environment HTTP operations. **Wave:** 3 (after the named prerequisites).
- **Lane:** serialized overlapping paths with T5. No standalone compile-breaking interface task.

## Why (user story)

> **As a** QA engineer
> **I want** to create an Environment within the Project
> **So that** verification applicability has a specific deployed target
>
> — `spec.md §4, US-02, verbatim` · full text: [spec.md](../spec.md)

Implement both use cases with T3's application-facing `apps/api/src/app/workspace-repository.ts` contract. Import it directly, inject it, and type structural repository doubles against it; do not import `infra/**`, concrete factories, database/schema types or transport. The contract and its Drizzle implementation are read-only T3 outputs; return any needed seam correction to T3's scope before proceeding. Existing composition wiring remains T9's responsibility.

## Inlined context

> The Walking Skeleton uses a progressive evidence-applicability workspace that exposes the persisted hierarchy, external-run context, operation outcomes, and current Evidence Status.
>
> — `spec.md §1, committed approach, verbatim` · full text: [spec.md](../spec.md)

> - Invalid or failed submissions do not alter previously accepted data.
> - Missing hierarchy prerequisites prevent dependent records from being accepted.
> - Unreadable authoritative data produces `UNAVAILABLE`, not an inferred applicability conclusion.
>
> — `spec.md §6.1, limited trust-boundary behavior, abridged` · full text: [spec.md](../spec.md)

> The API is a layered (hexagonal-leaning) service: transport (Fastify handlers) → application (use-cases) → domain (pure deterministic rules: Evidence Status derivation, trimming/comparison); application → repository abstraction ← infrastructure implementation (Drizzle over node-postgres). Deterministic domain logic has no I/O and no dependency on outer layers, per the repo convention (`docs/project-map.md`). The web client is a thin SPA that calls the API and holds no business rules. Chosen because durability and derivation correctness (QG-1/QG-2) must be provable without the UI. The current architecture gate protects foundation paths; T3 extends it to the planned application/domain boundaries below.
>
> — `sad.md §5, module boundaries, verbatim` · full text: [sad.md](../sad.md)

> U->>W: submits Project name
> W->>S: send Project name
> S->>S: trim value, preserve remaining characters, reject if empty
> S->>D: accept Project in one transaction
> else name empty after trimming
> S-->>W: VALIDATION_ERROR
> W-->>U: show VALIDATION_ERROR and allow retry
>
> — `sad.md §6, US-01 — Create Project, abridged` · full text: [sad.md](../sad.md)

> U->>W: chooses Environment action
> W->>S: send Environment name
> S->>S: read current Project context, trim value, reject if empty
> S->>D: accept Environment in one transaction within the Project
> else no Project accepted
> S-->>W: prerequisite missing, Environment requires a Project context
> W-->>U: keep action unavailable and explain prerequisite
>
> — `sad.md §6, US-02 — Create Environment, abridged` · full text: [sad.md](../sad.md)

> **Chosen:** Option 1 — a single request-scoped transaction per accept; `SAVED` is returned only after confirmed durable commit, `SAVE_FAILED` only after known non-acceptance, and unknown acceptance requires authoritative recovery.
>
> — `adr/0002-transactional-record-acceptance.md §Decision outcome, ADR-0002, abridged` · full text: [0002-transactional-record-acceptance.md](../adr/0002-transactional-record-acceptance.md)

> **Chosen:** Option 1 — uuid v7 generated at the application layer.
>
> — `adr/0005-uuid-v7-record-ids.md §Decision outcome, ADR-0005, abridged` · full text: [0005-uuid-v7-record-ids.md](../adr/0005-uuid-v7-record-ids.md)

**Fallback:** If a signed slice is insufficient, ambiguous or contradicts the code, read its linked source in full; the source wins. Do not invent missing requirements.

## Data delta

No DB changes.

Existing/staged persistence structures may be read or written by this task; schema ownership remains T1.

## API contract

- `POST /api/v1/projects` — body {name:string}; 201 {outcome:SAVED, record:{id,name,created_at}}; 400 project.invalid_name (details.fields:[name]); 503 project.save_failed (known non-acceptance) / project.save_outcome_unknown (recover via GET).

— `contracts/openapi.yaml §paths / components.schemas, createProject, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

- `POST /api/v1/environments` — body {name:string}, current Project resolved server-side; 201 {outcome:SAVED, record:{id,project_id,name,created_at}}; 400 environment.invalid_name (details.fields:[name]); 409 environment.project_missing; 503 environment.save_failed (known non-acceptance) / environment.save_outcome_unknown (recover via GET).

— `contracts/openapi.yaml §paths / components.schemas, createEnvironment, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

All error responses use `{code,message,details?}`; `details.fields` identifies failed fields. Create bodies and success schemas reject additional properties. IDs are UUID strings and timestamps date-time strings.

— `contracts/openapi.yaml §components.schemas, Error / owned Create and record schemas, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

## Acceptance criteria

### AC-01 — contribution verified by this task

> **Given** no Project has been recorded
> **When** the QA engineer submits a Project name that is non-empty after trimming
> **Then** QuVeTrail durably records the Project and shows `SAVED`
>
> — `spec.md §5, AC-01, verbatim` · full text: [spec.md](../spec.md)

### AC-02 — contribution verified by this task

> **Given** no Project has been recorded
> **When** the QA engineer submits a Project name that is empty after trimming
> **Then** QuVeTrail shows `VALIDATION_ERROR`, records no Project, and allows retry
>
> — `spec.md §5, AC-02, verbatim` · full text: [spec.md](../spec.md)

### AC-03 — contribution verified by this task

> **Given** the current Project exists
> **When** the QA engineer submits an Environment name that is non-empty after trimming
> **Then** QuVeTrail durably records the Environment within that Project and shows `SAVED`
>
> — `spec.md §5, AC-03, verbatim` · full text: [spec.md](../spec.md)

### AC-04 — contribution verified by this task

> **Given** no Project exists
> **When** the QA engineer attempts to record an Environment
> **Then** QuVeTrail accepts nothing and explains that an Environment requires a Project context
>
> — `spec.md §5, AC-04, verbatim` · full text: [spec.md](../spec.md)

### AC-05 — contribution verified by this task

> **Given** the current Project exists
> **When** the QA engineer submits an Environment name that is empty after trimming
> **Then** QuVeTrail shows `VALIDATION_ERROR`, records no Environment, and allows retry
>
> — `spec.md §5, AC-05, verbatim` · full text: [spec.md](../spec.md)

### AC-14a — contribution verified by this task

> **Given** the QA engineer submits a textual value that is accepted
> **When** QuVeTrail records or compares that value
> **Then** it removes leading and trailing whitespace before recording, preserves every remaining character without further normalization, and compares Verification Target and Observed Run State keys and values case-sensitively
>
> — `spec.md §5, AC-14a, verbatim` · full text: [spec.md](../spec.md)

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

## Save-outcome obligations

Preserve the T3 three-way result in both use cases: confirmed commit → SAVED; known non-acceptance → SAVE_FAILED; acceptance unknown → distinct recovery-required result (HTTP *.save_outcome_unknown). A parent-context read that fails before acceptance writes can yield SAVE_FAILED because no acceptance transaction/COMMIT follows it. An arbitrary exception from an acceptance call defaults to unknown unless adapter evidence establishes non-acceptance. Do not replay transactions. Test the three outcomes independently and prove that unknown yields neither success nor retry-safe failure.

## Checklist

- [ ] Implement both use cases against T3's application-facing contract using injection and typed doubles, with no infrastructure imports or contract edits. (owned paths below).
- [ ] Generate UUID v7 IDs at the application boundary, using a small established generator if the runtime has none. (owned paths below).
- [ ] Resolve current Project server-side, trim before validation, reject missing prerequisites, and await acceptance before returning success. (owned paths below).
- [ ] Update dependencies only if the chosen UUID generator requires them. (owned paths below).
- [ ] Implement focused verification in the owned test paths; use the plan-tests allocation before execution.
- [ ] Keep changes within: `apps/api/src/app/record-project.ts`, `apps/api/src/app/record-environment.ts`, `apps/api/src/app/record-id.ts`, `apps/api/test/unit/record-context.spec.ts`, `apps/api/package.json`, `pnpm-lock.yaml`.

## Edge cases

| Case | Behaviour |
|---|---|
| Empty after trim / case or internal whitespace differs | Reject empty inputs with field error and retry; preserve remaining characters and compare case-sensitively. |
| Missing accepted parent | Accept nothing, explain prerequisite, do not offer dependent creation. |
| Pending commit | No SAVED or status from the submitted record. |
| Known non-acceptance | SAVE_FAILED preserves prior rows/input and permits user-initiated POST retry. |
| Unknown acceptance / lost COMMIT acknowledgement | No SAVED or SAVE_FAILED; preserve uncertainty and recover authoritative workspace via GET before explicit continuation. |

— `spec.md §5, AC-01, AC-02, AC-03, AC-04, AC-05, AC-14a, AC-16, AC-17, abridged` · full text: [spec.md](../spec.md)
— `sad.md §6, US-01 — Create Project, US-02 — Create Environment, abridged` · full text: [sad.md](../sad.md)

## Definition of Done

- [ ] Injected-repository tests prove trimmed names and character preservation, no calls on invalid/missing-parent input, no success before confirmed commit, SAVE_FAILED only on known non-acceptance, and distinct unknown acceptance without retry or success. Parent-read failure before acceptance writes is known non-acceptance; generic acceptance exceptions default to unknown. Repository doubles are typed against app/workspace-repository.ts; no infrastructure imports or contract edits.
- [ ] All inlined hard rules remain true; no unaccepted data used for conclusions.
- [ ] `pnpm check:architecture` and relevant focused tests/typecheck pass. No dedicated lint command exists; do not invent lint/vet commands.
- [ ] Follow [AGENTS.md verification execution policy](../../../../AGENTS.md#verification-execution-policy) and [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff); report retained evidence and actual contract impact.
