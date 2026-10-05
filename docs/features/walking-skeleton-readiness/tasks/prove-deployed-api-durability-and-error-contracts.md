---
id: "T13"
title: "Prove deployed API durability and error contracts"
layer: "tests"
deps: ["T9"]
blocks: ["T15"]
acs: ["AC-04", "AC-07", "AC-13", "AC-14a", "AC-16", "AC-16a", "AC-17", "AC-20"]
files_hint: ["tests/api/workspace.spec.ts", "tests/api/workspace-fixtures.ts"]
owner: "<TBD lead>"
estimate: "7h"
context_budget: "M"
status: "todo"
---

# T13 — Prove deployed API durability and error contracts

## Place in the sequence

- **Blocked by:** T9 — Wire the workspace API and persistence into the existing server.
- **Blocks:** T15 — Extend the canonical persistence smoke to product restart recovery. **Wave:** 7 (after the named prerequisites).
- **Lane:** own lane. No standalone compile-breaking interface task.

## Why (user story)

> **As a** QA engineer
> **I want** an unsuccessful save to preserve previously accepted data
> **So that** I can retry without corrupting the verification context
>
> — `spec.md §4, US-07, verbatim` · full text: [spec.md](../spec.md)

Add isolated real-PostgreSQL/API cases for prerequisites, persisted trimming, unreliable reads, known non-acceptance and unknown COMMIT outcomes.

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

> QA->>Web: submits next valid record
> Web->>API: send record
> API->>DB: accept record in one transaction
> DB-->>API: confirmed rollback / no commit dispatched
> API-->>Web: SAVE_FAILED (nothing accepted, prior data preserved)
> Web-->>QA: show SAVE_FAILED and allow retry
>
> — `sad.md §6, Critical flow 3, abridged` · full text: [sad.md](../sad.md)

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

### AC-04 — contribution verified by this task

> **Given** no Project exists
> **When** the QA engineer attempts to record an Environment
> **Then** QuVeTrail accepts nothing and explains that an Environment requires a Project context
>
> — `spec.md §5, AC-04, verbatim` · full text: [spec.md](../spec.md)

### AC-07 — contribution verified by this task

> **Given** no Environment exists
> **When** the QA engineer attempts to define a Verification Target
> **Then** QuVeTrail accepts nothing and explains that a Verification Target requires an Environment
>
> — `spec.md §5, AC-07, verbatim` · full text: [spec.md](../spec.md)

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

### AC-20 — contribution verified by this task

> **Given** any authoritative persisted record required to restore the current Project → Environment → Verification Target → optional Verification Run and Observed Run State hierarchy cannot be read reliably
> **When** QuVeTrail attempts recovery or status derivation
> **Then** an explicit read failure or malformed or inconsistent accepted relationships produce Evidence Status `UNAVAILABLE`, no `MATCH` or `MISMATCH` applicability conclusion, and an explanation that the evidence context cannot currently be relied upon; a successful read with no accepted Verification Run follows AC-09 instead
>
> — `spec.md §5, AC-20, verbatim` · full text: [spec.md](../spec.md)

