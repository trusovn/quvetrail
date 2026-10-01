# QuVeTrail — Walking Skeleton Delivery Plan

## Purpose

Deliver the accepted QuVeTrail Walking Skeleton as one complete development path from local checkout to browser workflow, persistence, automated verification, and CI.

This plan implements only the scope defined by `walking-skeleton.md`. It does not expand the product scope or define the first MVP.

## Target Outcome

From a clean checkout, a contributor can start QuVeTrail locally and complete this flow:

```text
Create/open Project
  → create Environment
  → record one Environment state value
  → record one Verification result for that state
  → see Readiness
```

Example:

```text
Project: Shop Platform
Environment: QA
State: frontend = 1.0.0
Verification: ui-smoke = PASSED
Readiness: READY
```

The same capability is persisted in PostgreSQL, exposed through the backend API, verified by automated tests, and exercised in GitHub Actions.

## Fixed Baseline

| Area | Choice |
|---|---|
| Language | TypeScript |
| Frontend | React + Vite |
| Backend | Node.js + Fastify |
| Database | PostgreSQL |
| Data access | Drizzle |
| Local runtime | Docker Compose |
| UI / API automation | Playwright |
| Lower-level tests | Vitest |
| CI | GitHub Actions |
| Package/workspace management | pnpm workspace |

The implementation should stay simple. Additional infrastructure or framework layers require a concrete need inside the Walking Skeleton.

## Delivery Rules

- Build vertically: keep the end-to-end path working as early as possible.
- Prefer one real implementation path over temporary mocks between QuVeTrail layers.
- Keep domain behaviour deterministic.
- Keep the readiness rule intentionally fixed and simple for the skeleton.
- Do not add later-MVP concepts while implementing the skeleton.
- Add automated verification alongside behaviour, not after the application is complete.
- Every work item should leave the repository in a runnable state.

---

## WS0 — Repository and Runtime Baseline

### Goal

Create a clean repository that can start the intended application and database locally.

### Deliverables

- pnpm workspace initialized.
- React/Vite web application present.
- Fastify API application present.
- PostgreSQL service defined in Docker Compose.
- Database connection from the API established through Drizzle.
- Initial migration mechanism established.
- Root-level commands documented for the normal developer workflow.
- Basic health/readiness checks available for local orchestration.
- `.env.example` or equivalent documents required local configuration without committing secrets.

### Minimum developer flow

A clean checkout should have a short documented path equivalent to:

```text
install dependencies
start local system
run checks/tests
stop local system
```

Exact commands may be chosen during implementation, but there should be one canonical set of repository commands used both locally and by CI where practical.

### Verification

- Web application loads.
- API responds.
- API can reach PostgreSQL.
- Migration runs successfully on a clean database.
- Re-running local startup does not require manual database repair.

### Done when

The repository is a working full-stack shell rather than disconnected frontend/backend examples.

---

## WS1 — Persist the Smallest QuVeTrail Domain

### Goal

Establish only the persistent product state needed by the accepted Walking Skeleton.

### Required concepts

- Project
- Environment
- Environment state value
- Verification result

The implementation may use additional technical identifiers/timestamps as required, but no additional product concepts should be introduced unless needed for this flow.

### Required behaviour

The backend can:

- create and retrieve a Project;
- create and retrieve an Environment belonging to a Project;
- record one state value for an Environment;
- record a Verification result associated with that Environment/state;
- retrieve enough information to derive and present Readiness.

### Skeleton readiness rule

Keep the rule fixed:

```text
required verification exists and is PASSED
→ READY

otherwise
→ NOT_READY
```

For the Walking Skeleton, the required verification may be a fixed verification name such as `ui-smoke`. Configurable readiness rules are explicitly out of scope.

### Persistence requirement

Created data must survive API/application restart while the PostgreSQL data volume remains intact.

### Verification

- Lower-level tests cover the readiness rule.
- Backend-level automated tests prove persistence of the core records.
- Restarting the application does not lose the created Project, Environment, state, or Verification result.

### Done when

The complete skeleton state can be created and recovered without the frontend.

---

## WS2 — Complete the Browser Flow

### Goal

Make the entire Walking Skeleton usable through the real frontend.

### Required user-visible behaviour

A user can:

1. open QuVeTrail;
2. create or open a Project;
3. create an Environment;
4. record the environment state value;
5. record the verification result;
6. see the resulting Readiness status.

### UI scope

Only UI required for this flow should be built.

The UI must expose useful states for:

- initial/empty data;
- successful operations;
- validation errors needed by the flow;
- backend failures at a basic usable level;
- current Readiness.

Visual polish is secondary. The UI should nevertheless be coherent enough to remain the base for subsequent product work rather than a throwaway test page.

### Verification

Perform the full workflow manually from a clean database and confirm that a page refresh reads persisted state rather than relying on client-only state.

### Done when

The accepted smallest user-visible flow works end-to-end through Browser → Web → API → PostgreSQL.

---

## WS3 — Establish the Automation Foundation

### Goal

Prove the same vertical slice automatically at multiple useful levels without building a full future test framework prematurely.

### Playwright UI coverage

Create at least one end-to-end test that performs the complete browser workflow:

```text
Project
→ Environment
→ Environment state
→ Verification result
→ READY
```

The test must interact with the real web application and real backend/database used by the local test environment.

### API coverage

Create API-level automation that verifies the same core capability without using the browser.

