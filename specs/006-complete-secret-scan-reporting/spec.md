# Feature Specification: Complete Secret-Scan Reporting

**Feature Branch**: `006-complete-secret-scan-reporting`
**Created**: 2026-07-27
**Status**: Draft
**Input**: The `regex-forbidden` evaluator stops after the first matching file, so
the repository's secret scan reports one finding no matter how many files are
affected. Specify complete, bounded, deterministic reporting.

## Overview

The `regex-forbidden` evaluator is the engine behind SicarioSpec's secret scan.
The shipped rule `SICARIO-HARDCODED-SECRET` (severity `critical`) points that
evaluator at every text file in the repository and fails the gate when a file
contains a credential-shaped assignment.

The evaluator walks its resolved target list, appends a finding for the first
file whose text matches, and then leaves the loop. Everything after that file is
never examined. The consequences are narrow, specific, and worth stating exactly:

- A repository with ten affected files reports one.
- Remediation degrades into a serial loop: fix one, re-run the gate, discover the
  next one, repeat. The number of round trips equals the number of affected
  files, and nobody knows that number until the last round trip returns clean.
- `--format json` and `--format sarif` carry the same single result, so any
  downstream consumer — GitHub code scanning, a security dashboard, a metrics
  pipeline — records an exposure count of one for a repository that may have
  dozens. The undercount is the artifact's own claim, not an inference a
  consumer made, which makes it worse than no data.

**What this is not.** The pass/fail verdict is unaffected. One finding already
fails the gate, and a repository with ten hardcoded credentials fails today
exactly as hard as it will after this change. There is no bypass here, no
suppressed verdict, and no way to use the current behavior to make a dirty
repository pass. This is a **completeness-of-reporting defect**: the gate's
verdict is correct and its evidence is incomplete. That distinction is load-bearing
for how this work is prioritized and how it is described in release notes, and
overstating it as a gate bypass would be inaccurate.

Incomplete evidence still matters. SicarioSpec's proposition is that the gate
produces evidence an auditor can rely on without re-deriving it. An artifact that
says "1 finding" when the truth is "34 occurrences across 11 files" is a
correct-verdict, wrong-evidence outcome, and the evidence is the product.

This feature specifies complete reporting: every occurrence, deterministically
ordered, bounded by caps that can never truncate silently, with no change to who
passes and who fails.

### Scope

In scope: the reporting behavior of the `regex-forbidden` evaluator kind for
every rule that uses it, including `SICARIO-HARDCODED-SECRET`; the location
detail carried on a finding; occurrence and per-rule caps with mandatory overflow
reporting; deterministic ordering; the coverage record written into gate
evidence; and the documentation that describes finding counts.

Out of scope: the content of the secret-detection patterns themselves; new
evaluator kinds; a suppression, baseline, or allowlist mechanism; changes to
which repositories pass or fail.

### Non-Goals

- **No new suppression mechanism.** A completeness fix and a new way to hide
  findings must not ship together. Per-rule exclusion lists, inline ignore
  comments, and finding baselines are deliberately excluded from this feature.
- **No verdict change.** Nothing here alters exit codes, severity, or the rule's
  pass/fail semantics.
- **No detection improvement.** Making the patterns catch more real credentials
  or fewer false positives is a separate feature with a separate risk profile.
- **No network, model, or AI dependency.** The gate stays stdlib-only.

## User Scenarios & Testing

### User Story 1 - See the Whole Exposure in One Run (Priority: P1)

As an engineer remediating a credential leak, I want one gate run to name every
affected location, so I can fix the exposure in a single pass instead of
discovering it one file at a time.

**Why this priority**: This is the defect. Everything else in this feature exists
to make this behavior safe to ship.

**Independent Test**: Create a repository with credential-shaped assignments in
several files, run the gate once, and confirm every affected file appears in the
output and in `generated/sicario/gate-summary.json`.

**Acceptance Scenarios**:

1. **Given** a repository where ten files each contain a credential-shaped
   assignment, **When** the gate runs, **Then** the run reports ten distinct
   locations, not one.
2. **Given** a repository where a single file contains three such assignments on
   three different lines, **When** the gate runs, **Then** the run reports three
   distinct locations within that file.
3. **Given** a repository with no matches, **When** the gate runs, **Then** the
   rule contributes zero findings and the gate passes, exactly as before.
4. **Given** a repository with exactly one match, **When** the gate runs,
   **Then** the output is equivalent to today's output for that repository.

---

### User Story 2 - Locate the Finding Precisely Enough to Act (Priority: P1)

As a reviewer reading a pull-request annotation, I want each finding to name the
file and the line, so the annotation lands on the offending line rather than on
the file as a whole.

**Why this priority**: A file-level finding in a two-thousand-line file is a
search task, not a remediation instruction. Line precision is also what SARIF
consumers expect; without it, the richer output is more rows of the same
imprecision.

**Independent Test**: Place a credential-shaped assignment on a known line, run
the gate with SARIF output, and confirm the result carries that line number in
its region and a clean, resolvable file path in its artifact location.

**Acceptance Scenarios**:

1. **Given** a match on line 42 of a file, **When** the gate emits SARIF,
   **Then** the result's artifact location is the repository-relative file path
   with no positional suffix, and the region's start line is 42.
2. **Given** the same match, **When** the gate prints human-readable output,
   **Then** the location reads as path and line together in the repository's
   existing `path:line` convention.
