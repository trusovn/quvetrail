---
id: "T5"
title: "Implement Target and atomic Run acceptance use cases"
layer: "app"
deps: ["T4"]
blocks: ["T8"]
acs: ["AC-06", "AC-07", "AC-08", "AC-10", "AC-11", "AC-12", "AC-13", "AC-14a", "AC-16", "AC-16a", "AC-17"]
files_hint: ["apps/api/src/app/record-target.ts", "apps/api/src/app/record-run.ts", "apps/api/src/app/record-id.ts", "apps/api/test/unit/record-evidence.spec.ts"]
owner: "<TBD lead>"
estimate: "7h"
context_budget: "M"
status: "todo"
---

# T5 — Implement Target and atomic Run acceptance use cases

## Place in the sequence

- **Blocked by:** T4 — Implement Project and Environment acceptance use cases.
- **Blocks:** T8 — Expose Target and Run HTTP operations. **Wave:** 4 (after the named prerequisites).
- **Lane:** serialized overlapping paths with T4. No standalone compile-breaking interface task.

## Why (user story)

> **As a** QA engineer
> **I want** to record an external Verification Run and its Observed Run State
> **So that** QuVeTrail retains what was verified and the configuration the run actually exercised
>
> — `spec.md §4, US-04, verbatim` · full text: [spec.md](../spec.md)

Resolve the current Environment/Target from the server repository, trim each input and reject empty fields or absent prerequisites.

Consume T3's `apps/api/src/app/workspace-repository.ts` contract directly through injection and typed structural doubles; it is available transitively through T4. Do not import `infra/**`, concrete factories, database/schema types or transport, or edit the contract/adapter. T3 establishes all four acceptance operations, including atomic Run/State, before this task starts; return any missing seam capability to T3's scope before proceeding.

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

> U->>W: submits target key and value
> W->>S: send target key and value
> S->>S: read current Environment context, trim values, reject if either is empty
> S->>D: accept Verification Target in one transaction within the Environment
> else no Environment accepted
> S-->>W: prerequisite missing, Verification Target requires an Environment
> W-->>U: keep action unavailable and explain prerequisite
>
> — `sad.md §6, US-03 — Define Verification Target, abridged` · full text: [sad.md](../sad.md)

> U->>W: submits run reference and Observed Run State key and value
> W->>S: send run context
> S->>S: read current Verification Target, trim values, reject if any is empty
> S->>D: accept Verification Run and Observed Run State in one transaction
> else no Verification Target accepted
> S-->>W: prerequisite missing, Verification Target must be defined first
> W-->>U: keep action unavailable and explain prerequisite
>
> — `sad.md §6, US-04 — Record external Verification Run, abridged` · full text: [sad.md](../sad.md)

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

No DB changes.

Read/write persisted records only through the injected application contract; schema/migrations and adapter source remain read-only T1/T3 outputs.

## API contract

- `POST /api/v1/verification-targets` — body {key:string,value:string}, current Environment resolved server-side; 201 {outcome:SAVED, record:{id,environment_id,key,value,created_at}} with no evidence_status; 400 verification_target.invalid_key / verification_target.invalid_value (single-field details.fields:[key] / [value]; simultaneous failures follow the rule below); 409 verification_target.environment_missing; 503 verification_target.save_failed (known non-acceptance) / verification_target.save_outcome_unknown (recover via GET).

— `contracts/openapi.yaml §paths / components.schemas, createVerificationTarget, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

- `POST /api/v1/verification-runs` — body {run_reference:string,observed_run_state:{key:string,value:string}}, current Target resolved server-side; 201 {outcome:SAVED,evidence_status:MATCH|MISMATCH,record:{id,verification_target_id,run_reference,created_at,observed_run_state:{id,verification_run_id,key,value,created_at}}}; 400 verification_run.invalid_run_reference / verification_run.invalid_observed_key / verification_run.invalid_observed_value (single-field details.fields:[run_reference] / [observed_run_state.key] / [observed_run_state.value]; simultaneous failures follow the rule below); 409 verification_run.verification_target_missing; 503 verification_run.save_failed (known non-acceptance) / verification_run.save_outcome_unknown (recover via GET).

— `contracts/openapi.yaml §paths / components.schemas, createVerificationRun, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

All error responses use `{code,message,details?}`; `details.fields` identifies failed fields. Create bodies and success schemas reject additional properties. IDs are UUID strings and timestamps date-time strings.

