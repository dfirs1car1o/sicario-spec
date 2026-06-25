# Declarative Rule Engine

SicarioSpec 0.5.1 moved `sicario verify` from hardcoded Python checks to a
declarative rule engine. The pass/fail verdict is still deterministic and owned
by code, but the checks are now data: `*.rule.json` files validated against a
schema and dispatched to fixed evaluator kinds.

This matters for teams adopting the bundle because custom governance gates no
longer require a Python release. A platform or security team can add a project
rule, review it like any other policy file, and run the same halting gate in CI.

## Where Rules Live

`sicario verify` reads rules from:

1. `.sicario/rules/*.rule.json` in the target project.
2. Shipped SicarioSpec rules in `presets/sicario-core/rules/`.

Project rules are loaded first, and rules with the same `id` override earlier
rules. Use that behavior to disable or narrow a shipped rule without editing the
package:

```json
{
  "id": "SICARIO-HARDCODED-SECRET",
  "severity": "critical",
  "kind": "regex-forbidden",
  "path": "**/*",
  "params": {
    "pattern": "(?i)\\b(api[_-]?key|secret|token|password)\\b\\s*[:=]\\s*['\"][^'\"]{12,}['\"]"
  },
  "message": "Potential hardcoded secret",
  "enabled": false
}
```

That example keeps the same rule id and sets `enabled` to `false`, so the rule is
skipped. A real project should record the rationale in its risk or exception
register before disabling a gate.

## Rule Contract

Every rule is valid JSON. Do not use JSON comments. Explain intent through
field names, clear messages, README text, or adjacent documentation.

Required fields:

| Field | Purpose |
|---|---|
| `id` | Stable finding code or policy identifier, uppercase with hyphens. |
| `severity` | `critical`, `high`, `medium`, or `low`. |
| `kind` | Fixed evaluator kind. Rules cannot execute arbitrary code. |
| `path` | File path or glob pattern relative to the project root. |
| `message` | Human-readable failure message emitted by `sicario verify`. |

Optional fields:

| Field | Purpose |
|---|---|
| `params` | Kind-specific settings such as required headings, keywords, regex patterns, or minimum file count. |
| `enabled` | Boolean. Defaults to `true`; set to `false` to suppress a rule by id. |
| `fix` | Reserved for future auto-remediation metadata. |

## Supported Kinds

| Kind | Use |
|---|---|
| `file-exists` | Require a single file to exist. |
| `file-glob` | Require at least one file matching a glob. |
| `section-exists` | Require headings or section text in a file. |
| `keyword-exists` | Require one or more keywords. |
| `keyword-absent` | Fail when forbidden keywords appear. |
| `regex-forbidden` | Fail when a regex appears in matching text files. |
| `regex-required` | Fail when a regex is absent from a matching file. |
| `risk-rows-valid` | Validate active risk/exception rows for owner, expiry, rationale, approval, and evidence. |
| `classification-complete` | Validate data-classification documentation completeness. |
| `tagging-complete` | Validate tagging-taxonomy documentation completeness. |

## Validation Workflow

Validate rules without running the full project checks:

```bash
sicario verify --validate-rules
```

Run the full gate:

```bash
sicario verify
```

Machine-readable output is available for automation:

```bash
sicario verify --format json
sicario verify --format sarif
```

## Current Community Queue

Two public contribution tracks are intentionally left open for community PRs:

- Add a custom-rule example under `examples/custom-rules/`.
- Add another control map, choosing one of SOC 2, FedRAMP, or BSI C5.

Both are good review targets because they exercise the public extension points:
rule files and control-map JSON. The maintainer should review them for valid
JSON, clear evidence mapping, correct docs, and passing `sicario verify`.
