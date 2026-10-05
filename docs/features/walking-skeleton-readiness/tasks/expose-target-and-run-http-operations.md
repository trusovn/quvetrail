---
id: "T8"
title: "Expose Target and Run HTTP operations"
layer: "ports"
deps: ["T5", "T7"]
blocks: ["T9"]
acs: ["AC-06", "AC-07", "AC-08", "AC-10", "AC-11", "AC-12", "AC-13", "AC-15", "AC-16", "AC-16a", "AC-17"]
files_hint: ["apps/api/src/ports/http/evidence-routes.ts", "apps/api/test/unit/evidence-routes.spec.ts"]
owner: "<TBD lead>"
estimate: "6h"
context_budget: "M"
status: "todo"
---

# T8 — Expose Target and Run HTTP operations

## Place in the sequence

- **Blocked by:** T5 — Implement Target and atomic Run acceptance use cases; T7 — Expose Project and Environment HTTP operations (shared request policy).
- **Blocks:** T9 — Wire the workspace API and persistence into the existing server. **Wave:** 5 (after the named prerequisites).
- **Lane:** own lane. No standalone compile-breaking interface task.

## Why (user story)

> **As a** QA engineer
> **I want** to record an external Verification Run and its Observed Run State
> **So that** QuVeTrail retains what was verified and the configuration the run actually exercised
>
> — `spec.md §4, US-04, verbatim` · full text: [spec.md](../spec.md)

Add isolated route registration and strict Target/Run DTOs, including nested observed_run_state.

## Shared HTTP policy consumption

Consume T7's `apps/api/src/ports/http/request-policy.ts` read-only. Keep Target/Run strict DTO definitions and operation-specific 400/409/503 mappings local in `evidence-routes.ts`; inject use cases, never persistence infrastructure. Register these routes in an encapsulated Fastify scope and install T7's same scoped error handler before the POST handlers so malformed JSON/absent-body failures before handler execution are normalized too. Do not duplicate structural-error construction, issue-path sorting/deduplication or parser-error handling, and do not edit T7's helper/tests. Return a missing shared-policy capability to T7's bounded scope before proceeding.

Injection tests exercise the real Target/Run DTOs with the shared helper: strict top-level and nested missing/wrong-type/unexpected fields; full unexpected-key paths such as `observed_run_state.extra`; multiple paths sorted/deduplicated; absent/empty/malformed/non-object bodies using `$`; and zero use-case calls on structural failure. Keep operation-specific empty-after-trim errors distinct and prove no Fastify/Zod default body escapes. T7 owns helper-level policy tests; this task owns feature-route integration evidence.

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

> **Chosen:** Option 1 — declare `target_surfaces: ["backend-service", "web-frontend"]`, written to `sad.md` frontmatter and one §5 C4 container per surface.
>
> — `adr/0001-target-surfaces-backend-service-web-frontend.md §Decision outcome, ADR-0001, abridged` · full text: [0001-target-surfaces-backend-service-web-frontend.md](../adr/0001-target-surfaces-backend-service-web-frontend.md)

> **Chosen:** Option 1 — a single request-scoped transaction per accept; `SAVED` is returned only after confirmed durable commit, `SAVE_FAILED` only after known non-acceptance, and unknown acceptance requires authoritative recovery.
>
> — `adr/0002-transactional-record-acceptance.md §Decision outcome, ADR-0002, abridged` · full text: [0002-transactional-record-acceptance.md](../adr/0002-transactional-record-acceptance.md)

> **Chosen:** Option 1 — a pure function in `apps/api/src/domain/` derives Evidence Status from the readable hierarchy on each read.
>
> — `adr/0003-derive-evidence-status-at-read-time.md §Decision outcome, ADR-0003, abridged` · full text: [0003-derive-evidence-status-at-read-time.md](../adr/0003-derive-evidence-status-at-read-time.md)

**Fallback:** If a signed slice is insufficient, ambiguous or contradicts the code, read its linked source in full; the source wins. Do not invent missing requirements.

## Data delta

No DB changes.

## API contract

- `POST /api/v1/verification-targets` — body {key:string,value:string}, current Environment resolved server-side; 201 {outcome:SAVED, record:{id,environment_id,key,value,created_at}} with no evidence_status; 400 verification_target.invalid_key / verification_target.invalid_value (single-field details.fields:[key] / [value]; simultaneous failures follow the rule below); 409 verification_target.environment_missing; 503 verification_target.save_failed (known non-acceptance) / verification_target.save_outcome_unknown (recover via GET).

— `contracts/openapi.yaml §paths / components.schemas, createVerificationTarget, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

- `POST /api/v1/verification-runs` — body {run_reference:string,observed_run_state:{key:string,value:string}}, current Target resolved server-side; 201 {outcome:SAVED,evidence_status:MATCH|MISMATCH,record:{id,verification_target_id,run_reference,created_at,observed_run_state:{id,verification_run_id,key,value,created_at}}}; 400 verification_run.invalid_run_reference / verification_run.invalid_observed_key / verification_run.invalid_observed_value (single-field details.fields:[run_reference] / [observed_run_state.key] / [observed_run_state.value]; simultaneous failures follow the rule below); 409 verification_run.verification_target_missing; 503 verification_run.save_failed (known non-acceptance) / verification_run.save_outcome_unknown (recover via GET).

— `contracts/openapi.yaml §paths / components.schemas, createVerificationRun, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

