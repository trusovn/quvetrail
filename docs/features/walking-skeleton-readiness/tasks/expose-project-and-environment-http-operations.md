---
id: "T7"
title: "Expose Project and Environment HTTP operations"
layer: "ports"
deps: ["T4"]
blocks: ["T8", "T9"]
acs: ["AC-01", "AC-02", "AC-03", "AC-04", "AC-05", "AC-16", "AC-16a", "AC-17"]
files_hint: ["apps/api/src/ports/http/context-routes.ts", "apps/api/src/ports/http/request-policy.ts", "apps/api/test/unit/context-routes.spec.ts", "apps/api/test/unit/request-policy.spec.ts"]
owner: "<TBD lead>"
estimate: "6h"
context_budget: "M"
status: "todo"
---

# T7 — Expose Project and Environment HTTP operations

## Place in the sequence

- **Blocked by:** T4 — Implement Project and Environment acceptance use cases.
- **Blocks:** T8 — Expose Target and Run HTTP operations; T9 — Wire the workspace API and persistence into the existing server. **Wave:** 4 (after the named prerequisites).
- **Lane:** own lane. No standalone compile-breaking interface task.

## Why (user story)

> **As a** QA engineer
> **I want** to create the current Project
> **So that** verification information belongs to the product or system being assessed
>
> — `spec.md §4, US-01, verbatim` · full text: [spec.md](../spec.md)

Add a Fastify route-registration function and strict Zod DTOs for Project/Environment bodies.

## Shared HTTP policy ownership

T7 is the sole owner of `apps/api/src/ports/http/request-policy.ts` and `apps/api/test/unit/request-policy.spec.ts`. Establish the small helper with its first real consumer here; T8 consumes it read-only. No shared transport policy exists in the current health-only app. Keep Project/Environment DTO definitions and operation-specific validation/prerequisite/save-outcome mappings in `context-routes.ts`; routes use injected application use cases, never persistence infrastructure.

The helper owns strict body validation and structural error normalization: no coercion or stripping; missing/wrong-type/unexpected fields, including nested paths; HTTP 400 `request.invalid_body` with a readable message and typed non-empty `details.fields`; full rejected-key paths for unexpected properties; sorted/deduplicated paths; and body-level `$` for absent body, malformed JSON and non-object roots. Empty-after-trim errors still use operation-specific domain codes. Do not add a schema registry, generic validation framework or future API policy.

Export the reusable scoped Fastify error handler from the same helper so JSON-parser errors before route handlers use this policy too. Context/evidence registrations each install it inside their own encapsulated Fastify registration scope before POST routes; no root/global handler, alternate normalization, or framework-default Fastify/Zod body for these structural failures. The policy is identical in both scopes, not duplicated. T9 mounts these registrations without implementing policy in `app.ts`.

Test the helper with a test-local nested DTO and isolated injected Fastify registration (no T8 feature implementation). Prove missing/wrong-type/unexpected fields, nested full paths, multiple paths sorted/deduplicated, absent/empty/malformed/non-object bodies mapped to `$`, and zero use-case calls. Context tests also prove real registration uses this helper, preserves feature-specific errors and does not leak the scoped handler to a sibling health route.

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

> U->>W: submits Project name
> W->>S: send Project name
> S->>S: trim value, preserve remaining characters, reject if empty
> S->>D: accept Project in one transaction
> else name empty after trimming
> S-->>W: VALIDATION_ERROR
> W-->>U: show VALIDATION_ERROR and allow retry
>
> — `sad.md §6, US-01 — Create Project, abridged` · full text: [sad.md](../sad.md)

> U->>W: chooses Environment action
> W->>S: send Environment name
> S->>S: read current Project context, trim value, reject if empty
> S->>D: accept Environment in one transaction within the Project
> else no Project accepted
> S-->>W: prerequisite missing, Environment requires a Project context
> W-->>U: keep action unavailable and explain prerequisite
>
> — `sad.md §6, US-02 — Create Environment, abridged` · full text: [sad.md](../sad.md)

> **Chosen:** Option 1 — declare `target_surfaces: ["backend-service", "web-frontend"]`, written to `sad.md` frontmatter and one §5 C4 container per surface.
>
> — `adr/0001-target-surfaces-backend-service-web-frontend.md §Decision outcome, ADR-0001, abridged` · full text: [0001-target-surfaces-backend-service-web-frontend.md](../adr/0001-target-surfaces-backend-service-web-frontend.md)

> **Chosen:** Option 1 — a single request-scoped transaction per accept; `SAVED` is returned only after confirmed durable commit, `SAVE_FAILED` only after known non-acceptance, and unknown acceptance requires authoritative recovery.
>
> — `adr/0002-transactional-record-acceptance.md §Decision outcome, ADR-0002, abridged` · full text: [0002-transactional-record-acceptance.md](../adr/0002-transactional-record-acceptance.md)

