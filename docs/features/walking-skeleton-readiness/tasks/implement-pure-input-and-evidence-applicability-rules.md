---
id: "T2"
title: "Implement pure input and evidence-applicability rules"
layer: "domain"
deps: []
blocks: ["T3", "T4", "T6"]
acs: ["AC-09", "AC-14", "AC-14a", "AC-15", "AC-20"]
files_hint: ["apps/api/src/domain/", "apps/api/test/unit/evidence-status.spec.ts"]
owner: "<TBD lead>"
estimate: "4h"
context_budget: "M"
status: "todo"
---

# T2 — Implement pure input and evidence-applicability rules

## Place in the sequence

- **Blocked by:** none.
- **Blocks:** T3 — Implement transactional hierarchy persistence and reliable reads; T4 — Implement Project and Environment acceptance use cases; T6 — Implement authoritative workspace loading and recovery states. **Wave:** 1 (after the named prerequisites).
- **Lane:** own lane. No standalone compile-breaking interface task.

## Why (user story)

> **As a** QA engineer
> **I want** QuVeTrail to derive the Evidence Status from evidence availability and configuration applicability
> **So that** I can distinguish missing evidence, applicable evidence, mismatching evidence, and unavailable authoritative data
>
> — `spec.md §4, US-05, verbatim` · full text: [spec.md](../spec.md)

Implement typed hierarchy inputs, trim/non-empty validation and case-sensitive key/value comparison without I/O.

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

> **Chosen:** Option 1 — a pure function in `apps/api/src/domain/` derives Evidence Status from the readable hierarchy on each read.
>
> — `adr/0003-derive-evidence-status-at-read-time.md §Decision outcome, ADR-0003, abridged` · full text: [0003-derive-evidence-status-at-read-time.md](../adr/0003-derive-evidence-status-at-read-time.md)

**Fallback:** If a signed slice is insufficient, ambiguous or contradicts the code, read its linked source in full; the source wins. Do not invent missing requirements.

## Data delta

No DB changes.

## API contract

Internal — no API surface.

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

### AC-14a — contribution verified by this task

> **Given** the QA engineer submits a textual value that is accepted
> **When** QuVeTrail records or compares that value
> **Then** it removes leading and trailing whitespace before recording, preserves every remaining character without further normalization, and compares Verification Target and Observed Run State keys and values case-sensitively
>
> — `spec.md §5, AC-14a, verbatim` · full text: [spec.md](../spec.md)

### AC-15 — contribution verified by this task

> **Given** QuVeTrail presents Evidence Status
> **When** the QA engineer reviews it
> **Then** `MATCH` or `MISMATCH` describes only evidence applicability, while no Evidence Status claims anything about test outcomes or release Readiness
>
> — `spec.md §5, AC-15, verbatim` · full text: [spec.md](../spec.md)

### AC-20 — contribution verified by this task

> **Given** any authoritative persisted record required to restore the current Project → Environment → Verification Target → optional Verification Run and Observed Run State hierarchy cannot be read reliably
> **When** QuVeTrail attempts recovery or status derivation
> **Then** an explicit read failure or malformed or inconsistent accepted relationships produce Evidence Status `UNAVAILABLE`, no `MATCH` or `MISMATCH` applicability conclusion, and an explanation that the evidence context cannot currently be relied upon; a successful read with no accepted Verification Run follows AC-09 instead
>
> — `spec.md §5, AC-20, verbatim` · full text: [spec.md](../spec.md)

Use [data-model.md §Current hierarchy validity](../data-model.md#current-hierarchy-validity-ac-20) as the exact AC-20 predicate. Test empty/Project-only/Project+Environment/Target-without-Run as reliable; a full parent-linked chain with one state as complete; selected-parent mismatch, zero/multiple states for the selected Run, wrong-run returned state, and query failure as unreliable. Older branch rows alone remain reliable. Do not add persisted empty/untrimmed-string corruption detection.

Test each accepted-text input with empty and whitespace-only values plus valid trimmed content. Keep these rules pure; T5 owns operation-specific precedence and assembly of all failed fields, using this validation rather than an HTTP/DB-dependent rule.

## Checklist

- [ ] Implement typed hierarchy inputs, trim/non-empty validation and case-sensitive key/value comparison without I/O. (owned paths below).
- [ ] Distinguish absent target, absent run, complete run, and unreadable/inconsistent input. (owned paths below).
- [ ] Add deterministic factories only where tests need them. (owned paths below).
- [ ] Implement focused verification in the owned test paths; use the plan-tests allocation before execution.
- [ ] Keep changes within: `apps/api/src/domain/`, `apps/api/test/unit/evidence-status.spec.ts`.

## Edge cases

| Case | Behaviour |
|---|---|
| Empty after trim / case or internal whitespace differs | Reject empty inputs with field error and retry; preserve remaining characters and compare case-sensitively. |
| Target/run absent on successful authoritative read | Only accepted levels; no status before target; NO_EVIDENCE is workflow guidance when run absent. |
| Read failure or malformed/inconsistent accepted relationship | UNAVAILABLE explanation; no MATCH/MISMATCH or inferred recovery. |
| Key/value/case mismatch | MISMATCH; exact trimmed equality alone yields MATCH, applicability only. |

— `spec.md §5, AC-09, AC-14, AC-14a, AC-15, AC-20, abridged` · full text: [spec.md](../spec.md)
— `sad.md §6, US-05, US-06, US-09 — View Evidence Status, abridged` · full text: [sad.md](../sad.md)

## Definition of Done

- [ ] Focused unit cases prove null before target, NO_EVIDENCE without run, exact equality only for MATCH, every key/value/case difference for MISMATCH, and UNAVAILABLE for unreliable context with no outcome/readiness fields. Unreliable context follows the bounded data-model AC-20 predicate, not persisted textual revalidation. Pure accepted-text cases cover empty/whitespace-only and valid trimmed text for every input; validation exposes each failure so T5 can collect simultaneous failures without I/O or a generic error framework.
- [ ] All inlined hard rules remain true; no unaccepted data used for conclusions.
- [ ] `pnpm check:architecture` and relevant focused tests/typecheck pass. No dedicated lint command exists; do not invent lint/vet commands.
- [ ] Follow [AGENTS.md verification execution policy](../../../../AGENTS.md#verification-execution-policy) and [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff); report retained evidence and actual contract impact.
