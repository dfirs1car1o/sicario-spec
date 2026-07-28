# Documentation Impact

| Date | Change | Docs Impact | Decision |
|---|---|---|---|
| 2026-06-19 | Initial SicarioSpec MVP | Public docs, threat model, diagrams, completeness matrix | Required |
| 2026-06-23 | Extract preset inline writes into Python classes | `docs/architecture.md` updated with preset-class plugin tree; `docs/presets.md` updated with Python-class notes | Required |
| 2026-07-27 | Control-map tiering: 11 supported / 3 experimental frameworks; experimental keys excluded from profile defaults | `docs/control-maps.md` (Map Tiers), `docs/compliance/control-applicability.md`, `docs/compliance/control-maps/README.md` updated | Required |
| 2026-07-27 | Governed Spec Kit templates and constitution dogfooded in this repo | `.specify/templates/` and `.specify/memory/constitution.md` updated; changelog entry | Required |
| 2026-07-27 | Spec 006: per-line secret-scan findings, `max_findings_per_file` / `max_findings_per_rule` caps, mandatory `SICARIO-FINDINGS-TRUNCATED` overflow finding | `docs/rule-engine.md` caps section | Required |
| 2026-07-27 | `scan_coverage` evidence block written into `generated/sicario/gate-summary.json` | `docs/rule-engine.md` scan-coverage section | Required |
| 2026-07-27 | Machine-readable verify output: `--format json` / `--format sarif`, stdout carries only the artifact, summary on stderr | `docs/rule-engine.md`, `docs/getting-started.md` | Required |
| 2026-07-27 | Secret-scan rules 041-043 shipped (AWS access key, provider token, private-key material) with pattern boundary fix; `--validate-rules` repaired; `SICARIO-RULE-INVALID` / `SICARIO-RULE-UNREADABLE` / `SICARIO-NO-RULES-LOADED` fail-closed findings | `docs/rule-engine.md`, `docs/completeness-matrix.md`, `docs/compliance/evidence-index.md` | Required |
| 2026-07-27 | Rule precedence flip (project `.sicario/rules/` overrides shipped rules by id) with override evidence in `scan_coverage.overrides` | `docs/rule-engine.md` override-evidence section, `docs/security-model.md`, `docs/bundle-walkthrough.md`, `docs/security/threat-model.md`, `docs/security/abuse-cases.md` | Required |
| 2026-07-27 | `scan_coverage.asset_root` resolution evidence and `SICARIO-ASSET-ROOT-OVERRIDE` finding for `SICARIO_ASSET_ROOT` redirects | `docs/rule-engine.md` asset-root section | Required |

