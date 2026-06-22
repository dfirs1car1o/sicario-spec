# Feature Specification: Maintainer Operations Hardening

**Feature Branch**: `001-maintainer-operations`
**Created**: 2026-06-22
**Status**: Draft
**Input**: User description: "Add safe maintainer operations with issue triage, ownership, and issue-to-PR runbook. Make sure to use Spec Kit so we prove that we use the medicine that we're selling."

## User Scenarios & Testing

### User Story 1 - Maintainer Triage Path (Priority: P1)

A maintainer receives a public issue and can decide whether it should become a
discussion, be clarified, be handled privately, or move into a reviewed PR.

**Why this priority**: Public maintainability depends on an intake path that is
safe, repeatable, and visible to contributors.

**Independent Test**: Inspect issue templates, `MAINTAINERS.md`, and
`docs/maintainer-operations.md`; confirm every public issue type has a documented
triage outcome and no issue text is treated as executable change input.

**Acceptance Scenarios**:

1. **Given** a contributor opens a public maintenance request, **When** the
   issue is triaged, **Then** maintainers can route it to clarify, discussion,
   private security, decline, or accepted PR work.
2. **Given** an accepted issue requests agent assistance, **When** work starts,
   **Then** the implementation still uses a branch, PR, checks, and non-author
   review before merge.

### User Story 2 - Safe Automation Boundary (Priority: P1)

GitHub Actions can label and warn on issue intake without committing files,
opening PRs from untrusted text, moving tags, or publishing packages.

**Why this priority**: The repo should look operationally mature without adding
automation that undermines the security model.

**Independent Test**: Review `.github/workflows/issue-triage.yml`; confirm it is
triggered only by issues, has least practical permissions, and performs no code
mutation.

**Acceptance Scenarios**:

1. **Given** a new public issue is opened, **When** the triage workflow runs,
   **Then** it adds `needs-triage`.
2. **Given** possible sensitive content indicators appear in a public issue,
   **When** the triage workflow runs, **Then** it labels the issue `security` and
   comments with a private-reporting warning.
3. **Given** a low-structure issue is opened, **When** the triage workflow runs,
   **Then** it reminds the author to use structured templates and states that
   repository changes require PR review.

### User Story 3 - Dogfooded Spec Kit Evidence (Priority: P2)

The SicarioSpec repository visibly uses Spec Kit and the `sicario-core` preset
for its own repository-maintenance change.

**Why this priority**: Upstream reviewers and future users should see that the
project follows the workflow it promotes.

**Independent Test**: Confirm `.specify/` exists, `sicario-core` is installed as
a development preset, and this feature has `spec.md`, `plan.md`, and `tasks.md`
under `specs/001-maintainer-operations/`.

**Acceptance Scenarios**:

1. **Given** the repository is cloned, **When** a maintainer inspects the branch,
   **Then** Spec Kit project infrastructure and feature artifacts are present.
2. **Given** `specify preset info sicario-core` is run in the repo, **When** the
   preset registry is read, **Then** the local SicarioSpec Core preset is visible.

## Data Classification

- Data types processed: public issue metadata, public issue body text, labels,
  repository governance docs, Spec Kit project metadata.
- Highest classification: Public.
- Classification owner: Maintainer.
- Regulated data involved: none.
- Data retention and deletion expectations: GitHub issue and workflow retention
  follows repository and GitHub defaults; no new data store is introduced.
- Data residency or sovereignty constraints: none.
- Sharing, egress, or third-party disclosure: GitHub-hosted repository and
  Actions only.
- Redaction or masking requirements: public issue comments must not quote
  suspected secrets or sensitive issue text.

## Tagging Discipline

- Required metadata tags: owner=`maintainer`, system=`repository-governance`,
  environment=`github`, data-classification=`public`,
  compliance-scope=`repo-governance`.
- Cloud/IaC tags: not applicable.
- Evidence tags: feature-id=`001-maintainer-operations`,
  control-id=`SEC-001..SEC-004`.
- Accepted values source: `docs/governance/tagging-taxonomy.md`.
- Enforcement location: PR review, repository docs, GitHub Actions workflow
  review, `sicario verify`.

