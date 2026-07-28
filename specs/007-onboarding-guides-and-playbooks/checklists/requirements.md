# Specification Quality Checklist: New-User Technical Guide — Onboarding, Playbooks, and Use Cases

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-07-28
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
- [x] Trust Boundaries are explicit, including guide-text-to-reader and guide-text-to-agent as instruction channels
- [x] Security Requirements are stated as testable MUST statements
- [x] Misuse / Abuse Cases each carry a concrete detection and mitigation
- [x] Evidence artifacts are named with their audience and location
- [x] AI / LLM Risk section covers prompt injection and the tool boundary of the docs verification runner
- [x] Fleet Guardrails cover idempotency, retry, dead-letter, workflow state, and human approval

## Walkthrough Coverage

- [x] Both install paths are required (pip install and the Spec Kit bundle path), each with a confirmation step
- [x] The module-form CLI fallback is required before first command use
- [x] Init report reading is specified, including the dry-run per-file plan states
- [x] A staged failure, its finding code, the fix, and the green re-run are all required steps
- [x] Every command is paired with expected output, and a completion-time target exists
- [x] The walkthrough states its assumed platform and shell and notes known divergence points for other platforms
- [x] The selection guide is linked at the init step, before the init command, for readers whose repository differs from the walkthrough scenario

## Playbook Coverage

- [x] The playbook set is enumerated (initial-setup selection guide, brownfield adoption, first-spec loop, spec authoring, custom rule, rule override with evidence, failing-gate investigation, framework selection with tiers, CI wiring, evidence reading)
- [x] A mandatory playbook shape is specified: scenario, starting state, stepwise commands with expected output, success check
- [x] Each playbook is required to be self-contained
- [x] The override playbook is required to show the actual override-evidence record, including the disables-critical impact reading
- [x] The frameworks playbook is required to present supported versus experimental tiers and the not-a-certification statement
- [x] The evidence playbook covers override records, coverage records, excluded-versus-skipped, and the asset-root resolution
- [x] The at-init decision (selection guide) and the in-repo framework-change playbook are explicitly split, with a link instead of repetition
- [x] The first-spec playbook and the spec-authoring playbook are explicitly split (loop versus section depth), with a cross-reference

## Initial Setup Selection Guidance

- [x] A selection guide exists as the initial-setup playbook and is linked from the walkthrough before the init command
- [x] Every shipped profile is covered: repository kind it fits, presets composed, per-preset concrete contributions, framework defaults
- [x] Guide content is required to derive from the shipped composition metadata (profile-to-preset, profile-to-framework, preset manifests), not from memory
- [x] A decision path leads from repository kind to a recommended profile or composition, with the undecided-case baseline stated
- [x] Multi-profile composition behavior is specified (presets merge, framework defaults union)
- [x] The choice-to-enforcement link is required: which sections the composed templates add and which finding codes then enforce them
- [x] The experimental-tier default rule is stated: never selected implicitly, excluded from profile defaults even when listed, enforced only when named explicitly
- [x] Interactive init mode is documented (wizard steps, what it writes, when to prefer it)
- [x] Selection tables carry captured-version and fall under the release staleness discipline, since composition can drift without CLI output drift

## First-Spec Loop

- [x] The full loop is specified: create feature directory, fill template sections in order, run the gate at checkpoints, read findings, reach green
- [x] The baseline path is the universal floor on every adoption path: manual copy of the shipped spec template, shell only
- [x] The feature-creation script is labeled as available only where native Spec Kit scaffolding exists, since `sicario init` targets receive no scripts directory
- [x] Agent-only slash commands are labeled as agent-environment variants and are never presented as generally available
- [x] The playbook's prerequisites enumerate exactly the tooling its baseline path requires
- [x] The template-passes-by-construction honesty is required on both adoption paths (greenfield init and brownfield overlay): a fresh template satisfies the form checks, and the playbook says so
- [x] A deliberate finding-demonstration step is required so the reader sees real spec-contract findings and the fix before their first unplanned one
- [x] The final green run is tied to the evidence artifact (gate summary status and finding count)
- [x] First-run evaluation of this playbook is required to run without a coding-agent environment, validating the path every reader has

## Visual Asset Discipline

