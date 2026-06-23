# Governance Rule Schema

**Status**: Draft
**Author**: SicarioSpec
**Last Updated**: 2026-06-23
**Feature Directory**: `specs/002-governance-rule-schema/`

## Overview

The `sicario verify` command currently embeds all governance checks as hardcoded Python logic in `cli.py` — file-existence assertions, section-heading scans, regex-based secret detection, and keyword-pattern matching. Adding a new check requires editing `cli.py` and re-release. This feature externalizes those checks into a machine-readable rule definition so that:

- Anyone can add custom gates by writing a YAML/JSON rule file, without touching Python.
- The same rules can be consumed by CI/CD tools, policy engines, and IDE plugins.
- The sicario-core preset ships a standard rule set that gates merge on the same conditions as today.

The design extracts the *what* (which file patterns verify? which section headings are required? which keywords signal missing guardrails?) from the *how* (the Python logic that interprets them).

## Actors

- **Maintainers**: Developers who add or modify governance checks.
- **Project owners**: Teams using sicario-spec who want custom gates without forking.
- **SicarioSpec CLI**: The `verify` command reads rule files and evaluates them.

## User Stories

- As a **project owner**, I want to add a custom check ("every HTTP API spec must have an OpenAPI contract") by writing one YAML file, so I don't need to fork the CLI or learn Python.
- As a **maintainer**, I want to add a new governance requirement by adding a rule to the preset rule set, so the verify gate stays in sync without a CLI release.
- As a **CI/CD operator**, I want the verify output in SARIF format so I can surface findings in GitHub code scanning and PR annotations.
- As a **platform team**, I want to write a rule that says "any Terraform root module must have `required_version` pinned" without editing `cli.py`.

## Functional Requirements

### FR1: Rule Format

A rule definition is a YAML or JSON file with:

- `id`: Unique string identifier (e.g., `SICARIO-MISSING-THREAT-MODEL`)
- `severity`: `critical`, `high`, `medium`, `low`
- `kind`: One of:
  - `file-exists` — assert a relative path exists
  - `file-glob` — assert glob matches at least N files
  - `section-exists` — assert a case-insensitive heading appears in a file
  - `keyword-exists` — assert keyword(s) appear in a file (AND/OR logic)
  - `keyword-absent` — assert keyword(s) do NOT appear in a file
  - `regex-forbidden` — assert no matches for a regex pattern
  - `regex-required` — assert at least one match for a regex pattern
  - `risk-rows-valid` — validate active risk rows have non-empty cells
  - `classification-complete` — validate data-classification table has owner/retention/residency/sharing/redaction
  - `tagging-complete` — validate tagging table has owner/system/environment/data-classification/retention
- `path`: File or glob pattern relative to project root
- `params`: Kind-specific configuration (list of required sections, keywords, regex patterns, etc.)
- `message`: Human-readable failure message
- `fix`: Optional template path or inline patch for auto-remediation (future FR4)
- `enabled`: Boolean, default true

### FR2: Rule Discovery

1. `verify` scans `{project_root}/.sicario/rules/` for `*.rule.{yml,yaml}` files.
2. The sicario-core preset ships a standard set at `presets/sicario-core/rules/`.
3. `init` copies the shipped rules into the target project's `.sicario/rules/`.
4. Users add, remove, or override rules in `.sicario/rules/` directly.
5. (Future) Rule files will support `extends` to inherit from a base rule and override individual fields — not in scope for v1.

### FR3: Rule Engine

1. At startup, `verify` loads all discovered rule files, validates each against a JSON Schema, and collects errors for any invalid rules.
2. The engine evaluates each rule in order and produces a list of `Finding` objects.
3. The existing hardcoded checks in `cli.py` are migrated to rules one-for-one, with zero behavioral change to the output.
4. After migration, `verify_project()` becomes a thin loop: load rules → evaluate → collect findings → write evidence.
5. Rule evaluation is deterministic and pure (no side effects).

### FR4: Output Formats

1. Default output remains human-readable stdout (same as today).
2. `--format sarif` writes findings to `generated/sicario/findings.sarif`.
3. (Future) `--format opa` — not in scope for v1 (see Non-Goals).
4. Exit code is 1 if any finding exists (unchanged behavior).

### FR5: Custom Rule Authoring

1. Project owners can add `my-org-policy.rule.yml` to `.sicario/rules/` without any CLI changes.
2. Custom rules use the same format and engine as built-in rules.
3. A `verify --validate-rules` flag validates all rule files without running checks.
4. An invalid rule file logs a warning and is skipped (does not crash the verify run).

### FR6: Backward Compatibility

1. All existing tests pass without modification.
2. All existing finding codes, severities, and messages remain identical.
3. The default rule set shipped with sicario-core matches the current hardcoded check set exactly.
4. `--dry-run`, `--force`, `--profile`, and all existing init flags are unaffected.

## Non-Goals

- Removing the ability to add checks in Python — hardcoded checks can coexist with rule-file checks.
- Building a web UI or dashboard for rule authoring.
- Real-time rule evaluation on file change.
- Dependency on external policy engines (OPA, Kyverno, etc.) — the engine is built-in.

## Success Criteria

1. All current hardcoded verify checks are expressed as rule files and produce identical findings.
2. A user can add a new check by writing one `.rule.yml` file, no Python edits.
3. Adding a JSON Schema validation that rejects a malformed rule with a clear error message.
4. `--format sarif` produces a valid SARIF 2.1.0 file.
5. All existing 50+ unit tests pass without modification.
6. The rule engine runs in <100ms on a project with 10 rules (cold start).

## Data Classification

| Classification owner / Category | Level | Owner | Retention | Residency | Sharing | Redaction |
|---|---|---|---|---|---|---|
| Rule definitions | Public | SicarioSpec team | Indefinite | GitHub | Public repo | N/A |
| SARIF output | Internal | SicarioSpec team | Per-run | Local filesystem | CI artifact | N/A |

## Tagging Discipline

| Tag | Value |
|---|---|
| owner | sicario-spec-team |
| system | sicario-spec |
| environment | development |
| data-classification | internal |
| retention | indefinite |
| project | governance-rule-schema |

## Trust Boundaries

- Rule files are loaded from the project's own `.sicario/rules/` directory — same trust boundary as the project itself.
- The rule engine does not make network calls.
- Rules only read files within the project root.

## Abuse Cases

- A malicious rule file with an expensive regex — mitigated by per-rule timeout or pattern-length limit.
- A rule that tries to read outside the project root — mitigated by path validation relative to root.
- A rule missing required fields — caught by JSON Schema validation at load time.

## AI / Tool Boundary

This feature does not involve AI. Rule evaluation is deterministic Python.

- **Prompt injection**: Rule files are plain JSON parsed by `json.loads()` — no code execution from rule content. The schema rejects arbitrary Python/code blocks.
- **Tool boundary**: The rule engine reads project files only within the project root. No network calls, no external tool invocation.

## Fleet Guardrails

N/A — single-process synchronous evaluation.

## Security Requirements

- Rule files must not be executable or support code injection.
- The rule schema must reject arbitrary Python/JS code blocks.
- Path patterns must be restricted to the project root.

## Evidence

- `generated/sicario/gate-summary.json` continues to be written.
- SARIF output, when requested, is an additional evidence artifact.
- Rule schema version is recorded in gate-summary.json.

## Dependencies

- JSON Schema (stdlib `jsonschema` or vendored minimal schema validator).
- `pathlib`, `re`, `fnmatch` for rule evaluation — all stdlib.
- No new runtime dependencies on hosted services or policy engines.
