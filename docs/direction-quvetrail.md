# Project Direction: QuVeTrail

Status: accepted

Source: owner conversation on 2026-10-01; `planning/QuVeTrail_Product_Vision.md`; `QuVeTrail_User_Story_Map.md`; `planning/QuVeTrail_User_Story_Map.canvas`; `planning/QuVeTrail_Walking_Skeleton_Plan.md`

## Direction at a glance

- Problem: A QA engineer must assemble environment details and verification results from separate places before they can advise whether a release can proceed.
- Desired experience: The QA engineer can see a clear, explainable, and persisted readiness result based on the environment state and verification evidence QuVeTrail has been given. For now, QuVeTrail informs the release decision; it does not make or enforce that decision.
- First useful proof: In one complete flow, a QA engineer records a release-candidate environment state and the result of one required check, sees `READY` only when that check passed and `NOT_READY` with a simple reason otherwise, and finds the accepted data and result still present after refresh or restart.

## How this should work in practice

| Situation | What should happen | When the owner must step in |
|---|---|---|
| Normal | A QA engineer records the current environment state and one required verification result. QuVeTrail stores both and shows an informational readiness result with its reason. The current environment state stands in for a release candidate during the skeleton. | The QA engineer remains responsible for the actual decision to proceed with the release. |
| Recovery | If a new entry is interrupted or rejected, QuVeTrail preserves all previously accepted data, clearly reports that the new entry was not accepted, and lets the QA engineer retry. | The QA engineer corrects the input or retries after the underlying problem is resolved. |
| Must stop | If QuVeTrail cannot reliably read stored data or complete an operation, it reports the failure and does not present a newly calculated readiness result. It must not turn a system failure into a misleading `READY` or `NOT_READY`. | The QA engineer or operator resolves the data or system problem before relying on a new result. |

## Priorities and conflict rule

1. Prove one complete, real, persisted path from recorded environment state and verification evidence to an informational readiness result.
2. Preserve trustworthy behavior: never report `READY` without the required evidence, and never lose previously accepted data after a failed operation.
3. Keep the path replaceable at its intended seams so later readiness logic, additional states, and integrations can be added without rebuilding the whole flow.
4. Keep the skeleton narrow, simple, reproducible, and understandable.
5. Defer product breadth, polished user experience, and sophisticated business logic to MVP planning.

Conflict rule: Trustworthy persisted behavior wins over speed. A coherent end-to-end path wins over breadth. Future replaceability warrants a small explicit seam, but not speculative frameworks or unused configurability.

## Scope

### In scope

- A small project and environment context in which a QA engineer can perform the proof.
- Manual entry of one current environment-state value and one fixed required verification result.
- A binary, informational readiness result: the required check passed means `READY`; a failed or missing check means `NOT_READY`.
- A simple explanation of why the result is `READY` or `NOT_READY`.
- Real persistence of accepted data across page refresh and application restart.
- Clear failure feedback, retry after an unsuccessful write, and preservation of previously accepted data.
- A repeatable end-to-end demonstration that establishes the framework on which MVP behavior can be built.

### Not in scope

- A separate Release concept; the current environment state stands in for a release candidate during the skeleton.
- Release approval, release triggering, or enforcement of a release gate.
- Automated delivery, test, or observability integrations.
- Configurable readiness rules, complex business logic, or readiness states beyond `READY` and `NOT_READY`.
- Change analysis, affected-area calculation, or deciding which verification is required.
- History, comparison, or audit behavior beyond retaining the data needed for the skeleton proof.
- Correction or deletion of accepted product data.
- Authentication, roles, permissions, or advanced multi-user behavior.
- Production deployment, hostile-user protection, or polished user experience.
- AI-driven product behavior.
- The first MVP slice; that will be governed separately after the skeleton is complete.

## Boundaries

### Trust

- Trusted: A QA engineer using a local or otherwise controlled installation, and the installation's ability to retain data once it reports that data as accepted.
- Fallible or untrusted: Manually entered environment and verification data are user assertions. They require basic validation but are not independently proven true or traced to an authoritative external source during the skeleton.
- Not a design target: Hostile users, production-grade access control, independent evidence authenticity, and regulated or high-assurance release control.

### Intervention and decision ownership

- May proceed without asking: QuVeTrail may accept valid manual entries, retain them, apply the fixed readiness check, and display the result and reason.
- Must ask or stop: QuVeTrail must not calculate a new result from unreadable data, treat a failed operation as accepted, invent missing evidence, or take action on an actual release. Invalid input or a storage/read failure must be shown to the QA engineer for correction or retry.
- Owner-controlled changes: The primary user, informational-only role, priority order, conflict rule, trust assumptions, release-decision boundary, and skeleton scope may not be changed by downstream technical planning.

## Direction ledger

### Confirmed decisions

- The first user is the QA engineer.
- The user question QuVeTrail ultimately helps answer is: “Can this release proceed?”
- During the skeleton, current environment state may stand in for a release candidate; a separate Release concept is deferred.
- The skeleton is a framework proof before MVP, not the MVP itself.
- Temporary simple logic is acceptable when the end-to-end path has appropriate replacement seams for later product logic.
- QuVeTrail currently provides information only. A human retains the release decision, and QuVeTrail neither approves nor triggers a release.
- One fixed required check and binary `READY`/`NOT_READY` behavior are sufficient for the skeleton.
- Additional readiness states should remain possible later, but they do not require unused configurability in the skeleton.
- Accepted state must be persisted realistically and must survive a later failed operation.
- Manual entry through the user interface or supported system interface is acceptable; integrations are deferred.
- The skeleton assumes a trusted QA engineer in a controlled installation.
- Manual entries are accepted as unverified user assertions.
- Data correction and deletion are deferred; the skeleton assumes valid data and supports retry after unsuccessful input.
- The priority order and conflict rule in this document are owner-confirmed.

### Recommendations awaiting approval

- None.

### Assumptions

- The exact label used for the fixed required check does not carry product meaning and may be chosen during technical planning.
- “Refresh or restart” requires accepted product data to remain available, but does not by itself require a complete historical or audit model.

### Unresolved direction questions

- The first MVP slice and its useful product logic remain intentionally unresolved until the skeleton is complete. This does not block skeleton planning or implementation, but it prevents the broader story map from being treated as committed MVP scope.

## Contract for technical planning

- Technical work must cite the direction outcome, scenario, priority, or boundary it advances.
- Technical work may choose implementation details inside this direction.
- Technical work may not silently add product behavior, reorder priorities, raise or lower assurance, change trust or intervention boundaries, or widen scope.
- If such a choice is needed, return a plain-language direction delta for owner approval before making the technical task implementation-ready.

## Source notes

- The Product Vision Board and User Story Map describe a substantially broader product. They are useful sources for future direction but are not committed skeleton or MVP scope.
- The story map explicitly has no MVP cut. No release slice should be inferred from its activity order.
- The Walking Skeleton Delivery Plan supplies a compatible candidate demonstration, but its technology stack, delivery stages, testing levels, and work order are technical proposals rather than governing product direction.
- The broad vision discusses release readiness while the skeleton has no Release concept. The confirmed temporary boundary is to treat current environment state as the release candidate until later planning decides otherwise.
