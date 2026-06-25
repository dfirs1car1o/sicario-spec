# Adoption and Launch

SicarioSpec should be marketed as an operating model, not a checklist. The
message is simple: teams using AI coding agents need risk, evidence, and human
approval built into the spec before code starts moving.

## Positioning

Use this short description when introducing the project:

> SicarioSpec turns GitHub Spec Kit into a security, governance, and evidence
> system for AI-era software delivery. It gives Claude Code, Codex/GPT, GitHub
> Copilot, and human reviewers one shared workflow for data classification,
> controls, risk exceptions, verification, and release approval.

Use this one-line version in social posts and repository descriptions:

> Secure-by-default Spec Kit governance for AI-assisted software teams.

## Audience

Primary audiences:

- security engineers who need repeatable AppSec and AI security gates
- platform teams standardizing agent-assisted delivery
- compliance and assurance teams that need evidence before release
- maintainers of public or regulated repositories
- teams adopting Claude Code, Codex/GPT, and GitHub Copilot together

## Proof Points

Lead with concrete artifacts instead of broad claims:

- a **halting** verify gate: `sicario verify` exits non-zero with a finding code
  on any violation, so a CI/merge gate actually blocks (prove it from a clean
  clone — `examples/python-api/` passes, `examples/python-api-failing/` fails)
- a **code-owned verdict**: pass/fail comes from stdlib-only code with no model
  call and no AI import — the LLM is structurally barred from the decision path
- one-command bootstrap for governed Spec Kit projects, turnkey-wired into the
  live Spec Kit paths (`--apply-to-speckit`) and **brownfield-safe** by default
- agent-native instructions for Claude Code, Codex/GPT, and Copilot
- data classification and tagging built into specs, plans, tasks, and docs
- threat model, abuse cases, evidence index, risk registers, and **selectable**
  control maps across 14 frameworks (`--frameworks`)
- GitHub Actions verification, CodeQL, Dependabot, OpenSSF Scorecard, and
  release packaging
- MIT license, security policy, code of conduct, issue forms, and Pages docs

When differentiating, contrast with advisory-append patterns **generally** —
enforce versus advise — without naming specific projects, and do not claim a
multi-framework-breadth win (other presets cover frameworks SicarioSpec does not
yet map).

## Launch Checklist

Before announcing:

- publish the GitHub Pages docs site
- cut a tagged release with attached distributions and attestations
- confirm CI, CodeQL, Scorecard, release, and Pages badges resolve
- keep only genuinely open starter issues after folding release-ready examples
  into the tagged bundle
- add repository topics such as `spec-kit`, `appsec`, `ai-security`,
  `devsecops`, `governance`, `openssf`, and `compliance`
- pin the release and docs link in the repository sidebar

## First Posts

GitHub release notes:

```text
SicarioSpec is live: secure-by-default Spec Kit governance for AI-assisted
software teams.

This release bootstraps data classification, tagging discipline, threat
modeling, control maps, evidence indexes, risk registers, docs-as-code, GitHub
Actions gates, and agent-native instructions for Claude Code, Codex/GPT, and
GitHub Copilot.
```

Short social post:

```text
I released SicarioSpec: a Spec Kit governance bundle for AI-era delivery.

It gives Claude Code, Codex/GPT, Copilot, and humans the same rules for data
classification, threat modeling, evidence, risk exceptions, and release gates.

Repo: https://github.com/dfirs1car1o/sicario-spec
Docs: https://dfirs1car1o.github.io/sicario-spec/
```

Longer launch post:

```text
AI coding agents are changing delivery speed, but most teams still bolt on
security review and evidence collection at the end.

SicarioSpec moves that work into the spec. It extends GitHub Spec Kit with
data classification, tagging discipline, threat modeling, control maps,
evidence indexes, risk registers, docs-as-code, GitHub Actions gates, and
agent-native instructions for Claude Code, Codex/GPT, and GitHub Copilot.

The goal is not to claim security or compliance by magic. The goal is to make
risk visible early, turn it into work, and require deterministic evidence
before human approval.
```

## Brownfield-Safe Adoption

Most teams adopting SicarioSpec already have a constitution, Spec Kit templates,
or agent-instruction files. A tool that silently overwrites a user's existing
`constitution.md`, `CLAUDE.md`, or `mission.md` is a non-starter — so
**brownfield-safe adoption is the default** (no flag required).

`sicario init`/apply detects an existing setup before writing
(`.specify/memory/constitution.md`, `.specify/templates/*`, `CLAUDE.md` /
`AGENTS.md`, and `mission.md`/project-supremacy files), then per file:

- **Constitution** (exists): appends a clearly-marked **additive** SicarioSpec
  overlay that explicitly **defers** to the project's own principles and any
  `mission.md`. The existing constitution is never replaced.
- **Spec/plan/tasks template** (exists): appends the SicarioSpec
  governance-impact gate block **idempotently** (no double-append on re-run)
  rather than overwriting the file.
- **`CLAUDE.md` / `AGENTS.md`** (exists): never overwritten; appends a delimited,
  idempotent SicarioSpec section.
- New files are created.

Always: every modified file is backed up first to `*.sicario-bak.<UTC>`, and a
per-file report (`created` / `merged-overlaid` / `preserved` / `overwritten`)
prints at the end of the run.

Flags:

- `--dry-run` previews the per-file report and writes nothing.
- `--force` is the explicit full-overwrite opt-in (still backs up first).

## Contribution Hooks

Good first external contribution areas:

- additional control-map coverage
- cloud-provider policy examples
- agent workflow examples
- docs-site examples and diagrams
- OpenSSF hardening improvements
- verifier checks for new risk or evidence patterns

Do not market incomplete governance as certification. Keep claims tied to what
the repository actually generates and verifies.
