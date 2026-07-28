# Feature Specification: Advisory Quality Tier

**Feature Branch**: `004-advisory-quality-tier`
**Created**: 2026-07-27
**Status**: Draft

## Overview

SicarioSpec's tagline is "kill risk before it ships." Its enforced behavior is
narrower than that: `sicario verify` checks **completeness**, not **quality**.
A threat model that says "STRIDE considered, no threats identified" satisfies
every check the gate applies. This specification does not fix that by making the
gate smarter — it names the gap, states why the gate must stay exactly as dumb
and as trustworthy as it is, and specifies a **second, clearly-labeled advisory
tier** that carries a quality signal to the human approver without ever touching
the verdict.

### The gap, stated accurately

The problem is materially worse than "well-shaped boilerplate passes." The
evaluators were read directly, and none of them parse document structure:

- **`sicario_cli/rules/kinds/section_exists.py`** lowercases the **entire file**
  and tests `heading.lower() not in text_lower`. It never parses a Markdown
  heading. Heading level is irrelevant. Heading position is irrelevant. Whether
  the string is a heading at all is irrelevant. A single prose sentence reading
  "we did not write separate abuse cases for this change" fully satisfies the
  `Abuse Cases` requirement of `SICARIO-SPEC-SECTION`.
- **`sicario_cli/rules/kinds/classification_complete.py`** activates on the
  whole-file substring `data classification`, then tests whole-file substring
  membership for `classification owner`, `retention`, `residency`, `sharing`,
  and `redaction`, plus at least one level word from public / internal /
  confidential / restricted / regulated. It never locates a table, never reads a
  header row, never associates a data artifact with a level. Five words scattered
  anywhere in the file satisfy `SICARIO-DATA-CLASSIFICATION-INCOMPLETE`.
- **`sicario_cli/rules/kinds/tagging_complete.py`** has the same shape:
  whole-file substring membership for `owner`, `system`, `environment`,
  `data-classification`, and `retention`. Four of those five are ordinary English
  that appears incidentally in almost any technical document — and `owner` is
  already guaranteed by the `classification owner` string the classification rule
  demands. Only the hyphenated `data-classification` is distinctive enough to be
  written on purpose.

So the honest statement of the gate's contract is not "fill in the form before
it ships." It is: **make the right words appear somewhere in the file before it
ships.** The gate is a vocabulary check with an exit code.

### What this feature does and does not change

This is not a criticism that the deterministic gate should be replaced. The gate
is the product. It halts, it is stdlib-only, it has no model call, no network,
and no AI import, and that is precisely why its verdict can be trusted in a
merge gate. A cheap, legible, unfoolable-by-persuasion check is worth more than
an expensive check whose reasoning can be argued with.

The design tension is stated plainly and is not resolved in this feature:

> The only thing that could meaningfully assess the *quality* of a threat model
> is a model. A model is structurally barred from the verdict. **That bar is
> correct and must not move.** Nothing in this specification proposes weakening
> it, softening it, or creating an exception to it.

The consequence is accepted rather than engineered around: **quality is a human
judgment.** The advisory tier's only job is to make that human judgment
better-informed and cheaper to exercise. It is a research assistant for the
reviewer, not a second gate.

### The architecture already exists — this names it

`sicario hooks` already implements exactly this split, and has since before this
feature was proposed. In `sicario_cli/cli.py`, the `HOOK_COMMAND_KIND` map
(lines 1156-1165) classifies every hook as either `deterministic` or `agent`.
`hooks_command` (lines 1218-1246) then **executes** the deterministic hooks
(`sicario.verify`, `sicario.assess`, `sicario.evidence`) via
`_run_deterministic_hook`, letting them set `exit_code`, and for `agent` hooks
prints a pointer to the command doc with the explicit disclaimer
"a coding agent performs this; the runner does not execute it." The agent branch
cannot reach `exit_code`. The separation is enforced by control flow, not by a
label.

This feature **elevates that existing, shipped behavior into a named
architecture principle** and applies it to a second surface. It is not inventing
a concept.

**Named principle — Two-Tier Authority:**

- **Tier 1 (Authoritative).** Deterministic, code-owned, stdlib-only. Owns the
  exit code. No model call, no network, no AI import. Its character is unchanged
  by this feature. `sicario verify` is Tier 1.
