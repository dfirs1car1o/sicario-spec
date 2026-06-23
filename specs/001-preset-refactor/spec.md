# Preset System Refactoring

**Status**: Draft
**Author**: SicarioSpec
**Last Updated**: 2026-06-23
**Feature Directory**: `specs/001-preset-refactor/`

## Overview

The `init()` function in `cli.py` has grown to ~400 lines of inline writes interleaved with orchestration. All `_write_*`, `_default_*`, and `_*_overlay` helpers are also in `cli.py`, making the file ~2400 lines. This refactoring extracts preset content into standalone Python modules so each preset owns its files, centralizes rendering helpers into `_render.py`, and keeps `cli.py` as a thin orchestrator.

**Goal**: Reduce `cli.py` by extracting ~500 lines of content generators and write helpers into focused modules, with zero behavioral change to `init`, `verify`, `assess`, or `hooks` commands.

## Actors

- **Maintainers**: Developers running `sicario init` or working on `cli.py`
- **SicarioSpec CLI**: The `init()` command that writes governance artifacts to a target project

## User Stories

- As a **maintainer**, I want to understand the init flow at a glance without scrolling through 400 lines of file writes.
- As a **contributor**, I want preset content isolated in its own module so I can add or fix a preset without touching `cli.py`.
- As a **reviewer**, I want the diff on a preset change to touch only `presets/sicario-*/preset.py` and not `cli.py`.

## Functional Requirements

### FR1: Centralize Render Helpers

Move `_copy_tree`, `_write_text`, `_overlay_text`, `_backup_file`, `_backup_path`, `_record`, the `FileReport` dataclass, report printing, and outcome constants into `_render.py`. Keep the same public interface so existing callers (presets, agent integration writer, workflow writer) continue to work.

### FR2: Extract sicario-core Preset

Create `presets/sicario-core/preset.py` that owns:

- `.specify/presets/sicario-core/` directory copy
- Template/constitution overlay for Speck Kit paths
- `SICARIO.md` project readme
- Security docs: `docs/security/threat-model.md`, `docs/security/abuse-cases.md`
- Governance docs: `docs/governance/data-classification.md`, `docs/governance/tagging-taxonomy.md`
- Compliance docs: `docs/compliance/control-applicability.md`, `docs/compliance/evidence-index.md`
- Architecture docs: `docs/architecture/system-context.md`, `docs/diagrams/system-context.mmd`
- Risk docs: `docs/risk/risk-register.md`, `docs/risk/security-exceptions.md`, `docs/risk/accepted-risk-log.md`
- `CLAUDE.md` overlay, Claude skills/agents
- `AGENTS.md` overlay, Codex skills, Copilot instructions
- GitHub workflow files (sicario-verify.yml, docs-site.yml, etc.)
- `docs/docs-impact.md`
- Control maps directory copy
- Extension config copy (`sicario-guard`, `extensions.yml`)
- Framework selector config
- Cloud-IaC starter directory copy
- Security toolchain directory copy

### FR3: Extract sicario-docs Preset

Create `presets/sicario-docs/preset.py` that owns:

- Docusaurus docs-site boilerplate: `docs-site/package.json`, `docusaurus.config.js`, `sidebars.js`, `docs/intro.md`, `src/css/custom.css`

### FR4: Thin Orchestrator

Refactor `init()` to:

1. Resolve profiles to preset list (same as today)
2. Detect existing governance (same as today)
3. For each preset, call `preset.write(target, vars)` which internally uses `_render.py` helpers
4. Presets receive `(target, force, dry_run, actions, reports)` and call `_render.write_text()`, `_render.overlay_text()`, `_render.copy_tree()` as needed
5. Keep framework selector, extension config, and control-map copy in `cli.py` (these are orchestration, not content)

### FR5: Backward Compatibility

- All existing CLI flags (`--profile`, `--integration`, `--frameworks`, `--dry-run`, `--force`, `--apply-to-speckit`/`--no-apply-to-speckit`) behave identically
- All existing tests pass without modification
- No new runtime dependencies