3. **Given** two matches on the same line, **When** the gate runs, **Then** one
   finding is reported for that line, because one line is one remediation action.
4. **Given** a finding produced by a rule kind that has no line concept, **When**
   evidence is written, **Then** the finding is recorded without a line and
   nothing downstream breaks.

---

### User Story 3 - Bounded Output With a Loud Overflow (Priority: P1)

As a maintainer, I want a pathological repository to produce a bounded number of
findings, and I want any truncation to be reported as loudly as the findings
themselves, so a capped run can never look cleaner than reality.

**Why this priority**: A vendored directory containing a matching pattern can
produce thousands of findings. An unbounded run is unusable; a silently bounded
run is a governance defect strictly worse than the one being fixed, because it
converts an undercount from a known bug into a designed behavior.

**Independent Test**: Generate more matches than the configured caps allow, run
the gate, and confirm the output reports both the capped findings and a distinct
overflow finding stating the exact number suppressed.

**Acceptance Scenarios**:

1. **Given** matches exceeding the per-rule cap, **When** the gate runs, **Then**
   it emits the capped number of findings plus one overflow finding naming the
   rule, the number reported, the number suppressed, and the true total.
2. **Given** a single file containing more matches than the per-file cap, **When**
   the gate runs, **Then** that file cannot consume the entire per-rule budget,
   and matches in other files are still reported.
3. **Given** a truncated run, **When** the gate summary is written, **Then** it
   records the true occurrence total alongside the reported count, so the
   artifact is never internally consistent with a smaller exposure.
4. **Given** a truncated run, **When** the verdict is computed, **Then** it is
   identical to the verdict of an untruncated run of the same repository.
5. **Given** a configuration that attempts to set a cap to zero or a negative
   value, **When** rules load, **Then** the configuration is rejected rather than
   silently clamped to a permissive value.

---

### User Story 4 - Same Verdict, Same Contract (Priority: P2)

As an adopter with the gate wired into CI, I want this change to alter what I see
without altering what passes, so upgrading is safe and reviewable.

**Why this priority**: A completeness fix that quietly changes pass/fail behavior
would be indistinguishable from a policy change, and adopters would rightly stop
trusting patch upgrades.

**Independent Test**: Run the gate against a fixed corpus before and after the
change; confirm the set of repositories that pass is identical and only the
finding counts differ.

**Acceptance Scenarios**:

1. **Given** any repository, **When** the gate runs before and after this change,
   **Then** the exit code is identical.
2. **Given** an existing consumer that reads `finding_count` from the gate
   summary, **When** it runs against an affected repository, **Then** the value
   is larger than before, and the release notes state that the field counts
   occurrences and has never counted failing rules.
3. **Given** the existing test suite, **When** it runs against the changed
   evaluator, **Then** tests asserting the presence of a finding code still pass
   without modification.

### Edge Cases

- A matching file is unreadable, is not valid UTF-8, or is binary.
- A match appears in a file whose own path is attacker-influenced text.
- The glob resolves directories as well as files.
- A file matches on its final line with no trailing newline.
- A match spans a line boundary because the pattern permits it.
- Two files differ only by case on a case-insensitive filesystem.
- The same file is reachable through a symlink as well as directly.
- A repository contains zero text files at all.
- Caps are configured lower than the number of files, so truncation begins in the
  first file scanned.
- A rule other than the secret rule uses the same evaluator kind with a narrow
  glob and expects at most one finding.

## Data Classification

| Artifact | Level | Classification owner | Retention | Residency | Sharing | Redaction |
|---|---|---|---|---|---|---|
| Finding location (repository-relative path and line) | Internal | Maintainer group | Per CI run plus release evidence retention | CI artifact store and repository | CI consumers, reviewers, auditors | Location only; matched text is never carried |
| Matched credential material in a scanned file | Restricted | Security owner | Not retained by the gate at any point | Never leaves the scanned working tree | Never shared, never echoed, never logged | Total exclusion from all outputs, not masking |
| `generated/sicario/gate-summary.json` | Internal | Maintainer group | Per CI run plus release evidence retention | CI artifact store | CI consumers and auditors | Paths, lines, counts, and rule identifiers only |
| SARIF output (`--format sarif`) | Internal | Maintainer group | Per code-scanning platform policy | Code-scanning platform of the adopting org | Anyone with repository read access on that platform | Paths, lines, and static rule messages only |
| Scan coverage record (files scanned, files skipped, occurrence totals) | Internal | Maintainer group | Same as the gate summary that carries it | CI artifact store | CI consumers and auditors | Counts and paths only |

Classification rule for this feature: the scanner reads `restricted` material and
must emit only `internal` material. The boundary is absolute — a finding names
**where**, never **what**. No prefix, no suffix, no character count of the
matched value, and no digest of it. A digest is still derived from the credential
and belongs on the restricted side of the line.

## Tagging Discipline

| Tag | Value |
|---|---|
| owner | sicario-spec-maintainers |
| system | sicario-spec |
| environment | development |
| data-classification | internal |
| retention | per-run-plus-release-evidence |
| compliance-scope | appsec-secrets-management |
| project | complete-secret-scan-reporting |
| feature-id | 006-complete-secret-scan-reporting |
| control-family | detect-and-report |
| evidence-path | generated/sicario/gate-summary.json |

Every emitted finding carries the rule identifier, the severity, the
repository-relative path, and the line where one applies. Every truncation event
additionally carries `truncation-scope` (per-file or per-rule), the effective cap
value, and the suppressed count, so a capped run can be indexed and audited on
the same terms as an uncapped one.

