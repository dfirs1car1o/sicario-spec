# Feature Specification: New-User Technical Guide — Onboarding, Playbooks, and Use Cases

**Feature Branch**: `007-onboarding-guides-and-playbooks`
**Created**: 2026-07-28
**Status**: Draft
**Input**: A technical guide that onboards a new SicarioSpec user: a
zero-to-green getting-started walkthrough plus scenario-shaped playbooks for
the workflows a real adopter performs, published through the existing docs-site.

## Overview

This feature specifies a documentation product: a **getting-started
walkthrough** that takes a first-time user from an empty directory to a
passing `sicario verify` gate, and a set of **scenario playbooks** that each
walk one realistic workflow end-to-end — choosing profiles, presets, and
frameworks at initial setup, brownfield adoption, running the first spec from
a fresh init, authoring a spec that passes the gate, writing and overriding
rules, investigating a failure, selecting frameworks, wiring CI, and reading
gate evidence as a reviewer.
Reference documentation for all of this exists and is accurate (`USAGE.md`,
`docs/rule-engine.md`, the docs-site); a guided onboarding path does not, and
this feature adds one. Reference pages answer "what does this command do";
the guide and playbooks answer "how do I accomplish this outcome".

The deliverable is treated as a product with a contract, not as prose:

- **Guides quote real output.** Every command in the walkthrough and every
  playbook step is paired with the output a user should see. Quoted output is
  either **verified** — re-executed and compared in CI so it cannot silently
  rot — or explicitly labeled **illustrative**. There is no third, unlabeled
  state.
- **Guides have an acceptance test.** A playbook is not done when it is
  written; it is done when a **designated first-time evaluator** — a person
  with no prior hands-on exposure to the guide under test, on a clean
  environment — completes it cold, with every deviation between documented
  and observed behavior recorded as a defect, and reaches the documented end
  state without outside help. The filled first-run test log is committed as
  evidence.
- **Guides carry decision support, not just command reference.** The first
  decisions a new user makes — which profile, which frameworks, which init
  mode — are currently documented as flags, not as choices. The guide set
  includes a selection guide that turns the shipped profile-to-preset
  composition, per-preset contributions, and per-profile framework defaults
  into a decision path a first-time user can follow to a defensible choice,
  and a first-spec playbook that walks the full loop from a freshly
  initialized repository to a green gate, documenting only paths that work
  with the tooling the reader actually has.
- **Guides carry visual assets, and images are a leak surface.** Captures
  fall into three labeled classes: terminal interactions as text blocks,
  which are diffable and CI-verifiable; **tool-captured** screenshots —
  automated captures of real rendered surfaces (the docs-site, a CI run
  view, a checks panel) taken with the available browser tooling during a
  real run, reproducible by re-running the capture; and **manual**
  captures, reserved for surfaces that genuinely require a human desktop.
  A screenshot is expected wherever a playbook's flow surfaces a graphical
  view. Screencasts are optional, per-playbook, and never load-bearing,
  because the gate cannot verify video. The fabrication prohibition is
  absolute across all classes: a tool-captured image of a real surface is
  legitimate; composed or synthesized imagery is not. Every capture — and
  every quoted output — comes from a **reference run**: a net-new
  repository created fresh for the purpose and walked through the guide's
  exact steps, with run identifiers recorded so each capture is traceable
  and re-performable.

The guide is itself governed content. It lives in `docs/`, inside the tree
that `sicario verify` scans, so the repository's own secret scan applies to
every example the guide contains; it is published through the existing
docs-site (`docs-site/` builds from `../docs`), so everything in it is public
the moment it merges; and it instructs both humans and coding agents, so its
integrity is a security property, not a style preference.

### Scope

In scope: the getting-started walkthrough; the playbook set defined in
FR-010; the placement and docs-site publication of both; the visual-asset
conventions (location, naming, versioning, manual-capture marking); the
first-run acceptance test and its evidence artifact; and the staleness
discipline for quoted output, tied into the existing docs-impact record
(`docs/docs-impact.md`) and the existing docs-impact task discipline.

Out of scope: any change to `sicario verify` behavior, finding codes, rule
semantics, exit codes, or evidence schemas; any change to the CLI's commands
or output (the guide documents what exists); new rule kinds; docs-site theme
or infrastructure changes beyond registering the new pages; translation and
localization.

### Non-Goals

- **No behavior change to the gate.** If writing a guide reveals a defect in
  the product, the defect is filed and fixed as its own change; the guide
  documents the shipped behavior of a named version.
- **No marketing surface.** Playbooks state what the product does, including
  its stated limits — control maps are coarse traceability aids and not
  certification claims, experimental-tier maps are experimental, and the gate
  checks completeness rather than quality. A guide that overstates the
  product is a defect.
- **No video pipeline.** Screencasts are optional enrichment. Nothing in the
  acceptance path, the CI path, or the evidence path depends on video
  existing, and no infrastructure for hosting or transcoding video is
  introduced.
- **No AI-generated "screenshots".** A visual asset is a capture of a real
  surface or it does not exist. Fabricated imagery is prohibited outright.

## User Scenarios & Testing

### User Story 1 - Zero to First Passing Gate (Priority: P1)

As a first-time user, I want a single walkthrough that takes me from nothing
installed to a repository that passes `sicario verify`, showing me every
command and the exact output to expect, so that my first session ends with a
working governed repository instead of a partial mental model.

**Why this priority**: This is the front door. Every other guide assumes the
reader has once reached a green gate and knows what one looks like.

**Independent Test**: On a machine with only Python available, follow the
walkthrough verbatim: install, initialize with a chosen profile, read the
init report, run `sicario verify`, observe a real failure, fix it as
directed, and re-run to green. The test passes when the final command exits
`0` and no step required information from outside the walkthrough.

**Acceptance Scenarios**:

1. **Given** a clean environment with Python 3.9+ and no SicarioSpec
   installed, **When** the reader follows the install section, **Then** both
   documented install paths are present — pip install from the repository
   and the native Spec Kit bundle path via catalog add + `specify bundle
   install sicario-spec` — and each ends with a stated way to confirm the
   install worked.
2. **Given** the reader runs the documented `sicario init` with the
   walkthrough's chosen profile, **When** the init report prints, **Then**
   the walkthrough explains the report the reader is looking at, including
   the created / merged-overlaid / preserved states shown by `--dry-run`.
3. **Given** the initialized repository, **When** the reader runs
   `sicario verify` as directed, **Then** the walkthrough shows the expected
   output for the failure the walkthrough deliberately stages, names the
   finding code the reader sees, and shows the fix and the green re-run
   ending in `sicario verify passed` with exit code `0`.
4. **Given** a shell where `sicario` is not on PATH, **When** the reader
   reaches the first command, **Then** the walkthrough states the
   `python3 -m sicario_cli.cli` equivalent form before it is needed.

---

### User Story 2 - Choose Profiles, Presets, and Frameworks with Decision Support (Priority: P1)

As a first-time user at the init step, I want selection guidance that tells
me which profile fits my kind of repository and what each choice concretely
installs and enforces, so that my initial setup is a defensible decision
rather than a copied flag.

**Why this priority**: The init flags are the first irreversible-feeling
choice a new user makes, and the reference docs describe them without
deciding between them. A user who picks the wrong profile either drowns in
obligations that do not apply or ships without the ones that do.

**Independent Test**: Give a reader three one-line repository descriptions —
an API service, an agent system, a Terraform platform repository — and only
the selection guide. For each, the reader arrives at a profile choice (and
composition, where applicable), can state which presets that profile
composes, what those presets add to the target repository, which framework
defaults it selects, and which of the listed frameworks are experimental-tier
and therefore never selected implicitly.

**Acceptance Scenarios**:

1. **Given** the selection guide, **When** the reader looks up any shipped
   profile, **Then** the guide states: the kind of repository it fits, the
   presets it composes, what each composed preset concretely adds (which
   templates it appends, what those templates govern, which docs and rules
   land in the target), and the framework defaults it selects.
2. **Given** a reader who does not know which profile to pick, **When** they
   follow the guide's decision path, **Then** the path leads from the kind
   of work in the repository to a recommended profile or composition, with
   the baseline recommendation stated for the undecided case.
3. **Given** a profile whose framework table includes an experimental-tier
   map, **When** the reader reads its defaults, **Then** the guide states
   that experimental maps are excluded from implicit defaults and are only
   enforced when named explicitly on `--frameworks`.
