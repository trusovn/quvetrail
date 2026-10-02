---
status: Living
updated_at: "2026-10-03"
---

# Domain Context — walking-skeleton-readiness

## Glossary

- Environment — A named deployed target within one Project, such as QA or staging, for which verification applicability may be assessed. NOT a Verification Target: an Environment is the continuing context, while a Verification Target is the required configuration being assessed.
- Evidence Status — The system-derived state of evidence availability and applicability for a Verification Target: `NO_EVIDENCE`, `MATCH`, `MISMATCH`, or `UNAVAILABLE`. NOT a test-run outcome or Readiness: `MATCH` and `MISMATCH` compare configuration contexts, while `NO_EVIDENCE` and `UNAVAILABLE` state why no applicability conclusion exists.
- Observed Run State — The configuration recorded as the context against which an external Verification Run actually executed. NOT a Verification Target: the Observed Run State describes what the run exercised, while the Verification Target describes what needs applicable evidence.
- Project — A named workspace for the product or system under verification that groups its Environments, Verification Targets, and recorded evidence. NOT a Release: a Project does not represent a release candidate, approval, or deployment action.
- QA engineer — The trusted primary actor who defines a Verification Target, records an external Verification Run and its Observed Run State, and reviews the resulting Evidence Status. NOT a release approver: QuVeTrail neither grants approval nor acts on a release.
- Readiness — A future broader assessment that may combine evidence applicability, verification outcomes, required coverage, and other policy conditions. NOT an Evidence Status: Readiness is outside the current walking skeleton and cannot be inferred from `MATCH` alone.
- Verification Run — A recorded occurrence of verification performed outside QuVeTrail, identified by a run reference and accompanied by its Observed Run State. NOT test execution or test-outcome evaluation: the walking skeleton neither runs tests nor records whether they passed, failed, broke, or were partial.
- Verification Target — The Environment configuration context for which the QA engineer requires applicable verification evidence in the walking skeleton. NOT a desired-state or deployment-management instruction: it is a comparison target and does not tell QuVeTrail to change the Environment. NOT an Observed Run State: the target states what needs evidence, while the observed state records what a Verification Run actually exercised.

## Invariants

- Evidence Status is derived only from readable authoritative data: no Verification Run produces `NO_EVIDENCE`, exact equality between the Verification Target and Observed Run State produces `MATCH`, a difference produces `MISMATCH`, and unreadable authoritative data produces `UNAVAILABLE` without an applicability conclusion.
- A Verification Run's Observed Run State remains associated with that run so its applicability can always be evaluated against the relevant Verification Target.
- If any authoritative persisted record required to restore the Project → Environment → Verification Target → optional Verification Run hierarchy cannot be read reliably, QuVeTrail reports `UNAVAILABLE` and produces no applicability conclusion.

## Out of scope

- The walking skeleton may expose only one Project, one Environment, one Verification Target, and one Verification Run; this is a temporary scope restriction, not a domain rule that these concepts are singletons or intrinsically immutable.
- Project, Environment, Verification Target, and Verification Run editing, deletion, history, and multiple-record selection are not implemented in this slice; their absence does not define future lifecycle semantics.
- Test execution, test-run outcomes, verification-requirement selection, configurable readiness policies, automatic Environment discovery, integrations, and release decisions are outside this slice.
