# Implementation Plan: Maintainer Operations Hardening

**Branch**: `001-maintainer-operations` | **Date**: 2026-06-22 | **Spec**: `specs/001-maintainer-operations/spec.md`

## Summary

Add visible maintainer operations for SicarioSpec: maintainer ownership,
CODEOWNERS, a structured maintainer-task issue form, a least-privilege issue
triage workflow, and a documented issue-to-PR runbook. Dogfood Spec Kit by
initializing `.specify/`, installing the local `sicario-core` preset, and
tracking this change in `specs/001-maintainer-operations/`.

## Technical Context

**Language/Version**: Markdown, YAML, Bash, GitHub Actions
**Primary Dependencies**: GitHub Actions hosted runner, GitHub CLI available on runner, Spec Kit CLI 0.9.5
**Storage**: Repository files and GitHub issue metadata only
**Testing**: Python unit tests, `sicario verify`, Spec Kit preset inspection, shell syntax review
**Target Platform**: GitHub repository
**Project Type**: Python CLI and Spec Kit preset repository

## Data Classification And Handling

- Highest classification: Public.
- Classification owner: Maintainer.
- Regulated data: none expected.
- Retention and deletion: repository and GitHub issue retention only.
- Residency constraints: GitHub-hosted service only.
- Sharing and third-party disclosure: no new third parties beyond GitHub.
- Redaction, masking, or tokenization: workflow must not echo suspected secret
  values into comments.

## Tagging Plan

- Required tags: owner=`maintainer`, system=`repository-governance`,
  environment=`github`, data-classification=`public`,
  compliance-scope=`repo-governance`.
- Accepted values source: `docs/governance/tagging-taxonomy.md`.
- Cloud/IaC tagging enforcement: not applicable.
- Evidence, risk, and exception tag mapping:
  feature-id=`001-maintainer-operations`, control-id=`SEC-001..SEC-004`.
- Temporary resource expiration tags: not applicable.

## Threat Model

- Assets: repository source, workflow files, release process, maintainer approval
  trail, branch protection, public issue content.
- Entry points: public issues, issue form fields, workflow trigger, PR branch.
- Trust boundaries: public issue input to GitHub Actions, agent-authored PR to
  maintainer review, release workflow to public assets.
- Threat actors: malicious issue author, compromised account, accidental
  maintainer error, unsafe automation expansion.
- Abuse cases: issue text asks automation to commit code; public issue includes
  a credential; future workflow adds `contents: write` without review.
- Required controls: least-privilege workflow token, CODEOWNERS, non-author
  review, documented automation boundary, Spec Kit evidence.
- Residual risks: GitHub-hosted label/comment automation may false-positive on
  sensitive content; maintainer must still review labels and comments.

## Security Evidence Chain

Use this table as the delivery handoff between engineering, security, and
operations. Every high-impact decision, accepted risk, or material control should
have a chain entry.

| Chain ID | Risk / Decision | Control / Requirement | Test / Gate | Evidence Path | Owner | Approval / Accepted Risk |
|---|---|---|---|---|---|---|
| SEC-001 | Issue text could drive code changes | No issue-to-code mutation; PR-only implementation | Workflow review, branch protection | `.github/workflows/issue-triage.yml` | Maintainer | PR approval |
| SEC-002 | Maintainer process unclear to contributors | Runbook and maintainer authority documented | Docs review | `MAINTAINERS.md`, `docs/maintainer-operations.md` | Maintainer | PR approval |
| SEC-003 | Ownership unclear on release-critical paths | CODEOWNERS default and critical paths | CODEOWNERS review | `.github/CODEOWNERS` | Maintainer | PR approval |
| SEC-004 | Repo does not prove its own Spec Kit workflow | Initialize Spec Kit and record spec artifacts | `specify preset info sicario-core`, artifact review | `.specify/`, `specs/001-maintainer-operations/` | Maintainer | PR approval |

## Architecture / Security Decision Record

- Decision: use issue triage automation only for labels/comments; no automatic
  code generation, commits, PRs, releases, or tag movement from issue text.
- Alternatives: direct issue-to-PR automation; no automation at all.
- Security tradeoffs: label/comment automation improves operations visibility
  while keeping code mutation behind PR review.
- Approval needed: maintainer approval on PR.

## Well-Architected Review

- Operational excellence: adds triage runbook, issue form, labels, and visible
  maintainer ownership.
- Security: enforces the automation boundary and least-privilege workflow
  permissions.
- Reliability: workflow failures do not block issue creation; PR checks remain
  authoritative for repository changes.
- Performance efficiency: no long-running jobs; issue workflow uses simple shell
  checks.
- Cost optimization: no external services or paid dependencies.
- Sustainability: docs make maintenance responsibilities explicit for future
  maintainers.
- Tradeoffs accepted: sensitive-content detection is heuristic and advisory,
  not a replacement for maintainer review.

## Authn / Authz Design

