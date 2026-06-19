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
  <a href="https://github.com/dfirs1car1o/sicario-spec/releases"><img alt="GitHub release" src="https://img.shields.io/github/v/release/dfirs1car1o/sicario-spec?sort=semver"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green.svg"></a>
  <a href="pyproject.toml"><img alt="Python 3.9+" src="https://img.shields.io/badge/python-3.9%2B-blue.svg"></a>
</p>

SicarioSpec is a secure-by-default governance bundle for GitHub Spec Kit. It
adds AppSec, AI security, agent-fleet orchestration, cloud/IaC security,
supply-chain security, CCM/SOX evidence mapping, docs-as-code, diagrams,
well-architected review, risk exceptions, and human approval gates to
specification-driven development.

The goal is simple: make secure architecture, compliance evidence, and risk
decisions part of the spec before code is written.

## What It Adds

SicarioSpec provides:

- **Presets** that change what every Spec Kit spec, plan, task list, checklist,
  and constitution must contain.
- **Guard extension commands** for review, threat modeling, controls, evidence,
  verification, and finding remediation.
- **Bootstrap CLI** to install the bundle into a target repo with one command.
- **Control maps** for CSA CCM v4.1 and SOX 404 / ICFR ITGC evidence readiness.
- **Policy-as-code starters** for Checkov, OPA/Conftest, Azure Policy, and
  Kubernetes admission policy.
- **Security toolchain starters** for secrets, SAST, SCA, SBOM, container/IaC
  scanning, and evidence paths.

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
python3 -m pip install "git+https://github.com/dfirs1car1o/sicario-spec.git@v0.1.0"
```

## Quickstart

```bash
sicario init my-project --integration claude --profile public-core
cd my-project
sicario verify
```

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
- OpenSSF posture: [docs/openssf.md](docs/openssf.md)