4. **Given** a reader who prefers prompts over flags, **When** they reach
   the init step, **Then** the guide documents the interactive init mode —
   what the wizard asks (framework selection, data classification boundary,
   cloud provider targets), and what it writes — as an alternative to
   composing flags by hand.
5. **Given** the selection guide's tables, **When** the shipped profile
   composition or framework defaults change in a release, **Then** the
   staleness discipline applies to the tables exactly as it applies to
   quoted output.

---

### User Story 3 - Run the First Spec from a Fresh Init (Priority: P1)

As a new user with a freshly initialized repository, I want a playbook for
the full first-spec loop — create the feature directory, fill the governed
template section by section, run the gate iteratively, read each finding as
it appears, and reach green — so that my first spec is written against the
gate instead of thrown over the wall at it.

**Why this priority**: This is the loop the product exists to teach. The
authoring playbook explains what a complete spec contains; this playbook
covers the experience of getting there for the first time, including the
findings a half-finished spec produces — which are the first findings most
users ever see.

**Independent Test**: Starting from a repository initialized by the
walkthrough, follow the playbook: create a feature directory by the
documented path, fill sections in the documented order, run the gate at each
documented checkpoint, observe the documented finding codes shrink to zero,
and end with `sicario verify passed`. Every command must work with the
tooling the playbook itself lists as prerequisite.

**Acceptance Scenarios**:

1. **Given** a fresh init and no coding-agent environment, **When** the
   reader follows the playbook's baseline path, **Then** the feature
   directory and spec file are created by manually copying the shipped
   spec template — the one path available on every adoption route — and no
   step requires an agent-only command or a scripts directory the init
   never installed.
2. **Given** a reader working inside a coding-agent environment where the
   Spec Kit slash commands are available, **When** they follow the
   playbook's agent-flow variant, **Then** the playbook names which
   commands the agent environment provides and states plainly that they
   are unavailable outside such an environment.
3. **Given** the documented finding-demonstration step, **When** the reader
   stages the deliberate defect the playbook directs (removing a required
   section, blanking a required classification field), **Then** the gate
   reports the documented spec-contract finding codes, each explained as it
   first appears — and the playbook states plainly that the shipped
   template starts complete-in-form, so the gate's presence checks pass
   before a single word of real content is written, which is exactly why
   filling sections with real analysis remains a human obligation.
4. **Given** the reader fills the final documented section, **When** they
   run the gate, **Then** the run is green, and the playbook shows how the
   evidence artifacts reflect the now-passing spec.

---

### User Story 4 - First-Run Acceptance Test (Priority: P1)

As the person accountable for documentation quality, I want each guide
validated by a designated first-time evaluator who follows it cold on a clean
environment, so that "the guide works" is an evidence-backed claim rather
than the author's opinion.

**Why this priority**: An author cannot test their own guide — they fill
gaps from memory without noticing. The only reliable detector of a missing
step is a person who does not know the missing step.

**Independent Test**: Give a published guide to an evaluator who has never
performed the workflow it documents, on a machine or fresh virtual
environment with no prior SicarioSpec state. Confirm a filled first-run test
log is produced, that every documented-versus-observed deviation is recorded
as a defect, and that the pass verdict is only recorded for a run completed
without outside help.

**Acceptance Scenarios**:

1. **Given** a guide marked ready for evaluation, **When** the evaluator
   runs it cold, **Then** a first-run test log is filled from the template —
   environment, guide version, per-step observed result, deviations,
   verdict — and committed under the guide's test-log path.
2. **Given** any step where observed output differs from documented output,
   **When** the evaluator records it, **Then** the deviation is logged as a
   defect with the step identifier, the documented text, and the observed
   text, regardless of whether the evaluator recovered.
3. **Given** an evaluator who needed help from any source outside the guide
   text, **When** the log is completed, **Then** the run is recorded as a
   fail with the missing information named — a rescued run is a failed run.
4. **Given** a guide that materially changes after passing, **When** the
   change merges, **Then** the previous pass no longer stands and the guide
   requires a fresh first-run pass before it is again presented as validated.

---

### User Story 5 - Investigate a Failing Gate (Priority: P1)

As an engineer whose CI check just went red, I want a playbook that walks
from a failing `sicario verify` to a fixed repository, so that I can read a
finding code, find its meaning, locate the evidence, and fix the cause
without reverse-engineering the gate.

**Why this priority**: The failing gate is the product's most common
high-stress touchpoint, and the moment a user most needs scenario-shaped
help rather than reference tables.

**Independent Test**: Start from a repository staged to fail with at least
two distinct finding codes. Follow the playbook: read the human output, map
each code via the finding-code reference, open
`generated/sicario/gate-summary.json`, read `scan_coverage` to see what was
and was not scanned, fix each cause, and re-run to green. No step outside
the playbook is needed.

**Acceptance Scenarios**:

1. **Given** the staged failing repository, **When** the playbook is
   followed, **Then** each documented step shows the expected output — the
   finding lines, the relevant `gate-summary.json` fields, and the
   `scan_coverage` records — and the final step shows the green re-run.
2. **Given** a finding whose cause is a policy-excluded or unreadable file,
   **When** the reader reaches the coverage step, **Then** the playbook
   explains the difference between `files_excluded` (policy decision) and
   `skipped_files` (scanner limitation) using the actual record fields.
3. **Given** a reader tempted to silence the finding instead of fixing it,
   **Then** the playbook states the legitimate paths — fix, or a recorded
   exception with owner and expiry — and points at the override-evidence
   playbook rather than presenting disablement as a remedy.

---

### User Story 6 - Read Gate Evidence as a Reviewer (Priority: P2)

As a reviewer or auditor, I want a playbook for reading a run's evidence —
`gate-summary.json`, `scan_coverage`, `asset_root`, override records — so
that I can answer "what did this gate actually check, and was anything
weakened" from artifacts alone.

**Why this priority**: The evidence is the product's proposition. Evidence
nobody can read is decoration.

**Independent Test**: Give the playbook and a `gate-summary.json` from a
repository containing one rule override that disables a critical rule.
Following only the playbook, the reader locates the override record, reads
its `impact` value, and states which rule was weakened, where the winning
definition lives, and what the `asset_root` resolution says about where the
shipped rules came from.

**Acceptance Scenarios**:

1. **Given** the evidence file, **When** the reader follows the playbook's
   override-review step, **Then** they find `scan_coverage.overrides` and
   can apply the documented one-line search for `disables-critical` impact
   values across evidence.
2. **Given** the coverage record, **When** the reader follows the coverage
   step, **Then** they can state files scanned, files skipped, and files
   excluded for the secret-scan rule, and name the directory attribution for
   exclusions.
3. **Given** the `asset_root` record, **When** the reader follows the
   provenance step, **Then** they can state where the shipped rules were
   loaded from and why that matters for trusting the run.

---

### User Story 7 - Quoted Output Stays Honest (Priority: P2)

As a future release owner, I want every quoted output block in the guides to
be either machine-verified or labeled illustrative, and a standing rule that
a release changing CLI output must update the affected guides, so that the
guides remain true without anyone re-reading them end-to-end each release.

**Why this priority**: Guides that quote real output begin decaying at the
next release. Unmanaged, the walkthrough becomes the most confidently wrong
document in the repository — worse than no guide, because it is trusted.

**Independent Test**: Change a CLI output string in a working copy and run
the docs verification job. The job fails, naming the guide file and the
verified block whose quoted output no longer matches observed output.

**Acceptance Scenarios**:

1. **Given** the guides as merged, **When** the docs verification job runs
   in CI, **Then** every block marked verified is re-executed in a
   disposable working directory and its quoted output compared to observed
   output, and any mismatch fails the job naming the file and block.
2. **Given** a block that cannot be deterministically re-executed (for
   example, output including a timestamp or an absolute path), **Then** it
   is either normalized under a documented deterministic rewrite or labeled
   illustrative — never silently exempted.
3. **Given** a release that changes command output or the command surface,
   **When** the release is prepared, **Then** the affected guides are
   updated in the same change and a row is added to `docs/docs-impact.md`,
   under the same docs-impact task discipline the templates already enforce.

---

### Edge Cases

- The reader's platform differs from the capture platform (Windows path
  separators, shell prompt differences) — guides state their assumed shell
  and platform and what varies.
