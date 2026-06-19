# Changelog

All notable changes to SicarioSpec are tracked here.

The project follows semantic versioning once the public API stabilizes. During
the `0.x` line, minor versions may introduce breaking changes when needed to
improve the security model.

## [0.1.2] - 2026-06-19

Release for agent-native environments, the public documentation site, and
clearer launch positioning.

### Added

- Agent-native bootstrap outputs for Claude Code, Codex, and GitHub Copilot
  coding agent through `--integration codex`, `--integration copilot`, and
  `--integration all`.
- Repo-scoped SicarioSpec skills for verification, governance review, and
  release readiness.
- Copilot instructions and setup workflow for cloud-agent environments.
- Public GitHub Pages documentation site backed by the repository `docs/`
  content.
- Adoption and launch guide for positioning, proof points, and first outreach
  messages.

### Changed

- README positioning, badges, quickstart, generated artifact list, and
  agent-native delivery guidance.

## [0.1.1] - 2026-06-19

Patch release for repository hardening after the initial public release.

### Added

- Machine-user pull request workflow with an audited maintainer fallback for
  environments that cannot provision a machine account.
- Data classification and tagging evidence requirements in the public
  contribution and repository governance workflow.

### Fixed

- Release workflow now builds, smoke-tests, uploads the workflow artifact,
  emits provenance attestations, and treats existing GitHub releases as
  immutable.
- Release reruns no longer attempt to add, replace, delete, or rename assets on
  an existing immutable release.

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