## Roles, Assets, And Abuse Actors

- Legitimate roles: public contributor, maintainer, machine user, GitHub Actions
  runtime, upstream reviewer.
- Protected assets: repository contents, release integrity, branch protection,
  public issue safety, maintainer approval trail, Spec Kit adoption evidence.
- Abuse actors: spammer, malicious issue author, compromised contributor
  account, accidental maintainer mistake, unsafe automation prompt.
- High-impact actions: merging to `main`, publishing releases, changing
  workflows, changing CODEOWNERS, moving tags.

## Trust Boundaries

- User/input boundary: public issue body and labels are untrusted.
- Service/API boundary: GitHub Issues and Actions APIs.
- External system boundary: GitHub-hosted Actions runner and repository API.
- Generated/model output boundary: agent-assisted work may draft code, but PR
  review and deterministic checks remain authoritative.

## Security Requirements

- Authentication: GitHub identity and token permissions only; no custom secrets.
- Authorization: issue workflow may write issue labels/comments only; code
  changes require PR permissions and maintainer approval.
- Input validation: issue body is scanned only for routing hints; it is never
  executed or used to generate commits.
- Output handling: comments must avoid echoing suspected sensitive content.
- Audit logging: GitHub issue comments, labels, Actions logs, PR review, and
  commit history provide public audit trail.
- Rate limiting / abuse prevention: workflow runs only on opened/reopened
  issues and does not loop on comments.
- Secure error handling: workflow failure should not block issue creation or
  expose sensitive body content.

## Privacy Requirements

- Data minimization: only issue number/body and repository metadata are used.
- Purpose limitation: issue body is used for triage labels/warnings only.
- Consent or notice requirements: issue templates warn users not to include
  restricted data.
- Redaction requirements: suspected sensitive strings are not repeated in logs or
  comments.

## Compliance / Control Applicability

Map applicable requirements without claiming certification.

| Domain | Applicable? | Rationale | Evidence |
|---|---:|---|---|
| AppSec / ASVS | Yes | Public issue input is untrusted and must not become executable behavior. | `.github/workflows/issue-triage.yml` |
| NIST SSDF | Yes | Changes require reviewed PRs, checks, and release discipline. | `docs/maintainer-operations.md`, `MAINTAINERS.md` |
| Supply Chain / SLSA | Yes | Workflow and release changes are code-owned and reviewed. | `.github/CODEOWNERS`, branch protection docs |
| AI Risk / NIST AI RMF | Yes | Agent assistance is bounded by PR review and deterministic gates. | `docs/machine-user-pr-flow.md`, `docs/maintainer-operations.md` |
| Cloud/IaC | No | No cloud resources or IaC changes. | N/A |

## AI / LLM Risk

- Prompt injection exposure: public issue text could try to instruct an agent or
  workflow to change code.
- Tool boundary controls: issue triage workflow does not run generated commands;
  agent-assisted work must happen in a PR.
- Model routing: no model is invoked by the workflow.
- Memory poisoning risk: agent instructions are explicit that issue text is
  untrusted input.
- Data leakage risk: suspected sensitive issue content is not echoed.
- Human approval boundaries: non-author maintainer approval remains required.
- AI evals / red-team tests: not applicable for this docs/workflow slice.

## External System Access

- External systems: GitHub Issues API.
- Read/write permissions: issues write for labels/comments; contents read.
- Production impact: no production service; repository governance impact only.
- Human approval needed: required before merge.

## Secrets / Credential Handling

- Secret sources: default `GITHUB_TOKEN` only.
- Runtime injection method: GitHub Actions-provided token.
- Redaction requirements: do not print suspected secret values.
- Rotation owner: GitHub-managed token lifecycle.

## Audit / Logging Requirements

- Events to log: workflow run status, labels applied, PR review, merge commit.
- Fields to exclude: public issue body should not be echoed beyond normal GitHub
  issue storage.
- Retention: GitHub defaults.
- Alerting: maintainer review of `security` and `needs-triage` labels.

## Operational Signal / Response Path

