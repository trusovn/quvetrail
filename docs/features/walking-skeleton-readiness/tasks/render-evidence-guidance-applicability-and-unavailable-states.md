---
id: "T12"
title: "Render evidence guidance, applicability and unavailable states"
layer: "ui"
deps: ["T11"]
blocks: ["T14"]
acs: ["AC-09", "AC-10", "AC-11", "AC-14", "AC-15", "AC-18", "AC-19", "AC-20"]
files_hint: ["apps/web/src/EvidenceStatusPanel.tsx", "apps/web/src/App.tsx", "apps/web/src/styles.css", "apps/web/test/unit/evidence-presentation.spec.ts"]
owner: "<TBD lead>"
estimate: "5h"
context_budget: "M"
status: "todo"
---

# T12 — Render evidence guidance, applicability and unavailable states

## Place in the sequence

- **Blocked by:** T11 — Build the progressive hierarchy and record-entry workspace.
- **Blocks:** T14 — Prove progressive browser behavior and refresh recovery. **Wave:** 8 (after the named prerequisites).
- **Lane:** serialized overlapping paths with T11. No standalone compile-breaking interface task.

## Why (user story)

> **As a** QA engineer
> **I want** QuVeTrail to derive the Evidence Status from evidence availability and configuration applicability
> **So that** I can distinguish missing evidence, applicable evidence, mismatching evidence, and unavailable authoritative data
>
> — `spec.md §4, US-05, verbatim` · full text: [spec.md](../spec.md)

Create EvidenceStatusPanel because no existing primitive fits.

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

> U->>W: views Evidence Status
> W->>S: request current status
> S->>D: read the complete authoritative hierarchy
> D-->>S: accepted hierarchy
> D-->>S: read failure or malformed or inconsistent relationships
> S-->>W: Evidence Status UNAVAILABLE, no applicability conclusion
> W-->>U: show UNAVAILABLE and explain context cannot currently be relied upon
>
> — `sad.md §6, US-05, US-06, US-09 — View Evidence Status, abridged` · full text: [sad.md](../sad.md)

> **Chosen:** Option 1 — declare `target_surfaces: ["backend-service", "web-frontend"]`, written to `sad.md` frontmatter and one §5 C4 container per surface.
>
> — `adr/0001-target-surfaces-backend-service-web-frontend.md §Decision outcome, ADR-0001, abridged` · full text: [0001-target-surfaces-backend-service-web-frontend.md](../adr/0001-target-surfaces-backend-service-web-frontend.md)

> **Chosen:** Option 1 — a pure function in `apps/api/src/domain/` derives Evidence Status from the readable hierarchy on each read.
>
> — `adr/0003-derive-evidence-status-at-read-time.md §Decision outcome, ADR-0003, abridged` · full text: [0003-derive-evidence-status-at-read-time.md](../adr/0003-derive-evidence-status-at-read-time.md)

> **Chosen:** Option 1 — a client-rendered SPA whose authoritative state is fetched from and re-derived by the server on load/refresh/restart.
>
> — `adr/0004-spa-server-authoritative-state.md §Decision outcome, ADR-0004, abridged` · full text: [0004-spa-server-authoritative-state.md](../adr/0004-spa-server-authoritative-state.md)

> | error — unavailable | `getWorkspace` transport failure or 503 `workspace.unavailable` — an authoritative record cannot be read reliably or accepted relationships are malformed / inconsistent (AC-20, sad.md §6 Critical flow 2 `else` branch): `UNAVAILABLE` with the cannot-currently-be-relied-upon explanation, no MATCH/MISMATCH, no hierarchy conclusion | NEW: EvidenceStatusPanel (unavailable presentation) | wireframe W7 |
> | guidance (NO_EVIDENCE) | `getWorkspace` 200 with a Verification Target accepted and `evidence_status: "NO_EVIDENCE"` (AC-09, AC-19): the domain value is rendered as workflow guidance — a Verification Run has not been recorded yet — plus the run-entry action; never as an assessment result beside MATCH/MISMATCH | NEW: EvidenceStatusPanel (guidance presentation) | wireframe W9 |
> | evidence — MATCH | A Verification Run is accepted with exact trimmed key-and-value equality (201 `evidence_status: "MATCH"`, AC-10) or restored after refresh / restart (`getWorkspace` `MATCH`, AC-14, AC-18): status shown with the applicability-only explanation (AC-15) | NEW: EvidenceStatusPanel (result presentation) | wireframe W10 |
> | evidence — MISMATCH | A Verification Run is accepted with any key or value difference (201 `MISMATCH`, AC-11) or restored (`getWorkspace` `MISMATCH`, AC-14, AC-18): same result presentation with the applicability-only explanation (AC-15) | NEW: EvidenceStatusPanel (result presentation) | wireframe W10 |
>
> — `screens.md §Screens, SCR-01 guidance (NO_EVIDENCE), evidence — MATCH, evidence — MISMATCH, error — unavailable, verbatim` · full text: [screens.md](../screens.md)

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

