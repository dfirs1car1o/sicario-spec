# Machine-User Pull Request Flow

AI-authored repository-maintenance changes use a machine-user pull request flow
by default: the machine user authors branches and pull requests, a human
approves, and the machine user does not self-approve or self-merge.

The machine-user flow is the expected standard for maintainers working with AI
coding agents. Public contributors and organizations that cannot provision a
machine account may still contribute through the fallback path below.

## Roles

| Role | Responsibility |
|---|---|
| `svc-claude-dev` | Machine user for AI-authored commits, branches, and pull requests |
| Maintainer | Reviews scope and gives explicit approval |
| `SiCar10mw` | Maintainer/admin account that submits approval and merge after human approval |

## Rules

- Branch protection requires `test`, `analyze-python`, and one non-author
  approval before merge.
- The machine user may author a branch, open a pull request, and update that
  pull request after review.
- The machine user may not approve or merge its own pull request.
- The maintainer approval can be given in chat, but the GitHub approval must be
  submitted by a non-author account.
- Use admin merge only for a known-green branch-protection reporting issue, not
  to skip failed checks or unresolved review.
- Release tags are immutable; fixes ship as new commits and new patch releases,
  not by moving published tags.

## Fallback Path

Use the fallback only when a machine user is not available for the contributor,
organization, or local environment. In that case, a maintainer may author,
approve, and merge the change with an admin bypass or temporary review-count
exception after confirming these conditions:

- Required checks are green.
- The PR body records why the machine-user flow was unavailable.
- Security, data classification, tagging, and release impacts are documented.
- The exception is limited to that PR and branch protection is restored
  immediately after merge when a temporary setting change is used.

Do not use the fallback to merge failed checks, unresolved review comments, or
changes with unclear ownership.

## Local Account Setup

This repository expects two GitHub identities to be available locally:

- `svc-claude-dev` for code-authoring sessions
- `SiCar10mw` for maintainer approval and merge

Check the active account:

```bash
gh auth status
gh api user --jq .login
```

Switch identities when both are registered:

```bash
gh auth switch --hostname github.com --user svc-claude-dev
gh auth switch --hostname github.com --user SiCar10mw
```

Do not hardcode tokens in files, shell history, docs, or environment examples.
Tokens belong in the OS keyring or an approved secret manager.

If only one identity is available, use the fallback path and record that
constraint in the PR.

## Required PR Evidence

Every PR should include:

- Scope summary
- Tests and verification commands
- Security or governance impact
- Data classification and tagging impact
- Release or packaging impact
- Evidence paths or generated artifact notes
- Machine-user flow status, including the reason for any fallback
