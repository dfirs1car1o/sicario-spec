# Repository Settings

These settings keep the public repository aligned with the project security
model.

## Enabled Features

- Issues: enabled
- Discussions: enabled for questions and adoption help
- Dependabot version updates: configured in `.github/dependabot.yml`
- CodeQL: configured in `.github/workflows/codeql.yml`
- OpenSSF Scorecard: configured in `.github/workflows/scorecard.yml`

## Recommended Security Settings

Enable these in GitHub repository settings when available:

- Dependabot alerts
- Dependabot security updates
- Secret scanning
- Secret scanning push protection
- Private vulnerability reporting

## Branch Protection

Protect `main` after the initial release:

- Require pull request before merge.
- Require at least one approving review.
- Require conversation resolution.
- Require status checks for `test`, `codeql`, and `OpenSSF Scorecard`.
- Block force pushes and deletion.
- Require linear history when compatible with the maintainer workflow.
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
