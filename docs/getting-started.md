# Getting Started

Start here if you want to use SicarioSpec in a real project.

SicarioSpec has two paths:

1. Use the `sicario-core` Spec Kit preset directly with `specify`.
2. Use the `sicario` CLI when you want the full repo bootstrap: presets, docs,
   risk registers, workflows, docs-site scaffold, control maps, and verification.

For the upstream Spec Kit catalog, path 1 is the important one. For running this
as a complete security-governance starter kit, path 2 is faster.

## Use the Spec Kit Preset Only

Use this when you want the smallest upstream-compatible workflow.

From an existing Spec Kit project:

```bash
specify preset add --dev /Users/jerieljuarbe/sicario-spec/presets/sicario-core
specify preset resolve spec-template
specify preset info sicario-core
```

After a GitHub release publishes the preset ZIP, install it from the release
asset instead:

```bash
specify preset add --from https://github.com/dfirs1car1o/sicario-spec/releases/download/v0.1.2/sicario-core-0.1.2.zip
```

What this changes:

- feature specs must capture classification, trust boundaries, abuse cases,
  operational signal paths, and evidence expectations
- implementation plans must carry threat model, control mapping, rollback, and
  well-architected review
- tasks and checklists must turn security, operations, and evidence work into
  explicit delivery items
- the constitution sets the baseline governance principles

Use this path when submitting `sicario-core` to the Spec Kit community catalog.

## Use the Full SicarioSpec CLI

Use this when you want a target repo fully bootstrapped.

```bash
python3 -m pip install "git+https://github.com/dfirs1car1o/sicario-spec.git"
sicario init my-project --integration all --profile public-core
cd my-project
sicario verify
```

That creates a governed project with:

- Spec Kit preset material under `.specify/`
- agent instructions for supported coding agents
- security, compliance, risk, diagram, and docs-impact starter files
- a Docusaurus docs-site scaffold
- GitHub workflow templates
- deterministic SicarioSpec verification

Use this path when you want the whole operating model, not just the catalog
preset.

## Pick a Profile

Use `public-core` first unless you already know the project needs a deeper
security lane.

```bash
sicario init my-api --profile appsec,compliance
sicario init my-agent-system --profile ai-system,agent-fleet,supply-chain
sicario init my-platform --profile cloud-iac,security-toolchain,compliance
```

Profile rule of thumb:

| Profile | Use when |
|---|---|
| `public-core` | You need the baseline security evidence workflow. |
| `appsec` | You are building an app, API, or service. |
| `ai-system` | You use LLMs, agents, RAG, MCP, model tools, or evals. |
| `agent-fleet` | You coordinate workers, queues, workflows, or SOAR-style automation. |
| `cloud-iac` | You manage infrastructure, policy-as-code, containers, or Kubernetes. |
| `security-toolchain` | You need scan, SBOM, SCA, IaC, or policy evidence. |
| `compliance` | You need control applicability, evidence indexes, or risk acceptance. |
| `enterprise-strict` | You need stricter approval, CODEOWNERS, and change-control posture. |

## Daily Operating Loop

1. Write or update the feature spec.
2. Confirm the Security Evidence Chain is complete.
3. Generate or update the implementation plan.
4. Break the plan into tasks.
5. Complete security, docs, risk, and evidence tasks with the code.
6. Run verification.
7. Review approval or accepted-risk decisions before release.

```bash
sicario verify
```

The verification goal is not to claim the project is secure by magic. The goal
is to make missing evidence visible before the work ships.

## What To Read Next

- [Presets](./presets.md): what each preset changes.
- [Profiles](./profiles.md): which bootstrap profile to use.
- [Security Model](./security-model.md): the governance rules SicarioSpec tries
  to make unavoidable.
- [Control Maps](./control-maps.md): how control evidence is organized.
- [Release Process](./release-process.md): how this repo packages the CLI and
  preset assets.