## Roles, Assets, And Abuse Actors

- **Legitimate roles**: the engineer remediating findings; the reviewer reading
  pull-request annotations; the maintainer who owns rule files and caps; the
  security owner who accepts residual risk; the auditor reading gate evidence.
- **Protected assets**: the completeness of the finding set; the deterministic
  ordering of that set; the caps and their overflow reporting; the exclusion
  set; the guarantee that no credential material reaches an artifact.
- **Abuse actors**: a contributor under schedule pressure who wants a clean
  dashboard more than a clean repository; a compromised or careless dependency
  update that adds matching files in bulk; anyone able to open a pull request,
  since paths and file contents are attacker-influenced input to agent context;
  an insider hiding one real credential inside a flood of decoys.
- **High-impact actions**: raising or removing a cap; widening the skipped-path
  set; disabling the rule by identifier override; deleting the overflow finding;
  changing the ordering key.

## Trust Boundaries

- **Repository working tree to gate.** Every scanned file is untrusted data. The
  gate reads bytes and reports positions; it never interprets file content as
  instruction, configuration, or code, and no string inside a scanned file can
  turn a check off, raise a cap, or change a message.
- **File path to output.** Paths are attacker-influenced. A contributor chooses
  file and directory names, so path text flows from an untrusted source into
  evidence artifacts, terminal output, and agent context. Paths are emitted as
  data and are never treated as directives by anything downstream.
- **Matched content to output.** This boundary is one-way and closed. Matched
  text crosses into the evaluator and never crosses back out into a message, a
  log line, a summary, or a SARIF result.
- **Rule file to evaluator.** Rule files supply patterns and caps. They are
  repository content under code ownership, not runtime input from an untrusted
  party, and they cannot introduce executable behavior — the evaluator kind set
  is fixed in code.
- **Gate to verdict.** The verdict is a function of whether any finding exists.
  Caps, ordering, and formatting sit strictly downstream of the verdict and can
  never influence it.
- **Gate to consumers.** SARIF and JSON consumers sit outside the gate. They
  receive counts that are complete or explicitly marked truncated; they are never
  handed a silently partial set.

## Security Requirements

- **SEC-001**: The evaluator MUST report every distinct occurrence location of a
  forbidden pattern, subject only to the caps defined in this specification. It
  MUST NOT stop scanning after the first matching file.
- **SEC-002**: A finding MUST NOT contain any portion of the matched text, any
  transformation of it, or any digest of it. The message MUST remain the static
  message declared on the rule.
- **SEC-003**: Truncation MUST be impossible to perform silently. When any cap
  suppresses one or more occurrences, the run MUST emit a distinct, unsuppressible
  overflow finding naming the rule identifier, the reported count, the suppressed
  count, and the true total.
- **SEC-004**: The overflow finding MUST carry the same severity as the rule
  whose output it truncates, so a truncated critical finding set can never be
  represented by a low-severity notice.
- **SEC-005**: Occurrence counting MUST be exact and MUST continue after emission
  stops, so the suppressed and total counts reported are true counts rather than
  lower bounds.
- **SEC-006**: The verdict MUST be unchanged by this feature. A repository that
  failed before MUST fail after, a repository that passed before MUST pass after,
  and caps MUST NOT participate in the pass/fail decision.
- **SEC-007**: Findings MUST be emitted in a total, deterministic order: by
  repository-relative path in POSIX form, then by line, then by column. The order
  MUST NOT depend on filesystem enumeration order, locale, platform path
  separator, or run order.
- **SEC-008**: Caps MUST be positive integers. A cap of zero, a negative cap, or
  a non-integer cap MUST be rejected at rule load with a clear error rather than
  clamped, ignored, or defaulted.
- **SEC-009**: This feature MUST NOT introduce any new mechanism for excluding
  paths, suppressing findings, or baselining known findings.
- **SEC-010**: The effective caps and the effective skipped-path set used for the
  run MUST be recorded in gate evidence, so a later widening is visible in the
  evidence trail and not only in a configuration diff.
- **SEC-011**: Files that cannot be read or decoded MUST be counted and recorded
  as skipped in the coverage record. A file the scanner could not inspect MUST
  NOT be indistinguishable from a file the scanner cleared.
- **SEC-012**: The evaluator MUST remain stdlib-only, offline, and free of any
  model call, network call, subprocess, or AI library import, directly or
  transitively.
- **SEC-013**: The evaluator MUST be read-only with respect to the repository. It
  MUST NOT rewrite, quarantine, or repair a file containing a match.
- **SEC-014**: Path values written into evidence MUST be repository-relative and
  MUST NOT escape the project root, including via symlink traversal.

## Privacy Requirements

- **Data minimization**: the gate emits the minimum sufficient to act — rule
  identifier, severity, path, line, and static message. Matched text, surrounding
  context lines, file contents, and author identity are all outside that minimum
  and are not collected.
- **Purpose limitation**: the coverage record exists to make truncation and
  scan gaps visible. It is not a productivity metric and must not be repurposed
  as one; per-author or per-team attribution is deliberately absent.
- **Consent or notice requirements**: scanning covers repository content only,
  within a tool the repository owner runs on their own tree. No personal data is
  processed, and no notice obligation arises. This holds only while SEC-002 holds
  — echoing matched text could pull personal data into CI artifacts.
