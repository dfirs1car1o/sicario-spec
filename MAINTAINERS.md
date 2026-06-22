# Maintainers

SicarioSpec is maintained as a public security-governance project. The project
accepts issues and pull requests, but repository changes are merged only through
reviewed branches with deterministic checks.

## Current Maintainer

| Maintainer | GitHub | Role |
|---|---|---|
| Jeriel Juarbe | `@SiCar10mw` | Project owner, release authority, security/governance reviewer |

## Maintenance Model

- Issues capture public work requests, bugs, control-map proposals, and
  hardening ideas.
- Issues do not directly modify code, workflows, releases, or generated assets.
- Maintainers triage issues before implementation starts.
- AI-assisted changes use the machine-user pull request flow documented in
  `docs/machine-user-pr-flow.md`.
- Pull requests must pass required checks before review approval and merge.
- Releases are immutable; fixes ship as new commits and new semantic versions.

## Triage Expectations

New issues should be triaged into one of these outcomes:

| Outcome | Use When |
|---|---|
| Accept for PR | The scope is clear, public, and aligned with the roadmap. |
| Needs clarification | The issue lacks acceptance criteria, scope, or safe public detail. |
| Convert to discussion | The issue is a question, adoption conversation, or early design idea. |
| Private security | The issue may disclose exploitable behavior, secrets, or restricted data. |
| Decline | The request conflicts with the security model or maintenance scope. |

## Merge Authority

Maintainers may merge only after:

- the branch is based on current `main`;
- required checks pass;
- the PR records security/governance, data classification, and release impact;
- a non-author maintainer approves; and
- unresolved review comments are addressed or explicitly deferred.

## Automation Boundary

GitHub Actions may label, validate, build, test, package, and publish reviewed
release artifacts. Actions must not apply code changes from issue or comment
text. Any future automation that prepares code must do so through a branch and
pull request that receives the same review as human-authored work.