- [x] Three capture classes are defined and labeled in the asset record: terminal text, tool-captured, and manual
- [x] Terminal interactions are required to be text blocks, never images of text
- [x] Tool-captured screenshots are automated captures of real rendered surfaces during a real run, reproducible by re-running the capture
- [x] Screenshots are restricted to genuinely graphical surfaces, and one is expected wherever a playbook's flow surfaces a graphical view
- [x] The walkthrough and CI-wiring playbook explicitly require their graphical captures (failing run, passing run, checks panel)
- [x] Asset location and version-embedding naming convention are specified so staleness is computable from file names
- [x] Superseded assets must be replaced and deleted in the same change
- [x] Screencasts are optional and never load-bearing
- [x] MANUAL CAPTURE is reserved for surfaces genuinely requiring a human desktop; tool-reachable surfaces must use the tool-captured class
- [x] Fabricated or synthetic visual assets are prohibited outright for every class; tool capture of a real surface is the legitimate automated channel
- [x] The sanitation review applies identically to tool-captured and manual assets

## Reference Run

- [x] Quoted outputs and captures are required to come from a reference run: a net-new repository walked through the guide's exact steps
- [x] The reference-run repository contains nothing but what the guide's steps create, with org/user naming neutralized
- [x] Asset records carry reference-run identifiers (repository name, run date, captured-version) so captures are traceable and re-performable
- [x] Re-capture at a new version requires a fresh reference run; editing or splicing prior captures is prohibited
- [x] The reference run is distinct from the first-run acceptance test, and the evaluator role excludes whoever performed that guide's reference run

## First-Run Acceptance Test

- [x] The evaluator is defined by role (no prior hands-on exposure, clean environment), not by identity
- [x] The evaluator role excludes the performer of the guide's reference run, and the test log attests the exclusion held
- [x] The cold-run protocol is specified: guide text only, outside help fails the run
- [x] Every documented-versus-observed deviation is recorded as a defect, including recovered ones
- [x] The test log template fields and in-repo storage path are specified
- [x] Material guide changes invalidate a standing pass and require re-evaluation
- [x] Test-log verdicts are human attestations that automation cannot author or approve
- [x] Evaluator privacy is addressed (role attestation, consented handle only, no personal identifiers)

## Staleness Discipline

- [x] Every quoted output block must be marked verified or illustrative, with no unlabeled state
- [x] Verified blocks are re-executed and diffed in CI, failing with file and block identity
- [x] Volatile output is normalized deterministically or labeled illustrative, never silently exempted
- [x] A release changing CLI output must update affected guides and record a docs-impact row
- [x] Illustrative labeling is reader-visible on the published page
- [x] The verification job is read-only with respect to the repository and cannot auto-heal guides

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification
- [x] Nothing specified alters `sicario verify` behavior or wires documentation tooling into the verdict path
- [x] Guide examples are constrained so the repository's own secret scan enforces them continuously
- [x] Product limits (tiers, completeness-not-quality, maps-not-certification) carry defect standing in guides
- [x] Residual limitations are stated rather than implied as covered

## Notes

- Items marked incomplete require spec updates before `/speckit-clarify` or `/speckit-plan`.
- The video limitation is handled by construction rather than mitigation: the
  gate cannot verify screencasts, so no step may exist only in video and a
  stale screencast is removable without weakening any guide.
- The most likely erosion point is FR-051's normalization escape hatch: over
  time, hard-to-verify blocks drift toward the illustrative label. Plan and
  review should watch the verified-to-illustrative ratio, since a guide that
  is mostly illustrative has quietly exited the honesty contract.
- The first-run evaluation consumes a person's first exposure per guide;
  scheduling fresh evaluators for re-runs is an operational cost accepted in
  the Assumptions section.
- The Spec Kit slash-command flow exists in-repo as agent skills only, and
  `sicario init` targets receive templates but no scripts directory; the
  first-spec playbook's baseline path is therefore the manual template copy
  — the universal floor — with the feature-creation script labeled as a
  native-Spec-Kit-adoption convenience. Evaluating that playbook inside an
  agent environment would validate the wrong path — FR-075 pins the
  evaluation environment for this reason.
- Selection-guide tables can drift without any CLI output change, so they are
  deliberately covered by the release checklist rather than by verified
  output blocks alone; plan and review should keep that coverage when
  implementing the staleness tooling.
