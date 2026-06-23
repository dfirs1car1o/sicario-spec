# Risk Register

Track material security, privacy, compliance, operational, and AI/fleet risks.

| Risk ID | Status | Risk | Owner | Severity | Treatment | Evidence |
|---|---|---|---|---|---|---|
| RISK-001 | open | Bootstrap `init` could overwrite uncommitted user changes without `--force` guard | Maintainers | Medium | Mitigated: `--dry-run` preview, timestamped backups, explicit `--force` required | generated/sicario/gate-summary.json |
| RISK-002 | open | Generated AI agent spec omits prompt-injection or orchestration guardrails | Maintainers | High | Mitigated: `sicario verify` rejects AI specs without mandatory guardrail sections | generated/sicario/gate-summary.json |
| RISK-003 | open | Hardcoded credentials shipped inside governed repo | Maintainers | Critical | Mitigated: pattern-based secret scan in `sicario verify`, extendable via rule files | generated/sicario/gate-summary.json |
| RISK-004 | open | Documentation or diagram drift after feature changes | Maintainers | Medium | Mitigated: `docs-impact` and `docs/diagrams` checks in verify gate | generated/sicario/gate-summary.json |
| RISK-005 | open | Dependency on external Spec Kit version incompatible with installed version | Maintainers | Medium | Mitigated: `requires.speckit_version` in preset manifest, validated on init | generated/sicario/gate-summary.json |