It should prove at minimum:

- core state can be created through the API;
- Verification can be recorded;
- the expected Readiness is returned/observable.

### Lower-level coverage

Use Vitest for deterministic logic that is cheaper and clearer below E2E level, especially the readiness rule and any non-trivial validation introduced by the skeleton.

### Test-data principle

Do not use the UI to create prerequisite data when the UI itself is not what is being tested. Establish a simple reusable test-data/setup approach through supported APIs or repository test helpers.

Do not build a large fixture framework yet.

### Failure evidence

Configure Playwright to retain useful diagnostics for failed CI runs, at minimum the normal report plus trace/screenshot information appropriate for failures.

### Done when

A failing product behaviour can be detected automatically at UI, API, or lower level and produces enough evidence to investigate the failure.

---

## WS4 — Make Local Execution Reproducible

### Goal

Ensure another developer can run the same application and tests without reconstructing the setup from undocumented local knowledge.

### Docker Compose role

Docker Compose is the canonical local/test application environment definition for:

- PostgreSQL;
- API;
- web application.

Playwright may run from the host rather than inside Docker for the Walking Skeleton.

### Required repository documentation

Document:

- prerequisites;
- initial setup;
- start/stop commands;
- migration/reset commands if needed;
- lower-level test command;
- API test command;
- E2E test command;
- how to inspect failed Playwright output;
- how to reset to a clean local state.

### Clean-checkout verification

Validate the documented flow from a clean checkout / clean local data state rather than only from the original developer environment.

### Done when

A contributor can follow repository instructions without additional verbal steps and reach the same working skeleton.

---

## WS5 — GitHub Actions End-to-End Flow

### Goal

Prove that the repository can recreate and verify the Walking Skeleton on clean CI infrastructure.

### CI responsibilities

GitHub Actions should:

1. check out the repository;
2. install the pinned project dependencies;
3. run static/build checks needed by the repository;
4. run lower-level tests;
5. start the QuVeTrail Docker Compose environment;
6. wait for the application to become ready;
7. run API automation;
8. run Playwright E2E automation;
9. retain useful test reports/evidence on failure;
10. cleanly stop the Compose environment.

### Environment principle

CI should reuse the same Compose definition as local development/testing rather than independently redefining PostgreSQL/API/web as GitHub-specific services.

A small CI override is acceptable only when required by a concrete CI difference.

### Verification

- CI succeeds from a fresh runner with no pre-existing application/database state.
- Breaking the tested readiness behaviour causes CI to fail.
- Breaking the browser flow causes the Playwright job/step to fail with useful diagnostics.

### Done when

A pull request can demonstrate that the full Walking Skeleton builds and works on clean infrastructure.

---

## WS6 — Skeleton Exit Review

### Goal

Confirm that the Walking Skeleton is complete and stop before product-scope expansion begins.

### Exit checklist

The skeleton is complete only if all of the following are true:

- [ ] QuVeTrail starts locally through the documented repository workflow.
- [ ] React frontend, Fastify backend, and PostgreSQL participate in the same real flow.
- [ ] Project creation/opening works.
- [ ] Environment creation works.
- [ ] One environment state value can be persisted.
- [ ] One Verification result can be persisted against that state.
- [ ] Readiness is derived from the fixed skeleton rule.
- [ ] Refresh/restart preserves persisted data.
- [ ] At least one Playwright UI test covers the complete user-visible flow.
- [ ] API automation covers the core capability without the UI.
- [ ] Lower-level automated tests cover deterministic readiness logic.
- [ ] Failed E2E execution produces useful diagnostics.
- [ ] GitHub Actions recreates the system and runs the automated checks.
- [ ] Clean-checkout instructions have been exercised successfully.
- [ ] No excluded MVP/later-product capability was added accidentally.

### Final skeleton demonstration

The repository should be demonstrable using one short scenario:

```text
Start clean QuVeTrail
→ create Shop Platform
→ create QA
→ set frontend = 1.0.0
→ record ui-smoke = PASSED
→ observe READY
→ restart application
→ observe the same persisted state and READY result
→ show the same workflow passing in CI
```

When this demonstration is reliable, stop Walking Skeleton work and return to the User Story Map to define the first MVP slice.

---

## Explicitly Deferred

Do not pull the following work into the Walking Skeleton:

- environment history/snapshots beyond what persistence technically requires;
- state comparison/diffs;
- stale verification evidence;
- configurable readiness rules;
- change-impact analysis;
- selective verification invalidation;
- roles/permission model;
- advanced multi-user behaviour;
- releases/approvals;
- CI/CD vendor integrations;
- deployment/provisioning;
- test-case management;
- external quality gates;
- observability integrations;
- failure triage/reproduction bundles;
- performance-specific product semantics;
- AI product functionality;
- sophisticated AI-driven automation workflows.

If implementation exposes a need for one of these, record it for later planning rather than expanding the skeleton by default.

## Work Order

```text
WS0  Repository + runtime baseline
 ↓
WS1  Persist smallest QuVeTrail domain
 ↓
WS2  Complete browser flow
 ↓
WS3  Automation foundation
 ↓
WS4  Reproducible local execution
 ↓
WS5  GitHub Actions end-to-end flow
 ↓
WS6  Exit review
```

WS3 may start incrementally during WS1/WS2; automated checks should be added as the relevant behaviour becomes available rather than postponed until WS2 is finished.
