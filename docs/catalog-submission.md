# Spec Kit Catalog Submission

This page prepares the maintainer-facing submission package for optional
discovery in the GitHub Spec Kit community catalog. The outward action is a PR
against `github/spec-kit`, not this repository.

The install authority for current SicarioSpec releases is this repository's own
install-allowed catalogs:

```text
https://raw.githubusercontent.com/dfirs1car1o/sicario-spec/main/catalogs/presets.json
https://raw.githubusercontent.com/dfirs1car1o/sicario-spec/main/catalogs/extensions.json
https://raw.githubusercontent.com/dfirs1car1o/sicario-spec/main/catalogs/bundles.json
```

Do not open an upstream Spec Kit PR just to bump every SicarioSpec patch
version. Use the Sicario-owned catalogs for live installs, and use the upstream
community catalog only when the listing text or discovery entry needs to change.

## Ready-To-Paste Catalog Entry

If submitting to the upstream community preset catalog, insert this object into
the top-level `presets` map in `presets/catalog.community.json`, keeping the
catalog's alphabetical ordering by id:

```json
"sicario-core": {
  "name": "SicarioSpec Core",
  "id": "sicario-core",
  "version": "0.5.1",
  "description": "Evidence-first Spec Kit governance baseline with mandatory security, risk, control, and evidence sections for specs, plans, tasks, checklists, and constitutions.",
  "author": "SicarioSpec Contributors",
  "repository": "https://github.com/dfirs1car1o/sicario-spec",
  "download_url": "https://github.com/dfirs1car1o/sicario-spec/releases/download/v0.5.1/sicario-core-0.5.1.zip",
  "homepage": "https://dfirs1car1o.github.io/sicario-spec/",
  "documentation": "https://dfirs1car1o.github.io/sicario-spec/docs/getting-started",
  "license": "MIT",
  "requires": {
    "speckit_version": ">=0.9.0"
  },
  "provides": {
    "templates": 5,
    "commands": 0
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
  "created_at": "2026-06-25T00:00:00Z",
  "updated_at": "2026-06-25T00:00:00Z"
}
```

## Community Docs Row

If the catalog PR also updates a community docs table, use this row:

```markdown
| SicarioSpec Core | Evidence-first security/governance baseline for Spec Kit templates, with the full SicarioSpec bundle available from Sicario-owned catalogs. | [dfirs1car1o/sicario-spec](https://github.com/dfirs1car1o/sicario-spec) |
```

## Cover Note

SicarioSpec Core is the baseline Spec Kit preset for evidence-first governance.
The broader SicarioSpec release also ships a bundle, profile overlays, guard
commands, and the `sicario verify` gate. The pass/fail verdict is produced by
stdlib-only Python with no model call, no network, and no AI import. LLMs can
draft, explain, or suggest remediations, but they do not own the verdict.

The upstream community preset entry is intentionally narrow. It lists the
installable baseline preset. Users who want the full bundle should add the
Sicario-owned catalogs and run `specify bundle install sicario-spec`.

## Submission Checklist

| Requirement | Status | Evidence |
|---|---|---|
| Public repository | Ready | `https://github.com/dfirs1car1o/sicario-spec` |
| MIT license | Ready | `LICENSE` |
| Release tag | Ready | `v0.5.1` |
| Preset ZIP asset | Ready | `sicario-core-0.5.1.zip` attached to `v0.5.1` |
| Full bundle assets | Ready | 11 preset ZIPs, `sicario-guard-0.5.1.zip`, `sicario-spec-0.5.1.zip`, and three catalog JSON files |
| Native manifests | Ready | 11 `presets/sicario-*/preset.yml` files and `extensions/sicario-guard/extension.yml` use `schema_version: "1.0"` |
| Guard commands | Ready | 8 commands in `extensions/sicario-guard/commands/` |
| Rule engine docs | Ready | [Declarative Rule Engine](./rule-engine.md) |
| Bundle readiness docs | Ready | [Bundle Readiness](./bundle-readiness.md) |

Before opening the outward PR, smoke-test the exact ZIP URL with upstream Spec
Kit tooling and paste the result into the catalog PR body:

```bash
specify preset add --from https://github.com/dfirs1car1o/sicario-spec/releases/download/v0.5.1/sicario-core-0.5.1.zip
specify preset info sicario-core
```

For the full bundle, smoke-test the Sicario-owned catalogs:

```bash
specify preset catalog add https://raw.githubusercontent.com/dfirs1car1o/sicario-spec/main/catalogs/presets.json --name sicario --priority 1 --install-allowed
specify extension catalog add https://raw.githubusercontent.com/dfirs1car1o/sicario-spec/main/catalogs/extensions.json --name sicario --priority 1 --install-allowed
specify bundle catalog add https://raw.githubusercontent.com/dfirs1car1o/sicario-spec/main/catalogs/bundles.json --id sicario --priority 1 --policy install-allowed
specify bundle install sicario-spec
specify preset resolve spec-template
```
