# Changelog

All notable changes to SicarioSpec are tracked here.

The project follows semantic versioning once the public API stabilizes. During
the `0.x` line, minor versions may introduce breaking changes when needed to
improve the security model.

## [0.1.0] - 2026-06-19

Initial public release.

### Added

- `sicario` CLI with `init`, `verify`, and `assess` commands.
- Composable profiles for core governance, AppSec, AI systems, agent fleets,
  cloud/IaC, security toolchains, supply chain, compliance, docs, and
  enterprise controls.
- Spec Kit presets, templates, and Sicario guard extension commands.
- CCM v4.1 and SOX 404 / ICFR starter control maps.
- Terraform, Azure Bicep, Azure Verified Modules, AWS CloudFormation, GCP
  Terraform, Kubernetes, container, and policy-as-code starters.
- Docusaurus docs-site scaffold and docs impact tracking.
- Risk register, security exceptions, accepted risk log, threat model, abuse
  cases, evidence index, and system context defaults.
- Deterministic verification gates for missing threat models, docs impact,
  control maps, risk registers, spec sections, plan sections, AI guardrails,
  orchestration guardrails, and hardcoded secret patterns.
- Package assets so GitHub installs include presets, extensions, workflows, and
  control maps.
- Public repository health files, issue forms, PR template, CodeQL, Dependabot,
  and OpenSSF Scorecard workflow.
