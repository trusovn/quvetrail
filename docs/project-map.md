# Implemented system map

Verified against the repository tree on 2026-10-02.

## System path

```text
Browser → apps/web (React/Vite) → apps/api (Fastify) → PostgreSQL (Compose)
```

This is a technical foundation path only. The UI and API health route establish wiring and fail visibly when storage is unavailable. `foundation_probe` is technical smoke state, not a product entity. Product behavior remains deferred by `docs/foundation-plan.md`.

## Ownership and placement

| Path | Responsibility / next precedent |
|---|---|
| `apps/web/src/` | Browser UI. New screens and client adapters stay here and communicate through HTTP; never import API/database internals. |
| `apps/api/src/` | Fastify composition, validated runtime config, persistence adapter, and future API-owned behavior. `app.ts` is the nearest route/composition precedent. |
| `apps/api/src/domain/` | Reserved placement for future deterministic product rules when they exist; do not create empty layers or put transport/persistence dependencies here. |
| `apps/api/drizzle/` | Committed migration history generated from `apps/api/src/schema.ts`. Applied migrations are durable and are not edited in place. |
| `tests/api/` | Deployed API/database integration smoke. |
| `tests/e2e/` | Short user-observable browser/system paths only. |
| `tools/` | Testable repository validators and generators. |
| `scripts/` | Thin human/CI command wrappers. |
| `docs/contracts/` | Implemented reusable contracts only. Subsystem files are authoritative; `index.json` is generated. The empty baseline is intentional. |

Do not add shared code until two real consumers need it. Co-locate focused tests with the owning app; keep deployed-system tests under root `tests/`.

## Canonical verification

Commands are defined in root `package.json` and summarized in `README.md`. `pnpm check` is the fast local gate; `pnpm verify` adds Compose, real PostgreSQL, API, browser, restart persistence, and teardown. The direct architecture command is `pnpm check:architecture`.

Architecture enforcement is `CLEAN`, configured by `.dependency-cruiser.cjs`, with no baseline or exceptions. Hard rules are:

- `no-web-to-server`: browser code cannot import API/database internals;
- `no-domain-to-outer-layers`: future deterministic domain code cannot import transport or persistence;
- `no-production-to-tests`: production code cannot import test-only code.

Heuristic size, complexity, and fan-out signals are not blocking gates.

## Configuration, generated files, and state

- `.env.example` is the local environment contract; `.env` is ignored and required by start/reset commands.
- `compose.yaml` owns the local/test service topology and persistent `postgres-data` volume.
- `pnpm-lock.yaml` is generated and committed; update it only through pnpm.
- `dist/`, Playwright reports, test results, and local environment files are generated and ignored.
- Resetting with `pnpm db:reset` deletes local database state. Normal stop/start retains it.

## Authoritative direction

- Product direction: `docs/direction-quvetrail.md`
- Foundation boundaries: `docs/project-charter.md`
- Authorized foundation work and deferrals: `docs/foundation-plan.md`
- Currently implemented reusable contracts: `docs/contracts/index.json`