- **Redaction requirements**: redaction is achieved by exclusion rather than
  masking. Nothing derived from the matched value is emitted, so there is no
  masked value that could later be unmasked, correlated, or brute-forced.

## Compliance / Control Applicability

Map applicable requirements without claiming certification.

| Domain | Applicable? | Rationale | Evidence |
|---|---|---|---|
| AppSec / ASVS | Yes | Secret detection and its evidence quality fall under secret-management and logging verification requirements | `generated/sicario/gate-summary.json`, SARIF output |
| NIST SSDF | Yes | Automated detection of embedded credentials with reviewable output supports the review-and-scan practices | Gate summary, coverage record, CI run logs |
| Supply Chain / SLSA | Partial | Complete reporting improves the fidelity of build-time security evidence; it does not affect provenance or build integrity | Release evidence attached to tagged builds |
| AI Risk / NIST AI RMF | Partial | The change does not use AI, but it defines how untrusted repository text enters agent context through findings | AI / Tool Boundary section of this specification |
| Cloud/IaC | Yes | Infrastructure files are within the scanned set, and a credential in a template is a high-impact finding | Findings against `.tf`, `.yml`, and `.json` paths |

## AI / LLM Risk

This feature contains no AI. The evaluator is deterministic code over local
files. It matters here anyway, because this repository is worked by AI agents and
this change increases the volume of untrusted repository text that reaches an
agent's context through gate output.

- **Prompt injection exposure**: findings carry repository-relative paths, and
  paths are chosen by whoever opens a pull request. A contributor can create a
  directory or file whose name reads as an instruction — telling a reader to
  ignore prior direction, to mark findings resolved, or to raise a cap — and that
  text will appear in terminal output, in the gate summary, and therefore in the
  context of any agent that reads either. Increasing the number of reported
  findings increases the number of such strings that can be delivered per run.
  The mitigations are structural: the gate never interprets its own output; a
  finding's message is always the static rule message rather than anything drawn
  from the repository; and agent-facing documentation must state that paths and
  messages in gate output are data to be reported, never direction to be
  followed. An agent that "resolves" a finding because a path told it to is
  reporting a governance failure, not a fix.
- **Tool boundary controls**: the evaluator's entire tool surface is the local
  filesystem, read-only, scoped to the project root. No subprocess, no shell, no
  socket, no package resolution, no model endpoint. Nothing in this feature
  widens that surface, and the surface is fixed in code rather than configured in
  a rule file, so no rule and no scanned file can extend it.
- **Model routing**: not applicable. There is no model in the path, and adding
  one to any part of the verdict would violate the repository's central
  invariant.
- **Memory poisoning risk**: the gate holds no state between runs. Every run
  re-derives every finding from the working tree, so a poisoned prior run cannot
  influence a later verdict. This is also why no baseline mechanism is being
  introduced here — a baseline is exactly the kind of persistent state that can
  be poisoned.
- **Data leakage risk**: the dominant leakage risk is the scanner itself echoing
  the credential it found into a CI artifact that is far more widely readable
  than the source file. SEC-002 forbids it absolutely, and SA-004 tests for it.
- **Human approval boundaries**: raising a cap, widening the skipped-path set, or
  disabling the rule requires human approval by code ownership on rule files and
  a recorded entry in the exception register. No agent may make those changes as
  a side effect of remediating findings.
- **AI evals / red-team tests**: a negative test asserts that a repository
  containing an instruction-shaped file path produces an ordinary finding with
  the static rule message and no behavioral change.

## Fleet Guardrails

The gate runs inside CI orchestration alongside other checks, so it inherits
fleet discipline even though it is a single synchronous process:

- **Idempotency**: two runs over an unchanged tree produce byte-identical
  findings, in identical order, with identical counts. Nothing in a finding
  depends on the clock, the hostname, the runner, or the enumeration order of the
  filesystem.
- **Retry**: a re-run after an infrastructure failure re-derives everything from
  the working tree. No state is carried between runs, so a retry can neither
  double-count nor lose an occurrence.
- **Dead-letter**: a file that cannot be read or decoded is not silently dropped.
  It is counted as skipped and recorded in the coverage record, so an unscannable
  file is visible as a coverage gap rather than mistaken for a clean file. The
  same discipline applies to suppressed occurrences: truncation produces an
  explicit overflow record, never a silent drop.
- **Workflow state**: the only durable state is the repository itself. Caps and
  the skipped-path set live in rule files and code, both reviewable and
  revertible as ordinary changes, never in a CI variable, cache, or external
  store.
- **Human approval**: changes that reduce what the gate reports — cap increases
  that go unreviewed, exclusion widening, rule disablement — require human
  approval through code ownership on rule files. Automation may not make them.
- **Concurrency**: the evaluator does not write to the tree it scans, so parallel
  jobs sharing a checkout cannot interfere. Evidence is written once per run to a
  run-scoped output directory.

## External System Access

- **External systems**: none. The evaluator touches the local filesystem only.
- **Read/write permissions**: read-only on the project tree; write-only to
  `generated/sicario/` for evidence.
- **Production impact**: none directly. The indirect effect is on CI outcomes and
  on the counts a security dashboard displays, which will rise for affected
  repositories the first time the corrected gate runs.
- **Human approval needed**: not for running the scan. Yes for any change to
  caps, exclusions, or rule enablement.

## Secrets / Credential Handling