- `pip` installs the CLI outside PATH, so the very first documented command
  fails for the reader; the module-form fallback must appear before first
  use, not in a troubleshooting appendix.
- The pinned version in an install command lags the latest release, so the
  reader installs an older CLI whose output does not match the guide.
- A verified block's command mutates state, making a second CI run observe
  different output — verified blocks must be re-runnable from a clean
  staging directory (idempotency by reconstruction).
- A screencast is re-recorded but the old file name is kept, silently
  breaking the capture-version convention.
- The first-run evaluator's environment has a previously installed
  SicarioSpec version, contaminating the cold run.
- A guide passes evaluation, then a dependency of the guide (a template, a
  rule default) changes without any CLI output change — material change
  detection cannot rely on CLI diffs alone.
- The docs-site sidebar references a guide page that was renamed, breaking
  the build (`onBrokenLinks: 'throw'`).
- A reader outside any coding-agent environment reaches a step written as a
  slash command that only exists as an agent skill — the guide must have
  presented the environment-independent path first, so this reader is never
  stranded.
- A release changes a profile's preset composition or framework defaults
  without changing any CLI output string, so the selection guide's tables
  drift while every verified output block still passes.
- Two profiles are composed (`--profile appsec,cloud-iac`) and the reader
  needs to know how compositions merge presets and union framework defaults.

## Data Classification

The repository and docs-site are public; everything this feature commits is
published. Classification is therefore about what may **enter** the
artifacts, not who may read them.

| Artifact | Level | Classification owner | Retention | Residency | Sharing | Redaction |
|---|---|---|---|---|---|---|
| Guide and playbook pages (`docs/guides/`, `docs/playbooks/`) | Public | Docs owner (maintainer group) | Life of the repository; versioned in git | Repository host and docs-site host | World-readable by design | No real credentials, hostnames, internal URLs, or personal data; placeholders only |
| Quoted terminal output blocks | Public | Docs owner (maintainer group) | Life of the guide | Repository host | World-readable | Absolute paths, usernames, and timestamps normalized to documented stable forms before commit |
| Screenshots, tool-captured or manual (`docs/assets/guides/`) | Public | Docs owner (maintainer group) | Until superseded by a re-capture; superseded assets deleted | Repository host | World-readable | Captured in a sanitized environment; reviewed frame-by-frame for tokens, paths, personal detail before commit — identical policy for both capture classes |
| Reference-run repository (net-new, created per capture campaign) | Public | Docs owner (maintainer group) | Until its captures are superseded; identifiers retained in asset metadata | Repository host | World-readable where hosted publicly | Contains nothing but what the guide's steps create; org/user naming neutralized per the sanitation rules |
| Screencasts (optional, per playbook) | Public | Docs owner (maintainer group) | Until superseded; never load-bearing | Repository host or release asset | World-readable | Same capture policy as screenshots, applied to every frame; a leaked frame is a leaked credential |
| First-run test logs (`docs/guides/test-logs/`) | Public | Docs owner (maintainer group) | Life of the guide version they validate | Repository host | World-readable | Evaluator recorded by role attestation and, only with consent, a public handle; no names, emails, employer, or machine identifiers |
| Docs verification job output | Internal | Maintainer group | Per CI run | CI provider | CI consumers | Carries only file names, block identifiers, and diffs of already-public text |

Classification rule for this feature: capture environments may contain
Restricted material (a real shell has real credentials nearby); the
committed artifact must contain only Public material. The redaction burden
sits at capture time and review time, because after merge there is no
redaction — publication is immediate and history is permanent.

## Tagging Discipline

| Tag | Value |
|---|---|
| owner | sicario-spec-maintainers |
| system | sicario-spec |
| environment | development |
| data-classification | public |
| retention | life-of-guide-version |
| compliance-scope | documentation-integrity |
| feature-id | 007-onboarding-guides-and-playbooks |
| evidence-path | docs/guides/test-logs/ |

Per-artifact tags, carried in front matter or file naming as fits the
artifact kind:

- Every guide page carries `guide-slug` and the `captured-version` (the
  SicarioSpec release its quoted output was captured against).
- Every quoted output block carries a machine-readable marker declaring it
  `verified` or `illustrative`.
- Every visual asset embeds `guide-slug`, step identifier, and
  `captured-version` in its file name, so staleness is computable from the
  name alone; its asset record additionally carries `capture-class`
  (`terminal-text`, `tool-captured`, or `manual`) and the reference-run
  identifiers (repository name and run date) it was captured from.
- Every first-run test log carries the guide slug, the guide's
  `captured-version`, and the verdict.

## Roles, Assets, And Abuse Actors

- **Legitimate roles**: the first-time reader; the designated first-time
  evaluator; the guide author; the docs owner who approves guide changes;
  the release owner bound by the staleness rule; the reviewer using the
  evidence playbook; coding agents that read guides as context and perform
  the non-manual documentation tasks.
- **Protected assets**: the truthfulness of quoted output; the
  verified/illustrative labeling; the integrity of commands the guides tell
  readers to run; the sanitation of visual assets; the authenticity of
  first-run test logs; the accuracy of tier and capability claims.
- **Abuse actors**: a contributor editing a guide to smuggle a harmful
  command into an instruction channel that readers trust; an author under
  schedule pressure fabricating a first-run pass or relabeling a failing
  verified block as illustrative; an agent generating a plausible
  "screenshot" or "expected output" that was never observed; a well-meaning
  editor whose example teaches readers to paste real tokens into files.
- **High-impact actions**: changing a documented command; relabeling
  verified to illustrative; recording a first-run pass; committing a visual
  asset; publishing a claim about framework tiers or gate guarantees.

## Trust Boundaries

- **Guide text to human reader.** The guide is an instruction channel with
  high default trust — readers paste what it says into a shell. Every
  command a guide documents is therefore inside the repository's review
  boundary: a change to a documented command is a change to what thousands
  of shells may execute, and is reviewed with the same weight as code.
- **Guide text to agent context.** Coding agents ingest guides as trusted
  repository documentation. Text in a guide can function as instruction to
  an agent, which is precisely why guide changes require human review and
  why no guide may instruct an agent to weaken a gate, disable a rule, or
  mark an evaluation passed.
- **Capture environment to committed asset.** A real terminal and a real
  screen contain more than the subject of the capture — credentials in
  neighboring windows, real paths, personal identifiers. The boundary is
  crossed only by sanitized, reviewed artifacts; raw captures never touch
  the repository.
- **Docs verification runner to repository.** The CI job that re-executes
  verified blocks is an execution surface whose input is repository text.
  Its tool boundary is fixed: it executes only commands inside blocks
  marked verified, in a disposable working directory, with no credentials
  and no write access outside that directory, and its job is comparison,
  never repair.
- **Repository to docs-site.** Merge is publication. There is no staging
  moat between `docs/` and the public site, so the review boundary is the
  only boundary.

## Security Requirements

- **SEC-001**: No guide, playbook, test log, or visual asset may contain a
  real credential, token, key, or secret-shaped literal. Example values
  MUST be angle-bracketed placeholders (for example `<your-api-token>`)
  that neither work if pasted nor match the repository's own
  secret-scan patterns. The guides live inside the tree `sicario verify`
  scans, so this requirement is continuously enforced by the existing
  critical secret rules — a violating guide fails the repository's own gate.
- **SEC-002**: Every command a guide instructs the reader to run MUST be
  reviewed under code-owner review for the docs tree. A documented command
  is treated as executable content, not prose.
- **SEC-003**: Visual assets MUST be captured in a sanitized environment —
  the reference-run repository, generic prompt, no real tokens or personal
  paths on screen — and reviewed before commit. The sanitation review is
  identical for tool-captured and manual assets, and screencasts apply the
  same review to every frame.
- **SEC-004**: Visual assets MUST be genuine captures of real surfaces.
  Tool-captured screenshots — automated captures of a real rendered
  surface taken during a real run — are a legitimate class. Generating,
  synthesizing, or editing an asset to depict output that was not observed
  is prohibited for every class; automation MUST NOT create or check off a
  manual-capture task, and MUST NOT present a composed image as a capture.
- **SEC-005**: The docs verification runner MUST execute only the commands
  inside blocks marked verified, in an isolated disposable working
  directory, with no ambient credentials, and MUST fail loudly on any
  mismatch rather than updating quoted output to match observation.