- **Tier 2 (Advisory).** Model-generated, explanation-only, addressed to a named
  human approver at the merge gate. Never touches the exit code. Never gates.
  Never blocks. Never fails a build. Its absence is never a pass. Its presence is
  never an approval. `sicario.threatmodel` and `sicario.review` already sit on the
  non-authoritative side of this boundary: the runner reports them rather than
  executing them, so neither can reach `exit_code`. They are not, however,
  explanation-only — `sicario.threatmodel` creates or updates
  `docs/security/threat-model.md`. The advisory signal specified here is
  deliberately narrower than they are: it writes nothing at all.

### Non-Goals

- Making `sicario verify` parse Markdown structure, count table rows, or score
  content. (Worth doing, and out of scope here — it would still be completeness,
  just stricter completeness. Tracked separately.)
- Any path by which advisory output can influence, delay, or veto a merge.
- Any "advisory-strict mode," "advisory threshold," or configuration flag that
  turns the advisory tier into a gate. This is specified as impossible, not as
  discouraged.
- Removing, weakening, or adding an exception to the no-AI-in-the-verdict
  invariant.
- Auto-remediation: the advisory tier never edits the spec it is reviewing.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reviewer sees where the form was filled but the thinking was not (Priority: P1)

As the human approver on a pull request, I want a clearly-labeled advisory read
on whether the governance sections contain real analysis or only the required
vocabulary, so I can spend my review time on the sections that are thin instead
of re-reading every section from scratch.

**Why this priority**: This is the entire value of the feature. The
deterministic gate already told the reviewer the words are present; the reviewer
still has to decide whether the words mean anything, and today gets no help at
all.

**Independent Test**: Take a spec that passes `sicario verify` with zero
findings but whose Abuse Cases section is a single sentence saying none were
identified. Confirm the advisory read flags that section as thin, and that
`sicario verify` on the same repository still exits 0.

**Acceptance Scenarios**:

1. **Given** a spec that passes the deterministic gate with zero findings and
   contains a placeholder threat model, **When** the advisory tier runs,
   **Then** it emits a labeled observation naming that section and the specific
   reason it appears unsubstantiated, **And** the deterministic exit code for
   the same repository is unchanged at 0.
2. **Given** a spec that fails the deterministic gate, **When** the advisory
   tier also runs, **Then** the deterministic findings are presented first and
   visually separated from advisory observations, **And** the exit code is
   determined solely by the deterministic findings.
3. **Given** any advisory observation of any severity, **When** the merge gate
   evaluates the pull request, **Then** the advisory observation contributes
   nothing to the pass/fail computation.

---

### User Story 2 - Reviewer can tell the two tiers apart without training (Priority: P1)

As a reviewer who has never read this specification, I want it to be
unmistakable at a glance which statements are the authoritative verdict and
which are a model's opinion, so I never treat an opinion as a blocking failure
or a blocking failure as an opinion.

**Why this priority**: A misread tier is worse than no advisory tier at all. If
advisory output is mistaken for authority, the project has quietly put a model
in the decision path through the reviewer's eyes instead of through the code.

**Independent Test**: Show the combined output to a reviewer with no context and
ask which lines block the merge. Every deterministic finding and no advisory
observation must be identified.

**Acceptance Scenarios**:

1. **Given** combined output containing both tiers, **When** a reviewer reads
   any single line in isolation, **Then** that line itself states its tier —
   the distinction never depends on a heading further up the page.
2. **Given** advisory output, **When** it is rendered anywhere, **Then** it
   never uses the words "fail", "failed", "pass", "passed", "blocking",
   "violation", or a `SICARIO-` finding code, and never uses the severity
   vocabulary of the deterministic gate.
3. **Given** an advisory observation is quoted or forwarded out of context,
   **When** it is read on its own, **Then** it still carries its
   non-authoritative label and a statement that it did not affect the verdict.

---

### User Story 3 - Reviewer is never let off the hook (Priority: P1)

As a security lead, I want the advisory tier to be incapable of expressing
approval, so no one can point at it and say the review was already done.

