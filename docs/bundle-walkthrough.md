# Bundle Walkthrough

This page explains the SicarioSpec bundle from first principles: what it is,
why it exists, how to install it, how to use it, and what to look for after it
lands in a target repository.

## The Short Version

SicarioSpec is a governance bundle for GitHub Spec Kit. It turns a normal
feature-planning workflow into a security-and-evidence workflow.

Instead of asking a developer or AI agent to remember security later, the bundle
puts security, compliance, risk, evidence, and approval questions directly into
the spec, plan, tasks, docs, and CI checks.

The important idea is this:

```text
feature idea -> spec -> plan -> tasks -> implementation -> verify -> approval
```

SicarioSpec adds required evidence to that chain:

```text
feature idea
  -> data classification
  -> trust boundaries
  -> threat model
  -> abuse cases
  -> control applicability
  -> risk and exceptions
  -> deterministic verify gate
  -> human approval
```

That is why the bundle matters. It is not just a bigger template. It changes the
operating model.

## What A Bundle Is

Spec Kit has primitives:

- **Presets**: template packages that change specs, plans, tasks, checklists,
  and constitutions.
- **Extensions**: commands that add workflows such as review, assessment,
  controls, and evidence collection.
- **Bundles**: install recipes that compose multiple presets and extensions
  into one named product.

The SicarioSpec bundle is named `sicario-spec`. It installs:

- 11 SicarioSpec presets.
- The `sicario-guard` extension.
- 8 guard commands.
- The full template overlay stack.

The Python package, `sicario-spec`, adds another layer:

- a `sicario` CLI;
- starter docs and risk registers;
- control maps;
- example projects;
- a deterministic `sicario verify` gate;
- release and docs automation.

Use the native Spec Kit bundle when you want Spec Kit to install the template
and extension components. Use the Python CLI when you want a target repository
to receive the whole operational scaffold quickly.

## Why The Full Bundle Makes Sense

A small preset is good for discovery. The full bundle is good for real work.

The reason is scope. Security posture is not a single document. It usually
requires several connected artifacts:

| Need | SicarioSpec surface |
|---|---|
| Who owns the decision? | spec, plan, tasks, maintainers, CODEOWNERS |
| What data is involved? | data-classification section and docs |
| What can go wrong? | threat model and abuse cases |
| What framework applies? | selectable control maps |
| What evidence proves it? | evidence index and generated verify evidence |
| What exception was accepted? | risk register, security exceptions, accepted-risk log |
| What blocks bad changes? | `sicario verify` and CI |
| What do agents follow? | Claude, Codex, Copilot, and generic agent instructions |

If you only install one template, these pieces drift apart. The full bundle
keeps them connected.

## What The 11 Presets Do

The presets are composable. `sicario-core` is the base layer. The other presets
append more detail for specific delivery contexts.

| Preset | Purpose |
|---|---|
| `sicario-core` | Baseline governance sections, evidence chain, risk, verification expectations. |
| `sicario-docs` | Docs-as-code, diagrams, docs impact, public/private documentation discipline. |
| `sicario-appsec` | Application security requirements, abuse cases, tests, secrets, auth, logging. |
| `sicario-ai-system` | AI system risk, evals, model routing, safety boundaries, approval gates. |
| `sicario-agent-fleet` | Multi-agent coordination, tool boundaries, memory controls, review checkpoints. |
| `sicario-cloud-iac` | Cloud/IaC risk, tagging, IAM, network exposure, encryption, drift, rollback. |
| `sicario-security-toolchain` | SAST, SCA, secrets, SBOM, container/IaC scanning, evidence paths. |
| `sicario-supply-chain` | Dependency, provenance, build, release, and third-party risk discipline. |
| `sicario-compliance` | Control applicability, evidence index, audit readiness, exceptions. |
| `sicario-saas` | SaaS posture, privacy, tenant risk, operational readiness, customer evidence. |
| `sicario-enterprise-strict` | High-assurance review, approvals, release gates, CODEOWNERS, exception discipline. |

The full bundle installs all of them because real repositories often cross
these boundaries. A SaaS product can also have AI behavior, cloud/IaC, supply
chain risk, appsec requirements, and enterprise approval gates.

## What The Guard Extension Does

The `sicario-guard` extension contributes command surfaces for common review
work:

| Command | Intent |
|---|---|
| `sicario.init` | Initialize SicarioSpec governance posture. |
| `sicario.assess` | Assess repo readiness and gaps. |
| `sicario.threatmodel` | Drive threat-model and abuse-case review. |
| `sicario.controls` | Connect work to control evidence. |
| `sicario.evidence` | Build or inspect evidence chain artifacts. |
| `sicario.verify` | Run deterministic verification. |
| `sicario.review` | Review security and governance readiness. |
| `sicario.apply-findings` | Turn findings into remediation work. |

