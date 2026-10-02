# Tracker — walking-skeleton-readiness

> States: `todo` · `in_progress` · `blocked` · `review` · `done`. `implement` updates status as tasks are committed.

| # | Task | Layer | Owner | Estimate | Blocked by | Status |
|---|---|---|---|---|---|---|
| T1 | [Promote the staged hierarchy schema into Drizzle history](promote-the-staged-hierarchy-schema-into-drizzle-history.md) | migration | TBD lead | 6h | — | todo |
| T2 | [Implement pure input and evidence-applicability rules](implement-pure-input-and-evidence-applicability-rules.md) | domain | TBD lead | 4h | — | todo |
| T3 | [Implement transactional hierarchy persistence and reliable reads](implement-transactional-hierarchy-persistence-and-reliable-reads.md) | infra | TBD lead | 8h | T1, T2 | todo |
| T4 | [Implement Project and Environment acceptance use cases](implement-project-and-environment-acceptance-use-cases.md) | app | TBD lead | 6h | T2, T3 | todo |
| T5 | [Implement Target and atomic Run acceptance use cases](implement-target-and-atomic-run-acceptance-use-cases.md) | app | TBD lead | 7h | T4 | todo |
| T6 | [Implement authoritative workspace loading and recovery states](implement-authoritative-workspace-loading-and-recovery-states.md) | app | TBD lead | 5h | T2, T3 | todo |
| T7 | [Expose Project and Environment HTTP operations](expose-project-and-environment-http-operations.md) | ports | TBD lead | 6h | T4 | todo |
| T8 | [Expose Target and Run HTTP operations](expose-target-and-run-http-operations.md) | ports | TBD lead | 6h | T5, T7 | todo |
| T9 | [Wire the workspace API and persistence into the existing server](wire-the-workspace-api-and-persistence-into-the-existing-server.md) | wiring | TBD lead | 5h | T6, T7, T8 | todo |
| T10 | [Implement the browser HTTP adapter from the approved contract](implement-the-browser-http-adapter-from-the-approved-contract.md) | ports | TBD lead | 4h | — | todo |
| T11 | [Build the progressive hierarchy and record-entry workspace](build-the-progressive-hierarchy-and-record-entry-workspace.md) | ui | TBD lead | 8h | T9, T10 | todo |
| T12 | [Render evidence guidance, applicability and unavailable states](render-evidence-guidance-applicability-and-unavailable-states.md) | ui | TBD lead | 5h | T11 | todo |
| T13 | [Prove deployed API durability and error contracts](prove-deployed-api-durability-and-error-contracts.md) | tests | TBD lead | 7h | T9 | todo |
| T14 | [Prove progressive browser behavior and refresh recovery](prove-progressive-browser-behavior-and-refresh-recovery.md) | tests | TBD lead | 8h | T12 | todo |
| T15 | [Extend the canonical persistence smoke to product restart recovery](extend-the-canonical-persistence-smoke-to-product-restart-recovery.md) | tests | TBD lead | 6h | T13, T14 | todo |
| T16 | [Document implemented workspace contracts and UI inventory](document-implemented-workspace-contracts-and-ui-inventory.md) | docs | TBD lead | 4h | T15 | todo |

**Total:** 16 tasks, 95h (~11.9 person-days).
