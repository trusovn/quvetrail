# API sync report — walking-skeleton-readiness

Written by the `api` stage (2026-10-05) alongside `contracts/openapi.yaml`. The contract is
derived, never hand-written: fields+constraints ← `data-model.md`; error responses ← `sad.md`
§6 alt-branches; endpoint list + shape ← `spec.md` §4/§5. This report is the bidirectional
drift check the skill defines (→ `api` references/drift-check.md) and doubles as this stage's
structural self-check.

**Inputs found:** `data-model.md` (present — derive from it, no fast-lane skip), `sad.md` §6
(8 sequence diagrams incl. 3 critical flows + 5 US flows, all synchronous), `spec.md` §4 (9
user stories) / §5 (AC-01…AC-20), `.size` = M, `.route` = standard, 5 Accepted ADRs, `CONTEXT.md`
glossary. **Interface kind:** `target_surfaces: ["backend-service", "web-frontend"]` (sad.md
frontmatter) → HTTP/OpenAPI contract; the web-frontend surface consumes it, it does not author one.

**Contract form decisions (3 flags, all resolved with the user before the contract was locked):**

1. **Duplicate-record behavior absent upstream.** The one-record restriction is workspace UI scope
   (SAD §11, CONTEXT.md Out of scope); no §6 flow and no AC defines what
   the API does when a record of a type is already durably accepted. **Resolution (user, 2026-10-05):
   no duplicate-forbidding in the contract** — "focus on the deps logic but don't explicitly forbid
   based on the limited scope of the skeleton". The contract therefore carries only the
   prerequisite-missing `409`s the sequences define; a repeated create follows the data model's
   existing "current record" semantics (`ORDER BY id DESC LIMIT 1`, data-model §`project` access
   patterns). No `already_exists` codes, no extra scope to reverse next iteration.
2. **UNAVAILABLE over HTTP.** AC-20 requires user-visible `UNAVAILABLE` with no applicability
   conclusion; SAD §8 left exact status codes to this stage. **Resolution (user, 2026-10-05):**
   `GET /api/v1/workspace` answers `503` + `{code: "workspace.unavailable", …}` on an unreliable
   authoritative read — matching the repo's existing 503-on-database-unavailability convention
   (`/health`, apps/api/src/app.ts). `UNAVAILABLE` is never a 200 payload: a knowingly incomplete
   read is not a workspace. The UI maps the 503 error envelope to the visible UNAVAILABLE state.
3. **Auth scaffold dropped.** spec §6.1 defers authentication (one trusted QA engineer,
   controlled installation); SAD §8 `Authentication: N/A`. **Resolution (user, 2026-10-05):** the
   contract declares **no security scheme at all** (no BearerAuth scaffold, no `security: []`
   overrides) so no consumer wires a token no code will check. Deviation from the scaffold default
   recorded here; revisit before production deployment planning (spec §8 OQ already carries the
   production-assurance revisit).

## Pre-implementation clarifications (2026-10-05)