Use [data-model.md §Current hierarchy validity](../data-model.md#current-hierarchy-validity-ac-20) as the exact AC-20 predicate. Test empty/Project-only/Project+Environment/Target-without-Run as reliable; a full parent-linked chain with one state as complete; selected-parent mismatch, zero/multiple states for the selected Run, wrong-run returned state, and query failure as unreliable. Older branch rows alone remain reliable. Do not add persisted empty/untrimmed-string corruption detection.

## Coherent workspace-read evidence

Verify [T3's coherent-read evidence](implement-transactional-hierarchy-persistence-and-reliable-reads.md#coherent-workspace-read-obligation-and-evidence) against the adapter's actual PostgreSQL query/transaction mechanism: one GET must select the complete current chain, absences and Run state/count at one visibility snapshot. Reject evidence that would also pass independently changing snapshots, even if the resulting parent links are valid. Reuse T3's deterministic lower-level oracle when it establishes the database guarantee; add an isolated, controlled real-PostgreSQL interleaving only if that proof is insufficient. Record which evidence proves coherence separately from deployed envelope/ordering cases. Do not require a timing-sensitive concurrency test or infer an uncertain POST's historical outcome from GET.

## Save-outcome obligations

Separate the evidence oracles. For known non-acceptance, force a statement failure after Run insert but before COMMIT, prove controlled rollback/no later COMMIT, assert 503 verification_run.save_failed, both attempted rows absent and prior rows unchanged, then remove the fault and explicitly retry.

For unknown acceptance, compose the same API/use cases/repository with real PostgreSQL and a test-owned node-postgres client wrapper in the owned fixtures. One fixture forwards COMMIT to real PostgreSQL, awaits its completion, then withholds that acknowledgement from the adapter by reporting connection loss. Another reports the same loss at the COMMIT boundary without forwarding COMMIT and disposes/rolls back the client. At the adapter boundary both are unknown, regardless of fixture ground truth: assert 503 verification_run.save_outcome_unknown, no accepted record/status, and no transaction replay. After each fixture's transaction is settled, GET must restore both Run/State for the committed case or neither for the non-committed case; prior rows are unchanged. Do not use a generic throw as evidence of rollback or treat snapshot absence as historical rollback proof.

Use dependency injection at existing composition/driver seams, not a production fault endpoint or runtime toggle. These deterministic composed API/real-DB cases prove the adapter's lost-acknowledgement handling and recovery, not actual packet loss against the deployed process. Keep deployed success/confirmed-rollback checks and their evidence separately identified; T14 owns browser handling of the received unknown response.

With readable prerequisites, submit both-empty Target and all-empty Run and assert the OpenAPI multi-field examples plus no new rows. Submit a mixed wrong-type/whitespace-only body and assert structural-only `request.invalid_body`. Keep exhaustive invalid-field combinations in T5/T8; these deployed cases prove boundary wiring.

## Checklist

- [ ] Add isolated real-PostgreSQL/API cases for prerequisites, persisted trimming, unreliable reads, known non-acceptance and unknown COMMIT outcomes. (owned paths below).
- [ ] Force failure after run insert but before aggregate acceptance using test-controlled database conditions, without a production fault endpoint. (owned paths below).
- [ ] For known non-acceptance only, assert both attempted rows absent and prior rows unchanged, then remove the fault and explicitly retry. (owned paths below).
- [ ] Keep test cleanup isolated from previously accepted user data. (owned paths below).
- [ ] Implement focused verification in the owned test paths; use the plan-tests allocation before execution.
- [ ] Keep changes within: `tests/api/workspace.spec.ts`, `tests/api/workspace-fixtures.ts`.

## Edge cases

| Case | Behaviour |
|---|---|
| Empty after trim / case or internal whitespace differs | Reject empty inputs with field error and retry; preserve remaining characters and compare case-sensitively. |
| Missing accepted parent | Accept nothing, explain prerequisite, do not offer dependent creation. |
| Pending commit | No SAVED or status from the submitted record. |
| Known non-acceptance | SAVE_FAILED preserves prior rows/input and permits user-initiated POST retry. |
| Unknown acceptance / lost COMMIT acknowledgement | No SAVED or SAVE_FAILED; preserve uncertainty and recover authoritative workspace via GET before explicit continuation. |
| Read failure or malformed/inconsistent accepted relationship | UNAVAILABLE explanation; no MATCH/MISMATCH or inferred recovery. |

— `spec.md §5, AC-04, AC-07, AC-13, AC-14a, AC-16, AC-17, AC-20, abridged` · full text: [spec.md](../spec.md)
— `sad.md §6, Critical flow 3, Critical flow 2, abridged` · full text: [sad.md](../sad.md)

For AC-20 database evidence, isolate fixtures with a selected Run lacking state, a selected Run with two states (allowed by the current non-UNIQUE FK schema), older complete branches plus a valid current partial branch, and a controlled query failure. Assert `503 workspace.unavailable` for the first two and query failure, and `200` for the older-branch case. Wrong-parent/wrong-run returned objects are adapter/loader cases in T3/T6; do not disable live FK constraints to fabricate them.

## Definition of Done

- [ ] pnpm test:api passes on the controlled Compose system with exact envelopes, durable state inspection and safe retry only after known non-acceptance. Real PostgreSQL evidence distinguishes atomic rollback from commit with acknowledgement hidden at a test-owned driver boundary: unknown response followed by GET restores both rows; a controlled non-commit with the same unknown response restores neither. Prior rows remain unchanged and no automatic transaction retry occurs. Label composed API/real-DB fault fixtures separately from deployed checks. AC-20 zero/multiple current-Run states and query failure yield 503 workspace.unavailable, older branches plus current partial hierarchy yield 200, and structural request failures use typed 400 envelopes. Deployed both-empty Target, all-empty Run and mixed structural/domain cases assert exact precedence/complete field lists and no durable writes; controlled ordering fixtures confirm greatest-UUID parent-scoped current selection rather than insertion/commit order. Coherent-read evidence is validated against the actual PostgreSQL mechanism per the task's evidence allocation; independently changing snapshots cannot pass the oracle, and a controlled database interleaving is added only if lower-level proof is insufficient.
- [ ] All inlined hard rules remain true; no unaccepted data used for conclusions.
- [ ] `pnpm check:architecture` and relevant focused tests/typecheck pass. No dedicated lint command exists; do not invent lint/vet commands.
- [ ] Follow [AGENTS.md verification execution policy](../../../../AGENTS.md#verification-execution-policy) and [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff); report retained evidence and actual contract impact.
