---
status: Draft
owner: "Product Owner"
reviewers: ["Tech Lead", "Security Lead"]
updated_at: "2026-10-05"
feature_size: "M"
---

# Spec — walking-skeleton-readiness

> **Glossary:** [CONTEXT](./CONTEXT.md)
> **Reference module / docs / channels used:** `README.md`; `docs/project-map.md`; `docs/architecture-map.md`; `docs/direction-quvetrail.md`; `docs/project-charter.md`; `docs/foundation-plan.md`; `docs/planning/QuVeTrail_Product_Vision.md`; `docs/planning/walking-skeleton.md`; `docs/planning/QuVeTrail_Walking_Skeleton_Plan.md`
> **Discovery:** Not triggered — this controlled informational skeleton has no regulatory, specialized-domain, or current-authoritative dependency.

## 1. Context

A QA engineer needs to know whether recorded verification evidence applies to the exact Environment configuration that requires evidence. A successful or otherwise completed external run against a different configuration cannot establish applicability for the Verification Target, and test-run outcome is a separate semantic dimension.

The repository now has a working end-to-end technical foundation, so the next proof is the smallest real product flow across the intended boundaries. The Walking Skeleton must establish a durable target-to-run-context relationship and trustworthy recovery before broader MVP behavior is planned.

The Walking Skeleton uses a progressive evidence-applicability workspace that exposes the persisted hierarchy, external-run context, operation outcomes, and current Evidence Status.

For this slice, refresh or restart includes browser refresh and application, process, container, or operating-system restart or crash, including a host hardware reset, provided the durable storage remains available and uncorrupted. Recovery from deleted, lost, or corrupted storage is outside this boundary.

The governing distinction is between the Verification Target—the configuration context for which evidence is required—and the Observed Run State—the configuration an external Verification Run actually exercised. The target is a comparison context, not a desired-state or deployment-management instruction. `MATCH` therefore means only that recorded evidence applies to the target; it does not describe the test outcome or imply Readiness.

- **Decision override: Evidence applicability replaces binary Readiness as the Walking Skeleton proof.** Owner-approved on 2026-10-03 because test outcome and evidence applicability are independent; this slice derives Evidence Status while deferring test outcomes and Readiness.
- **Decision override: Explicit target and run-context concepts supersede the generic state/result model.** Owner-approved on 2026-10-03 because the persisted comparison between required configuration and observed run configuration is the seam this skeleton must prove; record counts remain narrow and broader capabilities stay deferred.

## 2. Goals

- Establish a complete persisted hierarchy from Project and Environment through Verification Target and optional Verification Run context.
- Derive an explainable Evidence Status that distinguishes missing evidence, matching context, mismatching context, and unavailable authoritative data without evaluating test outcomes.
- Preserve accepted data across failed saves, refresh, and restart so the same readable hierarchy produces the same Evidence Status.

## 3. Non-goals

- Test execution, test-run outcome capture, and selection of required tests are excluded because this slice proves evidence applicability rather than verification semantics.
- Readiness policies, release approval, release triggering, and release enforcement are excluded because `MATCH` alone cannot establish release readiness.
- Environment discovery, deployment management, change tracking, multiple verification requirements, and configurable comparison or readiness rules are deferred to later product slices.
- Multiple-record selection plus editing, deletion, and history are not implemented; the one-record Walking Skeleton restriction is temporary scope, not a singleton or immutability rule for the product model.
- Authentication, permissions, advanced multi-user behavior, external evidence integrations, and production assurance are deferred because the slice assumes one trusted QA engineer in a controlled installation.

## 4. User stories

### US-01: Create Project

**As a** QA engineer
**I want** to create the current Project
**So that** verification information belongs to the product or system being assessed

### US-02: Create Environment

**As a** QA engineer
**I want** to create an Environment within the Project
**So that** verification applicability has a specific deployed target

### US-03: Define Verification Target

**As a** QA engineer
**I want** to define the Environment configuration context for which evidence is required
**So that** QuVeTrail has an exact comparison target without treating it as an instruction to change the Environment

### US-04: Record external Verification Run

**As a** QA engineer
**I want** to record an external Verification Run and its Observed Run State
**So that** QuVeTrail retains what was verified and the configuration the run actually exercised

### US-05: Understand Evidence Status