- **SEC-006**: First-run test logs MUST be authored by the evaluator of an
  actual run. Recording a pass without a corresponding run is a governance
  failure of the same class as fabricating gate evidence.
- **SEC-007**: Guides MUST present rule disablement and overrides only
  alongside their evidence trail — the override record in
  `scan_coverage.overrides` and the exception-register expectation — never
  as an unqualified way to make a red gate green.
- **SEC-008**: Guides MUST state product limits accurately: experimental-tier
  control maps are named experimental, control maps are traceability aids
  and not certification claims, and the gate checks completeness rather
  than quality. Overclaiming in a guide is a defect with the same standing
  as a wrong command.
- **SEC-009**: Nothing in this feature may alter `sicario verify` behavior,
  and no documentation tooling may be wired into the gate's verdict path.
  The docs verification job is a separate CI check.

## Privacy Requirements

- **Data minimization**: first-run test logs record role attestation,
  environment class (OS, Python version), guide version, and per-step
  results — not names, emails, employers, IP addresses, or hardware
  identifiers. A public handle appears only with the evaluator's consent.
- **Purpose limitation**: test logs exist to validate guides. They are not
  performance records of the evaluator and MUST NOT be used to assess a
  person; the evaluator is the instrument, the guide is the subject.
- **Consent or notice requirements**: the evaluator is told before the run
  that the log is committed to a public repository, and chooses between
  role-only attestation and an attributed handle.
- **Redaction requirements**: quoted output and captures are normalized so
  no home-directory path, local username, or hostname survives into a
  committed artifact.

## Compliance / Control Applicability

Map applicable requirements without claiming certification.

| Domain | Applicable? | Rationale | Evidence |
|---|---|---|---|
| AppSec / ASVS | Partial | Documentation of security tooling and secure-usage instructions; no new code surface beyond the docs verification job | Guide review records, docs verification CI runs |
| NIST SSDF | Yes | Documented, verified usage of the security gate supports well-secured-software practice communication | Guides, first-run test logs, docs-impact rows |
| Supply Chain / SLSA | Partial | Guides are trusted instruction inputs to builds and agents; integrity is protected by review and CI verification | Code-owner review on docs tree, docs verification job |
| AI Risk / NIST AI RMF | Partial | Guides enter agent context; injection posture and manual-task boundaries are specified here | AI / LLM Risk section, SEC-004, test logs |
| Cloud/IaC | No | No infrastructure is created or changed by this feature | — |

## AI / LLM Risk

The guides contain no AI features, but they are read by AI agents and partly
produced with AI assistance, so the boundary is stated explicitly.

- **Prompt injection exposure**: a guide is high-trust text in agent
  context. A tampered guide could instruct an agent to disable a rule,
  fabricate a test log, or exfiltrate content — which is why documented
  commands are review-gated (SEC-002) and why no guide text may direct an
  agent to bypass an approval. Quoted output blocks additionally reproduce
  gate output, which can carry attacker-influenced path text; guides state
  that reproduced output is data to be read, never direction to be
  followed.
- **Tool boundary controls**: the docs verification runner is the only
  automation this feature adds, and its tool boundary is closed: it runs
  the commands of verified blocks only, in a disposable directory, with no
  credentials, no repository write access, and no network beyond what the
  documented install command itself requires. Agents performing
  documentation tasks operate under the repository's normal review flow and
  MUST NOT perform manual-capture or evaluation tasks (SEC-004, SEC-006).
- **Model routing**: not applicable; no model call exists in any path this
  feature adds.
- **Memory poisoning risk**: guides are durable, trusted context — the
  closest thing a repository has to long-term memory for agents. Poisoning
  it is the attack AC-006 describes; review and verification are the
  mitigations.
- **Data leakage risk**: the dominant risk is capture-time leakage into
  public artifacts (AC-001), mitigated by SEC-003 capture policy and
  review.
- **Human approval boundaries**: recording a first-run verdict, checking
  off a manual-capture task, and approving a guide change are human acts.
  Automation may draft; it may not attest.
- **AI evals / red-team tests**: a negative review check confirms that no
  guide instructs an agent or reader to disable a rule without the
  exception path, and the repository gate continuously asserts that no
  guide content matches a secret pattern.

## Fleet Guardrails

The docs verification job and the first-run process inherit the repository's
orchestration discipline:

- **Idempotency**: the verification job rebuilds its staging directory from
  scratch each run, so re-running it over an unchanged tree yields an
  identical verdict and identical diffs. Verified blocks are written to be
  reproducible by reconstruction, never dependent on leftover state.
- **Retry**: a transport or infrastructure failure may be retried; a
  content mismatch may not. A verified block that fails comparison is a
  defect to fix in the guide or the label, never a flake to re-run until
  green.
- **Dead-letter**: a block that cannot be executed at all (missing marker
  data, malformed command) is reported as its own named failure, not
  silently skipped — an unverifiable "verified" block is treated as a
  mismatch, so decay cannot hide in tooling gaps.
- **Workflow state**: the only durable state is the repository: guide
  files, markers, assets, and test logs, all reviewable and revertible in
  git. The verification job keeps nothing between runs.
- **Human approval**: first-run verdicts and manual-capture completions are
  human-only acts, and guide changes merge through the same code-owner
  review as any governed content.

## External System Access

- **External systems**: the docs verification job reaches the package
  source only where a verified install block requires it; the docs-site
  deploy is the existing pipeline, unchanged.
- **Read/write permissions**: read-only on the repository; write-only to a
  disposable staging directory and the job's own logs.
- **Production impact**: none. A failing docs verification job blocks a
  docs change, not a release of the gate.
- **Human approval needed**: for merging guide changes, recording first-run
  verdicts, and committing visual assets — yes. For running verification —
  no.

## Secrets / Credential Handling

- **Secret sources**: none. No guide, asset, test log, or verification run
  requires a credential of any kind.
- **Runtime injection method**: none; the verification job runs
  credential-free by requirement (SEC-005), so a verified block that needs
  a secret is unwritable — which is intended.
- **Redaction requirements**: placeholders by construction in text
  (SEC-001); sanitized capture and frame review for images and video
  (SEC-003).
- **Rotation owner**: not applicable in steady state. If a real credential
  is ever found in a committed guide artifact, the repository's security
  owner owns rotation and revocation, and removal from the working tree is
  not sufficient — history is publication.

## Audit / Logging Requirements

- **Events to log**: docs verification runs with per-block pass/mismatch
  results; first-run evaluations via committed test logs; guide-affecting
  releases via `docs/docs-impact.md` rows; asset supersessions via git
  history of `docs/assets/guides/`.
- **Fields to exclude**: evaluator personal data beyond consented handle;
  any capture-environment detail; any credential-shaped content (there is
  none to log by construction).
- **Retention**: test logs and docs-impact rows live with the repository;
  verification job output per CI run.
- **Alerting**: a failing docs verification job fails the CI check on the
  change that broke it — the alert is the red check.

## Operational Signal / Response Path

- **Signals this feature should emit**: verified-block mismatches (guide
  drift), first-run defect lists (guide gaps), stale `captured-version`
  values relative to the current release (asset drift).
- **Detection or alert logic**: CI comparison for verified blocks; release
  checklist comparison of guide `captured-version` against the release
  version; human review for everything visual.
- **Triage owner**: the docs owner for guide defects; the release owner for
  staleness introduced by a release.
- **Response or rollback action**: fix the guide or correct the label in
  the same change that altered output; re-capture superseded assets; re-run
  first-run evaluation after material guide changes. Never resolve a
  mismatch by copying observed output into the guide without review of
  whether the observed behavior is itself correct.
- **Evidence retention location**: `docs/guides/test-logs/`,
  `docs/docs-impact.md`, and CI run history for the verification job.

## Misuse / Abuse Cases

Each case names the abuse, the detection, and the mitigation.

- **AC-001 — A capture publishes a real credential.** A screencast or
  screenshot is recorded in a live working environment; a neighboring
  terminal, an environment listing, or an editor tab carries a real token,
  and merge publishes it worldwide, permanently, in history.
  *Detection*: pre-commit review of every image and every screencast frame
  is a mandatory review step for asset-bearing changes; the text-side
  equivalent is caught mechanically by the repository's secret scan.
  *Mitigation*: SEC-003 requires capture in a sanitized environment that
  has nothing to leak — a demo directory, generic prompt, no credentials
  configured — so the review step is a second line, not the only line. If
  a leak merges anyway, the response is rotation and revocation, not
  deletion.