- `GET /api/v1/workspace` — no request body; 200 {project:Project|null,environment:Environment|null,verification_target:VerificationTarget|null,verification_run:VerificationRun|null,evidence_status:null|NO_EVIDENCE|MATCH|MISMATCH}; Project:{id,name,created_at}; Environment:{id,project_id,name,created_at}; VerificationTarget:{id,environment_id,key,value,created_at}; VerificationRun:{id,verification_target_id,run_reference,created_at,observed_run_state:{id,verification_run_id,key,value,created_at}}; 503 workspace.unavailable, with no applicability conclusion.

— `contracts/openapi.yaml §paths / components.schemas, getWorkspace, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

- Accepted Run presentation context: `POST /api/v1/verification-runs` returns 201 {outcome:SAVED,evidence_status:MATCH|MISMATCH,record:{id,verification_target_id,run_reference,created_at,observed_run_state:{id,verification_run_id,key,value,created_at}}}. T12 presents the accepted status through T11's workspace state; T10/T11/T14 own save-outcome handling and recovery.

— `contracts/openapi.yaml §paths / components.schemas, createVerificationRun, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

## Acceptance criteria

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

### AC-20 — contribution verified by this task

> **Given** any authoritative persisted record required to restore the current Project → Environment → Verification Target → optional Verification Run and Observed Run State hierarchy cannot be read reliably
> **When** QuVeTrail attempts recovery or status derivation
> **Then** an explicit read failure or malformed or inconsistent accepted relationships produce Evidence Status `UNAVAILABLE`, no `MATCH` or `MISMATCH` applicability conclusion, and an explanation that the evidence context cannot currently be relied upon; a successful read with no accepted Verification Run follows AC-09 instead
>
> — `spec.md §5, AC-20, verbatim` · full text: [spec.md](../spec.md)

## Checklist

- [ ] Create EvidenceStatusPanel because no existing primitive fits. (owned paths below).
- [ ] Reuse T11 hierarchy/outcome components, global CSS and text/aria-live feedback. (owned paths below).
- [ ] Present server status without deriving business rules: hide before Target, guidance plus run action for NO_EVIDENCE, applicability-only explanations for MATCH/MISMATCH, and UNAVAILABLE explanation without a hierarchy/status conclusion after unreliable reads. (owned paths below).
- [ ] Implement focused verification in the owned test paths; use the plan-tests allocation before execution.
- [ ] Keep changes within: `apps/web/src/EvidenceStatusPanel.tsx`, `apps/web/src/App.tsx`, `apps/web/src/styles.css`, `apps/web/test/unit/evidence-presentation.spec.ts`.

## Edge cases

| Case | Behaviour |
|---|---|
| Target/run absent on successful authoritative read | Only accepted levels; no status before target; NO_EVIDENCE is workflow guidance when run absent. |
| Read failure or malformed/inconsistent accepted relationship | UNAVAILABLE explanation; no MATCH/MISMATCH or inferred recovery. |
| Key/value/case mismatch | MISMATCH; exact trimmed equality alone yields MATCH, applicability only. |

— `spec.md §5, AC-09, AC-10, AC-11, AC-14, AC-15, AC-18, AC-19, AC-20, abridged` · full text: [spec.md](../spec.md)
— `sad.md §6, US-05, US-06, US-09 — View Evidence Status, abridged` · full text: [sad.md](../sad.md)

## Definition of Done

- [ ] Presentation tests cover SCR-01 guidance and both results, hidden pre-target status, and unavailable state without stale MATCH/MISMATCH; no text treats evidence status as outcome or Readiness.
- [ ] All inlined hard rules remain true; no unaccepted data used for conclusions.
- [ ] `pnpm check:architecture` and relevant focused tests/typecheck pass. No dedicated lint command exists; do not invent lint/vet commands.
- [ ] Follow [AGENTS.md verification execution policy](../../../../AGENTS.md#verification-execution-policy) and [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff); report retained evidence and actual contract impact.
