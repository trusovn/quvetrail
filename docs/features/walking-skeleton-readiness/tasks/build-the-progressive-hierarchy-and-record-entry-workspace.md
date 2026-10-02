---
id: "T11"
title: "Build the progressive hierarchy and record-entry workspace"
layer: "ui"
deps: ["T9", "T10"]
blocks: ["T12"]
acs: ["AC-01", "AC-02", "AC-03", "AC-04", "AC-05", "AC-06", "AC-07", "AC-08", "AC-12", "AC-13", "AC-16", "AC-16a", "AC-17", "AC-17a", "AC-19a"]
files_hint: ["apps/web/src/App.tsx", "apps/web/src/WorkspaceHierarchy.tsx", "apps/web/src/RecordForm.tsx", "apps/web/src/OutcomeBanner.tsx", "apps/web/src/styles.css", "apps/web/test/unit/workspace-interaction.spec.ts"]
owner: "<TBD lead>"
estimate: "8h"
context_budget: "L" # justified: One progressive form controller shares pending, retry and prerequisite state across four record actions; splitting adds temporary incomplete UI wiring.
status: "todo"
---

# T11 — Build the progressive hierarchy and record-entry workspace

## Place in the sequence

- **Blocked by:** T9 — Wire the workspace API and persistence into the existing server; T10 — Implement the browser HTTP adapter from the approved contract.
- **Blocks:** T12 — Render evidence guidance, applicability and unavailable states. **Wave:** 7 (after the named prerequisites).
- **Lane:** serialized overlapping paths with T12. No standalone compile-breaking interface task.

## Why (user story)

> **As a** QA engineer
> **I want** to define the Environment configuration context for which evidence is required
> **So that** QuVeTrail has an exact comparison target without treating it as an instruction to change the Environment
>
> — `spec.md §4, US-03, verbatim` · full text: [spec.md](../spec.md)

Replace foundation-only screen content with authoritative load and progressive forms.

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

> **Chosen:** Option 1 — a single request-scoped transaction per accept; `SAVED` is returned only after confirmed durable commit, `SAVE_FAILED` only after known non-acceptance, and unknown acceptance requires authoritative recovery.
>
> — `adr/0002-transactional-record-acceptance.md §Decision outcome, ADR-0002, abridged` · full text: [0002-transactional-record-acceptance.md](../adr/0002-transactional-record-acceptance.md)

> **Chosen:** Option 1 — a client-rendered SPA whose authoritative state is fetched from and re-derived by the server on load/refresh/restart.
>
> — `adr/0004-spa-server-authoritative-state.md §Decision outcome, ADR-0004, abridged` · full text: [0004-spa-server-authoritative-state.md](../adr/0004-spa-server-authoritative-state.md)