**Why this priority**: An advisory signal that says "looks good" is more
dangerous than one that says nothing. It manufactures false assurance and
transfers accountability from a named human to an unaccountable system.

**Independent Test**: Attempt to produce an advisory output that a reasonable
reader could quote as sign-off. Confirm the output contract makes this
unrepresentable rather than merely unlikely.

**Acceptance Scenarios**:

1. **Given** a spec the model assesses as excellent, **When** the advisory tier
   emits output, **Then** the output contains observations and open questions
   only, **And** contains no overall verdict, score, grade, rating, or
   approval-shaped statement.
2. **Given** an advisory run that produced zero observations, **When** the
   output is rendered, **Then** it states that no observations were generated
   and explicitly states that this is not an assessment of quality.
3. **Given** a merge is approved, **When** the approval record is written,
   **Then** it names the human approver, **And** advisory output is never
   recorded as an approver or as a basis for approval.

---

### User Story 4 - Advisory unavailability is loud and harmless (Priority: P2)

As a maintainer, I want an unavailable advisory tier to be visibly absent rather
than silently interpreted as a clean bill of health, and I want its absence to
never block anyone's merge.

**Why this priority**: "No output" is the most common failure mode of any
model-backed component and the easiest to misread as "nothing to report."

**Independent Test**: Run with no credential configured and with an unreachable
endpoint. Confirm a distinct unavailable state is rendered in both cases and
that the deterministic exit code is unaffected in both cases.

**Acceptance Scenarios**:

1. **Given** no advisory credential is configured, **When** the tier runs,
   **Then** the output states that the advisory tier did not run and that no
   quality signal exists for this change, **And** the deterministic verdict is
   emitted normally.
2. **Given** the advisory tier errors or times out, **When** output is
   rendered, **Then** the unavailable state is visually distinct from a
   zero-observation state, **And** the exit code is unchanged.
3. **Given** the advisory tier is unavailable, **When** the merge gate
   evaluates, **Then** the merge is neither blocked nor expedited by that
   unavailability.

---

### Edge Cases

- The spec under review contains text addressed to the advisory model itself.
- The spec is large enough to exceed the advisory context window — a truncated
  read must not be presented as a whole-document read.
- The same spec is reviewed twice and the advisory tier returns materially
  different observations; the reviewer must not conclude that either run was
  authoritative.
- The advisory tier flags a section that the deterministic gate passed, and a
  contributor asks for the deterministic gate to be relaxed to match.
- A downstream tool scrapes combined output and re-emits only the severity-like
  words.
- A repository sets the advisory tier to run on a fork pull request from an
  unknown contributor.

## Data Classification

| Data artifact | Level | Classification owner | Retention | Residency | Sharing | Redaction |
|---|---|---|---|---|---|---|
| Spec/plan text submitted to the advisory model | Internal | Repository maintainer | Not retained beyond the advisory call | Advisory provider region declared by the operator | Leaves the repository trust boundary; opt-in per repository | Secret-shaped strings removed before submission |
| Advisory observations returned to the reviewer | Internal | Repository maintainer | Life of the pull request; not archived as evidence | Repository host | Visible to anyone who can read the pull request | Model output truncated and escaped before rendering |
| Advisory run metadata (ran / did not run, timestamp, model identifier) | Internal | Repository maintainer | Retained with the pull request record | Repository host | Same audience as the pull request | None required |
| Deterministic gate summary (Tier 1) | Internal | Repository maintainer | Retained as release evidence | Repository host | Same audience as the release evidence | None required |

No regulated, restricted, or confidential data is in scope for this feature. If
a repository's specs contain data above Internal, that repository must not
enable the advisory tier — see FR-020.

## Tagging Discipline

| Tag | Value |
|---|---|
| owner | sicario-spec-maintainers |
| system | sicario-spec |
| environment | development |
| data-classification | internal |
| retention | pull-request-lifetime |
| tier | advisory |
| authority | none |

Every advisory artifact carries the `tier` and `authority` tags above. The
`authority` tag is `none` for all Tier 2 artifacts and is the machine-readable
form of the human-readable label required by FR-006. Any artifact tagged
`authority: none` is forbidden from appearing in the evidence set that supports
a release decision.

## Trust Boundaries

Three boundaries matter here, and only one of them is new.