- **Secret sources**: the gate consumes no credentials of its own. The
  credentials it encounters are those already committed to the repository under
  inspection — which is the failure it exists to report.
- **Runtime injection method**: none. The evaluator requires no credential,
  token, or key of any kind to do its work, and it must never acquire one.
- **Redaction requirements**: matched values are excluded entirely from every
  output surface, per SEC-002. Exclusion, not masking.
- **Rotation owner**: the repository's security owner owns rotation of any
  credential this scan surfaces. Rotation and revocation, not deletion of the
  line, is the correct remediation — the value is compromised from the moment it
  reaches version control history, and removing it from the working tree does not
  remove it from history.

## Audit / Logging Requirements

- **Events to log**: rule identifier, severity, repository-relative path, line
  number, static message; per rule, the count of files scanned, files skipped as
  unreadable, total occurrences found, findings reported, and occurrences
  suppressed; the effective caps and skipped-path set; every truncation event
  with its scope and cap value.
- **Fields to exclude**: matched text, any substring or transformation of it, any
  digest of it, file contents, surrounding context lines, author identity,
  environment variables, and absolute filesystem paths.
- **Retention**: per CI run, plus whatever the adopting organization retains for
  release evidence. The gate imposes no retention of its own and keeps no history
  between runs.
- **Alerting**: a non-zero exit fails the CI check, which is the alert. A
  truncation event is additionally surfaced as its own finding so that a capped
  run is visible without reading the coverage record.

## Operational Signal / Response Path

- **Signals this feature should emit**: the per-occurrence findings; the overflow
  finding on truncation; the coverage record naming scanned, skipped, reported,
  suppressed, and total counts.
- **Detection or alert logic**: any occurrence fails the gate. A truncation event
  is a distinct signal reviewers should treat as "the exposure is at least this
  large," never as "the exposure is this large."
- **Triage owner**: the repository's security owner for the credentials
  themselves; the maintainer group for the scanner's own behavior, including
  false-positive volume and cap tuning.
- **Response or rollback action**: rotate and revoke every surfaced credential
  first, remove the literal second, then re-run to confirm a clean scan. If cap
  tuning is needed, tune it in the rule file under review with a recorded
  rationale — never by disabling the rule.
- **Evidence retention location**: `generated/sicario/gate-summary.json` plus the
  SARIF artifact where the adopting platform retains one.

## Misuse / Abuse Cases

Each case names the abuse, the deterministic detection, and the mitigation.
"Detected" means a finding and a non-zero exit, not a comment.

- **AC-001 — Moving a cap to make the dashboard look better.** A contributor
  under pressure edits the caps: lowering them so fewer findings are reported and
  a metrics dashboard shows a smaller exposure, or raising them so a review drowns
  in rows nobody reads. *Detection*: caps live in rule files under code ownership;
  the effective cap values are recorded in the coverage record on every run, so a
  reduction is visible in evidence as well as in the diff; and any cap that
  suppresses an occurrence produces an overflow finding stating the true total,
  so a lowered cap makes the run louder rather than quieter. *Mitigation*: cap
  changes require code-owner review and a recorded rationale; the true total is
  always present in evidence regardless of the cap; and no cap value can reduce
  the reported set to zero while occurrences exist, because a positive cap always
  emits at least one finding and a truncation always emits the overflow finding.

- **AC-002 — Adding an exclusion to hide a real finding.** Rather than fix a
  credential, a contributor adds the containing directory to the skipped-path set
  or narrows the rule's glob. *Detection*: the effective skipped-path set is
  recorded in the coverage record on every run, so a widening is comparable
  across runs from evidence alone rather than requiring a configuration diff.
  *Mitigation*: this feature introduces no new exclusion mechanism at all
  (SEC-009), so the only way to exclude is to change code or a rule file, both
  under code ownership. An exclusion that removes a previously reported location
  should be reviewed as a risk acceptance and recorded in the exception register.

- **AC-003 — Disabling the rule by identifier override.** The documented override
  mechanism lets a project redefine a shipped rule by identifier and set it to
  disabled. That is a legitimate feature and an obvious abuse path.
  *Detection*: the coverage record names every rule evaluated and every rule
  loaded but disabled, so a disabled critical rule is visible in evidence rather
  than only in an overriding file that a reviewer must think to look for.
  *Mitigation*: unchanged as a capability, made visible as an act. Project rule
  directories are code-owned, and disabling a `critical` rule should require a
  recorded exception with an owner and an expiry.

- **AC-004 — Output flooding to bury one real credential.** An actor commits
  hundreds or thousands of decoy matches — a vendored tree, a fixture directory,
  a generated file — so that the one real credential is either truncated away or
  lost in the noise. *Detection*: occurrence counting continues past the emission
  cap, so the true total is always reported even when the finding list is
  truncated; a sudden order-of-magnitude jump in the total is itself a reviewable
  signal. *Mitigation*: three structural properties. First, the per-file cap is
  applied before the per-rule cap, so no single file can consume the whole
  budget and matches in other files still surface. Second, ordering is by path,
  so the reported subset is a stable, explainable slice rather than an arbitrary
  one, and a reviewer can reason about what was truncated. Third, and decisively,
  the verdict is unaffected: flooding cannot make the gate pass, so burying a
  credential in noise still leaves a failing, blocking check that must be
  investigated before merge.

