# Implementation Plan: Governance Rule Schema

## Architecture

### Current State

```
cli.py (~2200 lines)
└── verify_project() — ~212 lines (lines 1575-1787)
    ├── File-existence checks (threat model, docs-impact, diagrams, governance files)
    ├── Compliance control-map checks (framework selector, control-maps dir)
    ├── Risk-register checks (file exists + _validate_active_risk_rows)
    ├── Secret scan (iter_text_files + SECRET_PATTERNS regex)
    ├── Evidence file scan (_scan_evidence_files)
    ├── Spec checks (required section headings, classification/tags, AI guardrails, fleet guardrails)
    ├── Plan checks (required section headings)
    └── Tasks checks (required keyword phrases)

Finding — dataclass in cli.py with severity, code, message, path
```

Every check is hardcoded Python in `verify_project()`. Adding a new check means editing `cli.py`, writing a new `if` block, and shipping a release.

### Target State

```
sicario_cli/
├── cli.py — thin orchestrator (~1700 lines)
│   └── verify_project() — ~30 lines
│       ├── load rules from project + preset dirs
│       ├── validate rules against schema
│       └── run each rule through RuleEngine
├── rules/
│   ├── __init__.py
│   ├── schema.json        — JSON Schema for rule definitions
│   ├── engine.py          — RuleEngine: load, validate, evaluate
│   └── kinds/             — one evaluator module per rule kind
│       ├── __init__.py
│       ├── file_exists.py
│       ├── section_exists.py
│       ├── keyword_exists.py
│       ├── keyword_absent.py
│       ├── regex_forbidden.py
│       ├── regex_required.py
│       └── ...
└── presets/sicario-core/
    └── rules/             — shipped default rule set
        ├── 010-file-exists.rule.yml
        ├── 020-control-maps.rule.yml
        ├── 030-risk-register.rule.yml
        ├── 040-secret-scan.rule.yml
        ├── 050-spec-sections.rule.yml
        ├── 060-plan-sections.rule.yml
        ├── 070-tasks-phrases.rule.yml
        ├── 080-evidence-files.rule.yml
        └── 090-fleet-ai-guardrails.rule.yml
```

### Key Design Decisions

1. **YAML as rule format** — YAML is more readable than JSON for humans writing rules by hand. Internally parsed to dict, validated against JSON Schema.

2. **`RuleEngine` is a single class** — loads rules, validates against schema, evaluates each, returns findings. Stateless and pure.

3. **One evaluator module per kind** — each `kind` (e.g. `file-exists`, `section-exists`) has a dedicated evaluator function. This keeps the evaluation logic isolated and testable, and makes adding a new kind a single-file change.

4. **`Finding` stays in `cli.py`** — the dataclass is shared by verify and other commands. No change to its signature.

5. **Shipped rules are the exact behavioral equivalent of current hardcoded checks** — same codes, same severities, same messages, same paths. Only the source of truth moves.

6. **No external rule engine dependency** — `json-schema` validation uses the `jsonschema` library (or a minimal vendor). Evaluation uses stdlib.

7. **`enabled: false` for disabling shipped rules** — users don't delete shipped rules; they set `enabled: false` in an override file.

## Rule Evaluation Logic

For each rule loaded from `.sicario/rules/` and `presets/sicario-core/rules/`:

1. Parse and validate against `schema.json` — skip invalid rules with a warning
2. Resolve `path` relative to project root
3. Dispatch to evaluator by `kind`:
   - `file-exists`: check `Path(path).exists()`
   - `file-glob`: `glob(path)` and match count against `params.min_count` (default 1)
   - `section-exists`: read file, check each `params.headings` case-insensitively in text
   - `keyword-exists`: read file, check `params.keywords` present (AND or OR per `params.match_all`)
   - `keyword-absent`: read file, assert none of `params.keywords` present
   - `regex-forbidden`: iterate all text files matching `path` pattern, apply `params.pattern` — finding if any match
   - `regex-required`: read file, apply `params.pattern` — finding if no match
   - `risk-rows-valid`: parse markdown table, validate row cells against `params.forbidden_values`
   - `classification-complete`: parse data-classification table, check required columns present
   - `tagging-complete`: parse tagging table, check required columns present
4. Collect `Finding(code, severity, message, path)` into result list

## Implementation Order

1. Create `sicario_cli/rules/schema.json` — JSON Schema defining the rule format
2. Create `sicario_cli/rules/engine.py` — `RuleEngine` class with load, validate, evaluate
3. Create `sicario_cli/rules/kinds/` with evaluator modules for all current check types
4. Create shipped rule files in `presets/sicario-core/rules/`
5. Refactor `verify_project()` in `cli.py` — replace inline checks with engine call
6. Add `--format sarif` and `--validate-rules` flags
7. Run tests, verify behavioral parity, commit

## Threat Model

- **Attacker model**: Project contributor with write access to `.sicario/rules/` — can add rules that trigger on any project file
- **Trust**: Rule files are project-owned and reviewed via normal PR process; same trust as the rest of the project
- **Mitigations**: Path traversal prevented by resolving all patterns relative to project root; no code execution from rules; schema validation rejects unknown fields

## Data Classification

| Artifact | Classification | Rationale |
|---|---|---|
| Spec docs (spec.md, plan.md, tasks.md) | Internal | Feature planning, not customer-facing |
| Built-in rule files (presets/*.rule.yml) | Public | Open-source governance definitions |
| Rule engine and schema | Public | Core library code |
| User-defined rules (.sicario/rules/*.rule.yml) | Internal | Project-specific policy gates |

## Tagging

All commits, PRs, and spec artifacts carry tags: `rule-schema`, `verify`, `governance`, `sicario`.

## Well-Architected

- **Reliability**: Deterministic evaluation; same rules always produce same output
- **Security**: Rules cannot execute code or read outside project root
- **Cost**: No new infrastructure or cloud dependencies
- **Operational Excellence**: Adding a gate is now a YAML file, not a Python release
- **Performance Efficiency**: Rule engine runs in <100ms for the default rule set

## Supply Chain

- New dependency: `PyYAML` (already a transitive dep or widely available)
- New dependency: `jsonschema` (or vendored minimal validator)
- All rule evaluators use stdlib only

## Rollback

- `git revert` of the merge commit restores inline checks in `cli.py`
- Shipped rule files are part of the package, so version pinning controls which rules apply
- User-defined rule files are versioned in their own VCS

## Human Approval

- Default `verify` behavior is unchanged — findings are surfaced but no automated changes
- `--fix` mode (future FR) would require explicit `--fix` flag
- Rule files themselves go through normal PR review

## Evidence

- Unit tests for each rule kind evaluator
- Integration test that shipped rules produce same findings as current hardcoded checks
- `--format sarif` output conforms to SARIF 2.1.0 spec
- Schema validation tests (reject invalid rule YAML)

## Dependencies

- Task 1 (schema.json) must complete before Task 2 (engine validates against schema)
- Tasks 2-3 (engine + evaluators) must complete before Task 4 (shipped rule files reference defined kinds)
- Task 4 (shipped rules) must complete before Task 5 (refactor verify — rules must exist to load)
- Task 6 (SARIF/output flags) can run in parallel with Tasks 2-4
- Task 7 (tests, commit) is the final step
