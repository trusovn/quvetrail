---
id: "T6"
title: "Implement authoritative workspace loading and recovery states"
layer: "app"
deps: ["T2", "T3"]
blocks: ["T9"]
acs: ["AC-09", "AC-14", "AC-15", "AC-18", "AC-19", "AC-19a", "AC-20"]
files_hint: ["apps/api/src/app/load-workspace.ts", "apps/api/test/unit/load-workspace.spec.ts"]
owner: "<TBD lead>"
estimate: "5h"
context_budget: "M"
status: "todo"
---

# T6 — Implement authoritative workspace loading and recovery states

## Place in the sequence

- **Blocked by:** T2 — Implement pure input and evidence-applicability rules; T3 — Implement transactional hierarchy persistence and reliable reads.
- **Blocks:** T9 — Wire the workspace API and persistence into the existing server. **Wave:** 3 (after the named prerequisites).
- **Lane:** own lane. No standalone compile-breaking interface task.

## Why (user story)

> **As a** QA engineer
> **I want** the complete Project, Environment, Verification Target, and optional Verification Run context restored after refresh or restart
> **So that** the same Evidence Status can be reproduced from the complete persisted hierarchy
>
> — `spec.md §4, US-08, verbatim` · full text: [spec.md](../spec.md)

Compose the consistent repository read and pure derivation.

Import T3's application-facing `apps/api/src/app/workspace-repository.ts` contract directly and inject it; focused tests use typed structural doubles. Do not import `infra/**`, concrete factories, database/schema types or transport, or edit the contract/adapter. Return any needed seam correction to T3's scope before proceeding. Domain derivation stays independent of this application contract.

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

> U->>W: opens the workspace
> W->>S: request current workspace
> S->>D: read the authoritative accepted hierarchy
> D-->>S: accepted hierarchy
> D-->>S: read failure or malformed or inconsistent relationships
> S-->>W: UNAVAILABLE, no applicability conclusion
> W-->>U: show UNAVAILABLE and explain context cannot currently be relied upon
>
> — `sad.md §6, US-08 — Recover partially accepted workspace, abridged` · full text: [sad.md](../sad.md)

> **Chosen:** Option 1 — a pure function in `apps/api/src/domain/` derives Evidence Status from the readable hierarchy on each read.
>
> — `adr/0003-derive-evidence-status-at-read-time.md §Decision outcome, ADR-0003, abridged` · full text: [0003-derive-evidence-status-at-read-time.md](../adr/0003-derive-evidence-status-at-read-time.md)

**Fallback:** If a signed slice is insufficient, ambiguous or contradicts the code, read its linked source in full; the source wins. Do not invent missing requirements.

## Data delta

No DB changes.

Load persisted records only through the injected application contract; schema/migrations and adapter source remain read-only T1/T3 outputs.

## API contract

- `GET /api/v1/workspace` — no request body; 200 {project:Project|null,environment:Environment|null,verification_target:VerificationTarget|null,verification_run:VerificationRun|null,evidence_status:null|NO_EVIDENCE|MATCH|MISMATCH}; Project:{id,name,created_at}; Environment:{id,project_id,name,created_at}; VerificationTarget:{id,environment_id,key,value,created_at}; VerificationRun:{id,verification_target_id,run_reference,created_at,observed_run_state:{id,verification_run_id,key,value,created_at}}; 503 workspace.unavailable, with no applicability conclusion.

— `contracts/openapi.yaml §paths / components.schemas, getWorkspace, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

General errors use `{code,message,details?}`. Every HTTP 400 uses `ValidationError`, requiring `details.fields` (a non-empty string array). Structural body failures use `request.invalid_body`; empty-after-trim failures retain operation-specific codes. Field paths and body-level `$` handling are defined in OpenAPI. Create bodies and success schemas reject additional properties. IDs are UUID strings and timestamps date-time strings.

— `contracts/openapi.yaml §components.schemas, Error / owned Create and record schemas, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

## Acceptance criteria

### AC-09 — contribution verified by this task

