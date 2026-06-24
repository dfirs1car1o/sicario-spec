# Spec Kit Community Catalog Submission - SicarioSpec

This is the maintainer-facing submission package for listing SicarioSpec in the
GitHub Spec Kit community preset catalog. The outward PR is opened against
`github/spec-kit`; this repository only holds the prepared entry, cover note,
and verification checklist.

The current package targets SicarioSpec `0.5.0`.

## Catalog Entry

```json
"sicario-spec": {
  "name": "SicarioSpec",
  "id": "sicario-spec",
  "version": "0.5.0",
  "description": "Evidence-first Spec Kit governance with a halting, stdlib-only verify gate. It enforces mandatory governance sections in specs, plans, and tasks, supports declarative .rule.json checks, and ships selectable starter control maps for 11 frameworks.",
  "author": "SicarioSpec Contributors",
  "repository": "https://github.com/dfirs1car1o/sicario-spec",
  "download_url": "https://github.com/dfirs1car1o/sicario-spec/releases/download/v0.5.0/sicario-core-0.5.0.zip",
  "homepage": "https://dfirs1car1o.github.io/sicario-spec/",
  "documentation": "https://dfirs1car1o.github.io/sicario-spec/docs/getting-started",
  "license": "MIT",
  "requires": {
    "speckit_version": ">=0.9.0"
  },
  "provides": {
    "templates": 11,
    "commands": 8
  },
  "tags": [
    "security",
    "governance",
    "devsecops",
    "deterministic-gate",
    "evidence",
    "compliance",
    "ai-security"
  ],
  "created_at": "2026-06-23T00:00:00Z",
  "updated_at": "2026-06-23T00:00:00Z"
}
```

## Cover Note

SicarioSpec turns Spec Kit into an evidence-first governance bundle. Its
distinguishing claim is narrow: `sicario verify` is a halting, code-owned gate.
It emits finding codes, exits non-zero on missing governance evidence, and has no
LLM in the decision path.

The bundle also includes declarative `.rule.json` checks, agent instructions,
risk registers, Docusaurus docs scaffolding, GitHub workflows, and 11 starter
control maps. Those maps are traceability aids, not certification claims.

## Pre-Submission Checks

Run these before opening the outward catalog PR:

```bash
python3 -m unittest discover -s tests
python3 -m sicario_cli.cli verify .
python3 -m sicario_cli.cli verify . --validate-rules
(cd docs-site && npm run build)
specify preset add --from https://github.com/dfirs1car1o/sicario-spec/releases/download/v0.5.0/sicario-core-0.5.0.zip
specify preset info sicario-core
```

The first four checks validate this repository. The final two checks validate
the exact release ZIP that the community catalog would consume.
