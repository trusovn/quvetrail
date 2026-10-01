# QuVeTrail — Walking Skeleton

## Objective

Establish a complete end-to-end development path for QuVeTrail before building the first MVP.

The walking skeleton must prove that the main product layers work together as one deployable, testable system.

## Smallest User-Visible Flow

A user can:

1. open QuVeTrail;
2. create or open a Project;
3. create one Environment;
4. record one piece of Environment state;
5. record one Verification result against that state;
6. see a simple Readiness result derived from that verification.

Example:

```text
Project: Shop Platform
Environment: QA
State: frontend = 1.0.0
Verification: ui-smoke = PASSED
Readiness: READY
```

The Readiness rule may be intentionally simple in the walking skeleton:

```text
required verification exists and passed
→ READY

otherwise
→ NOT READY
```

## System Boundaries That Must Participate

The flow must cross the real intended system boundaries:

```text
Browser
  ↓
Frontend
  ↓
Backend API
  ↓
Domain logic
  ↓
PostgreSQL
```

The same product flow must also be verifiable through automated testing and CI:

```text
Playwright
  ↓
QuVeTrail UI / API

GitHub Actions
  ↓
build + automated tests
```

Persistence must be real: restarting the application must not lose the created Project, Environment, state, Verification result, or Readiness result.

## Fixed Technology Baseline

| Area | Technology |
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

## Definition of Completion

The walking skeleton is complete when:

- the complete system can be started locally;
- the smallest user-visible flow works through the browser;
- the same underlying capability is accessible through the backend API;
- state is persisted in PostgreSQL;
- restarting the application preserves the created data;
- at least one Playwright UI test covers the complete user-visible flow;
- at least one API-level automated test verifies the same core capability without the UI;
- lower-level automated tests run successfully;
- all automated tests run in GitHub Actions;
- a clean checkout can be brought to a working local state using documented repository commands.

## Explicit Exclusions

The walking skeleton does not include:

- environment history or snapshot comparison;
- change diffs;
- stale verification evidence;
- configurable readiness rules;
- change-aware verification;
- selective evidence invalidation;
- multiple roles or permission levels;
- advanced multi-user workflows;
- release or approval workflows;
- CI/CD provider integrations;
- deployment or environment provisioning;
- test-case management;
- quality gates controlling external pipelines;
- observability integrations;
- failure triage or reproduction bundles;
- performance-testing semantics;
- AI product functionality;
- AI-driven test generation as a product feature.

These belong to later product planning and MVP slices.
