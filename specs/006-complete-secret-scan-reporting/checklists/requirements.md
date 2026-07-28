# Specification Quality Checklist: Complete Secret-Scan Reporting

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-07-27
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Governance Coverage

- [x] Data Classification section names classification owner, level, retention, residency, sharing, and redaction
- [x] Tagging Discipline section covers owner, system, environment, data-classification, and retention
- [x] Trust Boundaries are explicit, including the one-way boundary that matched content must never cross
- [x] Security Requirements are stated as testable MUST statements
- [x] Misuse / Abuse Cases each carry a concrete detection and mitigation
- [x] Evidence artifacts are named with their audience and generator
- [x] AI / LLM Risk section states that the verdict is deterministic and never model-decided
- [x] Fleet Guardrails cover idempotency, retry, dead-letter, workflow state, and human approval

## Defect Framing

- [x] The defect is characterized precisely as a completeness-of-reporting defect, not a gate bypass
- [x] The specification states plainly that the pass/fail verdict is unchanged before and after
- [x] The reason incomplete evidence still matters is argued rather than asserted
- [x] Downstream undercount in JSON and SARIF output is named as a concrete consequence

## Reporting Granularity Decision

- [x] File-level versus line-level granularity is decided, not deferred
- [x] The recommendation (line-level, one finding per matching line) is justified against the alternative
- [x] Same-line multiple matches are resolved to one finding with a stated rationale
- [x] The location shape is specified so that SARIF artifact locations stay resolvable
- [x] The adjacent inconsistency in existing importers is recorded and explicitly scoped out

## Output Volume Controls

- [x] Caps are specified with both per-file and per-rule scope
- [x] Cap ordering (per-file applied before per-rule) prevents one file from consuming the budget
- [x] Silent truncation is prohibited by an explicit MUST
- [x] The overflow finding is mandatory, unsuppressible, and carries the truncated rule's severity
- [x] Suppressed and total counts are exact rather than lower bounds
- [x] Invalid cap values are rejected at load rather than clamped or defaulted
- [x] Caps are proven not to participate in the pass/fail decision

## Determinism

- [x] A total ordering is specified (POSIX path, then line, then column)
- [x] Ordering independence from filesystem enumeration, locale, and platform is required
- [x] Caps are applied after ordering so truncated runs remain stable
- [x] A repeat-run byte-identical assertion exists in Success Criteria

## Backward Compatibility

- [x] Gate summary additions are required to be additive, with existing keys unchanged
- [x] The behavior of `finding_count` after the change is stated, including that it will increase
- [x] Existing tests are checked and confirmed to assert code presence, not counts
- [x] The change applies to the evaluator kind as a whole, not only the shipped secret rule
- [x] Documentation surfaces requiring updates are enumerated

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification
- [x] Nothing specified weakens the stdlib-only, offline, deterministic verify invariant
- [x] Performance cost is quantified honestly rather than dismissed or inflated
- [x] Residual limitations are stated rather than implied as covered
- [x] No new suppression, exclusion, ignore, or baseline mechanism is introduced

## Notes

- Items marked incomplete require spec updates before `/speckit-clarify` or `/speckit-plan`.
- The scanner's residual limitation — complete reporting of matches is not
  complete detection of credentials — is recorded in Assumptions by design.
  Closing it is a detection feature with its own risk profile, not part of this
  completeness fix.
- The prohibition on introducing a suppression mechanism alongside a completeness
  fix is deliberate and should be re-checked at plan and review time, since it is
  the most likely thing to be quietly relaxed during implementation.