1. **Repository → deterministic gate (Tier 1).** Unchanged. The gate reads files
   inside the project root and evaluates fixed rules in-process. It crosses no
   network boundary and loads no model. Spec content is untrusted input to a
   parser that does substring matching and nothing else; there is no
   instruction-following surface to attack.

2. **Repository → advisory model (Tier 2, new).** Spec content authored by any
   contributor, including an untrusted one, leaves the repository and enters a
   model context. This is a genuine egress boundary: it is a data-disclosure
   boundary in the outbound direction and an untrusted-content boundary in the
   inbound direction. Content crossing it is redacted on the way out and treated
   as hostile, non-authoritative text on the way back.

3. **Advisory output → human reviewer (Tier 2, new and the important one).**
   The reviewer is the component this feature is actually protecting. Advisory
   output entering the reviewer's decision is untrusted, persuasive text. The
   mitigations that matter most in this specification are the ones defending
   this boundary, because it is the only path by which a model could reach the
   verdict — through a human who mistook an opinion for a finding.

The boundary that does **not** exist, and must never be created, is
advisory → exit code. There is no code path, configuration flag, environment
variable, or plugin point from Tier 2 to the pass/fail computation.

## Security Requirements

- The deterministic verdict path MUST remain stdlib-only with no model call, no
  network access, and no AI import. This feature adds nothing to that path.
- The advisory tier MUST be a separate execution unit from the verdict path,
  such that removing the advisory tier entirely leaves the verdict byte-for-byte
  identical.
- The advisory tier MUST be opt-in per repository and MUST default to off.
- Content submitted to the advisory model MUST pass through secret redaction
  before egress, reusing the deterministic secret-detection patterns.
- Advisory model output MUST be treated as untrusted data: escaped before
  rendering, never executed, never interpreted as a command, and never parsed
  into anything that controls execution.
- Advisory output MUST NOT be written into `generated/sicario/gate-summary.json`,
  `spec-run-evidence.json`, or any SARIF findings file consumed by code
  scanning.
- Advisory output MUST NOT be assigned a `SICARIO-` finding code or a
  deterministic severity level.
- The advisory tier MUST NOT have write access to the repository, the pull
  request approval state, branch protection, or any file it reviews.
- Unavailability of the advisory tier MUST NOT change the exit code in either
  direction.
- The set of repositories with the advisory tier enabled, and the model
  identifier used, MUST be recorded so that a reviewer can tell after the fact
  which changes had an advisory read and which did not.

## AI / Tool Boundary

This feature deliberately introduces a model into the workflow for the first
time in a surface adjacent to the gate, so the boundary is drawn explicitly.

**Prompt injection.** Spec content is authored by contributors, including
untrusted contributors on fork pull requests, and is submitted verbatim to the
advisory model. A contributor can therefore write instructions into a spec aimed
at the advisory model — for example, text instructing the model to report that
the threat model is thorough, or to emit output shaped like a deterministic
pass. The structural mitigation is that prompt injection against the advisory
tier **cannot change any verdict**, because the advisory tier has no verdict to
change; the worst achievable outcome is a misleading advisory observation shown
to a human who has been told in the same breath that it is non-authoritative. On
top of that structural bar: submitted spec content is delimited and labeled as
untrusted data in the model context; the advisory tier's output schema is fixed
and constrained so injected text cannot introduce new output fields; returned
text is escaped before rendering so it cannot forge the deterministic tier's
formatting, severity words, or finding codes; and any returned string that
matches the deterministic finding-code pattern is stripped and replaced with a
notice that the advisory tier attempted to emit an authoritative-looking token.

**Tool boundary.** The advisory model receives text and returns text. It is
granted no tools, no filesystem write access, no repository write access, no
network fetch, no shell, and no ability to invoke `sicario verify` or any other
command. It cannot read files it was not given. It cannot request additional
context mid-run. The advisory tier is a pure function from submitted text to
observations, and every capability beyond that is withheld by default rather
than granted and constrained.

**No model in the verdict.** Restating the invariant so it cannot be lost in
this section: `sicario verify` remains the sole authority on pass/fail, and it
neither calls nor imports anything in this feature. The advisory tier is
explanation-only. It shares the non-authoritative property of the existing
AI-guidance hooks, and goes further than they do: those hooks may write
repository artifacts, whereas the advisory tier writes nothing.

