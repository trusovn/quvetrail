---
status: draft
feature_size: "M"
tool: "code"
updated_at: "2026-10-05"
---

# Screens — walking-skeleton-readiness

> The canonical **screen manifest** — every screen in every state — produced by `screens` (between
> `api` and `tasks`) and read by `tasks` (each `ui` task cites SCR ids + states), `implement`
> (builds the screen to the declared states) and `review` (the built screen must match this).
> Downstream stages reference **only this manifest** — never the raw Figma / `.pen` file.

## Source

- **Tool:** `code` — the committed `docs/design-system.md` canon selects inline Markdown
  wireframes, desktop-first posture, and `apps/web/src/styles.css` as the initial styling
  source. No Figma or Pencil integration is required.
- **File:** inline wireframes below — this manifest is the only artifact downstream stages consume.

## Screens

### SCR-01 — Evidence applicability workspace

One progressive browser workspace (ux-flows.md platform decisions): the QA engineer records the
hierarchy level by level, sees every operation outcome, and reads the Evidence Status area. All
states below are **derived** — each non-default state traces to a spec §5 AC, a sad.md §6
`alt`/`else` branch, or a contract error response; nothing is invented. Posture: web-first,
desktop resolution.

| State | Trigger / condition | Components (from the inventory) | Source-ref |
|---|---|---|---|
| default | `getWorkspace` 200 restores a partial hierarchy — Project only or Project + Environment (AC-19a): accepted levels listed, the next record action offered, every further dependent action unavailable with its prerequisite explanation (AC-17a, AC-04/AC-07/AC-13 — the contract's 409 envelopes carry these same explanations, which the UI normally never sees because the actions are gated); no Evidence Status area before a Verification Target is accepted | NEW: WorkspaceHierarchy, NEW: RecordForm | wireframe W1 |
| empty | `getWorkspace` 200 with every level null (fresh installation — US-08 `empty_workspace` example): only the Project action offered; Environment, Verification Target, and Verification Run actions unavailable with prerequisite explanations | NEW: WorkspaceHierarchy, NEW: RecordForm | wireframe W2 |
| loading | `getWorkspace` in flight after open / refresh / restart (sad.md §6 Critical flow 2): no hierarchy level, action, or status rendered before the authoritative read returns — the SPA trusts no client cache (ADR-0004) | NEW: WorkspaceHierarchy (loading presentation) | wireframe W3 |
| saving | A valid record has been submitted and durable acceptance is pending (AC-17): the active form is disabled, `SAVED` is not shown, and the pending record is not used to derive Evidence Status | NEW: RecordForm (disabled), NEW: WorkspaceHierarchy | wireframe W4 |
| validation | A create operation returns 400 `VALIDATION_ERROR` — the submitted name / key / value / run reference is empty after trimming (AC-02, AC-05, AC-08, AC-12): inline error naming known failed fields (`ValidationError.details.fields`); structural `request.invalid_body` uses the same envelope, with unknown paths / `$` shown at form level, nothing recorded, retry in place | NEW: RecordForm, NEW: OutcomeBanner | wireframe W5 |
| error — save failed | A create operation returns operation-specific 503 `*.save_failed` — non-acceptance is known (AC-16, sad.md §6 Critical flow 3): none of the attempted record accepted, all previously accepted levels still rendered unchanged, retry offered | NEW: OutcomeBanner, NEW: WorkspaceHierarchy | wireframe W6 |
| recovery — save outcome unknown | Received operation-specific 503 `*.save_outcome_unknown`, POST transport/network failure, or unrecognized/unusable POST response: explain acceptance cannot be confirmed, do not show SAVE_FAILED/SAVED or repeat POST; block creates and reload `getWorkspace`. Replace hierarchy on successful recovery and continue from it; failed recovery shows UNAVAILABLE with GET retry only (SAD §6) | NEW: OutcomeBanner, NEW: WorkspaceHierarchy | recovery presentation below |
| error — unavailable | `getWorkspace` transport failure or 503 `workspace.unavailable` — an authoritative record cannot be read reliably or accepted relationships are malformed / inconsistent (AC-20, sad.md §6 Critical flow 2 `else` branch): `UNAVAILABLE` with the cannot-currently-be-relied-upon explanation, no MATCH/MISMATCH, no hierarchy conclusion | NEW: EvidenceStatusPanel (unavailable presentation) | wireframe W7 |
| success | A create operation returns 201 — durable acceptance completed: `SAVED` shown in the record's own context and the next dependent action unlocked (AC-01, AC-03, AC-06); a saved Verification Run additionally transitions the Evidence Status area to `evidence — MATCH` or `evidence — MISMATCH` (AC-10/AC-11) | NEW: OutcomeBanner, NEW: WorkspaceHierarchy | wireframe W8 |
| guidance (NO_EVIDENCE) | `getWorkspace` 200 with a Verification Target accepted and `evidence_status: "NO_EVIDENCE"` (AC-09, AC-19): the domain value is rendered as workflow guidance — a Verification Run has not been recorded yet — plus the run-entry action; never as an assessment result beside MATCH/MISMATCH | NEW: EvidenceStatusPanel (guidance presentation) | wireframe W9 |
| evidence — MATCH | A Verification Run is accepted with exact trimmed key-and-value equality (201 `evidence_status: "MATCH"`, AC-10) or restored after refresh / restart (`getWorkspace` `MATCH`, AC-14, AC-18): status shown with the applicability-only explanation (AC-15) | NEW: EvidenceStatusPanel (result presentation) | wireframe W10 |
| evidence — MISMATCH | A Verification Run is accepted with any key or value difference (201 `MISMATCH`, AC-11) or restored (`getWorkspace` `MISMATCH`, AC-14, AC-18): same result presentation with the applicability-only explanation (AC-15) | NEW: EvidenceStatusPanel (result presentation) | wireframe W10 |

The wireframes are **structural, not visual**: layout intent is
described, not styling — the implementation follows `docs/design-system.md`, plain global CSS, and the
`App.tsx` state-feedback / `aria-live` precedent (`docs/architecture-map.md` §Frontend).

**W1 — SCR-01 default** (example: Project + Environment accepted, next action available, later
actions gated with explanations):

```text
+--------------------------------------------------------------------+
| QuVeTrail — Evidence applicability workspace                       |
+--------------------------------------------------------------------+
| Hierarchy (accepted levels only)                                   |
|   Project             "Test Project"                     [accepted] |
|   Environment         "QA"                               [accepted] |
|   Verification Target — [ Define Verification Target ]  (available) |
|   Verification Run     (action unavailable)                         |
|     A Verification Run requires a Verification Target.             |
|     Define the Verification Target first.                          |
+--------------------------------------------------------------------+
| Record a Verification Target                                      |
|   key   [ browser          ]    value [ chrome-130        ]         |
|                                    [ Save Verification Target ]   |
+--------------------------------------------------------------------+
| Evidence Status                                                    |
|   (not shown before a Verification Target is accepted — AC-19a)    |
+--------------------------------------------------------------------+
| last outcome: (none)                                    [aria-live]|
+--------------------------------------------------------------------+
```

**W2 — SCR-01 empty** (nothing accepted; only the Project action is offered):

```text
+--------------------------------------------------------------------+
| QuVeTrail — Evidence applicability workspace                       |
+--------------------------------------------------------------------+
| Hierarchy                                                          |
|   Project             — no Project accepted yet                    |
|   Environment         (action unavailable)                         |
|     An Environment requires a Project context.                     |
|     Create the Project first.                                      |
|   Verification Target (action unavailable)                         |
|     A Verification Target requires an Environment.                 |
|   Verification Run    (action unavailable)                         |
|     A Verification Run requires a Verification Target.             |
+--------------------------------------------------------------------+
| Create the Project                                                 |
|   name [                    ]            [ Save Project ]           |
+--------------------------------------------------------------------+
| Evidence Status                                                    |
|   (not shown before a Verification Target is accepted — AC-19a)    |
+--------------------------------------------------------------------+
| last outcome: (none)                                    [aria-live]|
+--------------------------------------------------------------------+
```

**W3 — SCR-01 loading** (authoritative read in flight; nothing rendered from non-authoritative
data):

```text
+--------------------------------------------------------------------+
| QuVeTrail — Evidence applicability workspace                       |
+--------------------------------------------------------------------+
| Hierarchy                                                          |
|   [ loading the authoritative workspace … ]                       |
|   No level, action, or status is rendered from anywhere other      |
|   than the authoritative read (server-authoritative — ADR-0004).   |
+--------------------------------------------------------------------+
| (record actions are not offered while the read is in flight)       |
+--------------------------------------------------------------------+
| last outcome: (none)                                    [aria-live]|
+--------------------------------------------------------------------+
```

**W4 — SCR-01 saving** (example: Verification Target submitted, acceptance pending — AC-17):

```text
+--------------------------------------------------------------------+
| Record a Verification Target                                      |
|   key   [ browser          ]    value [ chrome-130        ]         |
|   (inputs disabled — durable acceptance in progress … — AC-17)     |
|                                    [ Save Verification Target ]   |
|                                    (disabled)                      |
+--------------------------------------------------------------------+
| Hierarchy (unchanged — the pending record is not part of it yet)   |
+--------------------------------------------------------------------+
| Evidence Status (unchanged — no status is derived from the         |
|   pending record until durable acceptance completes — AC-17)       |
+--------------------------------------------------------------------+
```

**W5 — SCR-01 validation** (example: empty Verification Target value — AC-08):

```text
+--------------------------------------------------------------------+
| Record a Verification Target                                      |
|   key   [ browser          ]    value [           ]  <- failed field |
|                                    [ Save Verification Target ]   |
+--------------------------------------------------------------------+
| last outcome: VALIDATION_ERROR                          [aria-live]|
|   Verification Target value must be non-empty after trimming.       |
|   Nothing was recorded. Correct the highlighted field and save     |
|   again.                                                           |
+--------------------------------------------------------------------+
```

**W6 — SCR-01 error — save failed** (example: Verification Target non-acceptance confirmed — AC-16):

```text
+--------------------------------------------------------------------+
| Hierarchy (previously accepted levels — unchanged, AC-16)          |
|   Project             "Test Project"                     [accepted] |
|   Environment         "QA"                               [accepted] |
+--------------------------------------------------------------------+
| last outcome: SAVE_FAILED                               [aria-live]|
|   The Verification Target could not be durably accepted. Nothing   |
|   from this attempt was recorded; previously accepted data is       |
|   preserved. You can retry.                                         |
+--------------------------------------------------------------------+
```

**W7 — SCR-01 error — unavailable** (workspace read failed — AC-20):

```text
+--------------------------------------------------------------------+
| QuVeTrail — Evidence applicability workspace                       |
+--------------------------------------------------------------------+
| Evidence Status                                                    |
|   UNAVAILABLE — the recorded evidence context cannot be read       |
|   reliably and cannot currently be relied upon. No applicability   |
|   conclusion is shown (no MATCH or MISMATCH) — AC-20.               |
+--------------------------------------------------------------------+
| (no hierarchy conclusion is rendered; the workspace read can       |
|  be retried)                                             [aria-live]|
+--------------------------------------------------------------------+
```

**W8 — SCR-01 success** (example: Verification Target saved — AC-06; SAVED in the record's own
context, next action unlocked):

```text
+--------------------------------------------------------------------+
| Hierarchy                                                          |
|   Project             "Test Project"                     [accepted] |
|   Environment         "QA"                               [accepted] |
|   Verification Target "browser" = "chrome-130"          [accepted] |
|   Verification Run    — [ Record a Verification Run ]  (available)  |
+--------------------------------------------------------------------+
| last outcome: SAVED                                     [aria-live]|
|   The Verification Target was durably accepted.                    |
+--------------------------------------------------------------------+
| Evidence Status                                                    |
|   A Verification Run has not been recorded yet — evidence         |
|   applicability cannot be concluded. (workflow guidance — AC-09)  |
+--------------------------------------------------------------------+
```

**W9 — SCR-01 guidance (NO_EVIDENCE)** (target accepted, run absent — AC-09/AC-19):

```text
+--------------------------------------------------------------------+
| Evidence Status                                                    |
|   A Verification Run has not been recorded yet.                    |
|   Evidence applicability cannot be concluded until a run and its   |
|   Observed Run State are recorded. This is workflow guidance,      |
|   not an assessment result — AC-09 / AC-19.                        |
|   [ Record a Verification Run ]   <- run-entry action               |
+--------------------------------------------------------------------+
```

**W10 — SCR-01 evidence result** (MATCH shown; `evidence — MISMATCH` renders the identical
layout with the `MISMATCH` token and the differing observed value named — AC-14/AC-15):

```text
+--------------------------------------------------------------------+
| Evidence Status                                                    |
|   MATCH — the recorded Verification Run's Observed Run State       |
|   exactly equals the Verification Target: browser = chrome-130.    |
|   Run "run-001" · observed browser = chrome-130                    |
|   This describes evidence applicability only — it is not a test    |
|   outcome and says nothing about release Readiness — AC-15.        |
+--------------------------------------------------------------------+
```

**SCR-01 recovery — save outcome unknown:** show “The save outcome could not be confirmed. Reloading the recorded workspace…” in the live feedback region. Disable create actions while the authoritative GET is pending. On success show the recovered accepted levels and their server-derived status, without inventing a SAVED response. On failure use W7 UNAVAILABLE with a “Reload workspace” GET action; create actions remain disabled. Both a received server unknown-outcome response and POST response loss use this presentation (AC-16a). Any create after reliable recovery requires an explicit user action from recovered context; snapshot absence does not establish rollback or duplicate-free retry. This is operation recovery feedback, not a new Evidence Status.

## New components

The canon's implemented component inventory is empty (the repo has no shared UI primitives —
`docs/architecture-map.md` §Frontend), so every component is `NEW:` with its
why-no-primitive-fits line. After implementation, register each with its actual code source
in `docs/design-system.md` §Component inventory.

| Component | Why no existing primitive fits | Registered in design-system |
|---|---|---|
| WorkspaceHierarchy | No primitive exists at all; the progressive gated-levels list (accepted levels + unavailable dependent actions + prerequisite explanations, AC-17a) is a distinct responsibility no generic primitive would cover. | pending |
| RecordForm | No primitive exists; one entry form reused by all four record actions (Project name / Environment name / Target key+value / Run reference + Observed key+value) with disabled-while-pending (AC-17) and in-place retry behavior. | pending |
| OutcomeBanner | No primitive exists; an `aria-live` last-operation region (SAVED / VALIDATION_ERROR / SAVE_FAILED plus unknown-outcome recovery feedback) following the `App.tsx` state-feedback precedent (`docs/architecture-map.md` §Frontend, "Closest UI precedent"). | pending |
| EvidenceStatusPanel | No primitive exists; the presentation rules are domain-specific — hidden before a Target (AC-19a), guidance-not-result for `NO_EVIDENCE` (AC-09/AC-19), applicability-only wording for MATCH/MISMATCH (AC-15), UNAVAILABLE with no conclusion (AC-20). | pending |
