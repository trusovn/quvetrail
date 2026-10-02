---
id: "T15"
title: "Extend the canonical persistence smoke to product restart recovery"
layer: "tests"
deps: ["T13", "T14"]
blocks: ["T16"]
acs: ["AC-18", "AC-19", "AC-19a", "AC-20"]
files_hint: ["scripts/check-workspace-persistence.sh", "scripts/verify.sh", "package.json", "tests/api/workspace-restart-fixtures.ts"]
owner: "<TBD lead>"
estimate: "6h"
context_budget: "M"
status: "todo"
---

# T15 — Extend the canonical persistence smoke to product restart recovery

## Place in the sequence

- **Blocked by:** T13 — Prove deployed API durability and error contracts; T14 — Prove progressive browser behavior and refresh recovery.
- **Blocks:** T16 — Document implemented workspace contracts and UI inventory. **Wave:** 10 (after the named prerequisites).
- **Lane:** own lane. No standalone compile-breaking interface task.

## Why (user story)

> **As a** QA engineer
> **I want** the complete Project, Environment, Verification Target, and optional Verification Run context restored after refresh or restart
> **So that** the same Evidence Status can be reproduced from the complete persisted hierarchy
>
> — `spec.md §4, US-08, verbatim` · full text: [spec.md](../spec.md)

Add a bounded product persistence smoke following the existing foundation restart precedent.

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

- `GET /api/v1/workspace` — no request body; 200 {project:Project|null,environment:Environment|null,verification_target:VerificationTarget|null,verification_run:VerificationRun|null,evidence_status:null|NO_EVIDENCE|MATCH|MISMATCH}; Project:{id,name,created_at}; Environment:{id,project_id,name,created_at}; VerificationTarget:{id,environment_id,key,value,created_at}; VerificationRun:{id,verification_target_id,run_reference,created_at,observed_run_state:{id,verification_run_id,key,value,created_at}}; 503 workspace.unavailable, with no applicability conclusion.

— `contracts/openapi.yaml §paths / components.schemas, getWorkspace, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

All error responses use `{code,message,details?}`; `details.fields` identifies failed fields. Create bodies and success schemas reject additional properties. IDs are UUID strings and timestamps date-time strings.

— `contracts/openapi.yaml §components.schemas, Error / owned Create and record schemas, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

## Acceptance criteria

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

- [ ] Add a bounded product persistence smoke following the existing foundation restart precedent. (owned paths below).
- [ ] Use an isolated test hierarchy and record exact accepted IDs/values/status before and after API and normal Compose stop/start with retained storage; cover partial, target-without-run and both run outcomes. (owned paths below).
- [ ] Integrate it into pnpm verify, preserving diagnostics, nonzero failures and teardown. (owned paths below).
- [ ] Do not execute host reset or claim destructive-storage recovery. (owned paths below).
- [ ] Implement focused verification in the owned test paths; use the plan-tests allocation before execution.
- [ ] Keep changes within: `scripts/check-workspace-persistence.sh`, `scripts/verify.sh`, `package.json`, `tests/api/workspace-restart-fixtures.ts`.

## Edge cases

| Case | Behaviour |
|---|---|
| Target/run absent on successful authoritative read | Only accepted levels; no status before target; NO_EVIDENCE is workflow guidance when run absent. |
| Read failure or malformed/inconsistent accepted relationship | UNAVAILABLE explanation; no MATCH/MISMATCH or inferred recovery. |

— `spec.md §5, AC-18, AC-19, AC-19a, AC-20, abridged` · full text: [spec.md](../spec.md)
— `sad.md §6, Critical flow 2, abridged` · full text: [sad.md](../sad.md)

## Definition of Done

- [ ] Controlled restart checks pass with identical hierarchy/status and explicit failure on unavailable storage; pnpm verify invokes the new smoke and retains the existing foundation checks. Document that host-reset durability is provided by retained PostgreSQL storage, with no physical-reset test claimed.
- [ ] All inlined hard rules remain true; no unaccepted data used for conclusions.
- [ ] `pnpm check:architecture` and relevant focused tests/typecheck pass. No dedicated lint command exists; do not invent lint/vet commands.
- [ ] Follow [AGENTS.md verification execution policy](../../../../AGENTS.md#verification-execution-policy) and [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff); report retained evidence and actual contract impact.
