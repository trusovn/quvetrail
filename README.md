# QuVeTrail

QuVeTrail is being founded as a browser application that will help a QA engineer assess release readiness from persisted evidence. The current repository is intentionally only a full-stack technical shell: it proves Browser → React → Fastify → PostgreSQL wiring without implementing readiness or other product behavior.

## Prerequisites

- Node.js 24.21.x (the pinned LTS line; see `.node-version` / `.nvmrc`)
- pnpm 12.8.1
- Docker with Docker Compose
- Python 3 (stdlib only, for contract-registry validation)

## Setup and start

```bash
cp .env.example .env
pnpm install --frozen-lockfile
pnpm exec playwright install chromium
pnpm system:start
```

Open <http://localhost:4173>. The page reports whether the browser can reach the API and its PostgreSQL dependency. API health is available at <http://localhost:3000/health>.

Stop without deleting local database state:

```bash
pnpm system:stop
```

`pnpm system:start` is repeatable and applies pending Drizzle migrations before the API starts.

## Canonical commands

| Command | Purpose |
|---|---|
| `pnpm check` | Contract registry, architecture gate/sentinel, typecheck, build, and focused Vitest tests |
| `pnpm test` | Fast focused/unit tests |
| `pnpm test:api` | API/database smoke against the running Compose system |
| `pnpm test:e2e` | Playwright browser smoke against the running Compose system |
| `pnpm check:architecture` | Clean-mode dependency rules plus a controlled forbidden-import sentinel |
| `pnpm check:contracts` | Validate registry shape, generated index, and referenced paths |
| `pnpm smoke:persistence` | Store technical probe data, restart the API, and prove the data remains |
| `pnpm verify` | Canonical full local/CI gate; static checks, Compose start, API/E2E/persistence smoke, teardown |
| `pnpm db:reset` | **Destructive:** remove the local PostgreSQL volume, rebuild, migrate, and start clean |
| `pnpm system:logs` | Show the last 200 Compose log lines |
| `pnpm db:migrate` | Reapply pending migrations inside the running API container |

The committed migration in `apps/api/drizzle/` is the source of truth for database evolution. `apps/api/src/schema.ts` is its editable Drizzle schema input; future schema changes should be generated and reviewed rather than rewriting applied migrations.

## Failure evidence

Startup and dependency failures are written to Compose logs and return non-zero from the canonical scripts. On Playwright failure, inspect `playwright-report/index.html` and `test-results/`; traces, screenshots, and video are retained on failure. CI uploads both directories when present.

Repository ownership and placement rules are in [`docs/project-map.md`](docs/project-map.md). Product and scope authorities are routed from [`AGENTS.md`](AGENTS.md).