— `contracts/openapi.yaml §components.schemas, Error / owned Create and record schemas, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

For simultaneous empty-after-trim failures, follow [spec.md validation feedback](../spec.md#validation-feedback-ac-02--ac-05--ac-08--ac-12) / [OpenAPI](../contracts/openapi.yaml): collect every failing field; choose the first failing code by Target `key`, `value` or Run `run_reference`, `observed_run_state.key`, `observed_run_state.value`; return all paths sorted/deduplicated. Structural errors precede domain validation and use only `request.invalid_body`. Render every known domain path inline with its non-empty-after-trim explanation; the primary code is not the field list.

## Acceptance criteria

### AC-06 — contribution verified by this task

> **Given** the current Environment exists
> **When** the QA engineer submits a Verification Target key and value that are both non-empty after trimming
> **Then** QuVeTrail durably records them as the configuration comparison context and shows `SAVED`
>
> — `spec.md §5, AC-06, verbatim` · full text: [spec.md](../spec.md)

### AC-07 — contribution verified by this task

> **Given** no Environment exists
> **When** the QA engineer attempts to define a Verification Target
> **Then** QuVeTrail accepts nothing and explains that a Verification Target requires an Environment
>
> — `spec.md §5, AC-07, verbatim` · full text: [spec.md](../spec.md)

### AC-08 — contribution verified by this task

> **Given** no Verification Target has been recorded
> **When** the QA engineer submits a target key or value that is empty after trimming
> **Then** QuVeTrail shows `VALIDATION_ERROR`, records no Verification Target, and allows retry
>
> — `spec.md §5, AC-08, verbatim` · full text: [spec.md](../spec.md)

### AC-10 — contribution verified by this task

> **Given** a readable Verification Target exists and no Verification Run has been recorded
> **When** the QA engineer submits a non-empty run reference and a non-empty Observed Run State whose key and value exactly equal the Verification Target key and value
> **Then** QuVeTrail durably records the Verification Run and its Observed Run State, shows `SAVED`, and derives Evidence Status `MATCH`
>
> — `spec.md §5, AC-10, verbatim` · full text: [spec.md](../spec.md)

### AC-11 — contribution verified by this task

> **Given** a readable Verification Target exists and no Verification Run has been recorded
> **When** the QA engineer submits a non-empty run reference and a non-empty Observed Run State whose key or value differs from the Verification Target
> **Then** QuVeTrail durably records the Verification Run and its Observed Run State, shows `SAVED`, and derives Evidence Status `MISMATCH`
>
> — `spec.md §5, AC-11, verbatim` · full text: [spec.md](../spec.md)

### AC-12 — contribution verified by this task

> **Given** a Verification Target exists and no Verification Run has been recorded
> **When** the submitted run reference, observed-state key, or observed-state value is empty after trimming
> **Then** QuVeTrail shows `VALIDATION_ERROR`, records no Verification Run, and allows retry
>
> — `spec.md §5, AC-12, verbatim` · full text: [spec.md](../spec.md)

### AC-13 — contribution verified by this task

> **Given** no Verification Target exists
> **When** the QA engineer attempts to record a Verification Run
> **Then** QuVeTrail accepts nothing and explains that a Verification Target must be defined first
>
> — `spec.md §5, AC-13, verbatim` · full text: [spec.md](../spec.md)

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

Preserve the T3 three-way result for both Target and Run: confirmed commit → SAVED; known non-acceptance → SAVE_FAILED; acceptance unknown → distinct recovery-required result (HTTP *.save_outcome_unknown). Parent-context read failure before acceptance writes is known non-acceptance; an arbitrary acceptance exception is unknown without adapter evidence. Never derive MATCH/MISMATCH from an uncertain submitted Run/State or retry its transaction. Unit tests must use separate confirmed-rollback and unknown-outcome doubles; real atomicity remains T13's obligation.

For structurally valid inputs, validate every accepted-text field and assemble one rejection before acceptance writes. Use the fixed precedence and complete field list above, never short-circuit after the first invalid field. Test all three invalid Target-field subsets and all seven invalid Run-field subsets with input/property order varied and no acceptance repository call. No new validation taxonomy is needed.

## Checklist

- [ ] Resolve the current Environment/Target from the server repository, trim each input and reject empty fields or absent prerequisites. (owned paths below).
- [ ] Generate application UUID v7 IDs with T4 helper. (owned paths below).
- [ ] Accept the run and observed state together; only committed accepted inputs feed the pure status derivation. (owned paths below).
- [ ] Implement focused verification in the owned test paths; use the plan-tests allocation before execution.
- [ ] Keep changes within: `apps/api/src/app/record-target.ts`, `apps/api/src/app/record-run.ts`, `apps/api/src/app/record-id.ts`, `apps/api/test/unit/record-evidence.spec.ts`.

## Edge cases

| Case | Behaviour |
|---|---|
| Empty after trim / case or internal whitespace differs | Reject empty inputs with field error and retry; preserve remaining characters and compare case-sensitively. |
| Missing accepted parent | Accept nothing, explain prerequisite, do not offer dependent creation. |
| Pending commit | No SAVED or status from the submitted record. |
| Known non-acceptance | SAVE_FAILED preserves prior rows/input and permits user-initiated POST retry. |
| Unknown acceptance / lost COMMIT acknowledgement | No SAVED or SAVE_FAILED; preserve uncertainty and recover authoritative workspace via GET before explicit continuation. |
| Key/value/case mismatch | MISMATCH; exact trimmed equality alone yields MATCH, applicability only. |

— `spec.md §5, AC-06, AC-07, AC-08, AC-10, AC-11, AC-12, AC-13, AC-14a, AC-16, AC-17, abridged` · full text: [spec.md](../spec.md)
— `sad.md §6, US-03 — Define Verification Target, US-04 — Record external Verification Run, abridged` · full text: [sad.md](../sad.md)

## Definition of Done

- [ ] Focused use-case tests prove both match outcomes, each invalid field and prerequisite, atomic run acceptance, and preserved prior data on known non-acceptance. Unknown acceptance remains distinct with no SAVED, SAVE_FAILED, pending-record status or transaction replay; generic acceptance exceptions cannot imply rollback. Repository doubles are typed against app/workspace-repository.ts; no infrastructure imports or contract edits. Table-driven cases cover all three non-empty subsets of invalid Target fields and all seven non-empty subsets of invalid Run fields, with permuted JSON/input property order: fixed first-failing code, all sorted/deduplicated paths, and zero acceptance writes.
- [ ] All inlined hard rules remain true; no unaccepted data used for conclusions.
- [ ] `pnpm check:architecture` and relevant focused tests/typecheck pass. No dedicated lint command exists; do not invent lint/vet commands.
- [ ] Follow [AGENTS.md verification execution policy](../../../../AGENTS.md#verification-execution-policy) and [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff); report retained evidence and actual contract impact.