## Fleet Guardrails

The advisory tier is a per-change, single-shot, side-effect-free call, so it has
a deliberately small orchestration surface. The guardrails that apply:

- **Idempotency**: an advisory run performs no writes to the repository or to
  evidence, so re-running it is inherently safe and produces no cumulative
  effect. Re-running MUST NOT create duplicate reviewer-facing artifacts.
- **Retry**: at most one bounded retry on transport failure, with a hard overall
  timeout. On exhaustion the tier reports the unavailable state rather than
  retrying indefinitely or degrading into silence.
- **Dead-letter**: an advisory call that fails after retry is recorded to an
  advisory-only failure log for operational visibility. That log is never read
  by the deterministic gate and never enters the evidence set.
- **Workflow state**: the advisory tier holds no durable state between runs.
  Every run is independent and derives entirely from the change under review, so
  there is no state that could drift into gating behavior.
- **Human approval**: the merge decision remains a human approval backed by the
  deterministic verdict. The advisory tier is an input to that human, never a
  participant in the decision, and never a substitute for the approver.

## Misuse / Abuse Cases

This is the section that matters most, because the thing being introduced is a
persuasive signal placed next to an authoritative one. Every abuse case below is
an attack on the boundary between the two tiers, and most of them are committed
by well-meaning insiders rather than attackers.

### AC-001 — Advisory output is misread as authoritative

**Scenario**: Advisory observations are rendered in CI output next to real
deterministic findings. A reviewer sees "advisory: weak threat model" in the
same log, in the same shape as a `SICARIO-` finding, and treats it as a blocking
failure — blocking a merge that the gate passed. The mirror-image failure is
worse: a reviewer sees "advisory: looks reasonable" and treats it as approval,
merging without reading the threat model at all.

**Mitigation**: Advisory output is structurally incapable of resembling a
finding. It carries no `SICARIO-` code and no deterministic severity word; the
words "pass", "fail", "blocking", and "violation" are forbidden in advisory
text and stripped from model output if returned. Every advisory line is
self-labeling, so the label survives copy-paste out of context. Advisory output
is rendered in a separate, explicitly titled block after the deterministic
verdict and after the exit code is already determined, never interleaved with
findings. Most importantly, the approval-shaped failure is closed at the source:
per AC-003 and FR-011, the advisory tier cannot express approval at all.

### AC-002 — Tier boundary erosion over time

**Scenario**: The most likely way this feature fails. No one attacks it; it is
loved to death. A contributor observes that the advisory tier keeps catching
real problems and proposes, reasonably, "let's just fail the build on advisory
score < 3." The next proposal is an `--advisory-strict` flag "for teams that
want it." The next is making advisory unavailability a soft failure "so we know
it ran." Each step is individually defensible. The end state is a model in the
verdict path, arrived at without anyone deciding to put one there.

**Mitigation**: Four layers, because social mitigations alone do not survive
turnover. (1) The advisory tier emits no score, grade, or rating — there is
nothing to threshold, so the cheapest version of this request has no object.
(2) No configuration surface exists that could gate on advisory output;
requesting one is a change to this specification, not a config change. (3) A
regression test asserts that the exit code is identical with the advisory tier
enabled, disabled, unavailable, and returning maximally negative observations —
so any change that wires advisory into the verdict fails the project's own
tests. (4) The Two-Tier Authority principle is recorded as a constitutional
invariant with the same standing as "no secrets in the repository," and this
specification records that the correct response to "the advisory tier should
gate" is to write a deterministic rule instead, since anything worth gating on
is worth expressing as code.

### AC-003 — Advisory output used to justify skipping human review

**Scenario**: A team under delivery pressure adopts the shorthand "advisory was
clean, ship it." Over a quarter this hardens into practice, and the advisory
tier has silently replaced the reviewer it was built to assist. Accountability
moves from a named human to a system that cannot be held accountable.

