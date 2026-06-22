# Repository Settings

These settings keep the public repository aligned with the project security
model.

## Enabled Features

- Issues: enabled
- Discussions: enabled for questions and adoption help
- Dependabot version updates: configured in `.github/dependabot.yml`
- CodeQL: configured in `.github/workflows/codeql.yml`
- OpenSSF Scorecard: configured in `.github/workflows/scorecard.yml`
- Issue triage: configured in `.github/workflows/issue-triage.yml`
- CODEOWNERS: configured in `.github/CODEOWNERS`

## Recommended Security Settings

Enable these in GitHub repository settings when available:

- Dependabot alerts
- Dependabot security updates
- Secret scanning
- Secret scanning push protection
- Private vulnerability reporting
- Blank public issues disabled by `.github/ISSUE_TEMPLATE/config.yml`

## Branch Protection

Protect `main` after the initial release:

- Require pull request before merge.
- Require at least one approving review.
- Require conversation resolution.
- Require status checks for `test` and `analyze-python`.
- Consider adding `pages` for documentation-heavy branches after the workflow is
  stable as a required check.
- Block force pushes and deletion.
- Require linear history when compatible with the maintainer workflow.
- Consider enabling CODEOWNER review requirement after a backup maintainer or
  maintainer team exists.
- Use the machine-user PR flow by default for AI-authored maintainer changes:
  `svc-claude-dev` authors branches and pull requests; a non-author maintainer
  account approves and merges.
- Allow a documented maintainer fallback when a machine-user identity is not
  available. The fallback may use admin bypass or a temporary review-count
  exception only after required checks pass, with the reason recorded in the PR.

Maintainers may use an admin bypass only for urgent release repair or security
response. Record the reason in the release or security advisory.

## Labels

The public issue workflow expects these labels:

- `bug`
- `enhancement`
- `security`
- `governance`
- `control-map`
- `documentation`
- `dependencies`
- `needs-triage`
- `good first issue`
- `help wanted`
- `skip-changelog`

## Issue-To-PR Operations

Public issues are intake, not execution authority. The issue triage workflow may
apply labels and warning comments, but it does not commit files, open PRs from
issue text, publish packages, or move release tags.

Accepted work follows `docs/maintainer-operations.md`: triage, branch, Spec Kit
feature artifacts, implementation, verification, PR checks, non-author review,
and merge.