- **AC-005 — Treating richer output as permission to defer.** With ten findings
  visible instead of one, a team fixes the two that look important and leaves the
  rest, reasoning that the gate now shows "known" issues. *Detection*: the gate
  has no partial-pass state. Any remaining occurrence keeps the exit code
  non-zero, and there is no mechanism to mark a finding as known, accepted, or
  deferred — which is precisely why SEC-009 forbids introducing one in this
  feature. *Mitigation*: severity belongs to the rule, not to the finding, so all
  occurrences of a `critical` rule are `critical` and none can be triaged down at
  the finding level. A team that genuinely needs to defer must record an
  exception with an owner and an expiry, which the existing active-risk hygiene
  rule already validates.

- **AC-006 — Deleting or downgrading the overflow finding.** A contributor
  removes the truncation notice, or emits it at a low severity, so that a capped
  run reads as complete. *Detection*: the overflow finding is a mandatory,
  unsuppressible output of any truncating run (SEC-003), it inherits the
  truncated rule's severity (SEC-004), and the coverage record independently
  carries reported, suppressed, and total counts, so a missing overflow finding
  contradicts its own run's evidence. *Mitigation*: two independent artifacts
  must agree, and a positive test asserts both the overflow finding and the
  matching coverage counts, so removing either one fails the suite.

- **AC-007 — Rotating a credential's location instead of the credential.** A
  contributor moves the literal into a file the scanner does not cover — an
  unusual extension, an unreadable encoding — so the finding disappears without
  the credential being revoked. *Detection*: unreadable and undecodable files are
  counted as skipped and recorded (SEC-011), so coverage gaps are visible rather
  than silent. *Mitigation*: the residual limitation is stated honestly — pattern
  scanning cannot see what it cannot decode, and this feature does not claim
  otherwise. The response path requires rotation and revocation as the primary
  remediation, so removing the literal is never sufficient on its own.

- **AC-008 — Making findings unstable to hide a regression.** Ordering that
  varies by platform or enumeration order lets a real change hide inside output
  churn, and defeats any diffing a reviewer or a tool attempts. *Detection*:
  ordering is a total order on POSIX-form path, then line, then column (SEC-007),
  and a determinism test asserts byte-identical output across repeated runs.
  *Mitigation*: caps are applied after sorting, so the retained subset is stable
  too; a truncated run diffs cleanly against another truncated run of the same
  tree.

- **AC-009 — Echoing the credential into a widely readable artifact.** A
  well-meaning change adds the matched text to the finding message "to make
  remediation easier," publishing a live credential into CI logs and SARIF
  storage readable by everyone with repository access. *Detection*: SEC-002 and a
  negative test that asserts no output surface contains the matched value.
  *Mitigation*: messages are static rule text and are never composed from scanned
  content, so there is no code path that could carry matched text outward.

## Functional Requirements

### Occurrence reporting

- **FR-001**: The `regex-forbidden` evaluator MUST examine every resolved target
  file and MUST NOT terminate its scan after the first match.
- **FR-002**: The evaluator MUST report one finding per distinct matching **line**
  within each matching file, rather than one finding per file.
- **FR-003**: Where two or more matches occur on the same line, the evaluator
  MUST report exactly one finding for that line, because one line is one
  remediation action.
- **FR-004**: A finding MUST carry the repository-relative path in POSIX form and
  the one-based line number of the match.
- **FR-005**: The finding record MUST express the line as a distinct value rather
  than packing it into the path string, so that the path remains a resolvable
  file reference for consumers that require one.
- **FR-006**: Findings produced by rule kinds that have no line concept MUST
  remain valid with no line recorded, and consumers MUST treat an absent line as
  a file-scoped location.
- **FR-007**: Human-readable output MUST render a located finding in the
  repository's existing `path:line` convention, matching how active-risk row
  findings already read.
- **FR-008**: SARIF output MUST place the repository-relative path in the
  artifact location and the line number in the result's region start line. The
  artifact location MUST NOT carry a positional suffix.
- **FR-009**: The evaluator MUST scan each file's text in a single pass and MUST
  NOT re-run the pattern per line.

### Caps and overflow

- **FR-010**: The evaluator MUST support a per-file occurrence cap and a
  per-rule finding cap, both configurable per rule with documented defaults.
- **FR-011**: The per-file cap MUST be applied before the per-rule cap, so that
  no single file can consume the entire per-rule budget.
- **FR-012**: Both caps MUST be positive integers. Zero, negative, and
  non-integer values MUST be rejected at rule load rather than clamped or ignored.
- **FR-013**: When either cap suppresses one or more occurrences, the run MUST
  emit exactly one overflow finding per rule, carrying that rule's identifier,
  its severity, the number of findings reported, the number of occurrences
  suppressed, the true total occurrence count, and the number of distinct files
  involved.
- **FR-014**: The overflow finding MUST NOT be suppressible by any cap,
  configuration value, or rule parameter.
- **FR-015**: The evaluator MUST continue counting occurrences after it stops
  emitting findings, so suppressed and total counts are exact rather than lower
  bounds.
- **FR-016**: Caps MUST be applied after deterministic ordering, so the retained
  subset is stable across runs and machines.

### Determinism

- **FR-017**: Findings MUST be ordered by repository-relative POSIX path, then by
  line, then by column, producing a total order with no ties.
- **FR-018**: Ordering MUST NOT depend on filesystem enumeration order, locale
  collation, or the platform path separator.
- **FR-019**: Two runs over an unchanged tree MUST produce byte-identical finding
  lists and byte-identical coverage counts.

