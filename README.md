<p align="center">
  <img src="docs/assets/sicario-spec-mark.svg" alt="SicarioSpec mark" width="96" height="96">
</p>

<h1 align="center">SicarioSpec</h1>

<p align="center"><strong>Kill risk before it ships.</strong></p>

<p align="center">
  <a href="https://github.com/dfirs1car1o/sicario-spec/actions/workflows/test.yml"><img alt="CI" src="https://github.com/dfirs1car1o/sicario-spec/actions/workflows/test.yml/badge.svg"></a>
  <a href="https://github.com/dfirs1car1o/sicario-spec/actions/workflows/codeql.yml"><img alt="CodeQL" src="https://github.com/dfirs1car1o/sicario-spec/actions/workflows/codeql.yml/badge.svg"></a>
  <a href="https://github.com/dfirs1car1o/sicario-spec/actions/workflows/release.yml"><img alt="Release packaging" src="https://github.com/dfirs1car1o/sicario-spec/actions/workflows/release.yml/badge.svg"></a>
  <br>
  <a href="https://scorecard.dev/viewer/?uri=github.com/dfirs1car1o/sicario-spec"><img alt="OpenSSF Scorecard" src="https://api.scorecard.dev/projects/github.com/dfirs1car1o/sicario-spec/badge"></a>
  <a href="https://dfirs1car1o.github.io/sicario-spec/"><img alt="Docs" src="https://img.shields.io/badge/docs-GitHub%20Pages-0f766e.svg"></a>
  <a href="https://github.com/dfirs1car1o/sicario-spec/releases"><img alt="GitHub release" src="https://img.shields.io/github/v/release/dfirs1car1o/sicario-spec?sort=semver"></a>
  <br>
  <a href="https://github.com/dfirs1car1o/sicario-spec/issues"><img alt="Issues" src="https://img.shields.io/github/issues/dfirs1car1o/sicario-spec"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green.svg"></a>
  <a href="pyproject.toml"><img alt="Python 3.9+" src="https://img.shields.io/badge/python-3.9%2B-blue.svg"></a>
</p>

SicarioSpec turns GitHub Spec Kit into a security, governance, and evidence
system for AI-era software delivery. It gives Claude Code, Codex/GPT, GitHub
Copilot, and human reviewers the same operating model: classify the data, name
the risk, map the controls, generate the evidence, and block unsafe changes
before merge, deploy, or release.

Specs are where risk becomes work. SicarioSpec makes that work explicit.

The core preset is built around a Security Evidence Chain: material risks and
security decisions trace to a control or requirement, test/gate, evidence path,
owner, and approval or accepted-risk state.

> **New here? Read [USAGE.md](USAGE.md).** It is the copy-pasteable quickstart
> and explains the one thing people miss: SicarioSpec does **not** give you a
> "threat-model command." Security and threat modeling are *enforced as
> mandatory spec/plan sections* and checked by `sicario verify` — a
> fill-in-the-contract-then-gate model, not a tool you invoke. See a passing
> end-state in [`examples/python-api/`](examples/python-api/).

## What "Deterministic" Means Here

"Deterministic" is overloaded in the AI-governance space, so we define it
precisely: **non-AI code owns the verdict.** The pass/fail decision for a change
is produced by `sicario verify` — a stdlib-only Python gate that reads repository
files and applies fixed rules. An LLM never sets pass/fail status. AI is
**explanation-only**: it can draft a spec, summarize a threat model, or suggest
remediations, but it is structurally barred from the decision path. That bar is
enforced by design — the gate has no model call, no network, and no AI import —
not by prompt instruction.

## How SicarioSpec Is Different