**Mitigation**: The advisory tier has no clean state to report. Its output
contract admits observations and open questions only — there is no summary
verdict, no score, no "no issues found" that could be quoted as sign-off. A run
with zero observations renders as "no observations were generated; this is not
an assessment of quality" rather than anything resembling all-clear. Approval
records name a human approver and have no field in which advisory output could
be cited. Advisory artifacts are tagged `authority: none` and are excluded from
the evidence set backing any release decision, so an audit trail can never show
advisory output where a human sign-off belongs.

### AC-004 — Prompt injection through contributor-authored spec content

**Scenario**: An untrusted contributor opens a fork pull request whose spec
contains text addressed to the advisory model — instructing it to report the
governance sections as thorough, to suppress observations about a specific
section, or to emit text mimicking a deterministic pass so a hurried reviewer
sees what looks like a second clean gate.

**Mitigation**: Structurally, the ceiling on this attack is low by construction:
the advisory tier has no authority, no tools, and no write access, so a fully
successful injection yields only misleading advice shown to a human who was told
it is advice. Concretely: submitted spec content is delimited and labeled as
untrusted data rather than instruction; the output schema is fixed so injected
text cannot add fields or change the response shape; all returned text is
escaped before rendering so it cannot forge deterministic formatting; returned
strings matching the `SICARIO-` code pattern or the deterministic severity
vocabulary are stripped and the attempt is surfaced to the reviewer as a signal
in its own right; and the advisory tier is off by default for pull requests from
forks, requiring explicit maintainer opt-in per repository. Critically, the
deterministic gate is entirely unaffected by injection because it has no
instruction-following surface — it does substring matching, which cannot be
persuaded.

### AC-005 — Advisory unavailability misread as "quality passed"

**Scenario**: The credential expires, the provider has an outage, or a fork PR
runs without access. The advisory block renders empty. A reviewer glances at a
green build with nothing in the advisory section and concludes there was nothing
to report.

**Mitigation**: Absence is rendered as loudly as presence. The unavailable state
is a distinct, explicitly worded state — "the advisory tier did not run; no
quality signal exists for this change" — and is visually distinct from the
zero-observation state, which itself is worded to disclaim being an assessment.
Advisory run metadata records ran/did-not-run per change so a reviewer or
auditor can tell after the fact which changes had an advisory read. The
unavailable state never changes the exit code in either direction, which is what
makes it safe to render honestly: there is no incentive to suppress it, because
it blocks no one.

### AC-006 — Gaming: authors write to satisfy the model, not to reduce risk

**Scenario**: The same failure that produced this feature, one level up. Authors
learn what phrasing the advisory model rewards and write to that instead of
thinking about risk. The advisory tier becomes a second, subtler vocabulary
check — one that is harder to audit than the first because its criteria are
implicit and shift with the model version.

**Mitigation**: Partially mitigated, and this specification declines to
overclaim. Structurally: the advisory tier produces no score and no target to
optimize, which removes the tightest feedback loop; and because it never gates,
there is materially less incentive to game it than to game a blocker. Design
mitigations: advisory output is phrased as open questions directed at the
reviewer ("what happens to this data if the export job partially fails?") rather
than as pass-shaped judgments about the document, so satisfying it requires
answering a substantive question rather than adding a phrase. The advisory tier
does not publish a rubric that could be written to. Residual risk is accepted
and named: any quality signal can be gamed, and the honest defense is that the
reviewer, not the signal, remains accountable for the decision. That is the same
reason the verdict stays with deterministic code — the thing that cannot be
argued with is the thing worth trusting.

### AC-007 — Advisory findings used to argue the deterministic gate should relax

**Scenario**: The advisory tier flags a section the deterministic gate passed. A
contributor concludes the deterministic rule is wrong and proposes loosening it
so the two tiers agree, reasoning that a passing gate and a critical advisory
note is a confusing state.

**Mitigation**: Disagreement between tiers is the expected and intended state,
not a defect — Tier 1 measures presence and Tier 2 comments on substance, so
they will routinely differ. The output explicitly says so. The specified
resolution path is one-directional: a recurring advisory observation is evidence
for writing a **new deterministic rule**, never for removing one. Loosening a
Tier 1 rule requires the same review as any governance change and cannot be
justified by advisory output, which is tagged `authority: none`.

### AC-008 — Advisory output leaks sensitive spec content

**Scenario**: A repository enables the advisory tier on specs describing
production architecture, embedded credentials, or customer data, and that
content egresses to a third-party model provider outside the repository's trust
boundary.

