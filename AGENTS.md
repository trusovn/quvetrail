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