**As a** QA engineer
**I want** QuVeTrail to derive the Evidence Status from evidence availability and configuration applicability
**So that** I can distinguish missing evidence, applicable evidence, mismatching evidence, and unavailable authoritative data

### US-06: Recognize missing evidence

**As a** QA engineer
**I want** the absence of a recorded Verification Run shown explicitly
**So that** missing evidence is not mistaken for matching or mismatching evidence

### US-07: Retry unsuccessful saves

**As a** QA engineer
**I want** an unsuccessful save to preserve previously accepted data
**So that** I can retry without corrupting the verification context

### US-08: Recover persisted evidence context

**As a** QA engineer
**I want** the complete Project, Environment, Verification Target, and optional Verification Run context restored after refresh or restart
**So that** the same Evidence Status can be reproduced from the complete persisted hierarchy

### US-09: Recognize unavailable evidence status

**As a** QA engineer
**I want** unreadable authoritative data reported as `UNAVAILABLE`
**So that** I do not mistake incomplete recovery for a trustworthy applicability conclusion

## 5. Acceptance criteria

### AC-01 (US-01) — happy

**Given** no Project has been recorded
**When** the QA engineer submits a Project name that is non-empty after trimming
**Then** QuVeTrail durably records the Project and shows `SAVED`

### AC-02 (US-01) — error

**Given** no Project has been recorded
**When** the QA engineer submits a Project name that is empty after trimming
**Then** QuVeTrail shows `VALIDATION_ERROR`, records no Project, and allows retry

### AC-03 (US-02) — happy

**Given** the current Project exists
**When** the QA engineer submits an Environment name that is non-empty after trimming
**Then** QuVeTrail durably records the Environment within that Project and shows `SAVED`

### AC-04 (US-02) — cross-context

**Given** no Project exists
**When** the QA engineer attempts to record an Environment
**Then** QuVeTrail accepts nothing and explains that an Environment requires a Project context

### AC-05 (US-02) — error

**Given** the current Project exists
**When** the QA engineer submits an Environment name that is empty after trimming
**Then** QuVeTrail shows `VALIDATION_ERROR`, records no Environment, and allows retry

### AC-06 (US-03) — happy

**Given** the current Environment exists
**When** the QA engineer submits a Verification Target key and value that are both non-empty after trimming
**Then** QuVeTrail durably records them as the configuration comparison context and shows `SAVED`

### AC-07 (US-03) — cross-context

**Given** no Environment exists
**When** the QA engineer attempts to define a Verification Target
**Then** QuVeTrail accepts nothing and explains that a Verification Target requires an Environment

### AC-08 (US-03) — error

**Given** no Verification Target has been recorded
**When** the QA engineer submits a target key or value that is empty after trimming
**Then** QuVeTrail shows `VALIDATION_ERROR`, records no Verification Target, and allows retry

### AC-09 (US-06) — happy

**Given** the complete Project → Environment → Verification Target hierarchy is readable and no Verification Run has been recorded
**When** the QA engineer views Evidence Status
**Then** QuVeTrail derives domain Evidence Status `NO_EVIDENCE` but does not render it in the UI as an assessment result alongside `MATCH` and `MISMATCH`; instead, the UI explains that a Verification Run has not been recorded yet and offers the run-entry action

### AC-10 (US-04, US-05) — happy

**Given** a readable Verification Target exists and no Verification Run has been recorded
**When** the QA engineer submits a non-empty run reference and a non-empty Observed Run State whose key and value exactly equal the Verification Target key and value
**Then** QuVeTrail durably records the Verification Run and its Observed Run State, shows `SAVED`, and derives Evidence Status `MATCH`

### AC-11 (US-04, US-05) — happy

**Given** a readable Verification Target exists and no Verification Run has been recorded
**When** the QA engineer submits a non-empty run reference and a non-empty Observed Run State whose key or value differs from the Verification Target
**Then** QuVeTrail durably records the Verification Run and its Observed Run State, shows `SAVED`, and derives Evidence Status `MISMATCH`

### AC-12 (US-04) — error

**Given** a Verification Target exists and no Verification Run has been recorded
**When** the submitted run reference, observed-state key, or observed-state value is empty after trimming
**Then** QuVeTrail shows `VALIDATION_ERROR`, records no Verification Run, and allows retry