- Signals this feature should emit: `needs-triage` label, optional `security`
  label, issue comment warning when appropriate.
- Detection or alert logic: label-based issue review.
- Triage owner: maintainer.
- Response or rollback action: disable or revert `issue-triage.yml`; remove
  incorrect comments/labels if needed.
- Evidence retention location: GitHub issue timeline, PR, Actions logs,
  `specs/001-maintainer-operations/`.

## Misuse / Abuse Cases

- Abuse case 1: A malicious issue body instructs an agent to commit code.
- Abuse case 2: A public issue accidentally includes a token or tenant detail.
- Abuse case 3: A workflow is expanded later to mutate code without review.

## Functional Requirements

- **FR-001**: Repository MUST include a maintainer document defining roles,
  triage outcomes, merge authority, and automation boundaries.
- **FR-002**: Repository MUST include CODEOWNERS for default and
  release-critical paths.
- **FR-003**: Repository MUST include an issue form for maintainer or
  agent-assisted tasks.
- **FR-004**: Repository MUST include an issue triage workflow that labels
  public issues and warns on possible sensitive content.
- **FR-005**: Repository MUST document an issue-to-PR flow that requires a
  branch, required checks, and non-author review.
- **FR-006**: Repository MUST include Spec Kit/SicarioSpec dogfood artifacts for
  this change.
- **FR-007**: Repository MUST NOT include automation that commits, opens PRs,
  publishes releases, or moves tags directly from issue or comment text.

## Security Acceptance Criteria

- **SA-001**: Issue-triage workflow has `contents: read` and job-scoped
  `issues: write`, with no `contents: write`.
- **SA-002**: Public issue body text is not executed, passed to a shell as a
  command, or used to create code changes.
- **SA-003**: Maintainer docs explicitly state that issue-to-code work must move
  through PR review and deterministic checks.
- **SA-004**: Spec Kit artifacts for this change include Security Evidence Chain
  entries and verification tasks.

## Security Evidence Chain

Every material risk should trace to a control, verification gate, evidence path,
owner, and approval or accepted-risk decision.

| Chain ID | Risk / Decision | Control / Requirement | Test / Gate | Evidence Path | Owner | Approval / Accepted Risk |
|---|---|---|---|---|---|---|
| SEC-001 | Issue text could drive code changes | FR-007, SA-002 | Workflow review, PR review | `.github/workflows/issue-triage.yml` | Maintainer | PR approval required |
| SEC-002 | Maintainer handoff unclear | FR-001, FR-005 | Docs review | `MAINTAINERS.md`, `docs/maintainer-operations.md` | Maintainer | PR approval required |
| SEC-003 | Release-critical paths lack ownership signal | FR-002 | CODEOWNERS review | `.github/CODEOWNERS` | Maintainer | PR approval required |
| SEC-004 | Project fails to dogfood Spec Kit | FR-006 | Spec Kit artifact review, `specify preset info` | `.specify/`, `specs/001-maintainer-operations/` | Maintainer | PR approval required |

## Evidence To Produce

- Threat model update: this spec and `docs/maintainer-operations.md`.
- Abuse-case update: this spec.
- Data classification record: this spec; no restricted data.
- Tagging taxonomy updates: no taxonomy change required.
- Security Evidence Chain: this section and plan.
- Tests: `python3 -m unittest discover -s tests`, `python3 -m sicario_cli.cli verify .`,
  `specify preset info sicario-core`.
- Gate summary: command output in PR.
- Control applicability: this spec.
- Reviewer approval: GitHub PR review.

## Success Criteria

- **SC-001**: A new maintainer can read the repo and understand how issues become
  reviewed PRs.
- **SC-002**: A contributor can open a maintainer task without including unsafe
  private details.
- **SC-003**: The repo visibly contains Spec Kit project infrastructure and a
  feature spec/plan/tasks set for this work.
- **SC-004**: CI and local verification pass before merge.

## Assumptions

- `@SiCar10mw` remains the initial sole maintainer and release authority.
- `svc-claude-dev` remains the preferred machine user for AI-authored branches
  when available.
- The repo should optimize for safe reviewable automation before convenience.
