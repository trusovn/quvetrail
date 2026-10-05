---
id: "T14"
title: "Prove progressive browser behavior and refresh recovery"
layer: "tests"
deps: ["T12"]
blocks: ["T15"]
acs: ["AC-01", "AC-02", "AC-03", "AC-05", "AC-06", "AC-08", "AC-09", "AC-10", "AC-11", "AC-12", "AC-15", "AC-16", "AC-16a", "AC-17", "AC-17a", "AC-18", "AC-19", "AC-19a", "AC-20"]
files_hint: ["tests/e2e/workspace.spec.ts", "tests/e2e/foundation.spec.ts", "tests/e2e/workspace-fixtures.ts"]
owner: "<TBD lead>"
estimate: "8h"
context_budget: "L" # justified: One bounded browser suite verifies the same progressive path at each recovery checkpoint; all asserted ACs must stay verbatim.
status: "todo"
---

# T14 — Prove progressive browser behavior and refresh recovery

## Place in the sequence

- **Blocked by:** T12 — Render evidence guidance, applicability and unavailable states.
- **Blocks:** T15 — Extend the canonical persistence smoke to product restart recovery. **Wave:** 9 (after the named prerequisites).
- **Lane:** own lane. No standalone compile-breaking interface task.

## Why (user story)

> **As a** QA engineer
> **I want** the complete Project, Environment, Verification Target, and optional Verification Run context restored after refresh or restart
> **So that** the same Evidence Status can be reproduced from the complete persisted hierarchy
>
> — `spec.md §4, US-08, verbatim` · full text: [spec.md](../spec.md)

Add short browser scenarios for progressive acceptance, whitespace/field validation, pending saves, retry, guidance and both applicability outcomes.

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

> **Chosen:** Option 1 — a client-rendered SPA whose authoritative state is fetched from and re-derived by the server on load/refresh/restart.
>
> — `adr/0004-spa-server-authoritative-state.md §Decision outcome, ADR-0004, abridged` · full text: [0004-spa-server-authoritative-state.md](../adr/0004-spa-server-authoritative-state.md)

**Fallback:** If a signed slice is insufficient, ambiguous or contradicts the code, read its linked source in full; the source wins. Do not invent missing requirements.

## Data delta

No DB changes.

Existing/staged persistence structures may be read or written by this task; schema ownership remains T1.

## API contract

- `POST /api/v1/projects` — body {name:string}; 201 {outcome:SAVED, record:{id,name,created_at}}; 400 project.invalid_name (details.fields:[name]); 503 project.save_failed (known non-acceptance) / project.save_outcome_unknown (recover via GET).

— `contracts/openapi.yaml §paths / components.schemas, createProject, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

- `POST /api/v1/environments` — body {name:string}, current Project resolved server-side; 201 {outcome:SAVED, record:{id,project_id,name,created_at}}; 400 environment.invalid_name (details.fields:[name]); 409 environment.project_missing; 503 environment.save_failed (known non-acceptance) / environment.save_outcome_unknown (recover via GET).

— `contracts/openapi.yaml §paths / components.schemas, createEnvironment, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

- `POST /api/v1/verification-targets` — body {key:string,value:string}, current Environment resolved server-side; 201 {outcome:SAVED, record:{id,environment_id,key,value,created_at}} with no evidence_status; 400 verification_target.invalid_key / verification_target.invalid_value (single-field details.fields:[key] / [value]; simultaneous failures follow the rule below); 409 verification_target.environment_missing; 503 verification_target.save_failed (known non-acceptance) / verification_target.save_outcome_unknown (recover via GET).

— `contracts/openapi.yaml §paths / components.schemas, createVerificationTarget, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

- `POST /api/v1/verification-runs` — body {run_reference:string,observed_run_state:{key:string,value:string}}, current Target resolved server-side; 201 {outcome:SAVED,evidence_status:MATCH|MISMATCH,record:{id,verification_target_id,run_reference,created_at,observed_run_state:{id,verification_run_id,key,value,created_at}}}; 400 verification_run.invalid_run_reference / verification_run.invalid_observed_key / verification_run.invalid_observed_value (single-field details.fields:[run_reference] / [observed_run_state.key] / [observed_run_state.value]; simultaneous failures follow the rule below); 409 verification_run.verification_target_missing; 503 verification_run.save_failed (known non-acceptance) / verification_run.save_outcome_unknown (recover via GET).

— `contracts/openapi.yaml §paths / components.schemas, createVerificationRun, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

