---
status: Accepted
owner: "Architect / Tech Lead"
reviewers: ["Tech Lead"]
updated_at: "2026-10-03"
feature_size: "M"
ticket: "walking-skeleton-readiness"
---

# 0001 — Deliver the walking skeleton as a backend-service API plus a web-frontend browser client

- **Status:** Accepted
- **Date:** 2026-10-03
- **Deciders:** Architect + owner (Socratic walk)

## Context

The walking skeleton must prove the smallest real product flow across the intended boundaries (sad.md §3): a QA engineer records the Project → Environment → Verification Target → Verification Run hierarchy in a browser workspace (spec §1, ux-flows SCR-01), while validation, durability, and Evidence Status derivation belong behind a durable service. The feature touches both a human-facing UI (ux-flows is a real screen inventory) and persistent server-side state.

## Decision drivers

- spec §1 "browser workspace" + ux-flows SCR-01 progressive workspace → a UI surface exists.
- spec §6.1 trust boundary ends at the browser; validation/durability/derivation must be server-side and provable without the UI (QG-1/QG-2).
- Existing two-package monorepo (`apps/api`, `apps/web`) with enforced web/API boundaries (`pnpm check:architecture`).

## Considered options

1. **backend-service + web-frontend** — Fastify API + Drizzle/PostgreSQL, and a React/Vite browser SPA.
2. **backend-service only, browser as a thin throwaway shell** — do not declare a UI surface.
3. **Single monolith serving server-rendered HTML** — no separate frontend surface.

## Decision outcome

**Chosen:** Option 1 — declare `target_surfaces: ["backend-service", "web-frontend"]`, written to `sad.md` frontmatter and one §5 C4 container per surface. The API owns durability and derivation; the web client is a thin SPA with no business rules.

## Consequences

**Positive**
- §5 container view and the HTTP/JSON contract are well-defined and owned by downstream stages.
- Durability and Evidence Status correctness are testable at the API layer without a browser (matches deployed API tests in `tests/api`).

**Negative**
- Two deployable artifacts to keep in lockstep during the slice (web + API contracts).

**Neutral**
- ux-flows' progressive-workspace behavior (gated actions, operation outcomes) is realised entirely within the web-frontend surface.

## Links

- Spec: [[../spec.md]]
- SAD: [[../sad.md]] §4, §5
- Related ADR: [[0004-spa-server-authoritative-state]]
