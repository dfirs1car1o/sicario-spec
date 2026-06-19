# Architecture

SicarioSpec separates governance intent from enforcement.

```text
SicarioSpec
├── presets              # artifact shape: spec, plan, tasks, checklist, constitution
├── extensions           # commands, hooks, review workflows
├── sicario_cli          # bootstrap and deterministic verification
├── workflow_templates   # CI examples
├── control_maps         # CCM/SOX traceability starters
├── docs                 # public project docs
├── examples             # sample target projects
└── tests                # offline validation
```

## Presets

Presets make security and governance unavoidable in the normal Spec Kit flow.
They change what gets asked before code is written.

## Extension

The `sicario-guard` extension adds commands such as `/sicario.verify` and
`/sicario.review`. It is the review and enforcement layer.

## CLI

The `sicario` CLI installs presets and the extension into a target repo, creates
initial governance artifacts, and runs deterministic checks.

## Docs And Diagrams

Every project gets:

- internal docs under `docs/`
- Docusaurus public docs scaffold under `docs-site/`
- Mermaid diagram sources under `docs/diagrams/`
- docs impact tracking in `docs/docs-impact.md`

## Constitution And Architecture Discipline

The core constitution requires architecture decisions, trust boundaries, data
flows, well-architected review, operability, resilience, and rollback evidence
before a feature is considered complete.

The baseline well-architected review covers operational excellence, security,
reliability, performance efficiency, cost optimization, and sustainability.
Cloud-specific lenses can add provider detail, but they do not remove the
baseline.

## Control Maps And Risk

Control maps live under `control_maps/` in this repo and are copied into
`docs/compliance/control-maps/` for target projects. Risk and exception registers
live under `docs/risk/` and are part of `sicario verify`.