> | default | `getWorkspace` 200 restores a partial hierarchy — Project only or Project + Environment (AC-19a): accepted levels listed, the next record action offered, every further dependent action unavailable with its prerequisite explanation (AC-17a, AC-04/AC-07/AC-13 — the contract's 409 envelopes carry these same explanations, which the UI normally never sees because the actions are gated); no Evidence Status area before a Verification Target is accepted | NEW: WorkspaceHierarchy, NEW: RecordForm | wireframe W1 |
> | empty | `getWorkspace` 200 with every level null (fresh installation — US-08 `empty_workspace` example): only the Project action offered; Environment, Verification Target, and Verification Run actions unavailable with prerequisite explanations | NEW: WorkspaceHierarchy, NEW: RecordForm | wireframe W2 |
> | loading | `getWorkspace` in flight after open / refresh / restart (sad.md §6 Critical flow 2): no hierarchy level, action, or status rendered before the authoritative read returns — the SPA trusts no client cache (ADR-0004) | NEW: WorkspaceHierarchy (loading presentation) | wireframe W3 |
> | saving | A valid record has been submitted and durable acceptance is pending (AC-17): the active form is disabled, `SAVED` is not shown, and the pending record is not used to derive Evidence Status | NEW: RecordForm (disabled), NEW: WorkspaceHierarchy | wireframe W4 |
> | validation | A create operation returns 400 `VALIDATION_ERROR` — the submitted name / key / value / run reference is empty after trimming (AC-02, AC-05, AC-08, AC-12): inline error naming known failed fields (`ValidationError.details.fields`); structural `request.invalid_body` uses the same envelope, with unknown paths / `$` shown at form level, nothing recorded, retry in place | NEW: RecordForm, NEW: OutcomeBanner | wireframe W5 |
> | error — save failed | A create operation returns operation-specific 503 `*.save_failed` — non-acceptance is known (AC-16, sad.md §6 Critical flow 3): none of the attempted record accepted, all previously accepted levels still rendered unchanged, retry offered | NEW: OutcomeBanner, NEW: WorkspaceHierarchy | wireframe W6 |
> | success | A create operation returns 201 — durable acceptance completed: `SAVED` shown in the record's own context and the next dependent action unlocked (AC-01, AC-03, AC-06); a saved Verification Run additionally transitions the Evidence Status area to `evidence — MATCH` or `evidence — MISMATCH` (AC-10/AC-11) | NEW: OutcomeBanner, NEW: WorkspaceHierarchy | wireframe W8 |
>
> — `screens.md §Screens, SCR-01 default, empty, loading, saving, validation, error — save failed, success, verbatim` · full text: [screens.md](../screens.md)

> - **Styling approach:** one global plain-CSS stylesheet with class modifiers — `apps/web/src/main.tsx:3`, `apps/web/src/styles.css:33`.
>
> — `../../architecture-map.md §Frontend / UI foundation, existing styling, verbatim` · full text: [architecture-map.md](../../../architecture-map.md)

> No reusable primitives are implemented yet (`docs/architecture-map.md:79`).
>
> — `../../design-system.md §Component inventory, reuse inventory, verbatim` · full text: [design-system.md](../../../design-system.md)

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

### AC-19a — contribution verified by this task

> **Given** only a Project, or only a Project and Environment, have been accepted
> **When** QuVeTrail is refreshed or restarted within the recovery boundary defined in §1
> **Then** it restores and shows only the accepted hierarchy levels, shows no unaccepted dependent record, and presents no Evidence Status until a Verification Target has been accepted
>
> — `spec.md §5, AC-19a, verbatim` · full text: [spec.md](../spec.md)

Follow [SAD §6 browser acceptance outcomes](../sad.md#6-runtime-view): only received `503 *.save_failed` permits SAVE_FAILED retry. Received `503 *.save_outcome_unknown` and lost/unusable POST responses expose an unknown acceptance outcome, never SAVE_FAILED and never automatic POST retry. The workspace blocks creates and reloads `GET /api/v1/workspace`; continue from recovered hierarchy, or keep creates blocked with UNAVAILABLE and retry GET on failed recovery. A recovered record is shown as accepted without fabricating SAVED/SAVE_FAILED for the uncertain attempt. Any create after reliable recovery is an explicit user action from recovered context; snapshot absence is not proof of rollback or a duplicate-free retry guarantee.

## Save-outcome obligations

UI/state cases cover received 503 *.save_outcome_unknown as well as lost/unusable POST responses, each with a reliable GET containing the accepted record and a reliable GET where it is absent. Replace current hierarchy and derive status from that GET without retroactive SAVED/SAVE_FAILED, preserved stale conclusions, or automatic POST replay. While GET is pending or failing, all creates remain blocked; recovery retry sends GET only. After a reliable GET, any new create requires explicit user action from recovered context and is not described as a guaranteed duplicate-free retry.

Verify inline feedback on both Target fields and all three Run inputs simultaneously, with a non-empty-after-trim explanation for each returned path. Preserve draft inputs and accepted hierarchy for correction/retry; do not copy the primary field-specific message onto another field or select only its path.

## Checklist

- [ ] Replace foundation-only screen content with authoritative load and progressive forms. (owned paths below).
- [ ] Create WorkspaceHierarchy, one RecordForm for four actions, and OutcomeBanner because no primitives exist. (owned paths below).
- [ ] Reuse existing global CSS values/class modifiers, useState/useEffect/fetch pattern and aria-live feedback. (owned paths below).
- [ ] Disable pending forms, retain retry input and accepted data on known HTTP save failure, recover unknown POST outcomes via GET before further creates, gate each action on accepted parent, and refresh authoritative state after successful acceptance. (owned paths below).
- [ ] Implement focused verification in the owned test paths; use the plan-tests allocation before execution.
- [ ] Keep changes within: `apps/web/src/App.tsx`, `apps/web/src/WorkspaceHierarchy.tsx`, `apps/web/src/RecordForm.tsx`, `apps/web/src/OutcomeBanner.tsx`, `apps/web/src/styles.css`, `apps/web/test/unit/workspace-interaction.spec.ts`.

## Edge cases

| Case | Behaviour |
|---|---|
| Empty after trim / case or internal whitespace differs | Reject empty inputs with field error and retry; preserve remaining characters and compare case-sensitively. |
| Missing accepted parent | Accept nothing, explain prerequisite, do not offer dependent creation. |
| Pending / known HTTP save failure | No SAVED or status from a pending record; received 503 *.save_failed preserves accepted records and permits retry. |
| Received save_outcome_unknown / lost or unusable POST response | Unknown outcome; no SAVE_FAILED and no repeated POST; recover with GET before any further create. |
| Target/run absent on successful authoritative read | Only accepted levels; no status before target; NO_EVIDENCE is workflow guidance when run absent. |

— `spec.md §5, AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-12, AC-13, AC-16, AC-17, AC-17a, AC-19a, abridged` · full text: [spec.md](../spec.md)
— `sad.md §6, Critical flow 2, Critical flow 3, abridged` · full text: [sad.md](../sad.md)

## Definition of Done

- [ ] Focused UI/state tests prove no cached hierarchy during load, accepted-level-only display, every action gate, field errors/retry, contextual SAVED only after completion, and unchanged accepted levels/input on known HTTP SAVE_FAILED. Received save_outcome_unknown and lost/unusable POST responses block all creates and trigger GET recovery; recovered hierarchy replaces prior state without retroactive SAVED/SAVE_FAILED or POST replay, failed recovery stays UNAVAILABLE with GET retry only. Any create after reliable recovery requires explicit user action; T14 verifies the rendered path. Both-empty Target and all-empty Run cases show inline non-empty-after-trim feedback on every returned field, preserve input/accepted hierarchy, and permit correction/retry; the primary code never hides another field.
- [ ] All inlined hard rules remain true; no unaccepted data used for conclusions.
- [ ] `pnpm check:architecture` and relevant focused tests/typecheck pass. No dedicated lint command exists; do not invent lint/vet commands.
- [ ] Follow [AGENTS.md verification execution policy](../../../../AGENTS.md#verification-execution-policy) and [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff); report retained evidence and actual contract impact.