- **AC-002 — An example teaches readers to commit real tokens.** A guide
  shows a configuration snippet with a realistic-looking example value;
  readers paste it, substitute a real token, and commit, having been
  taught the shape of the mistake by the guide itself.
  *Detection*: guide review checks example values against SEC-001; the
  adopting repository's own SicarioSpec gate detects the committed result
  with its critical secret rules — and the guides say so.
  *Mitigation*: placeholders are angle-bracketed non-values that cannot
  work if pasted; wherever a guide introduces a value a reader will
  substitute, the adjacent text states where the real value belongs
  (environment or secret store, never the file) — the guide teaches the
  safe habit at the exact moment of risk.

- **AC-003 — Quoted output silently rots.** A release changes gate output;
  the walkthrough keeps quoting the old output; new readers see their
  first documented expectation fail and either lose trust or, worse,
  assume their correct result is an error.
  *Detection*: verified blocks are re-executed and diffed in CI, so drift
  in anything verified fails the docs check the moment the change is
  proposed, naming file and block.
  *Mitigation*: the release rule (FR-052) makes updating affected guides
  part of the changing release itself, recorded in `docs/docs-impact.md`;
  blocks that cannot be verified are labeled illustrative so the reader
  knows which expectations are exact and which are shaped.

- **AC-004 — A first-run pass is fabricated.** Under schedule pressure, a
  pass verdict is committed for an evaluation that never happened, or the
  guide's author "evaluates" their own guide from memory.
  *Detection*: the test log template demands run-specific content — exact
  environment, per-step observed output, deviations with observed text —
  that is difficult to invent and easy to challenge in review; review
  checks that the evaluator attestation states no prior hands-on exposure.
  *Mitigation*: SEC-006 classifies fabricated logs with fabricated gate
  evidence; the verdict is a human attestation under code-owner review,
  and automation is barred from authoring or approving it (SEC-004
  pattern applied to evaluation).

- **AC-005 — An agent fabricates the visuals or the "expected output".** A
  coding agent, asked to complete documentation tasks, generates an image
  of a terminal, or writes an output block from its model of what the CLI
  probably prints rather than from a run.
  *Detection*: manual-capture tasks are explicitly marked and cannot be
  checked off by automation; verified blocks are grounded by CI execution,
  so an invented output that differs from reality fails comparison.
  *Mitigation*: SEC-004 prohibits synthetic assets outright while giving
  automation a legitimate channel — the tool-captured class grounds an
  automated capture in a real rendered surface during a real run, so the
  compliant path is easier than the fabricating one; the reference-run
  traceability (FR-082) means every asset names the run that produced it,
  so an asset with no run to point at is visibly illegitimate; and the
  verified/illustrative discipline leaves no unlabeled middle state where
  invented output could sit unexamined.

- **AC-006 — A guide becomes an injection channel.** A contributor edits a
  playbook so its documented command carries a malicious addition, or
  embeds text aimed at agents that ingest the guide as trusted context —
  turning the repository's most-trusted prose into an execution vector for
  every reader and agent downstream.
  *Detection*: documented commands are diff-visible, and SEC-002 places
  them under code-owner review as executable content; the docs
  verification job actually executes verified commands in isolation, so a
  command whose behavior changed is exercised somewhere safe before any
  reader runs it.
  *Mitigation*: the review boundary is the publication boundary — nothing
  reaches readers or agents without human review of the exact command
  text; guides never instruct weakening a gate without the exception path,
  so instruction-shaped text that does is anomalous on its face.

- **AC-007 — The verification runner is turned into an execution surface.**
  A change marks a hostile command as a verified block, so CI executes it;
  or the runner is "improved" to auto-heal guides by rewriting quoted
  output, converting the honesty check into an automatic liar.
  *Detection*: new verified blocks are review-visible in the diff of a
  docs change; the runner's fixed contract (execute-compare-fail, never
  write) makes any write behavior a reviewable code change to the runner
  itself.
  *Mitigation*: SEC-005 bounds the runner — disposable directory, no
  credentials, no repository writes, comparison only — so the blast
  radius of a hostile verified block is a credential-free sandbox, and
  auto-healing is structurally out of contract.

- **AC-008 — The guide overclaims the product.** Onboarding prose slides
  into marketing: an experimental control map described as supported, the
  completeness gate described as a security guarantee, coarse traceability
  described as certification readiness. New users then trust the product
  for exactly the things it does not do.
  *Detection*: guide review includes a claims check against the reference
  docs (`docs/control-maps.md` tier table, the completeness-not-quality
  statements), and the first-run evaluator reads the guide cold — the
  audience most likely to take an overclaim literally and record the
  resulting confusion as a deviation.
  *Mitigation*: SEC-008 gives accuracy-of-limits the same defect standing
  as a wrong command; the framework playbook is required to present the
  supported/experimental tier split and the not-a-certification statement
  as part of its steps, not as a footnote.

## Functional Requirements

### Getting-started walkthrough

- **FR-001**: A getting-started walkthrough MUST exist that takes a reader
  from a clean environment to a repository where `sicario verify` exits `0`,
  as one continuous, ordered document.
- **FR-002**: The walkthrough MUST document both install paths: pip install
  from the repository (including the release-pinned form) and the native
  Spec Kit bundle path (catalog add for presets, extensions, and bundles,
  then `specify bundle install sicario-spec`), each ending with a
  confirmation step.
- **FR-003**: The walkthrough MUST state the `python3 -m sicario_cli.cli`
  module-form equivalent before the first `sicario` command is used.
- **FR-004**: The walkthrough MUST initialize with one explicitly chosen
  profile, explain in one or two sentences why that profile fits the
  walkthrough's scenario, and link the selection guide (FR-060) at the init
  step for the reader whose repository does not match the walkthrough's
  scenario — before the init command, not after it.
- **FR-005**: The walkthrough MUST show and explain the init report,
  including the `--dry-run` per-file plan and the meaning of created,
  merged-overlaid, and preserved states.
- **FR-006**: The walkthrough MUST include a deliberately staged gate
  failure: the reader runs `sicario verify`, sees a real finding with its
  code and severity, is shown how to interpret it, applies the documented
  fix, and re-runs to `sicario verify passed` with exit code `0`.
- **FR-007**: Every command in the walkthrough MUST be paired with its
  expected output as a quoted block, each block labeled verified or
  illustrative per FR-050.
- **FR-008**: The walkthrough MUST state its assumed platform and shell,
  and note the known points of divergence for other platforms.
- **FR-009**: The walkthrough MUST be completable, by a first-time
  evaluator meeting the FR-040 definition, in 30 minutes or less excluding
  download time.

### Playbooks

- **FR-010**: The following playbooks MUST exist, each as a self-contained
  document: (1) choosing profiles, presets, and frameworks at initial setup
  (the selection guide, per FR-060 through FR-065); (2) adopting
  SicarioSpec in a brownfield repository with an existing constitution;
  (3) running the first spec from a freshly initialized repository (per
  FR-070 through FR-075); (4) authoring a feature spec that passes the
  gate; (5) adding a custom project rule; (6) overriding or narrowing a
  shipped rule and reading the override evidence it produces;
  (7) investigating a failing gate; (8) selecting compliance frameworks and
  understanding the supported and experimental map tiers; (9) wiring the
  gate into CI with the shipped workflow templates; (10) reading gate
  evidence as a reviewer.
- **FR-011**: Every playbook MUST contain, in order: the scenario and
  intended reader; the starting state, stated precisely enough to
  reconstruct; numbered steps, each with its command or action and its
  expected output; and a success check stating how the reader confirms the
  end state was reached.
- **FR-012**: Every playbook MUST be completable without reading any other
  playbook. Cross-references are permitted for further depth, never for
  required steps.
- **FR-013**: The brownfield playbook MUST demonstrate the overlay-not-
  clobber contract: `--dry-run` first, the additive constitution overlay
  that defers to existing principles, idempotent re-runs, and the backup
  files with their gitignore entry.
- **FR-014**: The spec-authoring playbook MUST walk each governance section
  the gate checks, use the shipped passing example
  (`examples/python-api/`) as its completed reference, and show the
  finding produced when a required section is missing. It is the depth
  companion to the first-spec playbook: the first-spec playbook (FR-070)
  covers the loop from fresh init to green; this playbook covers what a
  complete section contains and why.
