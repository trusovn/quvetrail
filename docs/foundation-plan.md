# Foundation Plan

## Baseline

- Runtime/build: documentation-only repository; the planned baseline is a TypeScript pnpm workspace with React/Vite, Node.js/Fastify, PostgreSQL/Drizzle, and Docker Compose (`docs/planning/walking-skeleton.md`).
- Existing run command: none.
- Existing focused verification: none.
- Existing full verification: none.
- Existing architecture/maintainability gate: none.
- Existing repo instructions/maps: root `AGENTS.md` contains skill-resolution rules; `docs/direction-quvetrail.md` governs product direction; the planning documents describe the walking skeleton. There is no implemented-system map.
- Existing CI: none.
- Config/state: no environment contract, secret-handling example, datastore configuration, or migration mechanism exists.
- Development diagnostics: none; there is no running application.
- Generated files: none currently; lockfiles and database migrations will require explicit generated/source-of-truth guidance when introduced.
- AI in data/process flow: no. AI behavior is explicitly excluded from the walking skeleton.

## Capability decisions

| Capability | Status | Evidence | Minimum change | Verification |
|---|---|---|---|---|
| Bootstrap/runtime | ADD | No package manifest, application source, container definition, or run command exists. The fixed baseline is recorded in `docs/planning/walking-skeleton.md`. | Materialize the smallest pnpm workspace and Compose-based web/API/PostgreSQL shell, pin runtime/package-manager expectations, and expose canonical install/start/stop commands. | From a clean checkout, install succeeds; the canonical start command makes web and API health checks pass; stop exits cleanly; a second start requires no manual repair. |
| Verification | ADD | There is no test, lint, typecheck, build, API-test, or browser-test harness. | Add canonical focused and full verification commands with Vitest and Playwright harnesses, plus only the smoke coverage needed to prove the shell and test seams. | Focused tests, static/build checks, and the canonical full verification command all pass; an intentional smoke-test failure produces actionable output. |
| Repo navigation | REPAIR | `AGENTS.md` only covers skill installation; product direction and planning sources exist, but code placement and system ownership are undocumented. | Extend agent/contributor routing and add a concise implemented-system map with source/generated-file rules and closest-precedent guidance. | A fresh reviewer can identify canonical commands, module ownership, authoritative docs, and placement rules without oral context; referenced paths validate. |
| Implemented-contract discovery | ADD | No application contracts exist yet and there is no canonical machine-readable registry entry point. The expected multi-module, recurring-agent work makes repeated rediscovery material. | Create an empty canonical registry structure, route `AGENTS.md` to it, link future records to module and executable/declarative authorities, and validate schema plus repository paths. Do not populate product contracts during foundation work. | The registry validation command passes for the empty baseline and fails for an invalid record or missing referenced path. |
| Development diagnostics | ADD | No application logs, startup failure reporting, health status, or Playwright failure artifacts exist. | Provide readable web/API startup and error output, dependency health signals, and retained Playwright report/trace/screenshot evidence on failure; do not add external observability. | A failed dependency/startup check is visible and non-zero; a deliberately failing browser smoke test retains the documented local artifact. |
| Configuration/state | ADD | No config source of truth, `.env.example`, PostgreSQL definition, Drizzle setup, or migration command exists. | Define and validate the minimal local/test environment contract, keep secrets out of version control, establish persistent PostgreSQL storage and a repeatable migration/reset mechanism. | A clean database migrates successfully; migration/startup is repeatable; persisted smoke data survives application restart; missing required config fails clearly. |
| Automation/CI | ADD | No local automation entry point or GitHub Actions workflow exists. | Make the canonical repository commands usable locally and add one CI path that installs pinned dependencies, runs static/focused checks, starts the same Compose shell, runs smoke verification, retains failure evidence, and tears down. | The workflow definition validates and the same command sequence passes locally; once pushed, a fresh GitHub Actions runner must pass without pre-existing state. |
| AI foundation | N/A | `docs/direction-quvetrail.md` and both walking-skeleton documents explicitly exclude AI behavior. | None; do not invoke `ai-flow-foundation`. | Confirm no AI provider, prompt, model output, or AI retry/eval path is introduced by foundation materialization. |
| Maintainability / architecture guardrails | ADD | The accepted path has distinct browser/frontend/API/domain/database boundaries, but no executable boundary check exists. Recurring agent work and later replacement seams make accidental cross-layer imports costly. | Define discoverable ownership rules and one canonical deterministic gate that prevents frontend access to server/database internals and keeps deterministic domain logic independent of UI, transport, and persistence concerns. Let `repo-foundation` choose repo-native enforcement through `architecture-guardrails`. | The canonical architecture command passes, is included in full verification/CI, and fails against representative forbidden dependency fixtures or test cases. |