General errors use `{code,message,details?}`. Every HTTP 400 uses `ValidationError`, requiring `details.fields` (a non-empty string array). Structural body failures use `request.invalid_body`; empty-after-trim failures retain operation-specific codes. Field paths and body-level `$` handling are defined in OpenAPI. Create bodies and success schemas reject additional properties. IDs are UUID strings and timestamps date-time strings.

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

### AC-15 — contribution verified by this task

> **Given** QuVeTrail presents Evidence Status
> **When** the QA engineer reviews it
> **Then** `MATCH` or `MISMATCH` describes only evidence applicability, while no Evidence Status claims anything about test outcomes or release Readiness
>
> — `spec.md §5, AC-15, verbatim` · full text: [spec.md](../spec.md)

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

Apply the shared HTTP policy above before any use case/write. OpenAPI remains authoritative for `request.invalid_body`, typed `ValidationErrorDetails`, deterministic paths and body-level `$`; operation-specific empty-after-trim errors remain local.

## Save-outcome obligations

For each owned POST, map only known non-acceptance to 503 *.save_failed. Map unknown acceptance to 503 *.save_outcome_unknown in the existing Error envelope, with no SAVED, record or evidence_status. Do not catch arbitrary DB/use-case exceptions and label them save_failed. Injection tests distinguish both codes under the same status for Target and atomic Run/State; neither an uncertain Run nor a cleanup exception may yield retry-safe failure or a derived success status.

Test all non-empty invalid-field subsets (three Target, seven Run) plus reordered request properties. Assert primary code, complete sorted field list and no writes. A structurally invalid request that also contains empty-after-trim text returns only `request.invalid_body`, never a mixture of structural and domain field lists.

## Checklist

- [ ] Add encapsulated route registration and local strict Target/Run DTOs using T7's shared policy and scoped parser-error handler read-only. (owned paths below).
- [ ] Serialize committed records and only the allowed run MATCH/MISMATCH status. (owned paths below).
- [ ] Map each field error, prerequisite and save failure to its operation-specific contract envelope. (owned paths below).
- [ ] Implement focused verification in the owned test paths; use the plan-tests allocation before execution.
- [ ] Keep changes within: `apps/api/src/ports/http/evidence-routes.ts`, `apps/api/test/unit/evidence-routes.spec.ts`.

## Edge cases

| Case | Behaviour |
|---|---|
| Empty after trim / case or internal whitespace differs | Reject empty inputs with field error and retry; preserve remaining characters and compare case-sensitively. |
| Missing accepted parent | Accept nothing, explain prerequisite, do not offer dependent creation. |
| Pending commit | No SAVED or status from the submitted record. |
| Known non-acceptance | SAVE_FAILED preserves prior rows/input and permits user-initiated POST retry. |
| Unknown acceptance / lost COMMIT acknowledgement | No SAVED or SAVE_FAILED; preserve uncertainty and recover authoritative workspace via GET before explicit continuation. |
| Key/value/case mismatch | MISMATCH; exact trimmed equality alone yields MATCH, applicability only. |

— `spec.md §5, AC-06, AC-07, AC-08, AC-10, AC-11, AC-12, AC-13, AC-15, AC-16, AC-17, abridged` · full text: [spec.md](../spec.md)
— `sad.md §6, US-03 — Define Verification Target, US-04 — Record external Verification Run, abridged` · full text: [sad.md](../sad.md)

## Definition of Done

- [ ] Fastify injection tests prove 201 nested run/state shape, target response without status, all named 400/409 branches, and both operation-specific 503 codes: save_failed only for known non-acceptance, save_outcome_unknown for unknown acceptance with no success record/status. No success before confirmed commit. Nested and top-level missing/wrong-type/unexpected fields and invalid JSON return 400 request.invalid_body with deterministic typed details.fields and no writes/default framework payload. Consume T7 request-policy read-only in encapsulated evidence registration; prove absent/malformed/non-object bodies and sorted/deduplicated nested paths without policy duplication. Prove all three invalid Target-field subsets and all seven invalid Run-field subsets, independent of JSON property order: fixed first-failing code plus all sorted paths. Mixed structural/domain failures return only request.invalid_body with zero use-case calls.
- [ ] All inlined hard rules remain true; no unaccepted data used for conclusions.
- [ ] `pnpm check:architecture` and relevant focused tests/typecheck pass. No dedicated lint command exists; do not invent lint/vet commands.
- [ ] Follow [AGENTS.md verification execution policy](../../../../AGENTS.md#verification-execution-policy) and [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff); report retained evidence and actual contract impact.