### Coverage and evidence

- **FR-020**: The gate summary MUST record, per rule that uses this evaluator:
  files scanned, files skipped as unreadable or undecodable, total occurrences,
  findings reported, occurrences suppressed, a truncation flag, and the effective
  cap values.
- **FR-021**: The gate summary MUST record the effective skipped-path set used
  for the run, so a later widening is detectable from evidence alone.
- **FR-022**: The gate summary MUST record rules that were loaded but disabled by
  identifier override, so a disabled critical rule is visible in evidence.
- **FR-023**: Additions to the gate summary MUST be additive. Existing keys —
  including `status`, `finding_count`, and `findings` — MUST retain their names,
  types, and meanings.
- **FR-024**: The `finding_count` field MUST continue to mean "number of
  findings," which after this change is a count of occurrences plus any overflow
  findings. Documentation MUST state this plainly, because the field's value will
  increase for affected repositories.

### Invariants and compatibility

- **FR-025**: The verdict MUST be unchanged. The set of repositories that pass
  and fail MUST be identical before and after this change.
- **FR-026**: The evaluator MUST remain stdlib-only and offline, with no model
  call, no network call, no subprocess, and no AI library import.
- **FR-027**: A finding MUST NOT contain matched text, any substring or
  transformation of it, or any digest of it.
- **FR-028**: The change MUST apply to the `regex-forbidden` evaluator kind as a
  whole, not only to the shipped secret rule, so that every rule using the kind
  reports completely.
- **FR-029**: Existing tests that assert the presence of a finding code MUST
  continue to pass without modification.
- **FR-030**: No new exclusion, suppression, ignore-comment, or baseline
  mechanism may be introduced by this feature.
- **FR-031**: Documentation MUST be updated where it describes what a run
  reports: the finding-code reference, the rule-engine kind reference including
  the new cap parameters and their defaults, and the release notes.

## Security Acceptance Criteria

- **SA-001**: A repository with credential-shaped assignments in ten files
  produces ten located findings in one run, and the same run's exit code is
  non-zero — demonstrating completeness without a verdict change.
- **SA-002**: A repository with three such assignments on three lines of one file
  produces three findings, and a file with two matches on one line produces one.
- **SA-003**: A run whose occurrences exceed a cap produces the capped findings
  plus an overflow finding whose suppressed and total counts equal the coverage
  record's counts exactly.
- **SA-004**: No output surface — human-readable output, JSON, SARIF, or the gate
  summary — contains the matched value or any transformation of it, asserted by a
  negative test that plants a known value and searches every artifact for it.
- **SA-005**: A cap configured as zero or negative is rejected at rule load with
  a clear error, and no run proceeds with a permissive default substituted.
- **SA-006**: Ten consecutive runs over an unchanged tree produce byte-identical
  finding lists, including under truncation.
- **SA-007**: A file that cannot be decoded appears in the coverage record as
  skipped, and the count of skipped files is non-zero for a tree that contains
  one — so an unscannable file is never indistinguishable from a clean one.
- **SA-008**: A repository containing an instruction-shaped file or directory
  name produces an ordinary finding whose message is the static rule message,
  with no change to counts, ordering, or verdict.
- **SA-009**: A corpus run before and after the change yields an identical
  pass/fail set, with differences confined to finding counts and locations.
- **SA-010**: A single file containing more matches than the per-file cap does not
  prevent matches in other files from being reported.

## Security Evidence Chain

| Chain ID | Risk / Decision | Control / Requirement | Test / Gate | Evidence Path | Owner | Approval / Accepted Risk |
|---|---|---|---|---|---|---|
| SEC-001 | Exposure undercounted because scanning stops at the first file | FR-001, FR-002 | SA-001, SA-002 | `generated/sicario/gate-summary.json` | Maintainer group | Approved as a defect fix; no verdict change |
| SEC-002 | Caps silently hide occurrences | FR-013, FR-014, FR-015 | SA-003 | Gate summary coverage record and overflow finding | Maintainer group | Approved; silent truncation rejected as a design option |
| SEC-003 | Credential material leaked into CI artifacts | SEC-002, FR-027 | SA-004 | Negative test in the suite | Security owner | Approved; exclusion required over masking |
| SEC-004 | Non-deterministic output defeats diffing and hides regressions | FR-017, FR-018, FR-019 | SA-006 | Repeat-run comparison in CI | Maintainer group | Approved |
| SEC-005 | Unreadable files mistaken for clean files | SEC-011, FR-020 | SA-007 | Coverage record | Maintainer group | Residual limitation accepted and recorded |
| SEC-006 | Untrusted path text reaching agent context | AI / LLM Risk section, FR-027 | SA-008 | Agent-facing documentation and negative test | Maintainer group | Approved |
| SEC-007 | Output volume regression in large repositories | FR-010, FR-011, FR-016 | SA-010 | Coverage record, CI timing | Maintainer group | Approved with defaults documented |
| SEC-008 | Consumers misreading a larger `finding_count` as a policy change | FR-023, FR-024, FR-031 | SA-009 | Release notes and finding-code reference | Maintainer group | Approved |

## Evidence To Produce

- **Threat model update**: record that the scanner's output is an attacker-
  influenced channel into agent context, and that its content is data.
- **Abuse-case update**: add AC-001 through AC-009 to the repository abuse-case
  register, with their detections and mitigations.
