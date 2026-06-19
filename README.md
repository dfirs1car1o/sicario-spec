<p align="center">
  <img src="docs/assets/sicario-spec-mark.svg" alt="SicarioSpec mark" width="96" height="96">
</p>

<h1 align="center">SicarioSpec</h1>

<p align="center"><strong>Kill risk before it ships.</strong></p>

<p align="center">
  <a href="https://github.com/dfirs1car1o/sicario-spec/actions/workflows/test.yml"><img alt="CI" src="https://github.com/dfirs1car1o/sicario-spec/actions/workflows/test.yml/badge.svg"></a>
  <a href="https://github.com/dfirs1car1o/sicario-spec/actions/workflows/codeql.yml"><img alt="CodeQL" src="https://github.com/dfirs1car1o/sicario-spec/actions/workflows/codeql.yml/badge.svg"></a>
  <a href="https://github.com/dfirs1car1o/sicario-spec/actions/workflows/release.yml"><img alt="Release packaging" src="https://github.com/dfirs1car1o/sicario-spec/actions/workflows/release.yml/badge.svg"></a>
  <a href="https://scorecard.dev/viewer/?uri=github.com/dfirs1car1o/sicario-spec"><img alt="OpenSSF Scorecard" src="https://api.scorecard.dev/projects/github.com/dfirs1car1o/sicario-spec/badge"></a>
  <a href="https://dfirs1car1o.github.io/sicario-spec/"><img alt="Docs" src="https://img.shields.io/badge/docs-GitHub%20Pages-0f766e.svg"></a>
  <a href="https://github.com/dfirs1car1o/sicario-spec/releases"><img alt="GitHub release" src="https://img.shields.io/github/v/release/dfirs1car1o/sicario-spec?sort=semver"></a>
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
- **Control maps** for CSA CCM v4.1 and SOX 404 / ICFR ITGC evidence readiness.
- **Policy-as-code starters** for Checkov, OPA/Conftest, Azure Policy, and
  Kubernetes admission policy.
- **Security toolchain starters** for secrets, SAST, SCA, SBOM, container/IaC
  scanning, and evidence paths.
- **Open-source repo hygiene**: issue forms, security policy, code of conduct,
  Dependabot, CodeQL, OpenSSF Scorecard, release packaging, and Pages docs.

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
python3 -m pip install "git+https://github.com/dfirs1car1o/sicario-spec.git@v0.1.2"
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

## Generated Target-Repo Artifacts

`sicario init` creates:

- `.specify/presets/*`
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

SicarioSpec includes starter maps for:

- CSA Cloud Controls Matrix v4.1 domain-level traceability
- SOX 404 / ICFR ITGC evidence readiness

These maps are traceability aids. They are not certification claims and do not
replace the official framework artifacts, auditor judgment, or legal/accounting
scoping.

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

## Public Project Health

SicarioSpec ships public-repo hygiene for legitimate open source maintenance:

- MIT license
- code of conduct
- security policy and private vulnerability reporting path
- structured issue forms for bugs, features, security hardening, and control maps
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

- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Security: [SECURITY.md](SECURITY.md)
- Support: [SUPPORT.md](SUPPORT.md)
- Code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- Release process: [docs/release-process.md](docs/release-process.md)
- Repository settings: [docs/repository-settings.md](docs/repository-settings.md)
- Agent environments: [docs/agent-environments.md](docs/agent-environments.md)
- OpenSSF posture: [docs/openssf.md](docs/openssf.md)