## Non-Goals

- Behavioral changes to `init`, `verify`, `assess`, or `hooks`
- Changes to the `preset.yml` files (these remain as static metadata)
- Extracting other presets (sicario-appsec, ai-system, agent-fleet, cloud-iac, supply-chain, compliance, saas, security-toolchain, enterprise-strict) into Python modules
- Changing the packaging/distribution mechanism

## Success Criteria

1. `cli.py` line count is reduced by at least 400 lines
2. `_render.py` exports the same `copy_tree`, `write_text`, `overlay_text`, `FileReport` API
3. `presets/sicario-core/preset.py` exists and produces identical output to the inline code it replaced
4. `presets/sicario-docs/preset.py` exists and produces identical output to the inline code it replaced
5. All 66 existing tests pass (the 1 pre-existing PyYAML import error is not caused by this change)
6. `python3 -m sicario_cli.cli init /tmp/test-project --profile appsec` produces the same file set before and after

## Assumptions

- The `Preset(ABC)` base class is not required; Python duck typing suffices (presets just need a `write()` method)
- Existing presets do not need to be converted to Python — only sicario-core and sicario-docs (the two shipped by every profile) are extracted
- The existing `sicario_cli/assets/presets/` copies will continue to be the source of truth for `preset.yml` metadata and static template files

## AI Guardrails

This spec describes a CLI refactoring, not an AI agent, but preset content generation is invoked by an AI coding agent. Guardrails applied:
- **Prompt injection**: The `AGENTS.md` and `CLAUDE.md` preset output is plain text metadata, not executable instructions
- **Tool boundary**: All preset writes go through `_render.py` helpers which validate output paths are within the target project directory

## Fleet Guardrails

Refactored preset classes are invoked sequentially from `init()`, not as a distributed fleet. Guardrails applied:
- **Idempotency**: Each `preset.write()` is idempotent — re-running `init` with the same flags produces identical output
- **Retry**: Unnecessary at this layer; filesystem writes succeed or fail atomically
- **Dead-letter**: N/A — no async messaging
- **Workflow state**: N/A — single-process synchronous execution
- **Human approval**: N/A — the user explicitly runs `init` with their chosen flags

## Security Requirements

- No secrets, credentials, or tokens in generated project files
- The `--dry-run` flag must never write files (including preset tests)
- Brownfield safety must be preserved: pre-existing files are never silently clobbered

## Data Classification

| Classification owner / Category | Level | Owner | Retention | Residency | Sharing | Redaction |
|---|---|---|---|---|---|---|
| Source code | Public | SicarioSpec team | Indefinite | GitHub | Public repo | N/A |
| Spec documents | Internal | SicarioSpec team | Indefinite | GitHub | Org-internal | N/A |
| Test artifacts | Public | SicarioSpec team | Indefinite | GitHub | Public repo | N/A |

## Tagging Discipline

| Tag | Value |
|---|---|
| owner | sicario-spec-team |
| system | sicario-spec |
| environment | development |
| data-classification | internal |
| retention | indefinite |
| project | preset-refactor |

## Trust Boundaries

- The CLI runs on the developer's local machine; no network calls are made
- Preset output is written to the local filesystem only
- No secrets, tokens, or credentials are handled

## Abuse Cases

- A user passes `--force` to overwrite files they did not intend to lose — mitigated by `--dry-run` and backup behavior
- A user passes an invalid preset name — mitigated by profile validation before any writes

## Evidence

- `docs/compliance/evidence-index.md` is generated by the sicario-core preset
- Spec compliance is verified by `sicario verify` as a CI gate

## Dependencies

- All existing `_default_*` content generator functions (e.g., `_default_threat_model()`, `_claude_instructions()`) remain in `cli.py` and are called from presets, OR move to `_render.py` if used by multiple presets
- `_validate_specify_available()` stays in `cli.py`
