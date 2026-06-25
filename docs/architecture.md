# Architecture

SicarioSpec separates governance intent from enforcement.

```text
SicarioSpec
├── presets/              # artifact shape: spec, plan, tasks, checklist, constitution
│   ├── sicario-core/    #   static template and preset.yml files
│   ├── sicario-core.py  #   Python plugin — generates governance artifacts (SicarioCorePreset)
│   ├── sicario-docs/    #   static docs-site template assets
│   ├── sicario_docs.py  #   Python plugin — generates Docusaurus scaffold (SicarioDocsPreset)
│   ├── sicario-appsec/  #   (static preset.yml only)
│   └── …                #   9 more static presets
├── extensions/           # commands, hooks, review workflows
├── sicario_cli/          # bootstrap and deterministic verification
│   ├── cli.py           #   thin orchestrator: resolves profiles, delegates to preset classes
│   └── _render.py       #   shared write/copy/overlay helpers
├── workflow_templates/   # CI examples
├── control_maps/         # 14 framework traceability starters
├── docs/                 # public project docs (served by Docusaurus)
├── examples/             # sample target projects
├── specs/                # feature specs (e.g. 001-preset-refactor)
└── tests/                # offline validation
```

## Presets

Presets make security and governance unavoidable in the normal Spec Kit flow.
They change what gets asked before code is written.

Two presets — `sicario-core` and `sicario-docs` — are implemented as Python
plugin classes (`SicarioCorePreset`, `SicarioDocsPreset`). Their `write()`
methods generate governance documents, agent integrations, CI/CD workflows,
and docs-site scaffolds using shared helpers from `sicario_cli/_render.py`.
The remaining nine presets use only static `preset.yml` metadata and template
files, staged by `cli.py`'s directory-copy loop.

This split keeps `cli.py` thin: `init()` resolves the profile, copies static
presets, delegates content generation to preset classes, runs the framework
selector, and copies control maps.

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