These commands exist so agents and humans can talk about the same workflow.
They do not replace review. They structure it.

## What `sicario verify` Does

`sicario verify` is the enforcement gate. It is intentionally boring:

- stdlib-only Python;
- no model call;
- no network call;
- no AI import;
- named findings;
- non-zero exit when required evidence is missing;
- generated evidence under `generated/sicario/`.

That matters because an AI agent can draft or explain, but it cannot own the
pass/fail verdict. Code owns the verdict. Humans approve the result.

## Install The Native Spec Kit Bundle

Use this when you want Spec Kit itself to install the bundle:

```bash
specify init --here --integration codex --ignore-agent-tools --force
specify preset catalog add https://raw.githubusercontent.com/dfirs1car1o/sicario-spec/main/catalogs/presets.json --name sicario --priority 1 --install-allowed
specify extension catalog add https://raw.githubusercontent.com/dfirs1car1o/sicario-spec/main/catalogs/extensions.json --name sicario --priority 1 --install-allowed
specify bundle catalog add https://raw.githubusercontent.com/dfirs1car1o/sicario-spec/main/catalogs/bundles.json --id sicario --priority 1 --policy install-allowed
specify bundle install sicario-spec
specify preset resolve spec-template
```

Why three catalogs? Spec Kit resolves presets, extensions, and bundles through
separate catalog types. The bundle points to components, but those components
still need to be findable through the preset and extension catalogs.

## Install The Python CLI

Use this when you want to bootstrap a target repository with docs, risk
registers, control maps, workflows, and verification:

```bash
pip install sicario-spec
sicario init ./my-project --integration all --profile appsec,cloud-iac,security-toolchain,compliance
sicario verify ./my-project
```

For a smaller start:

```bash
sicario init ./my-project --profile public-core
sicario verify ./my-project
```

For a stronger default:

```bash
sicario init ./my-project --integration all --profile enterprise-strict --frameworks all
sicario verify ./my-project
```

## Choose Frameworks Deliberately

You do not owe evidence for every framework. Pick what applies.

Examples:

```bash
# SaaS readiness with SOC 2 and ISO evidence.
sicario init ./service --profile saas --frameworks soc2,iso27001

# Federal cloud readiness.
sicario init ./service --profile cloud-iac,compliance --frameworks fedramp,nist-800-53

# Cloud provider assurance.
sicario init ./service --profile cloud-iac --frameworks ccm,bsi-c5
```

The selected frameworks are written to:

```text
.sicario/frameworks.txt
```

Then `sicario verify` requires maps for those selected frameworks. It does not
force every framework onto every project.

## What To Inspect After Install

After installation, inspect these paths first:

| Path | Why it matters |
|---|---|
| `.specify/templates/` | Spec Kit templates now include governance evidence sections. |
| `.specify/memory/constitution.md` | The project constitution includes SicarioSpec governance principles. |
| `.sicario/rules/` | Rule files define deterministic local gates. |
| `.sicario/frameworks.txt` | Selected framework maps enforced by verification. |
| `docs/compliance/control-applicability.md` | Which frameworks and domains apply. |
| `docs/compliance/evidence-index.md` | Where evidence is recorded. |
| `docs/security/threat-model.md` | Threat model starting point. |
| `docs/security/abuse-cases.md` | Abuse-case starting point. |
| `docs/risk/risk-register.md` | Open risks and owners. |
| `docs/risk/security-exceptions.md` | Exceptions with expiry and rationale. |
| `generated/sicario/gate-summary.json` | Machine-readable verify result. |

## Daily Operating Loop

Use this loop during normal delivery:

1. Write the feature spec.
2. Fill in data classification, trust boundaries, threat model, and abuse cases.
3. Write the plan, including controls, evidence, rollback, and approval points.
4. Generate or update tasks.
5. Implement.
6. Run:

```bash
sicario verify
```

7. Fix findings or document accepted risk.
8. Require human review before merge or release.

## Release Meaning

A SicarioSpec release is bundle-ready only when it proves three things:

- the Python package installs and verifies;
- release ZIPs and catalogs build cleanly;
- native Spec Kit can install `sicario-spec` from catalogs and resolve the
  composed templates.

That is why the release workflow publishes:

- wheel and source distribution;
- 11 preset ZIP files;
- `sicario-guard` extension ZIP;
- `sicario-spec` bundle ZIP;
- `presets.json`, `extensions.json`, and `bundles.json`;
- artifact attestations.

The release is not just a tag. It is a tested install path.