- **Data classification record**: record the restricted-in, internal-out boundary
  for the scanner, including the prohibition on digests of matched values.
- **Tagging taxonomy updates**: add `truncation-scope` as an accepted evidence
  tag alongside the existing finding tags.
- **Security Evidence Chain**: the table above, carried into the plan and kept
  current as requirements move.
- **Tests**: positive tests for multi-file and multi-line reporting; a
  same-line deduplication test; cap and overflow tests asserting exact suppressed
  and total counts; a cap-validation test; a determinism test over repeated runs;
  a coverage-record test including skipped files; a negative test asserting no
  matched value appears in any artifact; a compatibility test asserting existing
  finding-code assertions still hold.
- **Gate summary**: `generated/sicario/gate-summary.json`, extended additively
  with the per-rule coverage record, the effective caps, the effective
  skipped-path set, and disabled rule identifiers.
- **Control applicability**: the table above, reviewed with the security owner.
- **Reviewer approval**: code-owner review on the evaluator, the rule file, and
  the documentation, with the security owner named on the review because the
  change touches a `critical` rule's output contract.

## Success Criteria

- **SC-001**: A repository with credential-shaped assignments in N files and M
  total occurrences reports M located findings in a single run, for every N and M
  below the configured caps — no serial fix-and-re-run loop remains.
- **SC-002**: The number of gate runs required to discover the full exposure
  drops from one per affected file to exactly one, measured on a fixture with at
  least ten affected files.
- **SC-003**: A reviewer can open a SARIF-consuming code-scanning view and land on
  the offending line of each affected file without opening a terminal.
- **SC-004**: No configuration, cap value, rule parameter, or repository content
  can produce a run in which occurrences are suppressed and the output does not
  say so — verified by an exhaustive test over cap boundaries.
- **SC-005**: Reported findings are byte-identical across ten consecutive runs, on
  more than one platform, including truncated runs — 100% reproducible with no
  observed variance.
- **SC-006**: The set of repositories that pass the gate is identical before and
  after this change across the full example and test corpus.
- **SC-007**: No artifact produced by the gate contains any part of a matched
  value, verified by planting a known distinctive value and searching every
  emitted artifact for it.
- **SC-008**: The additional wall-clock cost of complete reporting on a clean
  repository is nil, because a clean repository already reads every target file;
  and on an affected repository the added cost is bounded by the remainder of the
  same single full-tree read.
- **SC-009**: A run against a repository with an unreadable file reports a
  non-zero skipped count, so scan coverage is legible rather than assumed.
- **SC-010**: An adopter can determine, from the gate summary alone and without
  re-running the scan, how many occurrences exist, how many were reported, how
  many were suppressed, and which paths were excluded from scanning.

## Assumptions

- **Line-level over file-level is the right granularity, and the tradeoff is
  real.** File-level reporting is a smaller change: it needs no new location
  detail and no change to the finding record. It is also insufficient for the two
  uses that motivate the fix — a pull-request annotation must land on a line, and
  a reviewer fixing three occurrences in one file needs three locations. The
  repository already carries line numbers in findings (active-risk row findings
  and the scanner-output importers both do it), so line precision is an
  established convention here rather than a new concept. The cost is a location
  value on the finding record and a larger finding count; both are accepted, and
  the count increase is documented rather than smoothed over.
- **The line belongs in its own value, not appended to the path.** Packing
  `path:line` into the path field would require no change to the finding record
  and would match what the existing importers already do — but it corrupts the
  SARIF artifact location, which must be a resolvable file reference for a
  code-scanning platform to attach an annotation. The correct shape is a clean
  path plus a separate line, rendered as `path:line` only for human output. The
  existing importers that pack the two together are an adjacent inconsistency,
  recorded here and left out of scope.
- **Performance is a non-issue and should not be over-claimed.** The target glob
  already resolves the whole tree, and a clean repository already reads every
  file to the end, so complete reporting adds nothing to the common case. The
  only case that gets slower is a repository that already fails, where the scan
  no longer stops early — bounded above by the cost of the full read a passing
  run performs anyway. Within a matching file, a single pass over the text with
  line offsets computed only for files that actually match keeps the per-file
  cost linear.
- **Caps are a safety valve, not a policy.** The defaults should be high enough
  that a normal repository never reaches them and low enough that a pathological
  one stays usable. A run that hits a cap is an unusual event worth surfacing on
  its own terms, which is why the overflow finding exists.
- **The `finding_count` field will increase for affected repositories.** Any
  consumer that has been reading it as "number of failing rules" was already
  wrong; this change makes that visible. The correction belongs in release notes,
  not in a compatibility shim that would preserve the undercount.
- **Existing tests assert the presence of finding codes, not their counts.** The
  secret-scan test checks membership in a set of codes, and the clean-project test
  asserts an empty finding list, so neither constrains this change. Any future
  test that pins an exact count for a multi-file rule should be written against
  the coverage record instead.
- **Residual limitation, stated honestly**: this remains a pattern scanner. It
  reports what its patterns match in files it can decode. A credential in an
  encoding it cannot read, in a binary blob, in a compressed archive, or shaped
  unlike any configured pattern is not reported, and complete reporting of
  matches must never be read as complete detection of credentials. Coverage gaps
  are counted and recorded so the limit is visible rather than implied away.
- **Rotation, not deletion, is remediation.** A credential committed to version
  control is compromised from that moment. This feature makes the exposure
  legible; it does not reduce it, and the response path says so.