**Mitigation**: The advisory tier is opt-in per repository and off by default,
so egress is never a surprise. Submitted content is redacted with the same
patterns the deterministic secret scan uses before it leaves the boundary.
Repositories whose specs exceed Internal classification are directed not to
enable the tier. The data flow, its provider, and its residency are declared in
the Data Classification section above rather than left implicit.

## Functional Requirements *(mandatory)*

### Tier 1 — invariants that must not change

- **FR-001**: `sicario verify` MUST remain the sole authority on pass/fail for
  every change, release, and merge gate.
- **FR-002**: The verdict path MUST remain stdlib-only, with no model call, no
  network access, and no AI import introduced by this feature.
- **FR-003**: The deterministic exit code MUST be byte-for-byte identical
  whether the advisory tier is enabled, disabled, unavailable, or returning
  maximally negative observations.
- **FR-004**: Removing the advisory tier from the codebase entirely MUST leave
  the deterministic verdict, its findings, and its evidence artifacts unchanged.

### Tier 2 — the advisory contract

- **FR-005**: The advisory tier MUST be opt-in per repository and MUST default
  to off.
- **FR-006**: Every advisory artifact and every advisory line MUST carry a
  self-contained non-authoritative label that survives being read in isolation.
- **FR-007**: Advisory output MUST NOT be assigned a `SICARIO-` finding code or
  any deterministic severity level.
- **FR-008**: Advisory output MUST NOT contain the words "pass", "passed",
  "fail", "failed", "blocking", or "violation"; model output containing them
  MUST be stripped and the attempt surfaced to the reviewer.
- **FR-009**: Advisory output MUST be rendered in a separate, explicitly titled
  block presented after the deterministic verdict, never interleaved with
  deterministic findings.
- **FR-010**: Advisory output MUST NOT be written to
  `generated/sicario/gate-summary.json`, `spec-run-evidence.json`, or any SARIF
  file consumed by code scanning.
- **FR-011**: The advisory tier MUST NOT emit an overall verdict, score, grade,
  rating, or any approval-shaped statement. Its output vocabulary is
  observations and open questions only.
- **FR-012**: A run producing zero observations MUST render as an explicit
  statement that no observations were generated and that this is not an
  assessment of quality.
- **FR-013**: The advisory-unavailable state MUST be rendered distinctly from
  the zero-observation state and MUST state that no quality signal exists for
  the change.
- **FR-014**: Advisory run metadata (ran / did not run, timestamp, model
  identifier) MUST be recorded per change so a reviewer can determine after the
  fact whether an advisory read occurred.
- **FR-015**: Advisory artifacts MUST be tagged `authority: none` and MUST be
  excluded from the evidence set supporting any release decision.

### Tier 2 — boundary and injection defenses

- **FR-016**: Spec content submitted to the advisory model MUST be delimited and
  labeled as untrusted data, not as instruction.
- **FR-017**: Content MUST pass through secret redaction, reusing the
  deterministic secret-detection patterns, before leaving the repository trust
  boundary.
- **FR-018**: Advisory model output MUST be escaped before rendering, MUST NOT
  be executed, and MUST NOT be parsed into anything that controls execution.
- **FR-019**: The advisory tier MUST be granted no tools, no filesystem write
  access, no repository write access, no network fetch, and no ability to invoke
  any SicarioSpec command.
- **FR-020**: The advisory tier MUST be off by default for pull requests
  originating from forks and for repositories whose specs exceed Internal
  classification.
- **FR-021**: Where the advisory tier reviewed only part of an oversized
  document, the output MUST state that the read was partial and name what was
  omitted.

### Tier 2 — anti-erosion

- **FR-022**: No configuration flag, environment variable, plugin point, or
  extension hook MAY exist that causes advisory output to influence the exit
  code, block a merge, or delay a release.
- **FR-023**: A regression test MUST assert FR-003 across all four advisory
  states, so any change wiring advisory into the verdict fails the project's own
  test suite.
- **FR-024**: The Two-Tier Authority principle MUST be recorded as a
  constitutional invariant, with the documented resolution that a recurring
  advisory observation is grounds for writing a new deterministic rule and never
  grounds for gating on advisory output or relaxing a deterministic rule.
