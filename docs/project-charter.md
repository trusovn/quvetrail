# Project Charter

## Mission

QuVeTrail helps a QA engineer answer “Can this release proceed?” from recorded environment state and verification evidence. The first project outcome is a trustworthy, persisted walking skeleton that reports an explainable informational readiness result while leaving the release decision with the QA engineer.

## External actors / users

- Primary user: a QA engineer using a local or otherwise controlled installation.
- External integrations: none in the walking skeleton.

## Expected product shape

A browser-based web application with a backend API and PostgreSQL persistence. The current technical baseline is TypeScript, React with Vite, Node.js with Fastify, Drizzle, a pnpm workspace, Docker Compose, Vitest, Playwright, and GitHub Actions.

## Hard constraints

- The browser, frontend, backend API, deterministic domain logic, and PostgreSQL must participate in one real, testable path.
- Accepted data must survive refresh and application restart; a failed operation must not damage previously accepted data.
- A system or storage failure must not be presented as a newly calculated readiness result.
- Readiness is informational only: QuVeTrail must not approve, trigger, or enforce a release decision.
- The walking skeleton uses one fixed required check and only `READY` / `NOT_READY`; broader product behavior is deferred.
- Manual entries are trusted user assertions in this phase; hostile-user and production-grade security are not design targets.
- A clean checkout must have documented, reproducible commands for setup, start, verification, and stop.
- AI is not part of the product or engineering data/process flow for this phase.

## System-level success signals

- A contributor can start the complete system from a clean checkout using documented commands.
- A QA engineer can complete the narrow readiness flow and receive an explainable result without QuVeTrail taking the release decision.
- Accepted state and its derived result remain available after refresh or application restart.
- Invalid or failed operations are visible, retryable, and do not corrupt previously accepted state.
- Automated checks exercise the deterministic logic, API boundary, browser path, and clean CI environment with useful failure evidence.

## Quality priorities

1. Trustworthy persisted behavior
2. End-to-end verifiability
3. Simplicity and narrow scope
4. Maintainability / localized change
5. Agent and contributor legibility
6. Fast iteration

## Non-goals

- Defining the first MVP slice or implementing the broader story map.
- Release, approval, deployment, or external quality-gate workflows.
- Configurable readiness rules, history/comparison, change analysis, or evidence invalidation.
- Authentication, permissions, advanced multi-user behavior, or production deployment.
- External CI/CD, test-management, observability, or provisioning integrations.
- AI product behavior or AI-driven automation.
- Detailed feature APIs, schemas, screens, prompts, workflows, or task decomposition during bootstrap.

## Foundation-bearing unknowns

- Exact supported Node.js and pnpm versions are not yet pinned; foundation materialization may choose current supported versions and record them as reversible defaults.
- The eventual production deployment target and production assurance requirements are intentionally unknown and must not shape the walking-skeleton foundation.
- The first MVP slice remains intentionally unknown until the walking skeleton is complete.

