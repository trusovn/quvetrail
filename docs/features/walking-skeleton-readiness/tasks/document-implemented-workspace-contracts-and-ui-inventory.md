---
id: "T16"
title: "Document implemented workspace contracts and UI inventory"
layer: "docs"
deps: ["T15"]
blocks: []
acs: ["AC-15", "AC-18", "AC-20"]
files_hint: ["README.md", "docs/project-map.md", "docs/architecture-map.md", "docs/design-system.md", "docs/contracts/"]
owner: "<TBD lead>"
estimate: "4h"
context_budget: "M"
status: "todo"
---

# T16 — Document implemented workspace contracts and UI inventory

## Place in the sequence

- **Blocked by:** T15 — Extend the canonical persistence smoke to product restart recovery.
- **Blocks:** none. **Wave:** 11 (after the named prerequisites).
- **Lane:** own lane. No standalone compile-breaking interface task.

## Why (user story)

> **As a** QA engineer
> **I want** QuVeTrail to derive the Evidence Status from evidence availability and configuration applicability
> **So that** I can distinguish missing evidence, applicable evidence, mismatching evidence, and unavailable authoritative data
>
> — `spec.md §4, US-05, verbatim` · full text: [spec.md](../spec.md)

Reconcile the completed feature against subsystem records already synchronized at each task handoff; close omissions for implemented durable cross-task contracts and regenerate the index with pnpm check:contracts:index.

T16 is final reconciliation/documentation, not delayed first registration. Follow [AGENTS.md implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff): after each earlier implementation passes architecture/maintainability review, the updater synchronizes actual durable surfaces before acceptance. Keep planned contracts and private helpers absent. Registry/discovery edits belong to that updater stage, separately from the task implementer's production ownership.

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

> **Chosen:** Option 1 — a client-rendered SPA whose authoritative state is fetched from and re-derived by the server on load/refresh/restart.
>
> — `adr/0004-spa-server-authoritative-state.md §Decision outcome, ADR-0004, abridged` · full text: [0004-spa-server-authoritative-state.md](../adr/0004-spa-server-authoritative-state.md)

**Fallback:** If a signed slice is insufficient, ambiguous or contradicts the code, read its linked source in full; the source wins. Do not invent missing requirements.

## Data delta

No DB changes.

## API contract

Internal — no API surface.

## Acceptance criteria

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

### AC-20 — contribution verified by this task

> **Given** any authoritative persisted record required to restore the current Project → Environment → Verification Target → optional Verification Run and Observed Run State hierarchy cannot be read reliably
> **When** QuVeTrail attempts recovery or status derivation
> **Then** an explicit read failure or malformed or inconsistent accepted relationships produce Evidence Status `UNAVAILABLE`, no `MATCH` or `MISMATCH` applicability conclusion, and an explanation that the evidence context cannot currently be relied upon; a successful read with no accepted Verification Run follows AC-09 instead
>
> — `spec.md §5, AC-20, verbatim` · full text: [spec.md](../spec.md)

## Checklist

- [ ] Reconcile the completed feature against subsystem records already synchronized at each task handoff; close omissions for implemented durable cross-task contracts and regenerate the index with pnpm check:contracts:index. (owned paths below).
- [ ] Update setup/current-system descriptions to the product workspace and register the four implemented UI components with actual paths/states. (owned paths below).
- [ ] Keep future production NFRs and multiple-record scope explicit rather than marking them implemented. (owned paths below).
- [ ] Implement focused verification in the owned test paths; use the plan-tests allocation before execution.
- [ ] Keep changes within: `README.md`, `docs/project-map.md`, `docs/architecture-map.md`, `docs/design-system.md`, `docs/contracts/`.

## Edge cases

| Case | Behaviour |
|---|---|
| Read failure or malformed/inconsistent accepted relationship | UNAVAILABLE explanation; no MATCH/MISMATCH or inferred recovery. |
| Key/value/case mismatch | MISMATCH; exact trimmed equality alone yields MATCH, applicability only. |

— `spec.md §5, AC-15, AC-18, AC-20, abridged` · full text: [spec.md](../spec.md)
— `sad.md §6, Critical flow 2, abridged` · full text: [sad.md](../sad.md)

## Definition of Done

- [ ] pnpm check:contracts and pnpm check:architecture pass; every documented source path exists, inventory states match SCR-01 and recovery claims match T15 evidence without outcome/Readiness claims. Final reconciliation confirms earlier per-task registry synchronization, durable implemented cross-task surfaces only, and no planned/private-helper entries.
- [ ] All inlined hard rules remain true; no unaccepted data used for conclusions.
- [ ] `pnpm check:architecture` and relevant focused tests/typecheck pass. No dedicated lint command exists; do not invent lint/vet commands.
- [ ] Follow [AGENTS.md verification execution policy](../../../../AGENTS.md#verification-execution-policy) and [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff); report retained evidence and actual contract impact.
