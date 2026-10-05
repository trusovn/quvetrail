---
id: "T9"
title: "Wire the workspace API and persistence into the existing server"
layer: "wiring"
deps: ["T6", "T7", "T8"]
blocks: ["T11", "T13"]
acs: ["AC-09", "AC-18", "AC-19", "AC-19a", "AC-20"]
files_hint: ["apps/api/src/ports/http/workspace-route.ts", "apps/api/src/app.ts", "apps/api/src/server.ts", "apps/api/test/unit/app.spec.ts", "apps/api/test/unit/workspace-route.spec.ts"]
owner: "<TBD lead>"
estimate: "5h"
context_budget: "M"
status: "todo"
---

# T9 — Wire the workspace API and persistence into the existing server

## Place in the sequence

- **Blocked by:** T6 — Implement authoritative workspace loading and recovery states; T7 — Expose Project and Environment HTTP operations; T8 — Expose Target and Run HTTP operations.
- **Blocks:** T11 — Build the progressive hierarchy and record-entry workspace; T13 — Prove deployed API durability and error contracts. **Wave:** 6 (after the named prerequisites).
- **Lane:** own lane. No standalone compile-breaking interface task.

## Why (user story)

> **As a** QA engineer
> **I want** the complete Project, Environment, Verification Target, and optional Verification Run context restored after refresh or restart
> **So that** the same Evidence Status can be reproduced from the complete persisted hierarchy
>
> — `spec.md §4, US-08, verbatim` · full text: [spec.md](../spec.md)

Add GET workspace registration and connect all use cases/routes through existing buildApp injection and the server persistence boundary.

## Composition and shared-policy handoff

`server.ts` is the only concrete product-repository binding: use the existing `createDatabase` connection to construct T3's `infra/workspace-repository.ts` adapter, then pass it into `buildApp` through the application-facing `app/workspace-repository.ts` contract. `app.ts` composes use cases and transport around injected capabilities and imports no concrete product adapter; do not change `database.ts` or add a DI framework. The T3 contract/implementation and T4/T5/T6 use-case files are read-only here; return a missing capability to the owning task's scope before proceeding.

Mount the encapsulated context/evidence registrations from T7/T8. They install the same T7 `ports/http/request-policy.ts` helper in their route scopes; consume all three files read-only. Do not recreate normalization or install a competing root error handler. Preserve CORS, `/health`, and pool shutdown. App injection tests must exercise structural validation and malformed/absent JSON-body failures on all four mounted POSTs, including nested Run paths, deterministic details, and zero use-case calls; retain existing health behavior. This catches policy/wiring gaps that isolated route tests cannot prove.

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

> **Chosen:** Option 1 — declare `target_surfaces: ["backend-service", "web-frontend"]`, written to `sad.md` frontmatter and one §5 C4 container per surface.
>
> — `adr/0001-target-surfaces-backend-service-web-frontend.md §Decision outcome, ADR-0001, abridged` · full text: [0001-target-surfaces-backend-service-web-frontend.md](../adr/0001-target-surfaces-backend-service-web-frontend.md)

> **Chosen:** Option 1 — a pure function in `apps/api/src/domain/` derives Evidence Status from the readable hierarchy on each read.
>
> — `adr/0003-derive-evidence-status-at-read-time.md §Decision outcome, ADR-0003, abridged` · full text: [0003-derive-evidence-status-at-read-time.md](../adr/0003-derive-evidence-status-at-read-time.md)

**Fallback:** If a signed slice is insufficient, ambiguous or contradicts the code, read its linked source in full; the source wins. Do not invent missing requirements.

## Data delta

No DB changes.

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

## Checklist

- [ ] Add GET workspace registration and connect all use cases/routes through existing buildApp injection and the server persistence boundary. (owned paths below).
- [ ] Inject the application-facing repository contract through AppDependencies and bind its concrete adapter only in server.ts; update all existing production/test callers so it commits green. (owned paths below).
- [ ] Mount both policy-bearing route registrations read-only and prove the T7 normalization remains scoped and consistent on all four POSTs. (owned paths below).
- [ ] Preserve health/CORS and pool shutdown behavior. (owned paths below).
- [ ] Implement focused verification in the owned test paths; use the plan-tests allocation before execution.
- [ ] Keep changes within: `apps/api/src/ports/http/workspace-route.ts`, `apps/api/src/app.ts`, `apps/api/src/server.ts`, `apps/api/test/unit/app.spec.ts`, `apps/api/test/unit/workspace-route.spec.ts`.

## Edge cases

| Case | Behaviour |
|---|---|
| Target/run absent on successful authoritative read | Only accepted levels; no status before target; NO_EVIDENCE is workflow guidance when run absent. |
| Read failure or malformed/inconsistent accepted relationship | UNAVAILABLE explanation; no MATCH/MISMATCH or inferred recovery. |

— `spec.md §5, AC-09, AC-18, AC-19, AC-19a, AC-20, abridged` · full text: [spec.md](../spec.md)
— `sad.md §6, Critical flow 2, abridged` · full text: [sad.md](../sad.md)

## Definition of Done

- [ ] App injection tests cover workspace 200 and 503 envelopes and all four mounted create routes; existing health/config tests, typecheck and architecture gate pass with updated callers. server.ts alone binds the concrete product adapter and injects its application contract; all four POSTs preserve the T7 scoped policy for structural and parser failures without changing health behavior.
- [ ] All inlined hard rules remain true; no unaccepted data used for conclusions.
- [ ] `pnpm check:architecture` and relevant focused tests/typecheck pass. No dedicated lint command exists; do not invent lint/vet commands.
- [ ] Follow [AGENTS.md verification execution policy](../../../../AGENTS.md#verification-execution-policy) and [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff); report retained evidence and actual contract impact.