SicarioSpec is a security-governance preset for [GitHub Spec Kit](https://github.com/github/spec-kit).
It is **not** the first or only such preset, and we do not claim to be. Most
security-governance presets in the ecosystem follow an **advisory append**
pattern: they enrich the spec and plan with secure-SDLC templates, secure-coding
guidance, and regulatory applicability notes for an agent and a human reviewer to
consider. That guidance is genuinely useful, and SicarioSpec is complementary to
it — you can keep any advisory preset and still gate the result behind
SicarioSpec.

SicarioSpec operates at a different layer. Its defensible, distinguishing claim
is that the verdict is **enforced, not advised** — and the enforcement is
structural:

- **A halting gate.** `sicario verify` is a gate, not a comment. On any violation
  it **exits non-zero** and emits a specific finding code, so a CI check or merge
  gate actually **blocks the merge/release** instead of appending advice that can
  be ignored. It is wired into CI (`sicario-verify.yml`) and the Spec Kit hooks.
  (See it pass *and* fail from a clean clone: `examples/python-api/` exits 0,
  `examples/python-api-failing/` exits 1.)
- **A code-owned verdict with no LLM in the decision path.** Pass/fail is produced
  by `sicario verify` — a stdlib-only Python gate with no model call, no network,
  and no AI import. An LLM is **structurally barred** from the verdict (the gate
  cannot reach a model), not merely instructed to stay out. See "What
  Deterministic Means Here" above.
- **A mandatory governance contract.** Specs, plans, and tasks must contain
  required governance sections (data classification, tagging, trust boundaries,
  abuse cases, evidence, AI/fleet guardrails). A missing section is a hard fail,
  not a suggestion.
- **Compliance control maps you can scope.** Starter evidence maps for 11
  frameworks (CSA CCM v4.1, SOX 404 / ICFR ITGC, NIST SSDF, NIST AI RMF, ISO/IEC
  27001:2022, NIST SP 800-53 Rev 5, EU AI Act, GDPR (+ CPRA), PCI DSS v4.0,
  HIPAA Security Rule, and OWASP ASVS). A project selects the subset that applies
  (`--frameworks`), and the gate then enforces presence for exactly those. These
  maps are coarse traceability aids, not certification claims, and SicarioSpec
  does not yet ship maps for every framework other presets cover (for example
  SOC 2, FedRAMP, BSI C5, NIS2, CRA, DORA, SLSA supply-chain, OWASP SAMM, or
  OWASP LLM/Agentic AI risks). Those remain advisory here until a map exists.

In short: advisory presets recommend; SicarioSpec **enforces with a halting,
code-owned gate**. The two are complementary — adopt the advice you like, then
gate it behind SicarioSpec's deterministic verify contract.

## Why It Exists

AI agents can write code faster than most teams can explain the risk behind the
change. Compliance evidence is often reconstructed after the fact. Security
review gets pushed to the end, when architecture and delivery pressure are
already locked in.

SicarioSpec moves those decisions forward:

- every feature starts with data classification, tagging, threat modeling,
  controls, docs impact, and risk ownership
- every agent gets repo-native instructions and repeatable governance skills
- every release has a deterministic verification path before human approval
- every exception has an owner, expiration, rationale, compensating control, and
  evidence trail

## What You Get

SicarioSpec provides:

- **Presets** that change what every Spec Kit spec, plan, task list, checklist,
  and constitution must contain.
- **Agent-native instructions** for Claude Code, Codex/GPT, GitHub Copilot, and
  generic agent environments.
- **Guard extension commands** for review, threat modeling, controls, evidence,
  verification, and finding remediation.
- **Control maps** for 11 frameworks — CSA CCM v4.1, SOX 404 / ICFR ITGC, NIST
  SSDF (SP 800-218), NIST AI RMF (AI 100-1), ISO/IEC 27001:2022, NIST SP 800-53
  Rev 5, EU AI Act, GDPR (+ CPRA), PCI DSS v4.0, HIPAA Security Rule, and OWASP
  ASVS evidence readiness.
- **Policy-as-code starters** for Checkov, OPA/Conftest, Azure Policy, and
  Kubernetes admission policy.
- **Security toolchain starters** for secrets, SAST, SCA, SBOM, container/IaC
  scanning, and evidence paths.
- **Open-source repo hygiene**: issue forms, maintainer runbooks, CODEOWNERS,
  security policy, code of conduct, Dependabot, CodeQL, OpenSSF Scorecard,
  release packaging, Pages docs, and Spec Kit dogfood artifacts.

```text
spec idea
-> governed spec
-> threat model and abuse cases
-> architecture decision record
-> well-architected review
-> secure implementation plan
-> security/compliance/docs tasks
-> implementation
-> deterministic gates
-> evidence artifacts
-> human review before merge/deploy/publish
```

## Install

Native Spec Kit bundle install:

```bash
specify preset catalog add https://raw.githubusercontent.com/dfirs1car1o/sicario-spec/main/catalogs/presets.json --name sicario --priority 1 --install-allowed
specify extension catalog add https://raw.githubusercontent.com/dfirs1car1o/sicario-spec/main/catalogs/extensions.json --name sicario --priority 1 --install-allowed
specify bundle catalog add https://raw.githubusercontent.com/dfirs1car1o/sicario-spec/main/catalogs/bundles.json --id sicario --priority 1 --policy install-allowed
specify bundle install sicario-spec
specify preset resolve spec-template
```

Python CLI install:

From a local checkout:

```bash
python3 -m pip install -e .
```

From GitHub:

```bash
python3 -m pip install "git+https://github.com/dfirs1car1o/sicario-spec.git"
```

Install a specific release:

```bash
python3 -m pip install "git+https://github.com/dfirs1car1o/sicario-spec.git@v0.5.1"
```

## Quickstart

```bash
sicario init my-project --integration all --profile public-core
cd my-project
sicario verify
```

That single command gives the target repo a Spec Kit governance baseline,
security/compliance docs, risk registers, Docusaurus docs scaffold, GitHub
Actions gates, and agent instructions for Claude Code, Codex/GPT, and Copilot.

For the full step-by-step flow (install → init → write specs → verify → hooks),
the finding-code reference, and a "where does X live?" table, see
**[USAGE.md](USAGE.md)**.

Useful profile combinations:

```bash
sicario init my-api --profile appsec,compliance
sicario init my-agent --profile ai-system,agent-fleet,supply-chain
sicario init my-cloud-build --profile cloud-iac,security-toolchain
sicario init my-audit-ready-build --profile appsec,cloud-iac,security-toolchain,compliance
```

## Profiles

| Profile | Purpose |
|---|---|
| `public-core` | Core governance, data classification, tagging discipline, docs, diagrams, threat model, evidence, and risk registers. |
| `appsec` | Application/API security requirements, authn/authz, validation, logging, and negative tests. |
| `ai-system` | AI, LLM, agent, RAG, MCP, model output, tool boundary, eval, and red-team requirements. |
| `agent-fleet` | LangGraph-style state graphs, durable workflows, queues, workers, distributed execution, SOAR playbooks, and multi-agent orchestration. |
| `cloud-iac` | Terraform/OpenTofu, Azure Verified Modules, Azure Bicep, AWS, GCP, Kubernetes, containers, and policy-as-code. |
| `security-toolchain` | Secret scanning, SAST, SCA, SBOM, container/IaC scans, policy-as-code, and scan evidence. |
| `supply-chain` | SBOM, SCA, provenance, pinned dependencies, pinned actions/images, and release integrity. |
| `compliance` | Control applicability, CCM/SOX maps, evidence index, exceptions, and accepted risk. |
| `saas` | SaaS-tenant work (Salesforce/Workday/ServiceNow/M365): read-only-SaaS, tenant/data-boundary, and mission-supremacy invariants from the saas-assurance origin. |
| `enterprise-strict` | High-assurance review, approval, release controls, CODEOWNERS, and exception discipline. |

Profiles are composable:

```bash
sicario init my-service --profile appsec,ai-system,agent-fleet,security-toolchain,supply-chain
```

## Agent-Native Delivery

Use `--integration all` when multiple coding agents touch the repo:

| Environment | Generated support |
|---|---|
| Claude Code | `CLAUDE.md`, `.claude/skills/*`, `.claude/agents/*` |
| Codex / GPT | `AGENTS.md`, `.agents/skills/*` |
| GitHub Copilot | `AGENTS.md`, `.github/copilot-instructions.md`, path-specific instructions, setup workflow |
| Generic agents | `SICARIO.md`, Spec Kit templates, docs, workflows, and guard commands |

The generated instructions use a machine-user-first flow when available:
agents prepare code changes, a human maintainer approves with personal
credentials, and a documented single-maintainer fallback remains available for
organizations that cannot provision machine users.

## Use It When

- you are adopting Spec Kit and want security/compliance built into the spec
- AI agents are opening PRs and you need consistent repository instructions
- evidence, data classification, tagging, or release approval is currently
  manual or inconsistent
- your team needs a public-repo-ready security posture from day one
- auditors, security reviewers, or platform teams need traceability from
  feature intent to release evidence

## Constitution Foundation

The core constitution requires:

- least privilege and read-only defaults
- deterministic authority for pass/fail decisions
- evidence integrity
- data classification before storage, logging, external sharing, or release
- consistent tagging for data, resources, evidence, risk, and exceptions
- trust-boundary sanitization
- source-of-truth authority
- quality gates
- architecture discipline
- well-architected review
- operability and resilience
- honest documentation
- documentation impact tracking
- human-gated high-impact changes
- no secrets in the repository, logs, generated artifacts, or LLM context

The well-architected baseline covers operational excellence, security,
reliability, performance efficiency, cost optimization, and sustainability.
Provider-specific lenses may add detail, but they do not remove the baseline.

## Brownfield-Safe Adoption (Default)

SicarioSpec is built to adopt into a repository that **already has** a
constitution, Spec Kit templates, or agent-instruction files. It will **never
silently clobber** your existing governance. This is the default — no flag
required.

Before writing, `sicario init`/apply detects an existing setup:
`.specify/memory/constitution.md`, `.specify/templates/*`, `CLAUDE.md` /
`AGENTS.md`, and `mission.md` (or other project-supremacy instruction files).

Then, per file:

| File | Default behavior |
|---|---|
| **Constitution** (exists) | Appends a clearly-marked **additive** SicarioSpec overlay that explicitly **defers** to your existing principles and any `mission.md`. Your constitution is never replaced. |
| **Spec/plan/tasks template** (exists) | Appends the SicarioSpec governance-impact gate block — **idempotently** (no double-append on re-run) — instead of overwriting the file. |
| **`CLAUDE.md` / `AGENTS.md`** (exists) | Never overwritten; appends a delimited, idempotent SicarioSpec section. |
| Any file (new) | Created. |

Always:

- Every modified file is **backed up first** to `*.sicario-bak.<UTC-timestamp>`.
- A per-file **adoption report** prints at the end: `created` /
  `merged-overlaid` / `preserved` / `overwritten`, plus a summary line.

Flags:

- `--dry-run` — preview the full per-file report and write **nothing**.
- `--force` — explicit **full overwrite** opt-in (still takes a timestamped
  backup before replacing any file). Use only when you intend to discard the
  existing file in favor of the SicarioSpec template.

```bash
# Safe to run against an existing repo; overlays, never clobbers:
sicario init . --profile appsec --integration claude

# See exactly what would happen first:
sicario init . --profile appsec --integration claude --dry-run

# Intentionally replace existing files with the SicarioSpec templates:
sicario init . --profile appsec --integration claude --force
```

## Generated Target-Repo Artifacts

`sicario init` creates (new) or **merges/overlays** (existing — see
[Brownfield-Safe Adoption](#brownfield-safe-adoption-default)):

- `.specify/templates/{spec,plan,tasks}-template.md` (the live Spec Kit template
  paths, so `/speckit-*` commands pick up the governance; disable with
  `--no-apply-to-speckit`)
- `.specify/memory/constitution.md` (the live Spec Kit constitution path)
- `.specify/presets/*` (staged reference copies of all selected presets)
- `.specify/extensions/sicario-guard`
- `.specify/extensions.yml`
- `SICARIO.md`
- `CLAUDE.md` when using `--integration claude`
- `AGENTS.md` when using `--integration codex`, `--integration copilot`, or
  `--integration all`
- `.claude/skills/*` and `.claude/agents/*` when using `--integration claude`
  or `--integration all`
- `.agents/skills/*` when using `--integration codex` or `--integration all`
- `.github/copilot-instructions.md`, `.github/instructions/*`, and
  `.github/workflows/copilot-setup-steps.yml` when using
  `--integration copilot` or `--integration all`
- `docs/security/threat-model.md`
- `docs/security/abuse-cases.md`
- `docs/governance/data-classification.md`
- `docs/governance/tagging-taxonomy.md`
- `docs/compliance/control-applicability.md`
- `docs/compliance/evidence-index.md`
- `docs/compliance/control-maps/*`
- `docs/risk/risk-register.md`
- `docs/risk/security-exceptions.md`
- `docs/risk/accepted-risk-log.md`
- `docs/architecture/system-context.md`
- `docs/diagrams/system-context.mmd`
- `docs/docs-impact.md`
- `docs-site/` Docusaurus scaffold
- `.github/workflows/sicario-verify.yml`
- `.github/workflows/docs-site.yml`
- `.github/workflows/security-toolchain.yml` when using `security-toolchain`

## Control Maps

SicarioSpec ships starter maps that link its evidence to framework outcomes at a
coarse level (domain, practice group, or function):

- CSA Cloud Controls Matrix v4.1 — domain-level traceability (17 domains)
- SOX 404 / ICFR ITGC — control-area evidence readiness
- NIST SSDF (SP 800-218) — PO/PS/PW/RV practice-group evidence
- NIST AI RMF (AI 100-1) — Govern/Map/Measure/Manage function evidence
- ISO/IEC 27001:2022 — Annex A theme + control-group evidence (4 themes, 93 controls)
- NIST SP 800-53 Rev 5 — control-family evidence (20 families)
- EU AI Act (Reg. 2024/1689) — risk-tier + high-risk obligation (Art. 9-15) evidence
- GDPR (+ CPRA parallels) — Article 5 principles, DPIA, rights, and breach duties
- PCI DSS v4.0 — 12-requirement cardholder-data-environment evidence
- HIPAA Security Rule — Administrative/Physical/Technical ePHI safeguards
- OWASP ASVS — application security verification evidence for architecture,
  authentication/session management, and access-control evidence

These maps are traceability aids. They are not control-by-control crosswalks,
not certification claims, and do not replace the official framework artifacts,
auditor judgment, or legal/accounting/regulatory scoping (the EU AI Act, GDPR/CPRA,
PCI DSS, and HIPAA maps are guidance, not legal advice or a conformity/compliance
assessment). Frameworks referenced in templates but not yet shipped as a map
(SLSA, OWASP SAMM, OWASP LLM/Agentic AI risks, NIS2, CRA, DORA, SOC 2, FedRAMP,
and BSI C5) are advisory until a map exists.

**Pick the frameworks that apply.** You rarely owe evidence for all 11. The
framework selector records the subset your project enforces, so `sicario verify`
requires a control map for exactly those (and only those):

```bash
# Enforce only ISO 27001 + HIPAA:
sicario init my-project --profile compliance --frameworks iso27001,hipaa
# Enforce every shipped framework:
sicario init my-project --profile enterprise-strict --frameworks all
```

This writes `.sicario/frameworks.txt` (one key per line). A missing selected map
fails the gate as `SICARIO-MISSING-FRAMEWORK-MAP`; unselected frameworks are not
required. Omit `--frameworks` to default to the profile's framework set; delete
the file to fall back to the prior coarse control-map check. Selector keys and
per-profile defaults: [docs/control-maps.md](docs/control-maps.md) and
[docs/profiles.md](docs/profiles.md).

## Verification

Run:

```bash
sicario verify
```

The verifier currently checks for:

- required threat model, abuse cases, data classification, tagging taxonomy,
  docs impact, diagrams, control maps, and risk registers
- hardcoded secret patterns
- required spec sections, including data classification and tagging discipline
- required plan sections, including data classification, tagging, and
  well-architected review
- required security/docs/evidence/threat-model/classification/tagging tasks
- AI-sensitive specs missing prompt-injection or tool-boundary guardrails
- orchestration specs missing retry, idempotency, dead-letter, workflow state,
  or approval guardrails
- active risks/exceptions with missing owner, expiration, approval/rationale,
  compensating control, or evidence

`sicario verify` is the only authority on pass/fail — no AI involvement.

## Spec Kit Hooks

`sicario init` registers Spec Kit hooks (`after_specify`, `after_plan`,
`after_tasks`) in `.specify/extensions.yml`. Run them with:

```bash
sicario hooks                  # all events
sicario hooks --event after_tasks
```

`sicario hooks` **executes** the deterministic hooks (`sicario.verify`,
`sicario.assess`, `sicario.evidence`) and **reports** the agent-guidance hooks
(`sicario.threatmodel`, `sicario.review`, `sicario.controls`,
`sicario.apply-findings`) with a pointer to their command doc — it does not
pretend to run AI-authoring steps. See [docs/extensions.md](docs/extensions.md).

## Public Project Health

SicarioSpec ships public-repo hygiene for legitimate open source maintenance:

- MIT license
- code of conduct
- security policy and private vulnerability reporting path
- maintainer ownership, CODEOWNERS, and issue-to-PR operations runbook
- structured issue forms for bugs, features, maintenance tasks, security
  hardening, and control maps
- safe issue-triage workflow for labels and public-safety warnings
- checked-in Spec Kit project infrastructure and feature specs for repo changes
- pull request template with security/governance checklist
- Dependabot configuration
- CodeQL workflow
- OpenSSF Scorecard workflow and badge
- changelog and release process
- immutable semantic release tag discipline

OpenSSF Best Practices status is not claimed yet. It should only be displayed
after the external self-assessment is actually completed.

## Development

Run the local checks:

```bash
python3 -m unittest discover -s tests
python3 -m sicario_cli.cli verify .
sicario --version
```

Build/install smoke test:

```bash
tmpdir=$(mktemp -d)
python3 -m pip wheel . -w "$tmpdir/wheelhouse"
python3 -m venv "$tmpdir/venv"
"$tmpdir/venv/bin/pip" install "$tmpdir"/wheelhouse/sicario_spec-*.whl
"$tmpdir/venv/bin/sicario" init "$tmpdir/project" --profile appsec,cloud-iac,security-toolchain,compliance
"$tmpdir/venv/bin/sicario" verify "$tmpdir/project"
```

## What It Does Not Claim

SicarioSpec does not guarantee secure code, certify compliance, or replace human
security review. It makes risk visible early, turns it into work, and blocks
common unsafe paths before merge.

## Community

- Usage quickstart: [USAGE.md](USAGE.md)
- Worked example: [examples/python-api](examples/python-api/)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Maintainers: [MAINTAINERS.md](MAINTAINERS.md)
- Maintainer operations: [docs/maintainer-operations.md](docs/maintainer-operations.md)
- Security: [SECURITY.md](SECURITY.md)
- Support: [SUPPORT.md](SUPPORT.md)
- Code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- Release process: [docs/release-process.md](docs/release-process.md)
- Repository settings: [docs/repository-settings.md](docs/repository-settings.md)
- Agent environments: [docs/agent-environments.md](docs/agent-environments.md)
- OpenSSF posture: [docs/openssf.md](docs/openssf.md)