- **FR-015**: The custom-rule playbook MUST create a rule in
  `.sicario/rules/`, validate it with `sicario verify --validate-rules`,
  show it firing and passing, and state the top-level-only loading rule for
  rules directories.
- **FR-016**: The override playbook MUST override a shipped rule by id,
  then open `generated/sicario/gate-summary.json` and read the resulting
  `scan_coverage.overrides` record — including `winning_origin`,
  `changed`, `material`, and `impact` — and MUST show the
  `disables-critical` impact reading for disabling a critical rule
  alongside the exception-register expectation.
- **FR-017**: The failing-gate playbook MUST cover reading finding codes in
  human output, mapping them via the finding-code reference, reading
  `gate-summary.json`, and reading `scan_coverage` — including the
  distinction between skipped (could not read) and excluded (policy) files.
- **FR-018**: The frameworks playbook MUST demonstrate `--frameworks`
  selection, the resulting `.sicario/frameworks.txt`, the
  `SICARIO-MISSING-FRAMEWORK-MAP` behavior, the supported versus
  experimental tier split, and the statement that maps are traceability
  aids, not certification claims. Its scope is changing and understanding
  the selection in an existing repository; the at-init decision belongs to
  the selection guide (FR-060), which it links rather than repeats.
- **FR-019**: The CI playbook MUST wire `sicario-verify.yml` from
  `workflow_templates/` into a repository, show the check failing on a
  staged finding and passing after the fix, and state where evidence
  artifacts land in CI.
- **FR-020**: The reviewer playbook MUST cover, from artifacts alone:
  verdict and finding fields in `gate-summary.json`; the override records
  and a one-line search for `disables-critical` impact values; the
  `asset_root` resolution record and what it says about where shipped
  rules were loaded from; and per-rule coverage including `files_excluded`
  with its directory attribution.

### Placement and publication

- **FR-021**: The walkthrough and playbooks MUST live under `docs/` so the
  existing docs-site build (`docs-site/` reading `../docs`) publishes them,
  and MUST be registered in the docs-site sidebar as a distinct learning
  category separate from reference material.
- **FR-022**: `README.md` and `USAGE.md` MUST link to the walkthrough as
  the entry point for new users; existing reference docs remain the
  reference.
- **FR-023**: Guide pages MUST carry their `guide-slug` and
  `captured-version` per the Tagging Discipline section.

### Visual assets

- **FR-030**: Every capture MUST belong to one of three labeled classes,
  recorded in its asset record: (a) **terminal text** — terminal
  interactions captured as text blocks, never as images of text;
  (b) **tool-captured** — automated screenshots of real rendered surfaces
  (the docs-site, a CI run view, a PR checks panel) taken with the
  available browser tooling during a real run, reproducible by re-running
  the documented capture; (c) **manual** — reserved for surfaces that
  genuinely require a human desktop. Screenshots of any class are
  permitted only for genuinely graphical surfaces.
- **FR-031**: Visual assets MUST live under `docs/assets/guides/<guide-slug>/`
  and MUST be named `<step-slug>--v<captured-version>.<ext>`, so the release
  an asset was captured against is computable from its file name.
- **FR-032**: A superseded asset MUST be replaced under the new
  captured-version name and the old file deleted in the same change, so a
  stale asset cannot survive beside its replacement.
- **FR-033**: Screencasts are optional per playbook, never required, and
  never load-bearing: no step may exist only in video, and every screencast
  duplicates steps that exist in text.
- **FR-034**: The `MANUAL CAPTURE:` task prefix is reserved for captures a
  tool cannot perform — surfaces genuinely requiring a human desktop, and
  all screencasts. Automation MUST NOT perform or complete such tasks. A
  surface reachable by the browser tooling MUST be captured as
  tool-captured rather than manual, so the manual class stays small and
  every manual task's justification is the surface itself.
- **FR-035**: Asset-bearing changes MUST include the SEC-003 sanitation
  review as an explicit review step, for tool-captured and manual assets
  alike.
- **FR-036**: A screenshot is expected wherever a playbook's flow surfaces
  a graphical view: if a step directs the reader to look at a rendered
  page, a run view, or a checks panel, the step carries a capture of that
  surface. Omitting one requires a stated reason in the guide source.
- **FR-037**: The walkthrough and the CI-wiring playbook MUST include
  tool-captured screenshots of their graphical surfaces — for the
  CI-wiring playbook, at minimum the CI run failing, the CI run passing,
  and the pull-request checks panel; for the walkthrough, each rendered
  surface its steps direct the reader to view.

### First-run acceptance test

- **FR-040**: A designated first-time evaluator is defined by role: a
  person with no prior hands-on exposure to the guide under test — which
  includes not having performed that guide's reference run (FR-084) —
  using a clean machine or a fresh virtual environment with no
  pre-existing SicarioSpec installation or configuration.
- **FR-041**: Each guide and each playbook MUST pass a first-run evaluation
  before it is presented as validated: the evaluator follows the guide
  cold, using only the guide's text, and reaches the documented end state.
- **FR-042**: Every deviation between documented and observed output or
  behavior MUST be recorded in the test log as a defect, with step
  identifier, documented text, and observed text — including deviations
  the evaluator recovered from.
- **FR-043**: A run in which the evaluator required information from
  outside the guide MUST be recorded as a fail, naming the missing
  information. A guide passes only on a run completed without outside
  help.
- **FR-044**: The filled test log MUST be committed to
  `docs/guides/test-logs/` named by guide slug and captured-version, from
  a template covering: evaluator role attestation (and consented handle
  only), the FR-084 attestation that the evaluator did not perform the
  guide's reference run, environment class, guide version, per-step
  results, deviation list, verdict, and elapsed time.
- **FR-045**: A material change to a guide — any change to a command, a
  verified output block, or step ordering — invalidates its standing pass;
  the guide MUST NOT be presented as validated again until a fresh
  first-run evaluation passes.
- **FR-046**: Test-log verdicts are human attestations: automation MUST
  NOT author, complete, or approve a first-run test log.

### Staleness discipline

- **FR-050**: Every quoted output block in every guide MUST carry a
  machine-readable marker declaring it `verified` or `illustrative`. An
  unmarked output block is a defect.
- **FR-051**: A CI docs verification job MUST re-execute the commands of
  every verified block in a disposable working directory and compare
  observed output to the quoted block, failing with file and block
  identity on any mismatch. Volatile output fields MUST be normalized by
  documented deterministic rewrites or the block labeled illustrative.
- **FR-052**: A release that changes CLI output, command surface, finding
  text, or evidence schema MUST update every affected guide in the same
  release and record the change as a row in `docs/docs-impact.md`, under
  the existing docs-impact task discipline.
- **FR-053**: Illustrative blocks MUST be visibly labeled to the reader as
  representative rather than exact, so the two classes of expectation are
  distinguishable on the published page, not only in source markers.
- **FR-054**: The release checklist MUST include comparing every guide's
  `captured-version` and every asset file name's version against the
  release version, and either re-capturing or explicitly carrying forward
  each stale item with a recorded rationale.
- **FR-055**: The docs verification job MUST NOT modify any repository
  file. Its output is a verdict and a diff; repairing a guide is a
  reviewed human change.

### Initial-setup selection guidance

- **FR-060**: A selection guide MUST exist as the initial-setup playbook,
  presenting the profile choice as a decision with consequences rather than
  a flag reference, and MUST be the document the walkthrough links at its
  init step (FR-004).
- **FR-061**: For every shipped profile, the guide MUST state in one table
  or equivalent structure: the kind of repository it fits; the presets the
  profile composes; what each composed preset concretely adds to the
  target (which templates it appends and which docs and rules land); and
  the framework defaults the profile selects. This content MUST be derived
  from the shipped composition metadata — the CLI's profile-to-preset and
  profile-to-framework tables and each preset's own manifest — and the
  tables carry the guide's `captured-version` and fall under the FR-052
  release discipline and the FR-054 release-checklist comparison, because
  composition can change without any CLI output string changing.
- **FR-062**: The guide MUST include a decision path from the kind of work
  in the repository to a recommended profile or composition: the baseline
  recommendation for the undecided case, when to compose multiple profiles
  with the comma-separated form, and how composition behaves — composed
  profiles merge their preset lists and union their framework defaults.
