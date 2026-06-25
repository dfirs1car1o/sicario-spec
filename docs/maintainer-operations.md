# Maintainer Operations

This runbook explains how maintainers convert public requests into reviewed
changes without allowing issues or comments to mutate the repository directly.

## Intake

Use structured issue forms for public work:

| Template | Use For |
|---|---|
| Bug report | Reproducible CLI, package, preset, extension, or docs defects |
| Feature request | New behavior, profiles, generated artifacts, or workflows |
| Control map or governance request | Framework mappings, evidence rules, or governance gates |
| Security hardening | Public hardening work that is not an exploitable vulnerability |
| Maintainer task | Repository operations or agent-assisted maintenance work |

Private vulnerabilities, secrets, tenant identifiers, customer data, and
restricted details do not belong in public issues. Route them through
`SECURITY.md`.

## Triage

Every new issue receives `needs-triage`. During triage, decide:

- whether the request is safe for public handling;
- whether it is a question, bug, feature, governance request, or hardening task;
- whether the acceptance criteria are clear enough for implementation;
- whether data classification, tagging, control maps, release assets, or docs
  are impacted; and
- whether an agent may prepare a pull request after maintainer review.

Remove `needs-triage` only when the next action is clear.

## Issue To PR Flow

1. Confirm the issue is public-safe and scoped.
2. Add or adjust labels.
3. Decide whether a maintainer, outside contributor, or machine user will author
   the change.
4. Create or update the Spec Kit feature artifacts under `specs/`.
5. Create a branch from current `main`.
6. Implement the smallest complete change that satisfies the issue.
7. Run local verification:

   ```bash
   specify preset info sicario-core
   python3 -m unittest discover -s tests
   python3 -m sicario_cli.cli verify .
   ```

8. Open a pull request with the PR template completed.
9. Wait for required GitHub checks.
10. Require non-author maintainer review before merge.
11. Close or link the issue from the PR.

## Spec Kit Dogfood

SicarioSpec uses Spec Kit for its own material repository changes. Maintainers
should preserve `.specify/`, keep `sicario-core` installed as a local
development preset, and record meaningful repo changes under `specs/`.

Expected artifacts for material changes:

- `specs/<number>-<short-name>/spec.md`
- `specs/<number>-<short-name>/plan.md`
- `specs/<number>-<short-name>/tasks.md`

The feature artifacts should include data classification, trust boundaries,
Security Evidence Chain entries, verification commands, and human approval
points. This is how the repo proves it uses the same operating model it ships.

## Agent-Assisted Work

Agent-assisted changes are allowed only through pull requests. The expected flow
is documented in `docs/machine-user-pr-flow.md`:

- a dedicated machine account authors the branch and pull request when
  available;
- a human maintainer reviews and merges as the non-author account;
- failed checks, unresolved comments, unclear ownership, or missing evidence
  block merge; and
- release tags are never moved after publication.

Maintainer approval in chat is not enough by itself. The GitHub PR must show the
approval, required checks, and final merge action.

## Automation Boundary

The issue triage workflow may label issues and warn about possible sensitive
public content. It must not:

- commit files;
- open pull requests from untrusted issue text;
- run generated commands from an issue body;
- create or move release tags; or
- publish packages.

Future automation that drafts changes must create a branch and PR, use least
privilege credentials, and preserve the same review gates as human-authored
changes.

## Release Handoff

Release-visible changes should update `CHANGELOG.md`, relevant docs, and package
assets. Release packaging follows `docs/release-process.md`; published tags and
release assets are immutable.
