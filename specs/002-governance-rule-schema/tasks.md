# Tasks: Governance Rule Schema

## Task 1: Create `rules/schema.json`

**Depends on**: None

**Docs impact**: New `sicario_cli/rules/` package documented in architecture.

**Evidence**: Rule schema JSON file, validation tests in test suite.

**Threat model**: Schema rejects arbitrary code injection fields — values are plain data types only.

1. Create `sicario_cli/rules/` package with `__init__.py`
2. Author JSON Schema at `sicario_cli/rules/schema.json` defining:
   - Top-level `$schema`, `$id`, `title`, `description`
   - `Rule` object properties: `id` (string, required), `severity` (enum: critical/high/medium/low), `kind` (enum of ALL supported kinds), `path` (globregex pattern, required), `params` (object), `message` (string, required), `fix` (optional object), `enabled` (boolean, default true)
   - `params` definitions per kind (section headings array, keywords array, regex pattern string, forbidden values array, match_all boolean, min_count integer)
   - `$defs` section for reusable sub-schemas
3. Add `jsonschema` to `pyproject.toml` dependencies (or use vendored fallback)
4. Add validation test: valid rule passes, missing `id` fails, unknown `kind` fails

## Task 2: Create `rules/engine.py`

**Depends on**: Task 1

1. Create `RuleEngine` class with:
   - `load_rules(rules_dirs: List[Path]) -> List[dict]` — scan for `*.rule.{yml,yaml}` in dirs, parse YAML, validate each against schema, collect errors
   - `evaluate(rule: dict, project_root: Path) -> List[Finding]` — dispatch to kind-specific evaluator
   - `run(project_root: Path) -> List[Finding]` — load + evaluate all rules
2. Include `ValidationError` for invalid rules (rule is skipped, not crashed)
3. Rule merging: if two rules have same `id`, later one wins (project overrides preset)
4. Write unit tests: loading from temp dir, invalid YAML, missing schema fields

## Task 3: Create evaluator modules per kind

**Depends on**: Task 2

1. Create `sicario_cli/rules/kinds/__init__.py` with kind-to-module mapping dict
2. Create each evaluator module:
   - `file_exists.py` — `evaluate(rule, root) -> [Finding]`
   - `file_glob.py` — supports `params.min_count` (default 1)
   - `section_exists.py`
   - `keyword_exists.py` (supports `match_all: true/false`)
   - `keyword_absent.py`
   - `regex_forbidden.py` (iterate all text files in `path` glob, apply pattern)
   - `regex_required.py`
   - `risk_rows_valid.py`
   - `classification_complete.py`
   - `tagging_complete.py`
3. Each module exports a single `evaluate(rule, root) -> List[Finding]` function
4. Write unit tests for each evaluator: happy path, missing file, edge cases
5. Add **security test** for each evaluator verifying it rejects invalid params gracefully
6. Add **negative** test: evaluator called with empty/missing file produces zero findings

## Task 4: Create shipped rule files

**Depends on**: Tasks 2, 3

1. Create `presets/sicario-core/rules/` directory
2. Author each rule as a `.rule.yml` file, one per current check group:
   - `010-file-exists.rule.yml` — threat model, docs-impact, diagrams, governance files
   - `020-control-maps.rule.yml` — framework selector + control maps directory
   - `030-risk-register.rule.yml` — risk files exist + active row validation
   - `040-secret-scan.rule.yml` — regex forbidden for SECRET_PATTERNS
   - `050-spec-sections.rule.yml` — required section headings in spec.md
   - `060-plan-sections.rule.yml` — required section headings in plan.md
   - `070-tasks-phrases.rule.yml` — required keyword phrases in tasks.md
   - `080-evidence-files.rule.yml` — evidence file scan (move `_scan_evidence_files` logic to rule)
   - `090-fleet-ai-guardrails.rule.yml` — AI keyword + fleet keyword guardrails
3. Each rule must produce exact same `Finding(code, severity, message, path)` as current hardcoded version
4. Integration test: run shipped rules against a known project, compare findings with current hardcoded output

## Task 5: Refactor `verify_project()` in `cli.py`

**Depends on**: Task 4

1. Replace all inline check blocks (lines 1579-1782) with `RuleEngine().run(root)`
2. Keep `_write_evidence()` and the `write` parameter handling
3. Keep `_validate_active_risk_rows()` until the risk evaluator is confirmed identical
4. Add `init` integration: copy `presets/sicario-core/rules/` into target project's `.sicario/rules/` during init flow
5. Remove hardcoded check code, keeping only:
   - `iter_text_files(root)` — still needed if `regex_forbidden` evaluator uses it directly
   - `_write_evidence(root, findings)` — unchanged
   - `verify_project()` signature unchanged
6. Run `python3 -m unittest discover -s tests` — all existing tests must pass without changes
7. Run `python3 -m sicario_spec.cli verify .` — output must be identical to pre-refactor run

## Task 6: Add `--format` and `--validate-rules` flags

**Depends on**: Task 5

1. Add `--format {text,sarif}` click option to verify command
2. Implement SARIF output: write findings to `generated/sicario/findings.sarif`
3. Add `--validate-rules` flag: validate all discovered rule files and print errors (or "All rules valid")
4. Update help text for verify command
5. Test SARIF output is valid SARIF 2.1.0 JSON; test `--validate-rules` on broken rule file

## Task 7: Test, Verify, Commit

**Depends on**: Task 6

1. Run full test suite: `python3 -m unittest discover -s tests`
2. Run `python3 -m sicario_spec.cli verify . --format text` — output matches pre-refactor
3. Run `python3 -m sicario_spec.cli verify . --format sarif` — valid SARIF produced
4. Run `python3 -m sicario_spec.cli verify . --validate-rules` — all rules valid
5. Run performance benchmark: cold-start load + evaluate 10 rules under 100ms
6. Run `ruff check . && ruff format .`
7. Commit and push changes