**Fallback:** If a signed slice is insufficient, ambiguous or contradicts the code, read its linked source in full; the source wins. Do not invent missing requirements.

## Data delta

No DB changes.

## API contract

- `POST /api/v1/projects` — body {name:string}; 201 {outcome:SAVED, record:{id,name,created_at}}; 400 project.invalid_name (details.fields:[name]); 503 project.save_failed (known non-acceptance) / project.save_outcome_unknown (recover via GET).

— `contracts/openapi.yaml §paths / components.schemas, createProject, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

- `POST /api/v1/environments` — body {name:string}, current Project resolved server-side; 201 {outcome:SAVED, record:{id,project_id,name,created_at}}; 400 environment.invalid_name (details.fields:[name]); 409 environment.project_missing; 503 environment.save_failed (known non-acceptance) / environment.save_outcome_unknown (recover via GET).

— `contracts/openapi.yaml §paths / components.schemas, createEnvironment, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

General errors use `{code,message,details?}`. Every HTTP 400 uses `ValidationError`, requiring `details.fields` (a non-empty string array). Structural body failures use `request.invalid_body`; empty-after-trim failures retain operation-specific codes. Field paths and body-level `$` handling are defined in OpenAPI. Create bodies and success schemas reject additional properties. IDs are UUID strings and timestamps date-time strings.

— `contracts/openapi.yaml §components.schemas, Error / owned Create and record schemas, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

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

Apply the shared HTTP policy above before any use case/write. OpenAPI remains authoritative for `request.invalid_body`, typed `ValidationErrorDetails`, deterministic paths and body-level `$`; operation-specific empty-after-trim errors remain local.

## Save-outcome obligations

For each owned POST, map only known non-acceptance to 503 *.save_failed. Map the distinct unknown-acceptance result to 503 *.save_outcome_unknown in the existing Error envelope, with no SAVED, record or evidence_status. Do not catch arbitrary DB/use-case exceptions and label them save_failed. Injection tests distinguish both codes under the same status and prove unknown has no success payload or automatic replay. HTTP owns serialization, not transaction-evidence inference.

## Checklist

- [ ] Establish the shared request policy and its focused tests, then use it in encapsulated Project/Environment registration with route-local strict DTOs. (owned paths below).
- [ ] Map use-case results to the exact contract status, envelope and field details; test registration in an isolated injected Fastify instance without changing composition yet. (owned paths below).
- [ ] Implement focused verification in the owned test paths; use the plan-tests allocation before execution.
- [ ] Keep changes within: `apps/api/src/ports/http/context-routes.ts`, `apps/api/src/ports/http/request-policy.ts`, `apps/api/test/unit/context-routes.spec.ts`, `apps/api/test/unit/request-policy.spec.ts`.

## Edge cases

| Case | Behaviour |
|---|---|
| Empty after trim / case or internal whitespace differs | Reject empty inputs with field error and retry; preserve remaining characters and compare case-sensitively. |
| Missing accepted parent | Accept nothing, explain prerequisite, do not offer dependent creation. |
| Pending commit | No SAVED or status from the submitted record. |
| Known non-acceptance | SAVE_FAILED preserves prior rows/input and permits user-initiated POST retry. |
| Unknown acceptance / lost COMMIT acknowledgement | No SAVED or SAVE_FAILED; preserve uncertainty and recover authoritative workspace via GET before explicit continuation. |

— `spec.md §5, AC-01, AC-02, AC-03, AC-04, AC-05, AC-16, AC-17, abridged` · full text: [spec.md](../spec.md)
— `sad.md §6, US-01 — Create Project, US-02 — Create Environment, abridged` · full text: [sad.md](../sad.md)

## Definition of Done

- [ ] Fastify injection tests match both 201 record shapes, 400 field errors, Environment 409 prerequisite message, and both operation-specific 503 codes: save_failed only for known non-acceptance, save_outcome_unknown for unknown acceptance with no success record/status. Pending commit cannot emit 201. Missing/wrong-type/unexpected fields and invalid JSON return 400 request.invalid_body with deterministic typed details.fields and no writes/default framework payload. Shared request-policy tests prove nested/full rejected-key paths, sorting/deduplication, absent/malformed/non-object bodies mapped to $, and strict validation without coercion/stripping before any use-case call; encapsulated context registration installs the shared parser-error policy. Mixed structural-invalid and whitespace-only inputs return only request.invalid_body before any domain/use-case call.
- [ ] All inlined hard rules remain true; no unaccepted data used for conclusions.
- [ ] `pnpm check:architecture` and relevant focused tests/typecheck pass. No dedicated lint command exists; do not invent lint/vet commands.
- [ ] Follow [AGENTS.md verification execution policy](../../../../AGENTS.md#verification-execution-policy) and [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff); report retained evidence and actual contract impact.
