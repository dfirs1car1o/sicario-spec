# SicarioSpec Core

<p align="center">
  <a href="https://github.com/dfirs1car1o/sicario-spec/actions/workflows/test.yml"><img alt="CI" src="https://github.com/dfirs1car1o/sicario-spec/actions/workflows/test.yml/badge.svg"></a>
  <a href="https://github.com/dfirs1car1o/sicario-spec/actions/workflows/codeql.yml"><img alt="CodeQL" src="https://github.com/dfirs1car1o/sicario-spec/actions/workflows/codeql.yml/badge.svg"></a>
  <a href="https://scorecard.dev/viewer/?uri=github.com/dfirs1car1o/sicario-spec"><img alt="OpenSSF Scorecard" src="https://api.scorecard.dev/projects/github.com/dfirs1car1o/sicario-spec/badge"></a>
  <a href="https://github.com/dfirs1car1o/sicario-spec/releases/tag/v0.4.0"><img alt="Preset v0.4.0" src="https://img.shields.io/badge/preset-v0.4.0-0f766e.svg"></a>
  <img alt="Spec Kit >=0.9.0" src="https://img.shields.io/badge/spec--kit-%3E%3D0.9.0-blue.svg">
  <img alt="5 templates" src="https://img.shields.io/badge/templates-5-black.svg">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green.svg"></a>
</p>

SicarioSpec Core is a security operations governance preset for
[Spec Kit](https://github.com/github/spec-kit). It provides five template
overrides that make every feature show its risk, control, gate, evidence path,
owner, and approval or accepted-risk decision.

It is intentionally small: templates only, no custom commands, no scripts, and
no runtime dependency on the broader SicarioSpec CLI.

## Install

From a Spec Kit project root:

```bash
specify preset add --from https://github.com/dfirs1car1o/sicario-spec/releases/download/v0.4.0/sicario-core-0.4.0.zip
specify preset info sicario-core
specify preset resolve spec-template
```

For local preset development:

```bash
specify preset add --dev /path/to/sicario-spec/presets/sicario-core
specify preset info sicario-core
specify preset resolve plan-template
```

If `specify` reports that the directory is not a Spec Kit project, initialize
the project first with `specify init`, then rerun the preset install command.

## What You Get

| Template | Purpose |
| --- | --- |
| `spec-template` | Captures classification, trust boundaries, abuse cases, security requirements, operational signals, and evidence expectations. |
| `plan-template` | Maps risks and decisions to controls, gates, owners, rollback, evidence paths, and human approval points. |
| `tasks-template` | Turns tests, scans, evidence production, documentation impact, and review into explicit delivery tasks. |
| `checklist-template` | Reviews whether the spec, plan, tasks, evidence, gates, and approvals are ready before merge or release. |
| `constitution-template` | Establishes least privilege, deterministic authority, evidence integrity, quality gates, and human-gated high-impact changes. |

## What Makes It Different

Most security presets focus on secure coding rules, compliance mappings,
threat-modeling technique, architecture records, or supply-chain transparency.
Those are useful, but they do not always prove that a feature was operated
safely.

SicarioSpec Core is narrower and more operational. It focuses on operational proof:
each meaningful risk or decision should map to a control, a test or gate, an
evidence path, an owner, and an approval or accepted-risk state.

## Security Evidence Chain

```text
feature intent
-> data classification
-> trust boundary
-> abuse case
-> control or requirement
-> test or gate
-> evidence artifact
-> owner / reviewer
-> approval or accepted risk
```

## Verify Installation

```bash
specify preset resolve spec-template
specify preset resolve plan-template
specify preset resolve tasks-template
specify preset resolve checklist-template
specify preset resolve constitution-template
```

The resolved templates should point to `.specify/presets/sicario-core/`.

## Next Step

Read [USAGE.md](USAGE.md) for the full workflow, template impact details, fit
guidance, and adoption notes.

For the broader SicarioSpec CLI, profiles, control maps, policy-as-code starters,
and evidence gates, start at the repository [README](../../README.md).
