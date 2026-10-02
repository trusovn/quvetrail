---
id: "T10"
title: "Implement the browser HTTP adapter from the approved contract"
layer: "ports"
deps: []
blocks: ["T11"]
acs: ["AC-16", "AC-16a", "AC-17", "AC-20"]
files_hint: ["apps/web/src/api/", "apps/web/test/unit/workspace-client.spec.ts"]
owner: "<TBD lead>"
estimate: "4h"
context_budget: "M"
status: "todo"
---

# T10 — Implement the browser HTTP adapter from the approved contract

## Place in the sequence

- **Blocked by:** none.
- **Blocks:** T11 — Build the progressive hierarchy and record-entry workspace. **Wave:** 1 (after the named prerequisites).
- **Lane:** own lane. No standalone compile-breaking interface task.

## Why (user story)

> **As a** QA engineer
> **I want** an unsuccessful save to preserve previously accepted data
> **So that** I can retry without corrupting the verification context
>
> — `spec.md §4, US-07, verbatim` · full text: [spec.md](../spec.md)

Implement browser-owned request/response types and five typed fetch operations from OpenAPI without importing API internals.

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

> **Chosen:** Option 1 — declare `target_surfaces: ["backend-service", "web-frontend"]`, written to `sad.md` frontmatter and one §5 C4 container per surface.
>
> — `adr/0001-target-surfaces-backend-service-web-frontend.md §Decision outcome, ADR-0001, abridged` · full text: [0001-target-surfaces-backend-service-web-frontend.md](../adr/0001-target-surfaces-backend-service-web-frontend.md)

> **Chosen:** Option 1 — a client-rendered SPA whose authoritative state is fetched from and re-derived by the server on load/refresh/restart.
>
> — `adr/0004-spa-server-authoritative-state.md §Decision outcome, ADR-0004, abridged` · full text: [0004-spa-server-authoritative-state.md](../adr/0004-spa-server-authoritative-state.md)

**Fallback:** If a signed slice is insufficient, ambiguous or contradicts the code, read its linked source in full; the source wins. Do not invent missing requirements.

## Data delta

No DB changes.

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

Follow [SAD §6 browser acceptance outcomes](../sad.md#6-runtime-view): only received `503 *.save_failed` permits SAVE_FAILED retry. Received `503 *.save_outcome_unknown` and lost/unusable POST responses expose an unknown acceptance outcome, never SAVE_FAILED and never automatic POST retry. The workspace blocks creates and reloads `GET /api/v1/workspace`; continue from recovered hierarchy, or keep creates blocked with UNAVAILABLE and retry GET on failed recovery. A recovered record is shown as accepted without fabricating SAVED/SAVE_FAILED for the uncertain attempt. Any create after reliable recovery is an explicit user action from recovered context; snapshot absence is not proof of rollback or a duplicate-free retry guarantee.

## Save-outcome obligations

Test all four POST operations with valid 503 *.save_failed and 503 *.save_outcome_unknown envelopes; branch on status plus the matching operation code. Received unknown, rejected fetch, malformed response body, and unrecognized status/code all expose recovery-required unknown acceptance, never SAVE_FAILED. The adapter never replays POST. Typed unknown operation feedback is distinct from workspace.unavailable (GET failure) and from domain Evidence Status.

Add injected-fetch multi-field 400 fixtures for both-empty Target, all-empty Run and valid-reference/both-empty observed fields. Preserve all `details.fields` paths independently of which field supplies the primary code; do not reduce feedback to that code.

## Checklist

- [ ] Implement browser-owned request/response types and five typed fetch operations from OpenAPI without importing API internals. (owned paths below).
- [ ] Preserve HTTP error code/message/details and distinguish failed saves from unavailable workspace reads; expose pending operations as promises, without client-derived evidence rules or persistence cache. (owned paths below).
- [ ] Implement focused verification in the owned test paths; use the plan-tests allocation before execution.
- [ ] Keep changes within: `apps/web/src/api/`, `apps/web/test/unit/workspace-client.spec.ts`.

## Edge cases

| Case | Behaviour |
|---|---|
| Pending / known HTTP save failure | No SAVED or status from a pending record; received 503 *.save_failed preserves accepted records and permits retry. |
| Received save_outcome_unknown / lost or unusable POST response | Unknown outcome; no SAVE_FAILED and no repeated POST; recover with GET before any further create. |
| Read failure or malformed/inconsistent accepted relationship | UNAVAILABLE explanation; no MATCH/MISMATCH or inferred recovery. |

— `spec.md §5, AC-16, AC-17, AC-20, abridged` · full text: [spec.md](../spec.md)
— `sad.md §6, Critical flow 2, Critical flow 3, abridged` · full text: [sad.md](../sad.md)

## Definition of Done

- [ ] Injected-fetch tests prove exact paths/bodies and successful payloads, 400 field details, 409 prerequisites, and status-plus-code distinction between known 503 save_failed and 503 save_outcome_unknown for all four creates; pending requests never resolve as accepted. Rejected/unusable/unrecognized POST responses expose unknown acceptance without POST replay; GET failure exposes unavailable recovery. Multi-field 400 fixtures preserve the primary code and complete sorted field list, including a Run reference code whose field sorts last.
- [ ] All inlined hard rules remain true; no unaccepted data used for conclusions.
- [ ] `pnpm check:architecture` and relevant focused tests/typecheck pass. No dedicated lint command exists; do not invent lint/vet commands.
- [ ] Follow [AGENTS.md verification execution policy](../../../../AGENTS.md#verification-execution-policy) and [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff); report retained evidence and actual contract impact.
