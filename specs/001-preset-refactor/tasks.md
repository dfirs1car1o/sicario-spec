# Tasks: Preset System Refactoring

## Task 1: Create `_render.py`

**Depends on**: None

- [x] Create `sicario_cli/_render.py`
- [x] Move from `cli.py`: `FileReport`, `OUTCOME_*`, `_record`, `_backup_path`, `_backup_file`, `_copy_tree`, `_write_text`, `_overlay_text`, `_print_report`
- [x] Re-export `SICARIO_OVERLAY_BEGIN`, `SICARIO_OVERLAY_END` (needed by overlay callers)
- [x] Update `cli.py` to import all moved symbols from `_render`
- [x] Verify `python3 -m sicario_cli.cli init /tmp/test --dry-run` still works

## Task 2: Create `presets/sicario-core/preset.py`

**Depends on**: Task 1

- [x] Create `presets/__init__.py` (empty)
- [x] Create `presets/sicario-core/__init__.py` (empty)
- [x] Create `presets/sicario-core/preset.py` with `SicarioCorePreset` class
- [x] Implements `write(target, *, force, dry_run, actions, reports)` that:
  - Copy `.specify/presets/sicario-core/` via `_render.copy_tree()`
  - Call `_apply_to_speckit()` (still in cli.py)
  - Write all docs files via `_render.write_text()`
  - Write agent integrations via `cli.py._write_agent_integrations()`
  - Write workflow files
  - Copy cloud-iac starters (if enabled) and security-toolchain starters (if enabled)
- [x] Receives `selected_presets` list so it can check conditions like `"sicario-cloud-iac" in selected_presets`

## Task 3: Create `presets/sicario-docs/preset.py`

**Depends on**: Task 1

- [x] Create `presets/sicario-docs/__init__.py` (empty)
- [x] Create `presets/sicario-docs/preset.py` with `SicarioDocsPreset` class
- [x] `write()` writes:
  - `docs-site/package.json`, `docusaurus.config.js`, `sidebars.js`
  - `docs-site/docs/intro.md`, `docs-site/src/css/custom.css`

## Task 4: Refactor `init()` in `cli.py`

**Depends on**: Tasks 2, 3

- [x] Import `SicarioCorePreset` and `SicarioDocsPreset`
- [x] Build preset-to-class mapping: `PRESET_CLASSES = {"sicario-core": SicarioCorePreset, "sicario-docs": SicarioDocsPreset}`
- [x] Replace inline docs writes with a loop over `selected_presets`: for each preset ID, if it has a class in `PRESET_CLASSES`, instantiate and call `.write()`
- [x] Keep in `cli.py`: framework selector writes, control maps copy, extension config
- [x] Keep in `cli.py`: `_default_*` content generators, `_write_agent_integrations()`, `_apply_to_speckit()`
- [x] Remove from `cli.py`: all 16 inline `_write_text()` calls for docs files
- [x] Remove from `cli.py`: cloud-iac and security-toolchain starter copies (move to SicarioCorePreset)
- [x] Remove from `cli.py`: docs-site writes (move to SicarioDocsPreset)

## Task 5: Test and Verify

**Depends on**: Task 4

- [x] Run full test suite: `python3 -m unittest discover -s tests`
- [x] Run dry-run init to verify output matches: `python3 -m sicario_cli.cli init /tmp/verify-before --profile appsec --dry-run`
- [x] Fix any test failures
- [x] Verify `python3 -m sicario_cli.cli init /tmp/test-project --profile appsec --force` produces a valid project tree

## Task 6: Security Test

**Depends on**: Task 4

- [x] Verify that `--dry-run` never creates files
- [x] Verify that `--force` overwrites files but creates backups
- [x] Verify that invalid profile names produce a clear error (no partial writes)
- [x] Add test: `test_init_dry_run_creates_nothing`
- [x] Add test: `test_preset_write_idempotent`

## Task 7: Negative Test

**Depends on**: Task 4

- [x] Test that `init` with an empty profile list exits gracefully
- [x] Test that `init` to a path without write permissions errors cleanly
- [x] Verify `--no-apply-to-speckit` suppresses Speck Kit overlay
- [x] Add test: `test_init_no_profiles_does_not_crash`

## Task 8: Data Classification

**Depends on**: Task 4

- [x] Add `Data Classification` section to `spec.md`
- [x] Verify no classified data leaks into preset output files
- [x] Add test scanning generated files for placeholder secrets

## Task 9: Tagging

**Depends on**: Task 4

- [x] Add `Tagging` section to `plan.md`
- [x] Verify all commits carry conventional-commit tags
- [x] Ensure all preset Python files have `# presets/` SPDX-like tags

## Task 10: Docs Impact

**Depends on**: Task 4

- [x] Add `docs-impact.md` entry documenting the `cli.py` → preset-class split
- [x] Update `docs/architecture.md` with the preset-class plugin tree (already done in this PR)

## Task 11: Evidence Generation

**Depends on**: Task 4

- [x] Ensure `docs/compliance/evidence-index.md` is generated with the new preset classes
- [x] Add test that `init --profile appsec` produces evidence-index.md

## Task 12: Threat Model Update

**Depends on**: Task 4

- [x] Add `Threat Model` section to `plan.md`
- [x] Verify the threat model covers preset output injection risks
- [x] Document the trust boundary between `cli.py` and `presets/`

## Task 13: Commit

**Depends on**: Task 5

1. `git add` all new and modified files
2. `git commit` with conventional message