- `GET /api/v1/workspace` — no request body; 200 {project:Project|null,environment:Environment|null,verification_target:VerificationTarget|null,verification_run:VerificationRun|null,evidence_status:null|NO_EVIDENCE|MATCH|MISMATCH}; Project:{id,name,created_at}; Environment:{id,project_id,name,created_at}; VerificationTarget:{id,environment_id,key,value,created_at}; VerificationRun:{id,verification_target_id,run_reference,created_at,observed_run_state:{id,verification_run_id,key,value,created_at}}; 503 workspace.unavailable, with no applicability conclusion.

— `contracts/openapi.yaml §paths / components.schemas, getWorkspace, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

General errors use `{code,message,details?}`. Every HTTP 400 uses `ValidationError`, requiring `details.fields` (a non-empty string array). Structural body failures use `request.invalid_body`; empty-after-trim failures retain operation-specific codes. Field paths and body-level `$` handling are defined in OpenAPI. Create bodies and success schemas reject additional properties. IDs are UUID strings and timestamps date-time strings.

— `contracts/openapi.yaml §components.schemas, Error / owned Create and record schemas, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

For simultaneous empty-after-trim failures, follow [spec.md validation feedback](../spec.md#validation-feedback-ac-02--ac-05--ac-08--ac-12) / [OpenAPI](../contracts/openapi.yaml): collect every failing field; choose the first failing code by Target `key`, `value` or Run `run_reference`, `observed_run_state.key`, `observed_run_state.value`; return all paths sorted/deduplicated. Structural errors precede domain validation and use only `request.invalid_body`. Render every known domain path inline with its non-empty-after-trim explanation; the primary code is not the field list.

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

### AC-05 — contribution verified by this task

> **Given** the current Project exists
> **When** the QA engineer submits an Environment name that is empty after trimming
> **Then** QuVeTrail shows `VALIDATION_ERROR`, records no Environment, and allows retry
>
> — `spec.md §5, AC-05, verbatim` · full text: [spec.md](../spec.md)

### AC-06 — contribution verified by this task

> **Given** the current Environment exists
> **When** the QA engineer submits a Verification Target key and value that are both non-empty after trimming
> **Then** QuVeTrail durably records them as the configuration comparison context and shows `SAVED`
>
> — `spec.md §5, AC-06, verbatim` · full text: [spec.md](../spec.md)

### AC-08 — contribution verified by this task

> **Given** no Verification Target has been recorded
> **When** the QA engineer submits a target key or value that is empty after trimming
> **Then** QuVeTrail shows `VALIDATION_ERROR`, records no Verification Target, and allows retry
>
> — `spec.md §5, AC-08, verbatim` · full text: [spec.md](../spec.md)

### AC-09 — contribution verified by this task

> **Given** the complete Project → Environment → Verification Target hierarchy is readable and no Verification Run has been recorded
> **When** the QA engineer views Evidence Status
> **Then** QuVeTrail derives domain Evidence Status `NO_EVIDENCE` but does not render it in the UI as an assessment result alongside `MATCH` and `MISMATCH`; instead, the UI explains that a Verification Run has not been recorded yet and offers the run-entry action
>
> — `spec.md §5, AC-09, verbatim` · full text: [spec.md](../spec.md)

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

### AC-17a — contribution verified by this task

> **Given** the parent record required for the next hierarchy level has not been accepted
> **When** the QA engineer views the progressive workspace
> **Then** QuVeTrail does not offer the action for creating that dependent record
>
> — `spec.md §5, AC-17a, verbatim` · full text: [spec.md](../spec.md)

### AC-18 — contribution verified by this task

> **Given** a Project, Environment, Verification Target, Verification Run, and Observed Run State have been accepted
> **When** QuVeTrail is refreshed or restarted
> **Then** it restores the complete Project → Environment → Verification Target → Verification Run and Observed Run State hierarchy and derives the same `MATCH` or `MISMATCH` Evidence Status
>
> — `spec.md §5, AC-18, verbatim` · full text: [spec.md](../spec.md)

### AC-19 — contribution verified by this task

> **Given** a Project, Environment, and Verification Target exist without a Verification Run
> **When** QuVeTrail is refreshed or restarted
> **Then** it restores the complete persisted Project → Environment → Verification Target hierarchy, preserves the absence of a Verification Run, derives domain Evidence Status `NO_EVIDENCE`, and shows workflow guidance that a Verification Run has not been recorded yet with the run-entry action instead of rendering `NO_EVIDENCE` as an assessment result
>
> — `spec.md §5, AC-19, verbatim` · full text: [spec.md](../spec.md)

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

Follow [SAD §6 browser acceptance outcomes](../sad.md#6-runtime-view): only received `503 *.save_failed` permits SAVE_FAILED retry. Received `503 *.save_outcome_unknown` and lost/unusable POST responses expose an unknown acceptance outcome, never SAVE_FAILED and never automatic POST retry. The workspace blocks creates and reloads `GET /api/v1/workspace`; continue from recovered hierarchy, or keep creates blocked with UNAVAILABLE and retry GET on failed recovery. A recovered record is shown as accepted without fabricating SAVED/SAVE_FAILED for the uncertain attempt. Any create after reliable recovery is an explicit user action from recovered context; snapshot absence is not proof of rollback or a duplicate-free retry guarantee.

## Save-outcome obligations

Add received 503 *.save_outcome_unknown browser cases alongside lost POST responses. For each source of uncertainty, exercise recovered accepted and absent state, assert all creates blocked during recovery, exactly the original POST until an explicit new action, GET before continuation, and no SAVE_FAILED/SAVED claim for the uncertain attempt. If GET fails, repeated reload actions send only GET and cannot unlock creates. For reliable absence, explicitly submit a new create to demonstrate user-directed continuation; do not label this proof of rollback or duplicate prevention.

Use controlled received-unknown responses for browser presentation/order and identify them as injected contract evidence. Real persistence/transaction classification is owned by T13; keep existing real response-loss recovery and known save_failed retry checks. No duplicate-forbidding behavior is introduced.

## Checklist

- [ ] Add short browser scenarios for progressive acceptance, whitespace/field validation, pending saves, retry, guidance and both applicability outcomes. (owned paths below).
- [ ] Reload at Project-only, Project+Environment, Target-without-Run and full-run checkpoints. (owned paths below).
- [ ] Use controlled responses for pending/error presentations and real persistence for recovery paths. (owned paths below).
- [ ] Update only foundation UI assertions invalidated by the new product screen; retain health-boundary proof. (owned paths below).
- [ ] Implement focused verification in the owned test paths; use the plan-tests allocation before execution.
- [ ] Keep changes within: `tests/e2e/workspace.spec.ts`, `tests/e2e/foundation.spec.ts`, `tests/e2e/workspace-fixtures.ts`.

## Edge cases

| Case | Behaviour |
|---|---|
| Empty after trim / case or internal whitespace differs | Reject empty inputs with field error and retry; preserve remaining characters and compare case-sensitively. |
| Missing accepted parent | Accept nothing, explain prerequisite, do not offer dependent creation. |
| Pending / known HTTP save failure | No SAVED or status from a pending record; received 503 *.save_failed preserves accepted records and permits retry. |
| Received save_outcome_unknown / lost or unusable POST response | Unknown outcome; no SAVE_FAILED and no repeated POST; recover with GET before any further create. |
| Target/run absent on successful authoritative read | Only accepted levels; no status before target; NO_EVIDENCE is workflow guidance when run absent. |
| Read failure or malformed/inconsistent accepted relationship | UNAVAILABLE explanation; no MATCH/MISMATCH or inferred recovery. |
| Key/value/case mismatch | MISMATCH; exact trimmed equality alone yields MATCH, applicability only. |

— `spec.md §5, AC-01, AC-02, AC-03, AC-05, AC-06, AC-08, AC-09, AC-10, AC-11, AC-12, AC-15, AC-16, AC-17, AC-17a, AC-18, AC-19, AC-19a, AC-20, abridged` · full text: [spec.md](../spec.md)
— `sad.md §6, Critical flow 2, Critical flow 3, abridged` · full text: [sad.md](../sad.md)

## Definition of Done

- [ ] pnpm test:e2e proves SCR-01 states, restored hierarchy and identical status after reload; injected responses are separated from real persistence evidence and normal Playwright failure artifacts remain available. Received 503 save_outcome_unknown and lost-response cases each cover accepted and absent recovery state, GET before continuation, no automatic POST replay, no retroactive SAVED/SAVE_FAILED, and failed recovery with GET-only retry. Known 503 save_failed still permits user-initiated safe POST retry; any create after unknown-outcome recovery is explicit continuation without a duplicate-free guarantee.
- [ ] All inlined hard rules remain true; no unaccepted data used for conclusions.
- [ ] `pnpm check:architecture` and relevant focused tests/typecheck pass. No dedicated lint command exists; do not invent lint/vet commands.
- [ ] Follow [AGENTS.md verification execution policy](../../../../AGENTS.md#verification-execution-policy) and [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff); report retained evidence and actual contract impact.
