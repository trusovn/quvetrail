# Data-model audit — walking-skeleton-readiness — 2026-10-05

**Stage:** `data-model` (size M, route `standard`). Owner: Backend Lead.

## Staged migration files (NOT in the live tree)

Migrations are staged — not yet in the live `apps/api/drizzle/` tree; `implement` promotes them (assigning the real sequence number) when the `layer: migration` task runs.

| Ordinal | Up | Down |
|---|---|---|
| 01 | `docs/features/walking-skeleton-readiness/migrations/01_create_project.up.sql` | `…/01_create_project.down.sql` |
| 02 | `…/migrations/02_create_environment.up.sql` | `…/02_create_environment.down.sql` |
| 03 | `…/migrations/03_create_verification_target.up.sql` | `…/03_create_verification_target.down.sql` |
| 04 | `…/migrations/04_create_verification_run.up.sql` | `…/04_create_verification_run.down.sql` |
| 05 | `…/migrations/05_create_observed_run_state.up.sql` | `…/05_create_observed_run_state.down.sql` |

Promote order 01→05 preserves intra-feature order and matches FK dependencies (child tables reference parents created earlier). The run + observed-run-state pair (04, 05) belongs to one aggregate but stays two tables; both are promoted before the `recordVerificationRun` use-case code exists — no code reads a half-designed schema meanwhile.

## Promote-time convention hint

The repo uses **Drizzle Kit** with forward-only sequential SQL under `apps/api/drizzle/` (`0000_foundation.sql` is the only entry; journal in `apps/api/drizzle/meta/_journal.json`). Repo is sequential, next ≈ **`0001`** — `implement` assigns the real number at promotion, since another feature may promote first. At promote time, `implement` must also update `apps/api/src/schema.ts` (the editable Drizzle schema is the source that generates/validates the SQL — architecture-map §Migrations: "edit `apps/api/src/schema.ts`, generate and review forward SQL") and the Drizzle journal. Per the architecture-map, there is no committed rollback mechanism (forward-only migrations); the staged `.down.sql` pairs still satisfy this stage's reversibility requirement and serve as the documented reverse path.

**T1 ownership:** allowed paths are `apps/api/src/schema.ts`, `apps/api/drizzle/**`, and `docs/features/walking-skeleton-readiness/migrations/**`. The schema is the editable authority; staged SQL is planning/reference input to the existing Drizzle Kit generation/review mechanism. Add new forward SQL and required generated journal/snapshot metadata; preserve applied SQL (including `0000_foundation.sql`) and retain applied-migration history when updating generated journal/snapshot metadata as required by Drizzle. The five staged ordinals specify table/FK order, not a requirement for five live migration files.

## Conventions detected and followed

- Migration tool: Drizzle Kit / Drizzle ORM migrator (`architecture-map.md` frontmatter `migration_tool`); staged pairs imitate its generated-SQL style (quoted lowercase identifiers, tab indentation, `DEFAULT now() NOT NULL` ordering) as seen in `0000_foundation.sql`.
- Naming: snake_case singular table names, snake_case columns (`foundation_probe` precedent).
- Strings: `text` (repo norm; spec §5 sets no length limits — only trim/non-empty).
- Audit columns: `created_at timestamptz DEFAULT now() NOT NULL` — user-confirmed choice; see Deviations.
- PK: app-generated UUID v7, single-column (ADR-0005, Accepted).
- Constraints: FKs only; no `CHECK`/`TRIGGER`/`UNIQUE`/`DEFAULT` beyond `created_at` — the repo uses none (`0000_foundation.sql` has no CHECKs; SAD §11 forbids encoding singleton assumptions as UNIQUEs).
- Idempotent DDL: `IF NOT EXISTS` on every `CREATE TABLE` / `CREATE INDEX`.

## Deviations (deliberate, flagged)

1. **`created_at` instead of `updated_at`.** The only repo precedent (`foundation_probe`) uses `updated_at` and has no `created_at`. User confirmed `created_at`-only for product tables: this slice's records are insert-only (spec §3 non-goals: no editing), so `updated_at` would never differ from the insert time — a permanently misleading column. `foundation_probe` is explicitly a non-generalizable technical fixture (architecture-map), so matching it literally is not required. If editing arrives in a later slice, `updated_at` is added via expand→backfill→contract.
2. **No UNIQUE constraints for the one-record restriction.** Per SAD §11 risk row (Medium): the restriction is slice scope, held in the application layer, not encoded in the schema.

## Drift findings

N/A — no domain layer exists yet (`apps/api/src/domain/` does not exist per `architecture-map.md` §Module inventory: "reserved for future deterministic product rules"). This feature *creates* the first product schema; there are no struct↔DDL pairs to drift against. No `_drift/*.sql` fixes proposed.

## Breaking-change decompositions

None — greenfield product tables; no existing table is altered, no column is added/renamed/dropped on an existing table, no expand→backfill→contract sequence is required.

## Seeds

None. The slice assumes an initially empty hierarchy (AC-01: "no Project has been recorded"); there is no bootstrap or lookup data. Test fixtures are colocated factory functions (documented in `data-model.md` § Test fixtures), never migrations. PII guard satisfied — no seeds, no person-related fields (spec §6.1).

## Open `<!-- TBD -->` markers

None — all choices were resolved (user-confirmed) at design time.

## Self-check result

4/4 pass (naming vs repo convention; down-reversibility of every up statement; FK-index coverage of all four FK columns; convention adherence with deviations flagged above). Structural ER-diagram lint: pass (no `mmdc`/mermaid dependency available in this environment; per `mermaid-check.md` fallback — valid `erDiagram` cardinality glyphs, `type name` attribute lines, declared entities, no placeholders).