- **FR-063**: The guide MUST connect the choice to its enforcement
  consequence: for the templates a profile composes, which spec, plan, and
  tasks sections they add, and which finding codes will then enforce those
  sections — so the reader can see, before initializing, what the choice
  will make the gate demand of every future feature.
- **FR-064**: The guide MUST state the framework-tier default rule
  precisely: experimental-tier maps are never selected implicitly — they
  are excluded from per-profile defaults even where a profile's framework
  table lists them — and are enforced only when named explicitly on
  `--frameworks`; and the strictest profile's explicit selection of all
  shipped frameworks is stated as the deliberate exception.
- **FR-065**: The guide MUST document the interactive init mode
  (`sicario init --interactive`) as the prompt-driven alternative to
  composing flags: the wizard's three steps — framework selection, data
  classification boundary, cloud provider targets — what it writes into
  the target's project configuration, and when a first-time user should
  prefer it over flags.

### First-spec loop

- **FR-070**: A first-spec playbook MUST walk the full loop from a freshly
  initialized repository to a green gate: create the feature directory and
  spec file, fill the governed template sections in a documented order, run
  the gate at documented checkpoints, read each finding as it appears, and
  end at `sicario verify passed`.
- **FR-071**: The playbook's baseline path MUST be environment-independent
  and MUST be the universal floor available on every adoption path: a
  documented manual copy of `.specify/templates/spec-template.md` into
  `specs/<NNN-short-name>/spec.md`, requiring nothing beyond a shell and
  the initialized repository. The feature-creation script under
  `.specify/scripts/` MUST be presented as a convenience available only
  where Spec Kit's own scaffolding is present — repositories adopted
  through native Spec Kit tooling — because `sicario init` targets do not
  receive a scripts directory, and the guide must not promise it there.
- **FR-072**: Where the playbook presents the Spec Kit slash-command flow
  (the `/speckit-specify` family), it MUST state that these commands exist
  as agent skills, available only inside a coding-agent environment that
  surfaces them, MUST present that flow as a variant of the baseline path,
  and MUST NOT document any step as generally available when it requires
  tooling the playbook's stated prerequisites do not include.
- **FR-073**: The playbook MUST define gate checkpoints across the fill
  order and state honestly what each reports — including that the template
  of a correctly initialized project satisfies the gate's presence and
  completeness checks in form on both adoption paths (greenfield init and
  brownfield overlay), so a freshly copied template passes before real
  content exists.
  The playbook MUST therefore include a deliberate finding-demonstration
  step that stages a spec-contract defect, shows the resulting finding
  codes and their meaning, and shows the fix — so the reader has read a
  real finding before their first unplanned one.
- **FR-074**: The playbook MUST show, on the final green run, where the
  passing spec is reflected in evidence — the gate summary's status and
  finding count — so the loop ends at the artifact reviewers will read.
- **FR-075**: The playbook MUST enumerate as prerequisites exactly the
  tooling its baseline path requires, and its first-run evaluation
  (FR-040 through FR-046) MUST be performed without a coding-agent
  environment, so the path validated cold is the path every reader has.

### Reference run — the canonical capture source

- **FR-080**: Quoted outputs and visual captures for a guide MUST be taken
  from a reference run: a net-new repository created fresh for the
  purpose and walked through the guide's exact steps in order, with the
  outputs and captures taken from that run as it happens.
- **FR-081**: The reference-run repository MUST contain nothing but what
  the guide's steps create, and its naming MUST be placeholder-sanitized —
  org and user identifiers neutralized under the same redaction rules that
  govern quoted output — so the repository itself is committable evidence
  of what the guide produces and nothing else.
- **FR-082**: Every capture's asset record and every guide's metadata MUST
  record the reference-run identifiers — repository name, run date, and
  the `captured-version` the run was performed against — so any capture is
  traceable to the run that produced it and re-performable by repeating
  the guide's steps in a fresh reference run.
- **FR-083**: A re-capture at a new `captured-version` MUST come from a
  fresh reference run. Editing prior captures, splicing runs, or reusing a
  stale reference-run repository for a new version is prohibited — the
  run, not the artifact, is the unit of refresh.
- **FR-084**: The reference run and the first-run acceptance test are
  distinct acts with distinct performers: performing a guide's reference
  run constitutes prior hands-on exposure to that guide, so the evaluator
  role for a guide excludes whoever performed that guide's reference run.
  The first-run test log records that this exclusion held.

## Security Acceptance Criteria

- **SA-001**: `sicario verify` over the repository with all guides,
  playbooks, test logs, and assets in place reports zero findings —
  demonstrating in particular that no guide artifact contains a
  secret-shaped literal, since the shipped critical secret rules scan the
  docs tree.
- **SA-002**: A working copy in which one verified block's quoted output is
  altered fails the docs verification job, and the failure names the guide
  file and the block.
- **SA-003**: A working copy in which a guide file contains a
  secret-shaped example value fails the repository gate with the
  appropriate critical finding code — the negative test for SEC-001.
- **SA-004**: Every image and screencast under `docs/assets/guides/`
  matches the FR-031 naming convention, and no committed asset's frames
  contain a credential, a personal path, or a non-consented identifier —
  asserted by the SEC-003 review step recorded on each asset-bearing
  change.
- **SA-005**: Every first-run test log present in the repository contains
  the FR-044 fields, and every guide presented as validated has a passing
  log at the current guide version.
- **SA-006**: The docs verification job runs with no credentials available
  and no write access outside its staging directory, and a run of the job
  produces no diff in the repository working tree.
- **SA-007**: The override playbook's worked example produces an override
  record in gate evidence whose `impact` value reads
  `disables-critical-severity-rule`, and the playbook text shows that
  exact evidence rather than asserting it.
- **SA-008**: No guide instructs disabling or weakening a rule without, in
  the same step sequence, the override-evidence reading and the
  exception-register expectation — checked in guide review against
  SEC-007.
- **SA-009**: The selection guide's per-profile statements — composed
  presets, per-preset contributions, framework defaults, tier exclusions —
  agree with the shipped composition metadata at the guide's
  `captured-version`, and a working copy in which they disagree is caught
  by the FR-054 release-checklist comparison rather than shipping.
- **SA-010**: The first-spec playbook's baseline path executes end-to-end
  on a machine with only a shell, git, Python, and the initialized
  repository — no coding-agent environment — demonstrated by its first-run
  evaluation being performed under exactly those conditions (FR-075), and
  no step of the baseline path names an agent-only command.
- **SA-011**: Every visual asset's record carries its capture class and
  reference-run identifiers, and every tool-captured asset is reproducible
  by re-running its documented capture against a fresh reference run — no
  committed asset exists without a run it traces to.
- **SA-012**: For every first-run test log, the recorded evaluator
  exclusion holds: the log attests that the evaluator did not perform that
  guide's reference run, and review confirms the attestation is present.

## Security Evidence Chain

| Chain ID | Risk / Decision | Control / Requirement | Test / Gate | Evidence Path | Owner | Approval / Accepted Risk |
|---|---|---|---|---|---|---|
| SEC-C-001 | Credential leak through captures or examples | SEC-001, SEC-003, FR-030–FR-037 | SA-001, SA-003, SA-004 | Repository gate output; asset review record | Docs owner (maintainer group) | Approved; sanitation at capture time, review before merge |
| SEC-C-002 | Quoted output drifts from real behavior | FR-050–FR-055 | SA-002 | Docs verification CI runs; `docs/docs-impact.md` | Release owner | Approved; illustrative labeling accepted for non-deterministic output |
| SEC-C-003 | Guide used as command/agent injection channel | SEC-002, AI / LLM Risk section | SA-006, review record | Code-owner review on docs tree | Maintainer group | Approved; review boundary is publication boundary |
| SEC-C-004 | Fabricated first-run evidence | SEC-006, FR-040–FR-046 | SA-005 | `docs/guides/test-logs/` | Docs owner (maintainer group) | Approved; human-only attestation |
| SEC-C-005 | Synthetic visual assets presented as real | SEC-004, FR-034 | SA-004 | Manual-capture tasks and asset review record | Docs owner (maintainer group) | Approved; fabrication prohibited outright |
| SEC-C-006 | Guides overclaim product guarantees or tiers | SEC-008, FR-018 | SA-008, first-run deviations | Guide review record; test logs | Docs owner (maintainer group) | Approved; limits carry defect standing |
| SEC-C-007 | Docs tooling reaches the gate's verdict path | SEC-009, FR-055 | SA-006 | CI configuration review | Maintainer group | Approved; verification is a separate check |
| SEC-C-008 | Guides promise tooling the reader lacks (agent-only commands presented as universal) | FR-071, FR-072, FR-075 | SA-010 | First-run test log for the first-spec playbook; guide review record | Docs owner (maintainer group) | Approved; baseline path is environment-independent by requirement |
| SEC-C-009 | Selection guidance drifts from shipped composition, steering setup choices wrongly | FR-061, FR-064, FR-054 | SA-009 | Release checklist comparison; `docs/docs-impact.md` | Release owner | Approved; tables are data-derived and release-checked |
| SEC-C-010 | Captures untraceable to a real run, or refreshed by editing instead of re-running | FR-080–FR-084, SEC-004 | SA-011 | Asset records with reference-run identifiers; git history of `docs/assets/guides/` | Docs owner (maintainer group) | Approved; the run is the unit of refresh |

