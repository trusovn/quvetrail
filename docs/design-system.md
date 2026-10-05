---
status: Living
tool: code
figma_file: ""
pen_file: ""
updated_at: "2026-10-05"
---

# Design system — QuVeTrail

The project's design canon for `ux-flows`, `screens`, `implement`, and `review`.
The tool choice, platform posture, and conventions are team-wide. The implemented
code inventory remains in `docs/architecture-map.md` §Frontend / UI foundation.
Refresh this canon with `$sdd-design-system` when the UI foundation changes.

## Platform posture

- **Posture:** desktop-first — the QA engineer's evidence workspace is designed first for work at a computer, matching `docs/features/walking-skeleton-readiness/ux-flows.md:17`.
- **Breakpoints / device classes:** desktop is primary; no fixed breakpoints are established. The foundation stylesheet has a 320px body minimum and a fluid content width (`apps/web/src/styles.css:8`, `apps/web/src/styles.css:14`); these are existing layout precedents, not a promise of feature support on phones.

## Design tool

- **Tool:** code — screens use inline Markdown wireframes in their feature's `screens.md`; React and CSS implement the visual presentation. No Figma or Pencil integration is required or available in this session.
- **Library location:** implemented reusable components belong in `apps/web/src/`. None exist yet; the current `App` is a foundation-health screen, not a reusable component (`docs/architecture-map.md:76`, `docs/architecture-map.md:79`).
- Wireframes describe structure and states; confirm the implemented visual presentation in the browser. The current feature manifest is `docs/features/walking-skeleton-readiness/screens.md`.

## Token source

`apps/web/src/styles.css` is the initial styling source. It contains literal values,
not named design tokens or CSS custom properties. This canon does not create tokens
or introduce a styling library; future shared token definitions should be recorded
here when implemented, and screens should reference that source rather than define
independent palettes or scales.

- **Colors:** root foreground `#17211b` and background `#eef3ed` (`apps/web/src/styles.css:1`); status surface, border, and health indicators (`apps/web/src/styles.css:33`, `apps/web/src/styles.css:45`). Health indicator colors have infrastructure meanings; they do not define the semantics of evidence applicability.
- **Spacing / sizing:** fluid content width (`apps/web/src/styles.css:14`); status gap, padding, and radius (`apps/web/src/styles.css:33`). These are initial precedents, not a formal spacing scale.
- **Typography:** `Inter, ui-sans-serif, system-ui, sans-serif` (`apps/web/src/styles.css:4`); eyebrow and fluid heading styles (`apps/web/src/styles.css:19`, `apps/web/src/styles.css:27`). No bundled Inter font is established by this stylesheet; system fallbacks apply when it is unavailable.

## Component inventory

No reusable primitives are implemented yet (`docs/architecture-map.md:79`).

| Component | Source (`file:line` / node / URL) | States it supports | Notes |
|---|---|---|---|

The proposed `WorkspaceHierarchy`, `RecordForm`, `OutcomeBanner`, and
`EvidenceStatusPanel` remain `NEW:` in
`docs/features/walking-skeleton-readiness/screens.md:230`. Their responsibilities
and state coverage are defined there. Register each here with its actual code
source and supported states after implementation; proposed components are not
available for reuse yet.

## Interaction & writing conventions

- **Errors:** show the operation outcome inline in the workspace, preserve previously accepted data after a failed save, and provide retry where allowed. An unreliable workspace read shows `UNAVAILABLE` without an applicability conclusion (`docs/features/walking-skeleton-readiness/screens.md:39`, `docs/features/walking-skeleton-readiness/screens.md:40`).
- **Empty states:** use plain guidance and the next available recording action; dependent actions carry their prerequisite explanations (`docs/features/walking-skeleton-readiness/screens.md:35`).
- **Loading:** use explicit checking/loading text, following `apps/web/src/App.tsx:25`. While the authoritative workspace read is pending, render no hierarchy or evidence conclusion; disable the active form during saving (`docs/features/walking-skeleton-readiness/screens.md:36`, `docs/features/walking-skeleton-readiness/screens.md:37`).
- **Validation:** validate submitted values and display field-specific errors inline, retaining an in-place correction/retry path (`docs/features/walking-skeleton-readiness/screens.md:38`). No on-blur validation convention is established.
- **Microcopy tone:** use plain, factual wording that states what was accepted, what failed, and what the user can do next. `MATCH` and `MISMATCH` describe evidence applicability only; missing evidence is workflow guidance, not a test outcome or release Readiness (`docs/features/walking-skeleton-readiness/ux-flows.md:21`).
- **Accessible feedback:** keep operation feedback in an `aria-live` region and convey status with text rather than color alone, following `apps/web/src/App.tsx:25` and the feature's `OutcomeBanner` contract (`docs/features/walking-skeleton-readiness/screens.md:241`).
