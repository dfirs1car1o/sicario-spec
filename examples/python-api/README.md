# Example: Customer Invoice Export API (fully governed, passes `sicario verify`)

This is a **complete, worked SicarioSpec example** — not a stub. It shows the
end-state a governed feature looks like: a `spec.md`, `plan.md`, and `tasks.md`
with every required governance section genuinely filled in (Data Classification,
Trust Boundaries, Threat Model, AI/LLM Risk, Secrets handling, Tagging
Discipline, abuse cases, evidence), plus the repo-level governance docs the
deterministic gate requires.

The feature itself is small and realistic: a read-only
`GET /api/v1/invoices/{id}/export` endpoint that returns one customer invoice as
PDF, with per-record authorization and no sensitive data in logs.

## What's here

```
examples/python-api/
├── specs/001-example/
│   ├── spec.md     # governed feature spec — all required sections filled in
│   ├── plan.md     # implementation plan — threat model, well-architected, etc.
│   └── tasks.md    # security/negative/classification/tagging/evidence tasks
└── docs/
    ├── security/threat-model.md
    ├── security/abuse-cases.md
    ├── governance/data-classification.md
    ├── governance/tagging-taxonomy.md
    ├── compliance/control-maps/README.md
    ├── risk/risk-register.md
    ├── risk/security-exceptions.md
    ├── risk/accepted-risk-log.md
    ├── diagrams/system-context.mmd
    └── docs-impact.md
```

`sicario verify` looks for both the per-feature artifacts under `specs/**/` and
the repo-level governance docs under `docs/`. This directory provides both, so
the gate passes.

## Reproduce the passing gate

From the repository root:

```bash
sicario verify examples/python-api
# or, without installing:
python3 -m sicario_cli.cli verify examples/python-api
```

Expected output:

```
sicario verify passed
```

The gate also writes evidence to `examples/python-api/generated/sicario/`
(gitignored). The `gate-summary.json` reports:

```json
{
  "status": "pass",
  "finding_count": 0,
  "findings": []
}
```

## Try breaking it (see the gate fail)

Delete a required section and re-run to watch the deterministic gate catch it:

```bash
# Remove the "## Data Classification" content from spec.md, then:
sicario verify examples/python-api
# -> HIGH SICARIO-DATA-CLASSIFICATION-INCOMPLETE ...  (exit 1)
```

That is the whole point of SicarioSpec: threat/security modeling is enforced as
mandatory, gate-checked sections — not an optional command you remember to run.
See [`USAGE.md`](../../USAGE.md) for the full mental model and finding-code
reference.