## Evidence To Produce

- **Threat model update**: record guides as a trusted instruction channel
  to humans and agents, and captures as a publication-time leak surface.
- **Abuse-case update**: add AC-001 through AC-008 to the repository
  abuse-case register with their detections and mitigations.
- **Data classification record**: record the capture-environment-to-public-
  artifact boundary and the placeholder-only rule for examples.
- **Tagging taxonomy updates**: add `guide-slug`, `captured-version`, and
  the `verified` / `illustrative` block marker as accepted documentation
  tags.
- **Security Evidence Chain**: the table above, carried into the plan and
  kept current.
- **Tests**: the docs verification job with a seeded-mismatch negative
  test; the repository gate as the standing negative test for
  secret-shaped guide content; a naming-convention and asset-record check
  over `docs/assets/guides/` covering capture class and reference-run
  identifiers.
- **Gate summary**: unchanged in schema; the walkthrough and playbooks
  quote real `generated/sicario/gate-summary.json` content as verified or
  illustrative blocks.
- **Control applicability**: the table above, reviewed with the docs
  owner.
- **Reviewer approval**: code-owner review on every guide change, with the
  SEC-003 sanitation step recorded on asset-bearing changes and human
  verdicts on all first-run test logs.

## Success Criteria

- **SC-001**: A designated first-time evaluator completes the
  getting-started walkthrough cold — clean environment, guide text only —
  reaching `sicario verify passed` with exit code `0`, in 30 minutes or
  less excluding downloads, with zero outside help.
- **SC-002**: Every playbook in the FR-010 set has a committed passing
  first-run test log at its current version, and every deviation recorded
  in any log is either fixed in the guide or reclassified with rationale
  before the pass verdict.
- **SC-003**: 100% of quoted output blocks across all guides carry a
  verified or illustrative marker, and 100% of verified blocks pass the
  docs verification job in CI.
- **SC-004**: `sicario verify` over the repository reports zero findings
  with the complete guide set, assets, and test logs in place.
- **SC-005**: A reader following the failing-gate playbook against the
  staged failing example resolves every finding and reaches a green gate
  using only the playbook.
- **SC-006**: A reviewer following the evidence playbook against a
  prepared evidence file correctly identifies the disabled critical rule,
  its winning definition's origin, and the run's `asset_root` resolution,
  from artifacts alone.
- **SC-007**: Every visual asset's file name resolves to a guide slug,
  step, and captured version, and no asset's captured version predates the
  current release without a recorded carry-forward rationale.
- **SC-008**: The release immediately following the guides' publication
  either changes no guide-affecting output, or ships with the affected
  guides updated and a `docs/docs-impact.md` row recorded — demonstrating
  FR-052 operating, not just existing.
- **SC-009**: Given three one-line repository descriptions of different
  kinds, a first-time evaluator using only the selection guide reaches a
  profile choice for each and correctly states its composed presets, its
  framework defaults, and which listed frameworks are experimental-tier —
  recorded in the guide's first-run test log.
- **SC-010**: A first-time evaluator with no coding-agent environment
  completes the first-spec playbook cold — fresh init to
  `sicario verify passed` — using only the baseline path, with zero steps
  requiring tooling outside the playbook's stated prerequisites, recorded
  with elapsed time in its test log.
- **SC-011**: 100% of committed visual assets carry a capture class and
  reference-run identifiers; the CI-wiring playbook contains the failing
  run, passing run, and checks-panel captures; and no first-run test log
  records an evaluator who performed that guide's reference run.

## Assumptions

- **The docs-site publishes `docs/` as-is.** The existing Docusaurus build
  reads `../docs` and throws on broken links, so registering the new pages
  in the sidebar is the only publication step, and a renamed guide fails
  the site build rather than 404ing silently.
- **The repository's own gate is the enforcement point for guide
  hygiene.** Guides live inside the scanned tree, so the critical secret
  rules apply to them continuously without any new mechanism. This is
  deliberate: the guides are governed by the product they teach.
- **Verified blocks constrain guide style.** Output that includes
  timestamps, absolute paths, or environment-dependent text either gets a
  documented deterministic normalization or is labeled illustrative.
  Authors are expected to prefer commands with stable output; that
  pressure is a feature, because stable output is also what readers can
  compare against.
- **The evaluator role is renewable.** Each first-time evaluation consumes
  a person's first exposure to that guide. Subsequent evaluations of the
  same guide need a fresh evaluator or a materially changed guide;
  re-evaluation by the same person validates less and the test log says
  so when it happens.
- **Thirty minutes is a target, not a guess to defend.** If first-run logs
  show consistent overruns, the walkthrough is too long and should be
  split, and the elapsed-time field in the test log is what makes that
  visible.
- **Screencasts will lag.** Video is the most expensive artifact to
  re-capture, which is exactly why FR-033 makes it never load-bearing:
  text and screenshots carry the guide, and a stale screencast is
  removable without weakening any step.
- **Tool capture makes visuals cheap enough to keep fresh.** Browser
  automation can navigate to a real rendered page and capture it during a
  reference run, which moves most screenshots from the expensive manual
  class into a reproducible, re-runnable one. That is what makes
  screenshot-per-graphical-surface (FR-036) a sustainable expectation
  rather than a decree that would rot: the cost of re-capture at a new
  version is re-running the run, not scheduling a human at a desktop.
- **The reference run doubles as an honesty device.** Because captures and
  quoted outputs must come from a net-new repository walked through the
  guide's exact steps (FR-080), a guide whose steps do not actually
  produce its outputs cannot assemble a coherent reference run — the
  capture discipline and the truthfulness discipline are the same
  mechanism seen from two sides.
- **The Spec Kit slash-command flow is agent-hosted, and the guide says
  so.** The `/speckit-*` commands exist in this repository as agent skills
  — prompt documents a coding-agent environment surfaces as slash
  commands — not as shell commands. A reader without such an environment
  cannot run them, and no amount of documentation quality fixes that. The
  first-spec playbook therefore treats the manual template copy as the
  baseline path — it is the universal floor on every adoption path, since
  `sicario init` targets receive templates but no scripts directory — with
  the feature-creation script labeled as a convenience of native Spec Kit
  adoption and the slash-command flow as an agent-environment variant,
  rather than promising commands that require tooling the reader may not
  have.
- **The template passes the gate's form checks by construction, on both
  adoption paths.** A spec created from the template of a correctly
  initialized project — greenfield init or brownfield overlay — already
  contains every required heading and term, so the gate's presence and
  completeness checks pass before any real content exists. That is
  precisely why the staged-defect step exists: the first-spec playbook
  states the property rather than hiding it, stages a deliberate defect so
  the reader sees real findings, and presents the honest consequence — the
  gate enforces the form, and the substance of each section remains a
  human obligation.
- **Selection guidance is data-derived and can drift without output
  drift.** Profile composition and framework defaults live in shipped
  metadata, not in CLI output a verified block would catch, so the
  selection guide's tables are tied to `captured-version` and re-checked
  at release (FR-054, SEC-C-009) instead of being trusted to the output
  diff.
- **The word "playbook" here means a documentation artifact.** These are
  human-followed documents, not executable automation; nothing in this
  feature adds an orchestration runtime, and the Fleet Guardrails section
  governs the docs verification job and human process around the guides.
