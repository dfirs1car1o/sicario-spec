# Spec Kit Catalog Submission

This page prepares the maintainer-facing submission package for listing
SicarioSpec in the GitHub Spec Kit community catalog. The outward action is a PR
against `github/spec-kit`, not this repository.

## Ready-To-Paste Catalog Entry

Insert this object into the top-level `presets` map in
`presets/catalog.community.json`, keeping the catalog's alphabetical ordering by
id:

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

## Community Docs Row

If the catalog PR also updates a community docs table, use this row:

```markdown
| SicarioSpec | Evidence-first security/governance bundle with a halting, code-owned verify gate, declarative `.rule.json` checks, mandatory spec/plan/tasks governance sections, and 11 starter control maps. | [dfirs1car1o/sicario-spec](https://github.com/dfirs1car1o/sicario-spec) |
```

## Cover Note

SicarioSpec is a Spec Kit governance preset whose `verify` command is a halting
gate. The pass/fail verdict is produced by stdlib-only Python with no model call,
no network, and no AI import. LLMs can draft, explain, or suggest remediations,
but they do not own the verdict.

The preset is intentionally complementary to advisory security presets. Advisory
presets enrich the documents an agent and reviewer consider. SicarioSpec adds a
mandatory governance contract and a blocking verification step that emits
finding codes and exits non-zero when required evidence is absent.

## Submission Checklist

| Requirement | Status | Evidence |
|---|---|---|
| Public repository | Ready | `https://github.com/dfirs1car1o/sicario-spec` |
| MIT license | Ready | `LICENSE` |
| Release tag | Ready | `v0.5.0` |
| Preset ZIP asset | Ready | `sicario-core-0.5.0.zip` attached to `v0.5.0` |
| Preset manifests | Ready | 11 `presets/sicario-*/preset.yml` files |
| Guard commands | Ready | 8 commands in `extensions/sicario-guard/commands/` |
| Rule engine docs | Ready | [Declarative Rule Engine](./rule-engine.md) |
| Bundle readiness docs | Ready | [Bundle Readiness](./bundle-readiness.md) |

Before opening the outward PR, smoke-test the exact ZIP URL with upstream Spec
Kit tooling and paste the result into the catalog PR body:

```bash
specify preset add --from https://github.com/dfirs1car1o/sicario-spec/releases/download/v0.5.0/sicario-core-0.5.0.zip
specify preset info sicario-core
```