- **AC-20 scope:** [data-model.md §Current hierarchy validity](../data-model.md#current-hierarchy-validity-ac-20) bounds the predicate to parent-scoped current selection and exactly one state for the current Run. Empty/partial hierarchies and older branches are reliable; selected relationship mismatch, zero/multiple current-Run states and database/query failure are unavailable. Persisted text inserted outside acceptance is not rescanned for trim/non-empty corruption; response text therefore has no `minLength` constraint. Acceptance validation is unchanged.
- **Durable acceptance outcomes:** `201 SAVED` requires confirmed durable commit; operation-specific `503 *.save_failed` requires known non-acceptance; operation-specific `503 *.save_outcome_unknown` represents acceptance that cannot be established, including lost PostgreSQL COMMIT acknowledgement. Both 503 variants use the existing Error envelope, with response-local code enums and examples for each operation. The browser branches on status plus matching operation code. Server-side unknown acceptance, lost POST response and unrecognized/unusable POST response all block creates and recover via the authoritative GET, with GET-only retry / UNAVAILABLE if recovery fails (SAD §6 / AC-16a). No idempotency machinery is introduced.
- **Typed validation:** all four POST 400 responses use `ValidationError`, requiring `ValidationErrorDetails.fields` as a non-empty string array. Strict structural body failures (missing/wrong-type/unexpected properties, absent body, malformed JSON) use one transport code, `request.invalid_body`, before domain validation/use cases/writes. Dotted paths are sorted/deduplicated; body-level errors use `$`. Known field paths render inline; other paths render at form level. Non-validation errors keep the general Error envelope.
- **Timestamp:** `created_at DEFAULT now()` is assigned during the acceptance transaction, not at commit. Only commit establishes acceptance. The three full-run response examples now include the required nested Observed Run State timestamp.

### Final implementation-readiness cleanup

- **Simultaneous domain failures:** [spec validation feedback](../spec.md#validation-feedback-ac-02--ac-05--ac-08--ac-12) / SAD §6 fix Target code precedence to `key`, `value`, and Run precedence to `run_reference`, `observed_run_state.key`, `observed_run_state.value`. Evaluate every accepted-text input; the first failing field supplies its existing code, while `details.fields` contains all failed paths sorted/deduplicated independently of precedence. JSON property order is irrelevant. Structural failures still win first with only `request.invalid_body`. Multi-field examples show both-empty Target, all-empty Run and valid-reference/both-empty observed fields. Every known path gets inline non-empty-after-trim feedback; no new codes or error taxonomy. T2/T5/T7/T8/T10/T11/T13 carry pure, use-case, structural-boundary, HTTP, adapter, UI and deployed verification respectively; exhaustive invalid-field subsets belong in T5/T8.
- **Execution authorization:** [AGENTS.md](../../../../AGENTS.md#verification-execution-policy) owns the rule referenced by all 16 tasks. Requests to implement a task authorize its prescribed bounded local PostgreSQL/Compose/E2E/restart checks once ready; no fresh class-by-class approval is needed within that scope. Uncovered slow/flaky/privileged/networked/expensive work still requires authorization, and destructive reset requires explicit target/data-loss authorization. Planning alone does not authorize system checks. This uses the local implementer/preflight/testing skills' “unless already authorized/approved” rule without waiving tool permissions.
- **Registry timing:** [implemented-contract handoff](../../../../AGENTS.md#implemented-contract-handoff) follows the local skill flow: implementation → architecture → maintainability review → registry updater → acceptance, repeating synchronization after contract-changing corrections. Only actual durable cross-task surfaces and stale discovery references are synchronized; T16 reconciles the completed feature rather than delaying all registration. No planned or private-helper contracts are registered in this cleanup; the current empty index remains truthful.
- **Timestamp scan:** task artifacts already carry the correct T1/T3 wording: PostgreSQL `now()` is assigned during the acceptance transaction; successful commit establishes acceptance and `created_at` is not its exact timestamp. No remaining stale timestamp assertion was found; no schema correction is needed.
- **Current-selection semantics:** spec, SAD, ADR-0005, data model, OpenAPI and initial UX guidance now distinguish greatest visible accepted UUID from exact acceptance/commit chronology. Repeated creates and recovery use parent-scoped descending UUID selection. Same-millisecond interleaving, clock skew and transaction completion do not require an ID strategy or schema change for this slice. T3/T13 own ordering fixtures.

### API ↔ PostgreSQL outcome correction

**Gap:** ADR-0002/SAD and copied task excerpts previously claimed that a failed commit accepted nothing. Drizzle 0.45.3's transaction wrapper catches a COMMIT exception and attempts cleanup ROLLBACK; rejection (even followed by successful cleanup) does not establish whether the earlier COMMIT happened. `apps/api/src/database.ts` currently provides pool/Drizzle/health only, with no product acceptance abstraction to resolve this gap.

**Smallest contract decision:** keep synchronous request-scoped transactions and HTTP 503/Error; add only the four operation-specific `*.save_outcome_unknown` codes. A distinct status, success-like 202, read-side `workspace.unavailable` code on POST, or new domain Evidence Status would blur the existing outcome model or add unnecessary shape. Unknown means the server cannot establish acceptance, not that it is queued. The four POST 503 schemas permit exactly that operation's `save_failed` and `save_outcome_unknown` codes; neither error carries a success record or Evidence Status.

**Evidence owner:** T3's persistence adapter controls the transaction lifecycle on one leased node-postgres client, with Drizzle statements on that client. It distinguishes acknowledged commit, known non-acceptance (COMMIT never dispatched and cannot follow, or definitive rollback/non-commit of that transaction), and unknown. Generic exceptions, timeout/cancellation and cleanup ROLLBACK after uncertain COMMIT are not non-acceptance proof. T4/T5 preserve the result; T7/T8 map it without inventing evidence. Post-commit read/response failures cannot be relabeled retry-safe save failures. T10/T11/T14 implement the recovery contract.

**Recovery composition:** a reliable GET replaces the current hierarchy and derives status from that read without retroactive `SAVED`/`SAVE_FAILED` or automatic POST replay. It is a snapshot, not a historical outcome query: absence does not prove rollback or prevent a still-completing transaction from committing. A subsequent create requires explicit user action from recovered context, with no duplicate-free retry guarantee. Repeated creates/current selection remain unchanged.

**Test allocation:** T3 covers dispatch/acknowledgement and cleanup evidence; T4/T5 use separate known-failure and unknown-outcome doubles; T7/T8 assert both 503 codes for every create; T10/T11 distinguish received unknown from known retry-safe failure and from unusable/lost responses; T13 uses real PostgreSQL plus a test-owned driver wrapper to hide a real commit acknowledgement and separately model non-commit with identical API uncertainty; T14 covers both accepted/absent GET recovery, blocked creates and GET-only retry. Composed API/real-DB fault fixtures are labeled separately from deployed checks and actual network-fault claims. No production fault hook is added.

## Section A — field-origins

| schema_path | origin | confidence |
|---|---|---|
| createProject.name (input) | data-model.md → `project.name` (text NOT NULL; non-empty after trimming, app layer — AC-01/02, AC-14a) | high |
| createProject.record.id | data-model.md → `project.id` (uuid PK, app-generated v7 — ADR-0005) | high |
| createProject.record.name | data-model.md → `project.name` (stored trimmed) | high |
| createProject.record.created_at | data-model.md → `project.created_at` (timestamptz default now — timestamp assigned during acceptance transaction; AC-17 gates acceptance on commit) | high |
| createProject.outcome ("SAVED") | sad.md §6 US-01 + ADR-0002 (SAVED only after commit) | high |
| createProject 400 `project.invalid_name` | spec AC-02 VALIDATION_ERROR (code coined here — no repo error registry, see point 2) | medium |
| createProject 503 `project.save_failed` | spec AC-16 + Critical flow 3 (SAVE_FAILED, nothing accepted) | medium |
| createProject 503 `project.save_outcome_unknown` | spec AC-16a + SAD §6 transaction evidence / Critical flow 3; acceptance unknown, GET recovery | high |
| createEnvironment.name (input) | data-model.md → `environment.name` (AC-03/05) | high |
| createEnvironment.record.project_id | data-model.md → `environment.project_id` (FK → project; server-derived from current context — not client input) | high |
| createEnvironment.record.id / created_at | data-model.md → `environment.id` / `environment.created_at` | high |
| createEnvironment 400 `environment.invalid_name` | spec AC-05 (coined code) | medium |
| createEnvironment 409 `environment.project_missing` | sad.md §6 US-02 else-branch «no Project accepted» (AC-04) | medium |
| createEnvironment 503 `environment.save_failed` | spec AC-16 + Critical flow 3 | medium |
| createEnvironment 503 `environment.save_outcome_unknown` | spec AC-16a + SAD §6 transaction evidence / Critical flow 3 | high |
| createVerificationTarget.key / .value (input) | data-model.md → `verification_target.key` / `.value` (AC-06/08, AC-14a trim + case-sensitive compare) | high |
| createVerificationTarget.record.environment_id | data-model.md → `verification_target.environment_id` (FK; server-derived) | high |
| createVerificationTarget.record.id / created_at | data-model.md → `verification_target.id` / `.created_at` | high |
| createVerificationTarget 400 `verification_target.invalid_key` / `.invalid_value` | spec AC-08 (coined codes) | medium |
| createVerificationTarget 409 `verification_target.environment_missing` | sad.md §6 US-03 else-branch «no Environment accepted» (AC-07) | medium |
| createVerificationTarget 503 `verification_target.save_failed` | spec AC-16 + Critical flow 3 | medium |
| createVerificationTarget 503 `verification_target.save_outcome_unknown` | spec AC-16a + SAD §6 transaction evidence / Critical flow 3 | high |
| createVerificationRun.run_reference (input) | data-model.md → `verification_run.run_reference` (trusted user assertion — spec §6.1; AC-10/12) | high |
| createVerificationRun.observed_run_state.key / .value (input) | data-model.md → `observed_run_state.key` / `.value` (AC-10/12) | high |
| createVerificationRun.record.verification_target_id | data-model.md → `verification_run.verification_target_id` (FK; server-derived) | high |
| createVerificationRun.record.observed_run_state (embedded) | data-model.md → `observed_run_state` columns (id, verification_run_id, key, value, created_at) — one-transaction aggregate pair (ADR-0002, US-04 persist note) | high |
| createVerificationRun.evidence_status | response-only computed field — derived at read time per ADR-0003; MATCH iff trimmed exact equality (AC-14/AC-10/AC-11), applicability only (AC-15) | medium |
| createVerificationRun 400 `verification_run.invalid_run_reference` / `.invalid_observed_key` / `.invalid_observed_value` | spec AC-12 (coined codes) | medium |
| createVerificationRun 409 `verification_run.verification_target_missing` | sad.md §6 US-04 else-branch «no Verification Target accepted» (AC-13) | medium |
| createVerificationRun 503 `verification_run.save_failed` | spec AC-16 + Critical flow 3 (run + state accepted together or not at all) | medium |
| createVerificationRun 503 `verification_run.save_outcome_unknown` | spec AC-16a + SAD §6 transaction evidence / Critical flow 3; atomicity retained even when outcome unknown | high |
| getWorkspace.evidence_status | response-only computed field — ADR-0003 derive-at-read; null before a Target (AC-19a), NO_EVIDENCE target-without-run (AC-09/19), MATCH/MISMATCH complete context (AC-14/15) | medium |
| getWorkspace.project / .environment / .verification_target / .verification_run | data-model.md → the four entity row shapes (all columns, verbatim types) | high |
| getWorkspace 503 `workspace.unavailable` | spec AC-20 + sad.md §6 US-08/US-09 unreadable-branch + Critical flow 2 alt «unreadable or inconsistent» (user-confirmed 503 shape) | medium |
| Error.code / .message / .details | scaffold convention (drift-check defaults: neutral `module.error_name`, unified envelope) | high |
| ValidationError.details.fields | existing domain 400 field guidance, now typed by ValidationErrorDetails (required non-empty array) | high |
| POST 400 request.invalid_body | SAD §6 strict request boundary; smallest shared transport convention for structural JSON-body failures | medium |

No `low` rows — every field traces to a `data-model.md` column or is an explicitly computed
response field grounded in an ADR/AC.

## Section B — drift findings (4-point checklist)

1. **Endpoint ↔ data-model (core): ✓** — createProject → `project`; createEnvironment →
   `environment`; createVerificationTarget → `verification_target`; createVerificationRun →
   `verification_run` + `observed_run_state` (one transaction, the run aggregate);
   getWorkspace → authoritative read of all four. Every request/response field maps to a column
   in Section A; no field was invented (the `evidence_status` computed field is ADR-0003-derived,
   flagged medium, response-only).
2. **Error code ↔ repo error definition (core): ✓ (with note)** — the repo has **no error
   registry** yet (`apps/api/src` holds only ad-hoc `throw new Error(...)` in config/migrate
   paths; the product domain module does not exist — architecture-map.md). Per the drift-check
   protocol this is recorded as: *no error registry found — codes are the contract's proposal;
   reconcile when the repo defines them.* All codes follow the neutral `module.error_name`
   convention: `project.invalid_name`, `project.save_failed`, `environment.project_missing`,
   `environment.invalid_name`, `environment.save_failed`, `verification_target.invalid_key`,
   `verification_target.invalid_value`, `verification_target.environment_missing`,
   `verification_target.save_failed`, `verification_run.invalid_run_reference`,
   `verification_run.invalid_observed_key`, `verification_run.invalid_observed_value`,
   `verification_run.verification_target_missing`, `verification_run.save_failed`,
   `workspace.unavailable`, `request.invalid_body`, `project.save_outcome_unknown`,
   `environment.save_outcome_unknown`, `verification_target.save_outcome_unknown`,
   `verification_run.save_outcome_unknown`.
3. **Validation ↔ constraint (core): ✓** — `data-model.md` uses unbounded `text` columns with
   **no CHECK constraints and no length limits** (conventions note; spec §5 defines no lengths),
   so the contract mints no `maxLength`/`pattern`. The one app-layer constraint (non-empty
   after trimming — AC-14a, enforced in the application layer per the model's notes) is
   expressed exactly where the model puts it: as the `400 VALIDATION_ERROR` response paths
   (`invalid_*` codes) on the inputs the API trims. Response text permits externally inserted
   empty/untrimmed values because read-side textual corruption detection is excluded by the
   bounded AC-20 predicate; application acceptance still guarantees trimmed non-empty values.
   All 400 envelopes require typed field details. Structural body failures are mapped before
   domain validation to `request.invalid_body`, not arbitrary framework payloads. Case-sensitivity
   and trim-before-compare remain stated on compared fields (AC-14a).
4. **OpenAPI ↔ sequence (supporting): ✓** — every §6 `alt`/`else` branch has a response:
   US-01 (happy→201 / empty→400), US-02 (happy→201 / empty→400 / no-Project→409), US-03
   (happy→201 / empty→400 / no-Environment→409), US-04 (equal→201+MATCH / differs→201+MISMATCH /
   empty→400 / no-Target→409), US-05·06·09 (readable→200 incl. no-run branch / unreadable→503),
   US-08 (full→200 / target-without-run→200 / partial→200 / unreadable→503), Critical flow 1
   (→201+MATCH/MISMATCH), Critical flow 2 (→200/503), Critical flow 3 (known non-acceptance→503
   *.save_failed; unknown acceptance→503 *.save_outcome_unknown or response loss, then GET→200/503).
   SAD §6 also bounds structural body failures to 400 `request.invalid_body`
   and describes server-side uncertainty/browser response-loss recovery without adding server operations. No orphan
   sequences; the user-resolved duplicate case remains deliberately not forbidden (flag 1).

### Back-feed (coverage cross-check)

- **AC → operation/response:** every AC maps — AC-01→201, AC-02→400, AC-03→201, AC-04→409,
  AC-05→400, AC-06→201, AC-07→409, AC-08→400, AC-09→200 `NO_EVIDENCE`, AC-10→201 `MATCH`,
  AC-11→201 `MISMATCH`, AC-12→400, AC-13→409, AC-14→derivation on 201/200, AC-14a→trim rules +
  400s, AC-15→`evidence_status` descriptions, AC-16→503 *.save_failed,
  AC-16a→503 *.save_outcome_unknown / lost response + GET recovery, AC-17→`SAVED`-after-confirmed-commit,
  AC-17a→409s (API side of gated actions), AC-18→200 full-hierarchy, AC-19→200 target-without-run,
  AC-19a→200 partial/empty, AC-20→503. No AC without an operation; no operation without an AC.
- **Operation → §4 user story:** createProject→US-01, createEnvironment→US-02,
  createVerificationTarget→US-03, createVerificationRun→US-04, getWorkspace→US-05/06/08/09
  (+ US-07 via the 503 retry-preserved semantics on every create).
- **Sequence gap found and resolved:** duplicate-record behavior (flag 1) — resolved by the
  user as *deps logic only, no scope to reverse later*; recorded here rather than silently
  encoded. No upstream OQ was opened because the decision closes the gap for this slice without
  contradicting any source artifact.

## Deviations from scaffold defaults (ADR/settings-grounded)

- **No security scheme** — spec §6.1 authentication N/A (user-confirmed; flag 3). The BearerAuth
  default is dropped, not commented out.
- **No `events.md`** — sad.md §6 sequencing notes: all flows synchronous request→response, no
  webhook/queue/scheduled step; ADR-0002 request-scoped transactions. The feature has no async
  flows, so the events contract is correctly absent.
- **No `Idempotency-Key`** — explicitly excluded in this slice. Known non-acceptance allows retry; unknown acceptance at either network boundary recovers authoritative state before explicit continuation (SAD §6), without promising duplicate-free retry. Synchronous requests can lose either the PostgreSQL commit acknowledgement or the HTTP response after commit.
- **No cursor pagination** — no list endpoints exist in this slice (one-record scope;
  `getWorkspace` is a singleton authoritative read; the data model defines no listing query).

Kept defaults: OpenAPI 3.1.0 (nullability via `type: ["string", "null"]`), URL versioning
`/api/v1/...`, unified `{code, message, details?}` error envelope, `$ref` for all shared
schemas, placeholder-only example data (no PII — the model has no person-related fields).

## Lint

`npx js-yaml` parse check: **OK** (no Spectral/Redocly in the repo's toolchain — `pnpm
check:architecture`/`check:contracts` do not lint OpenAPI; consider wiring `spectral lint
docs/features/<slug>/contracts/openapi.yaml` into the project's check target when the first
consumer integration starts).

**Cleanup validation (2026-10-05):** Ruby/Psych YAML parse passed; local Ajv 2020-12 compilation passed for all 18 component schemas and all 34 request/response examples. Negative probes rejected missing/empty/wrong-type/extra validation details and structural request errors; strict Zod probes confirmed missing/wrong-type and unexpected-key issue categories. All 16 task manifests match their Markdown metadata/DoDs, dependencies are acyclic, and task-local source links resolve. `pnpm check:contracts`, `pnpm check:architecture`, and `git diff --check` passed. These are planning/static checks, not implemented-feature or live-system evidence.

**Save-outcome correction validation (2026-10-05):** Ruby/Psych parsed OpenAPI and all task frontmatter. Local Ajv 2020-12 compiled 18 component schemas and 21 request/response schemas, validated all 38 examples, and rejected 20 negative POST-503 probes (wrong operation/read codes and fabricated record/status/SAVED fields). All 16 manifests match task metadata and full DoDs; all 24 ACs are covered, including AC-16a in T3/T4/T5/T7/T8/T10/T11/T13/T14; quoted ACs and local source links match, inverse blocks/dependencies are consistent and acyclic. A current-artifact scan plus manual outcome review found no remaining rule equating arbitrary transaction/COMMIT exceptions with known rollback. `pnpm check:contracts`, `pnpm check:architecture`, and `git diff --check` passed. Only planning artifacts changed; no production implementation, live database fault, or browser runtime test was performed. No remaining save-outcome design ambiguity blocks implementation; runtime evidence remains assigned to the tasks above.

## Structural self-check

**Final cleanup verification (2026-10-05):** Ruby/Psych parsed OpenAPI and all 16 task frontmatter blocks. Local Ajv 2020-12 compiled 18 component and 21 request/response schemas, validated all 41 examples, and passed three multi-field semantic oracles plus 15 negative structural/envelope probes. All 16 manifests match metadata, DoDs and writable scopes; inverse blocks and dependencies are consistent/acyclic, all 24 ACs retain matching quotations and all 408 task-local links/anchors resolve. Timestamp scan found no stale acceptance/commit-time claim. `pnpm check:contracts`, `pnpm check:architecture`, the canonical fast `pnpm check` (including registry tests, typecheck, build and four focused tests), and `git diff --check` passed. The implemented-contract index remains unchanged and empty. Only planning/policy artifacts changed; no feature implementation or real-system checks were performed. No unresolved ambiguity from this cleanup blocks implementation.

Section B + back-feed above = this stage's structural self-check: **4/4 core/supporting points ✓**,
3/3 flags resolved with the user, field-origins 0 low rows. No unresolved findings.
