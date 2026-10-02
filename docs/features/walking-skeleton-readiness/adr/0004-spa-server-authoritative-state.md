---
status: Accepted
owner: "Architect / Tech Lead"
reviewers: ["Tech Lead"]
updated_at: "2026-10-05"
feature_size: "M"
ticket: "walking-skeleton-readiness"
---

# 0004 — Deliver the web surface as an SPA with server-authoritative state

- **Status:** Accepted
- **Date:** 2026-10-03
- **Deciders:** Architect + owner (Socratic walk)

## Context

The browser workspace (SCR-01) must restore the accepted hierarchy after refresh or restart (AC-18/19). The UI-architecture decision for the declared `web-frontend` surface is how the app is delivered (server-rendered vs SPA) and where its state authority lives (client cache vs server).

## Decision drivers

- AC-18 / AC-19 — refresh or restart within the recovery boundary restores the accepted hierarchy and reproduces the same Evidence Status; the server must be the source of truth.
- AC-09 / AC-19 / ux-flows platform decisions — workflow guidance and operation outcomes live in the workspace; the UI derives presentation from server state.
- Existing precedent (`architecture-map.md`, `apps/web/src/App.tsx`): plain Vite SPA, `useState`/`useEffect`, `fetch` — no router, SSR infra, or state library exists.

## Considered options

1. **SPA, client-rendered, server-authoritative state** — React SPA calls the API; on load re-fetches persisted hierarchy and re-derives from the server; minimal client state (in-flight form + last operation outcome); no client cache, no router at this size.
2. **Server-rendered (SSR)** — deliver HTML from the server.
3. **Rich client state (query cache / global store)** — keep durable state in the client.

## Decision outcome

**Chosen:** Option 1 — a client-rendered SPA whose authoritative state is fetched from and re-derived by the server on load/refresh/restart. Option 2 needs SSR infrastructure the repo does not have. Option 3 risks the client becoming the source of truth for recovery and is heavier than one screen warrants.

**Unknown-acceptance clarification:** a received `503 *.save_outcome_unknown` (including lost PostgreSQL COMMIT acknowledgement), a lost POST response, or an unrecognized/unusable POST response leaves acceptance unknown. The SPA does not label it `SAVE_FAILED` or repeat the POST; it blocks creates and reloads the authoritative workspace before continuing (SAD §6). Failed recovery stays `UNAVAILABLE` with GET-only retry. Successful recovery restores current state without retroactively declaring `SAVED` or proving rollback; any subsequent create requires an explicit user action from the recovered context and carries no duplicate-free retry guarantee. This uses the existing server-authoritative recovery boundary, without idempotency machinery.

## Consequences

**Positive**
- Recovery (AC-18/19) is real: the browser re-reads server state rather than trusting any in-memory or cached copy.
- Matches the existing `App.tsx` precedent; no new dependencies (no router, no state library).

**Negative**
- An extra fetch on load before the workspace can render; trivial at this scale.

**Neutral**
- When multiple screens arrive, a router is added; the server-authoritative stance is unchanged.

## Links

- Spec: [[../spec.md]]
- SAD: [[../sad.md]] §4, §5
- Related ADR: [[0001-target-surfaces-backend-service-web-frontend]]