- Identity source: GitHub user identity and GitHub Actions `GITHUB_TOKEN`.
- Authorization checks: workflow job gets `issues: write` and `contents: read`;
  repository changes still require PR permissions.
- Privilege boundaries: no `contents: write`, no release permissions, no package
  publishing permission.
- Negative tests: review workflow YAML for absent code-write permissions and
  absent generated command execution.

## Data Flow And Trust Boundaries

```text
public issue body -> GitHub issue event -> issue-triage workflow -> label/comment
accepted issue -> branch/PR -> CI checks -> non-author maintainer review -> merge
Spec Kit init/preset -> .specify + specs -> PR evidence -> maintainer review
```

## Supply Chain

- New dependencies: no runtime dependencies.
- Dependency review: uses platform-provided `gh` instead of a new marketplace
  action.
- SBOM impact: none.
- Pinned actions/images: no new action dependency added.
- Build provenance: unchanged.

## Cloud / IaC Risk

- IAM: no cloud IAM.
- Network exposure: GitHub API only from hosted runner.
- Encryption: GitHub-managed transport/storage.
- Secrets: default GitHub token only.
- Logging: avoid printing suspected sensitive issue body content.
- Drift/policy checks: repository settings docs updated.

## AI / Tool Boundary

- Prompt injection controls: issue text is untrusted and never executed.
- Tool allowlist: workflow uses only GitHub CLI issue label/comment operations.
- Model routing: no model invocation.
- Memory controls: agent instructions point to current plan/spec; issue text is
  not committed as instruction.
- Human approval gates: non-author maintainer PR approval.
- Evals/red-team tests: not applicable for this slice.

## Operational Readiness

- Required telemetry: GitHub Actions run result, issue labels/comments, PR checks.
- Detection or alert rule: review `needs-triage` and `security` labels.
- Triage and response owner: maintainer.
- Runbook or rollback link: `docs/maintainer-operations.md`; rollback by
  reverting workflow/docs or disabling workflow.
- Evidence retention: GitHub PR, Actions logs, Spec Kit feature artifacts.

## Test Strategy

- Unit tests: run existing Python unit tests.
- Integration tests: run `sicario verify .`.
- Negative/security tests: inspect workflow permissions and no code-write path.
- Regression tests: build/install smoke already covered by existing test
  workflow; local command may be run if package assets change.
- Offline test constraints: issue workflow behavior is validated by static review
  locally and Actions run after PR opens.

## CI / Security Gates

- Lint/type gates: not present for docs/YAML; rely on shell/YAML static review.
- Secret scan: no secrets introduced; suspicious patterns are not embedded as
  real credentials.
- SAST: CodeQL remains unchanged for Python.
- Dependency/SCA: no new dependency.
- IaC/container scan: not applicable.
- Project verification gate: `python3 -m sicario_cli.cli verify .`.
- Optional SicarioSpec verification if installed: same as project verification.

## Rollback

- Rollback trigger: issue workflow causes incorrect labels/comments, Spec Kit
  footprint proves too noisy, or maintainer process needs revision.
- Revert steps: revert this PR or disable `.github/workflows/issue-triage.yml`
  first if urgent.
- Data migration rollback: none.
- Evidence of rollback readiness: docs identify automation boundary and workflow
  location.

## Evidence Outputs

- Threat model: this plan and spec.
- Abuse cases: this spec.
- Data classification register: this plan/spec.
- Tagging taxonomy: no change required.
- Control applicability: this plan/spec.
- Evidence index: PR body and GitHub checks.
- Security Evidence Chain: this plan/spec.
- Gate summary: local verification command output.
- Reviewer approval: GitHub PR review.

## Human Approval Points

- Production write: not applicable.
- External system write: issue labels/comments only after workflow merge.
- Security exception: none.
- Release: none in this PR; future release follows `docs/release-process.md`.

## Constitution Check

| Principle | Status | Evidence |
|---|---|---|
| Least privilege | Pass | `issue-triage.yml` limits write permission to issues |
| Deterministic authority | Pass | No model or issue text determines merge/release outcomes |
| Evidence integrity | Pass | Spec, plan, tasks, PR checks, and review are retained |
| Security Evidence Chain | Pass | SEC-001 through SEC-004 |
| Trust-boundary sanitization | Pass | Public issue body treated as untrusted |
| Source-of-truth authority | Pass | Maintainer docs and PR review govern repository changes |
| Quality gates | Pass | Existing tests and `sicario verify` remain required |
| Architecture discipline | Pass | Automation boundary documented before merge |
| Well-architected review | Pass | This section |
| Operability and resilience | Pass | Runbook and rollback path documented |
| Honest documentation | Pass | Docs state what automation does and does not do |

## Project Structure

```text
.github/
  CODEOWNERS
  ISSUE_TEMPLATE/maintenance_task.yml
  workflows/issue-triage.yml
.specify/
  ...
MAINTAINERS.md
docs/maintainer-operations.md
specs/001-maintainer-operations/
  spec.md
  plan.md
  tasks.md
```
