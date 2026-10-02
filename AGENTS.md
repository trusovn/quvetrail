<!-- personal-skills:development-install:begin -->
## Skill installation resolution

This block is managed by the `personal-skills` development-profile installer.
Rerun the installer to update it; keep repository-specific instructions outside
these markers.

- When work in the current repository uses a named skill and a matching project-local copy exists under `.agents/skills/`, resolve and read that project-local copy before considering user-global skill paths. Do not probe or switch to a user-global copy after a matching project-local skill has been selected for the invocation.
- Resolve shared tooling from the same installation root as the active skill. For a project-local `.agents/skills/` installation, use only the sibling `.agents/scripts/`; do not mix project-local skills with user-global helpers or vice versa.
- If optional shared tooling is missing or unavailable, follow the active skill's documented fallback behavior. Do not silently replace it with tooling from another installation root.
<!-- personal-skills:development-install:end -->

## Repository routing

- Start with `README.md` for setup and canonical commands.
- Read `docs/project-map.md` for module ownership, placement rules, and verification scope.
- Discover currently implemented reusable contracts through `docs/contracts/index.json`; it is generated from subsystem records and is intentionally empty until application contracts exist.
- Product direction is governed by `docs/direction-quvetrail.md`; the current foundation scope is governed by `docs/project-charter.md` and `docs/foundation-plan.md`.

## Maintainability

- Keep each changed module focused on one clear responsibility.
- Keep changes local to the owning subsystem; avoid unrelated edits.
- Keep dependencies explicit and narrow. Deterministic domain logic must not depend on UI, transport, persistence, or global state.
- Keep important logic testable without external I/O where practical.
- Prefer existing patterns; add abstraction only for a concrete boundary, variation, or test seam.
- Before handoff, run `pnpm check:architecture`. Fix hard failures; heuristic maintainability observations belong in review rather than this gate.

## Verification execution policy

- Start with targeted local/static checks; ensure dependencies and the required system are ready before dependent checks. A user request to implement a task authorizes its prescribed bounded local verification, including real PostgreSQL tests, local Compose startup/teardown, E2E and restart/persistence smoke. Reuse prior authorization for that scope; real-system access alone does not require fresh approval. A planning/review request or a task file's existence does not authorize executing the feature's system checks.
- Ask before checks outside that authorization that are slow, flaky, privileged, live-networked or otherwise expensive, including downloads/builds needing external access. Explicit authorization must cover the target and data loss for destructive reset (`pnpm db:reset` / volume deletion); normal implementation or `pnpm verify` authorization does not imply reset permission. Test-owned cleanup/rollback is limited to the authorized isolated disposable fixture, never accepted user data. Tool/sandbox approval requirements still apply.
- Report commands, results, retained evidence and required checks left unrun. Follow this policy from task DoDs rather than requiring separate approval for every check class.

## Implemented-contract handoff

- For each bounded implementation, report deliverables, actual durable cross-task contract impact (or none), and changed executable-contract declarations. After the architecture gate and maintainability review, run `task-contract-registry-updater` before acceptance; repeat synchronization if later correction changes the contract. This separate stage may update affected `docs/contracts/` records and stale discovery references beyond the implementer's production `files_hint`.
- Register only contracts that actually exist and future tasks can depend on: durable interfaces, persistence ownership/invariants, integration/lifecycle boundaries and reusable test capabilities. Exclude planned surfaces and private helpers. Regenerate with `pnpm check:contracts:index` and validate with `pnpm check:contracts`. T16 reconciles the completed feature's registry and documentation; it is not the first registry update.

Don't launch subagents without explicit approval. You may use ollama-guided skill for separate/independent research, 
analysis, verification, and similar work. Use models according to their capabilities.