## Authorized foundation changes

1. Materialize the reproducible full-stack shell.
   - Why before product planning: the chosen browser-to-database boundaries and persistence assumptions must be real before later plans depend on them.
   - Files: root workspace/package-manager configuration; minimal web and API package roots; Compose definition; runtime version declarations; root developer documentation.
   - DoD: clean install/start/health/stop/restart checks pass through canonical commands.
   - Reversible: yes; exact versions and shell details are replaceable defaults within the fixed baseline.

2. Establish configuration and persistent-state mechanics.
   - Why before product planning: feature work cannot safely define persistence behavior or deterministic tests without a known config and migration contract.
   - Files: `.env.example` or equivalent; ignored local overrides; Compose PostgreSQL configuration; Drizzle configuration and initial technical migration baseline; documented migrate/reset commands.
   - DoD: config validation is clear, clean migration is repeatable, and a technical persistence smoke check survives restart.
   - Reversible: partially; development data may be reset, while committed migration history becomes durable once product migrations build on it.

3. Establish verification and development diagnostics.
   - Why before product planning: later work needs deterministic, progressively scoped checks and useful evidence when a boundary fails.
   - Files: root scripts/config; Vitest and Playwright configuration; minimal shell-level smoke tests; test artifact ignores; developer documentation.
   - DoD: focused, static/build, browser smoke, and full verification commands pass; deliberate failures demonstrate non-zero exits and documented evidence.
   - Reversible: yes.

4. Establish repository navigation and current-contract discovery.
   - Why before product planning: multiple packages and recurring agents otherwise require repeated rediscovery and risk placing code against the intended boundaries.
   - Files: `AGENTS.md`; `README.md`; a concise architecture/project map; an empty machine-readable implemented-contract registry; deterministic registry validation.
   - DoD: instructions route to all authorities and commands; registry structure/path validation passes; no application contracts are pre-populated.
   - Reversible: yes.

5. Establish maintainability guardrails.
   - Why before product planning: the already accepted frontend/API/domain/database separation needs a cheap regression signal before parallel feature changes begin.
   - Files: ownership/boundary documentation; repo-native architecture-check configuration/tests; canonical root command and CI invocation.
   - DoD: one architecture command enforces the documented invariants and detects representative forbidden dependencies.
   - Reversible: yes.

6. Establish clean-run CI for the foundation shell.
   - Why before product planning: a clean environment must prove that the documented foundation is reproducible rather than dependent on one workstation.
   - Files: GitHub Actions workflow and only the minimal CI-specific configuration required to invoke canonical repository commands.
   - DoD: the workflow uses the same Compose/runtime path, runs all foundation gates, retains failure evidence, and cleans up; final hosted-run proof remains required after the workflow is pushed.
   - Reversible: yes.

## Explicitly deferred

- Product entities, database schema, readiness rule implementation, feature API routes, and UI screens.
- Product-flow API, browser, and persistence-recovery tests; foundation adds their harnesses and smoke seams only.
- Detailed walking-skeleton sequencing or task decomposition; the existing delivery plan is evidence, not work authorized by this bootstrap.
- Production deployment, production security, external observability, and service integrations.
- The first MVP slice and all broader story-map behavior.
- AI foundations unless project direction changes through an explicit owner decision.

## Materialization handoff

Read:

- `docs/project-charter.md`
- `docs/foundation-plan.md`
- `docs/direction-quvetrail.md`
- `docs/planning/walking-skeleton.md`
- `docs/planning/QuVeTrail_Walking_Skeleton_Plan.md`
- `AGENTS.md`

Use:

- `repo-foundation` as the governing materialization skill.
- `architecture-guardrails` through `repo-foundation` for the authorized ownership rules and canonical architecture gate.

Authorize only:

- the six foundation changes listed above;
- minimal smoke behavior needed to prove runtime, persistence, diagnostics, and verification seams;
- current supported Node.js/pnpm versions chosen and pinned as documented reversible defaults.

Required verification:

- clean install and canonical start/health/stop/restart;
- focused tests, static/build checks, browser smoke, full verification, contract-registry validation, and architecture gate;
- clean database migration/reset and technical persistence across restart;
- local reproduction of the CI command sequence, followed by hosted GitHub Actions proof when available.

Do not:

- implement product features or walking-skeleton domain behavior;
- broaden architecture beyond the authorized foundation;
- add AI infrastructure;
- infer the first MVP or production deployment model;
- populate implemented application contracts before they exist;
- guess unresolved values.

Unknown values that must remain unknown:

- production deployment target and production assurance requirements;
- the first MVP slice;
- future AI use, unless separately approved.