### AC-13 (US-04) — cross-context

**Given** no Verification Target exists
**When** the QA engineer attempts to record a Verification Run
**Then** QuVeTrail accepts nothing and explains that a Verification Target must be defined first

### AC-14 (US-05) — domain invariant

**Given** the complete persisted hierarchy and Verification Run context are readable
**When** QuVeTrail derives Evidence Status
**Then** it reports `MATCH` only when the accepted Verification Target key and value exactly equal the accepted Observed Run State key and value, and otherwise reports `MISMATCH`

### AC-14a (US-01, US-02, US-03, US-04, US-05) — domain invariant

**Given** the QA engineer submits a textual value that is accepted
**When** QuVeTrail records or compares that value
**Then** it removes leading and trailing whitespace before recording, preserves every remaining character without further normalization, and compares Verification Target and Observed Run State keys and values case-sensitively

### AC-15 (US-05) — domain invariant

**Given** QuVeTrail presents Evidence Status
**When** the QA engineer reviews it
**Then** `MATCH` or `MISMATCH` describes only evidence applicability, while no Evidence Status claims anything about test outcomes or release Readiness

### AC-16 (US-07) — error

**Given** previously accepted Walking Skeleton data exists
**When** saving the next valid record fails and non-acceptance is known (COMMIT was not dispatched and cannot follow, or rollback/non-commit of that transaction is confirmed)
**Then** QuVeTrail shows `SAVE_FAILED`, accepts none of that attempted record, preserves all previously accepted data, and allows retry

### AC-16a (US-07, US-08) — unknown acceptance

**Given** the QA engineer has submitted a valid record
**When** acceptance cannot be established, including loss of the API's PostgreSQL COMMIT acknowledgement or loss of the POST response
**Then** QuVeTrail claims neither `SAVED` nor retry-safe `SAVE_FAILED`, explains that the save outcome could not be confirmed, blocks creates, and reloads the authoritative workspace before continuing; reliable recovery replaces the displayed hierarchy without replaying the POST or inventing a `SAVED` outcome for that attempt, while failed recovery shows `UNAVAILABLE` and allows GET retry only

Recovery establishes the current accepted hierarchy, not the historical outcome of the uncertain attempt. A successful GET showing absence is not proof of rollback, particularly while the original transaction may still be completing. After recovery, the QA engineer may explicitly submit a new create from the recovered context; this is not a guaranteed duplicate-free retry. Repeated creates remain allowed and this slice adds no idempotency mechanism.

### AC-17 (US-07) — domain invariant

**Given** the QA engineer has submitted a valid record
**When** durable acceptance is not known
**Then** QuVeTrail does not show `SAVED` or derive Evidence Status using the submitted record; a reliable authoritative recovery may subsequently show persisted records and derive status from them without claiming `SAVED` for the uncertain attempt

### AC-17a (US-02, US-03, US-04) — cross-context

**Given** the parent record required for the next hierarchy level has not been accepted
**When** the QA engineer views the progressive workspace
**Then** QuVeTrail does not offer the action for creating that dependent record

### AC-18 (US-08) — cross-context

**Given** a Project, Environment, Verification Target, Verification Run, and Observed Run State have been accepted
**When** QuVeTrail is refreshed or restarted
**Then** it restores the complete Project → Environment → Verification Target → Verification Run and Observed Run State hierarchy and derives the same `MATCH` or `MISMATCH` Evidence Status

### AC-19 (US-06, US-08) — cross-context

**Given** a Project, Environment, and Verification Target exist without a Verification Run
**When** QuVeTrail is refreshed or restarted
**Then** it restores the complete persisted Project → Environment → Verification Target hierarchy, preserves the absence of a Verification Run, derives domain Evidence Status `NO_EVIDENCE`, and shows workflow guidance that a Verification Run has not been recorded yet with the run-entry action instead of rendering `NO_EVIDENCE` as an assessment result

### AC-19a (US-08) — cross-context

**Given** only a Project, or only a Project and Environment, have been accepted
**When** QuVeTrail is refreshed or restarted within the recovery boundary defined in §1
**Then** it restores and shows only the accepted hierarchy levels, shows no unaccepted dependent record, and presents no Evidence Status until a Verification Target has been accepted

### AC-20 (US-09) — error

