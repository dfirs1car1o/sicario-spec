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