> **Given** the complete Project → Environment → Verification Target hierarchy is readable and no Verification Run has been recorded
> **When** the QA engineer views Evidence Status
> **Then** QuVeTrail derives domain Evidence Status `NO_EVIDENCE` but does not render it in the UI as an assessment result alongside `MATCH` and `MISMATCH`; instead, the UI explains that a Verification Run has not been recorded yet and offers the run-entry action
>
> — `spec.md §5, AC-09, verbatim` · full text: [spec.md](../spec.md)

### AC-14 — contribution verified by this task

> **Given** the complete persisted hierarchy and Verification Run context are readable
> **When** QuVeTrail derives Evidence Status
> **Then** it reports `MATCH` only when the accepted Verification Target key and value exactly equal the accepted Observed Run State key and value, and otherwise reports `MISMATCH`
>
> — `spec.md §5, AC-14, verbatim` · full text: [spec.md](../spec.md)

### AC-15 — contribution verified by this task

> **Given** QuVeTrail presents Evidence Status
> **When** the QA engineer reviews it
> **Then** `MATCH` or `MISMATCH` describes only evidence applicability, while no Evidence Status claims anything about test outcomes or release Readiness
>
> — `spec.md §5, AC-15, verbatim` · full text: [spec.md](../spec.md)

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

Use [data-model.md §Current hierarchy validity](../data-model.md#current-hierarchy-validity-ac-20) as the exact AC-20 predicate. Test empty/Project-only/Project+Environment/Target-without-Run as reliable; a full parent-linked chain with one state as complete; selected-parent mismatch, zero/multiple states for the selected Run, wrong-run returned state, and query failure as unreliable. Older branch rows alone remain reliable. Do not add persisted empty/untrimmed-string corruption detection.

## Checklist

- [ ] Consume T3's single coherent workspace view ([SAD §6](../sad.md#6-runtime-view)) and compose pure derivation from it; do not assemble separate level reads. (owned paths below).
- [ ] Return only accepted hierarchy levels; before a target return null status, and without a run return NO_EVIDENCE. (owned paths below).
- [ ] Map failed, malformed or inconsistent authoritative reads to explicit unavailable results without a guessed hierarchy. (owned paths below).
- [ ] Implement focused verification in the owned test paths; use the plan-tests allocation before execution.
- [ ] Keep changes within: `apps/api/src/app/load-workspace.ts`, `apps/api/test/unit/load-workspace.spec.ts`.

## Edge cases

| Case | Behaviour |
|---|---|
| Target/run absent on successful authoritative read | Only accepted levels; no status before target; NO_EVIDENCE is workflow guidance when run absent. |
| Read failure or malformed/inconsistent accepted relationship | UNAVAILABLE explanation; no MATCH/MISMATCH or inferred recovery. |
| Key/value/case mismatch | MISMATCH; exact trimmed equality alone yields MATCH, applicability only. |

— `spec.md §5, AC-09, AC-14, AC-15, AC-18, AC-19, AC-19a, AC-20, abridged` · full text: [spec.md](../spec.md)
— `sad.md §6, Critical flow 2, US-08 — Recover partially accepted workspace, abridged` · full text: [sad.md](../sad.md)

## Definition of Done

- [ ] Focused loader tests cover empty, both partial levels, target without run, full MATCH/MISMATCH, and failed/malformed/inconsistent reads; repeated loads of identical inputs produce identical status. Use the data-model AC-20 cases: selected-parent/wrong-run mismatch, zero/multiple states and query failure are unavailable; partial hierarchies and older branches remain valid. Repository doubles are typed against app/workspace-repository.ts; no infrastructure imports or contract edits.
- [ ] All inlined hard rules remain true; no unaccepted data used for conclusions.
- [ ] `pnpm check:architecture` and relevant focused tests/typecheck pass. No dedicated lint command exists; do not invent lint/vet commands.
- [ ] Follow [AGENTS.md verification execution policy](../../../../AGENTS.md#verification-execution-policy) and [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff); report retained evidence and actual contract impact.