**Given** any authoritative persisted record required to restore the current Project → Environment → Verification Target → optional Verification Run and Observed Run State hierarchy cannot be read reliably
**When** QuVeTrail attempts recovery or status derivation
**Then** an explicit read failure or malformed or inconsistent accepted relationships produce Evidence Status `UNAVAILABLE`, no `MATCH` or `MISMATCH` applicability conclusion, and an explanation that the evidence context cannot currently be relied upon; a successful read with no accepted Verification Run follows AC-09 instead

**Authorization: N/A — the Walking Skeleton assumes one trusted QA engineer in a controlled installation and explicitly defers authentication, roles, and permissions (source: `docs/direction-quvetrail.md` § Scope and § Boundaries; `docs/project-charter.md` § Non-goals).**

### Validation feedback (AC-02 / AC-05 / AC-08 / AC-12)

Structural body validation runs first and uses `request.invalid_body`; do not mix structural failures with domain empty-after-trim failures. For a structurally valid request, evaluate every accepted-text input and report all fields empty after trimming in one `VALIDATION_ERROR`, accepting nothing. Use a fixed code precedence: Project/Environment `name`; Target `key` then `value`; Run `run_reference` then `observed_run_state.key` then `observed_run_state.value`. The first failing field in that order supplies its existing operation-specific code; `details.fields` contains all failing paths sorted and deduplicated, independently of code precedence. JSON property order must not affect the result. The UI marks every known path inline with a non-empty-after-trim explanation, preserving input for retry; the primary code must not limit feedback to one field or apply a field-specific primary message to another field.

### Current workspace selection

Repeated creates are allowed by this slice's HTTP contract. “Current” means the accepted, visible row with the greatest UUID (`ORDER BY id DESC LIMIT 1`): select the Project first, then each child within its selected parent, as defined in [data-model.md](./data-model.md#current-hierarchy-validity-ac-20). This deterministic selection is not a promise of exact acceptance/commit chronology; UUID v7 generation order, same-millisecond values and clock skew can differ from commit order. Refresh/recovery uses the same selection rule. No chronology column or ID-strategy change is required for this slice.

## 6. Non-functional requirements

**Measurement: N/A — Production performance, availability, and capacity targets are not meaningful for this controlled Walking Skeleton before a deployment model and expected workload exist. Functional correctness, durability, and recovery remain acceptance criteria rather than NFR measurements. (source: `docs/project-charter.md` § Mission, § Hard constraints, and § Foundation-bearing unknowns)**

## 6.1 Security / privacy

- **Data classification:** Context-dependent technical metadata; no universal classification is assigned by this slice. The QA engineer is instructed not to enter passwords, tokens, or other secrets in Project, Environment, target, run, or observed-state fields. QuVeTrail does not detect, classify, warn about, or reject suspected secret content in this controlled slice.
- **Personal data touched:** None intended. The fields are intended for technical names, references, and configuration context.
- **Authentication and authorization:** Out of scope. The Walking Skeleton assumes one trusted QA engineer in a controlled installation.
- **Limited trust-boundary behavior:**
  - Invalid or failed submissions do not alter previously accepted data.
  - Missing hierarchy prerequisites prevent dependent records from being accepted.
  - Unreadable authoritative data produces `UNAVAILABLE`, not an inferred applicability conclusion.
  - External-run details are trusted user assertions; QuVeTrail does not authenticate or independently prove them.
- **Security review scope:** Limited to confirming that the slice introduces no secret-bearing fields, authentication boundary, external integration, or release-control behavior. Production threat modeling and security assurance are deferred.

## 7. Metrics / KPIs

**Measurement: N/A — This Walking Skeleton is a framework proof before MVP, so product-outcome measurement is not yet meaningful; fabricated exit counts would measure test execution rather than product adoption or value. (source: `docs/direction-quvetrail.md` § Direction ledger; `docs/project-charter.md` § Mission and § Non-goals)**

## 8. Open questions

- [ ] What production performance, availability, and capacity targets apply? Default now: none for the controlled Walking Skeleton. — owner: Tech Lead, due: before production deployment planning
- [ ] Which product-outcome KPIs should govern the first MVP slice? Default now: none for the Walking Skeleton framework proof. — owner: Product Owner, due: before specifying the first MVP slice