- **FR-025**: The advisory tier MUST NOT modify, suggest edits directly into, or
  open changes against the specification it is reviewing.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With the advisory tier enabled, disabled, unavailable, and
  returning maximally negative output, the deterministic exit code and gate
  summary are identical across all four states in 100% of runs.
- **SC-002**: Deleting the advisory tier from the repository produces zero
  change in deterministic findings across the full example corpus.
- **SC-003**: A reviewer with no prior exposure to this feature, shown combined
  output, correctly identifies every deterministic finding as blocking and every
  advisory observation as non-blocking.
- **SC-004**: No advisory output in any run contains a `SICARIO-` code, a
  deterministic severity level, or a forbidden verdict word.
- **SC-005**: No advisory artifact appears in the evidence set backing any
  release decision.
- **SC-006**: For every merged change, the record shows whether an advisory read
  occurred, and no merge record cites advisory output as a basis for approval.
- **SC-007**: A spec that passes the deterministic gate with placeholder
  governance content receives at least one advisory observation naming the thin
  section — while the deterministic run for that same spec still exits 0.
- **SC-008**: A spec containing text crafted to instruct the advisory model
  produces no change in the deterministic verdict, and the injection attempt is
  surfaced to the reviewer rather than silently obeyed.
- **SC-009**: With no credential configured, output states the advisory tier did
  not run, and the exit code matches the credential-configured run.
- **SC-010**: Content egressing to the advisory model contains no string
  matching the deterministic secret-detection patterns.
- **SC-011**: No configuration path exists by which advisory output changes a
  merge outcome; an audit of the configuration surface finds zero such controls.
- **SC-012**: Reviewers report spending less time locating thin governance
  sections, with no measured increase in merges approved without a human reading
  the governance sections.

## Evidence

Tier 1 evidence is unchanged. `generated/sicario/gate-summary.json` and
`spec-run-evidence.json` continue to be the authoritative record of the verdict,
produced by the deterministic gate, and no advisory content is written into
either.

Tier 2 evidence is deliberately segregated and deliberately weak:

- Advisory observations are written to an advisory-only artifact, distinct in
  path and filename from any deterministic evidence file, and tagged
  `authority: none`.
- Advisory run metadata — ran / did not run, timestamp, model identifier,
  whether the read was partial, whether an injection attempt was stripped — is
  recorded alongside it. This metadata exists so a reviewer or auditor can tell
  which changes had an advisory read; it is not evidence that any change was
  reviewed for quality.
- The advisory-only failure log (see Fleet Guardrails) is operational
  telemetry and is never read by the deterministic gate.
- The release evidence set is defined as excluding every artifact tagged
  `authority: none`. An auditor pulling release evidence receives Tier 1
  artifacts and the human approval record, and never receives an advisory
  artifact that could be mistaken for a control.

Verifying this feature's own invariants produces evidence in Tier 1's terms: the
FR-003 regression test result is the artifact that demonstrates the tier
boundary held, and it is a deterministic test, not an advisory read.

## Assumptions

- The deterministic gate's substring-matching behavior described in the Overview
  is current as of this specification. Tightening it — parsing headings,
  validating table structure, requiring content beneath a section — is
  worthwhile and is explicitly out of scope here; it would still be
  completeness, and it would still not be quality.
- A human approver exists at the merge gate and is accountable for the decision.
  If that is not true for a given repository, this feature adds no safety to it,
  because its only output audience is that human.
- The advisory model is a third party outside the repository trust boundary.
  Repositories unwilling to accept that egress leave the tier off, which is the
  default.
- Advisory observations will sometimes be wrong, sometimes inconsistent between
  runs on identical input, and sometimes contradict the deterministic gate. All
  three are tolerable **only** because the advisory tier holds no authority, and
  none of the three is treated as a defect to be fixed by giving it authority.
- Where this specification is silent, it is silent on purpose. It does not
  specify an advisory score, threshold, rubric, grade, or any mechanism for
  escalating a persistent advisory observation into a blocking condition —
  because specifying any of those would create the object that AC-002 predicts
  someone will eventually try to gate on, and would weaken the invariant this
  entire feature exists to protect.
