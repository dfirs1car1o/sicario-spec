# Implementation Plan: Preset System Refactoring

## Architecture

### Current State

```
cli.py (~2411 lines)
├── PROFILE_PRESETS, framework constants (lines 1-130)
├── FileReport, _backup_*, _copy_tree, _write_text, _overlay_text (lines 230-478)
├── detect_existing_governance, _*_overlay, _apply_to_speckit (lines 481-699)
├── init_project() — 374 lines of inline writes (lines 700-1074)
│   ├── Phase 1-2: parse, detect, copy preset dirs
│   ├── Phase 3: apply to speckit
│   ├── Phase 4-5: cloud-iac, security-toolchain starters
│   ├── Phase 6-7: control maps, framework selector
│   ├── Phase 8: extensions
│   ├── Phase 9: SICARIO.md + 15 docs files (inline _write_text calls)
│   ├── Phase 10: agent integrations (dispatches to _write_agent_integrations)
│   └── Phase 11: workflows
├── _default_* content generators (lines 1100-1735)
├── _write_agent_integrations (lines 1736-1860)
├── verify_project, hooks command, parser (lines 1860-2411)
```

### Target State

```
sicario_cli/
├── __init__.py
├── version.py
├── cli.py — thin orchestrator (~1800 lines)
│   ├── imports from _render, presets/sicario-core, presets/sicario-docs
│   ├── PROFILE_PRESETS, framework constants
│   ├── detect_existing_governance, _*_overlay, _apply_to_speckit (unchanged)
│   ├── init_project() — ~50 lines orchestration
│   │   ├── parse, detect, resolve presets
│   │   ├── for each preset: preset.write(...)
│   │   ├── framework selector
│   │   └── control maps copy
│   ├── verify_project, hooks, parser (unchanged)
│   └── _default_* content generators (unchanged)
├── _render.py — new file
│   ├── from cli.py: FileReport, OUTCOME_* constants
│   ├── from cli.py: _record, _backup_path, _backup_file
│   ├── from cli.py: _copy_tree, _write_text, _overlay_text
│   └── from cli.py: _print_report
├── presets/
│   ├── __init__.py — empty
│   └── sicario-core.py — SicarioCorePreset
└── assets/
    └── presets/
        └── sicario-docs/ — existing preset.yml + templates (unchanged)
```

### Key Design Decisions

1. **`_render.py` is a module, not a class** — the `_write_*` helpers are standalone functions that take `actions` and `reports` lists. A module preserves this stateless design.

2. **Presets are callable classes** — each preset has a `write(target, *, force, dry_run, actions, reports)` method. They import `_render` for file ops and call `_default_*` content generators from `cli.py`.

3. **`_default_*` functions stay in `cli.py`** — they're only called during `init`, and keeping them there avoids circular imports while reducing the diff. A future refactoring can move them once they're shared more broadly.

4. **sicario-docs is a Python preset** — it also gets a `preset.py` even though it only writes docs-site files. This makes the preset resolution uniform: every profile expands to preset classes that all respond to `.write()`.

5. **No `Preset(ABC)`** — duck typing keeps it simple and avoids an abstract base class import.

## Implementation Order

1. Create `_render.py` — move the 6 write helpers + `FileReport` + `OUTCOME_*` + `_print_report`
2. Update `cli.py` — import from `_render` instead of defining locally
3. Create `presets/sicario-core/preset.py` — `SicarioCorePreset.write()`
4. Create `presets/sicario-docs/preset.py` — `SicarioDocsPreset.write()`
5. Refactor `init()` — replace inline writes with `preset.write(...)` calls
6. Create `__init__.py` for `presets/` if needed
7. Run tests, verify behavioral parity, commit

## Threat Model

- **Attacker model**: Local developer workstation — attacker with filesystem write access can modify preset outputs
- **Trust**: CLI binary is trusted; preset files ship with the package and are not fetched at runtime
- **Mitigations**: `--dry-run` prevents writes; backups created before overwrites; no network calls

## Data Classification

| Artifact | Classification | Rationale |
|---|---|---|
| Spec docs (spec.md, plan.md, tasks.md) | Internal | Feature planning, not customer-facing |
| Source code (presets/*.py) | Public | Open-source governance tooling |
| Test files | Public | No sensitive data |

## Tagging

All commits, PRs, and spec artifacts carry tags: `preset-refactor`, `init-refactor`, `sicario`.

## Well-Architected

- **Reliability**: Writes are idempotent; re-running produces the same output
- **Security**: No secrets in outputs; dry-run mode as safety net
- **Cost**: No new infrastructure or cloud dependencies
- **Operational Excellence**: clear separation of concerns (orchestration vs. content)
- **Performance Efficiency**: unchanged — same number of file writes, same total I/O

## Supply Chain

- No new runtime dependencies
- `_render.py` uses only `pathlib` and standard library
- Preset classes are packaged with `sicario-spec` wheel

## Rollback

- `git revert` of the merge commit restores the prior `cli.py` layout
- Preset output files in target projects are not versioned by sicario-spec (user manages their own VCS)

## Human Approval

- The `init` command is always explicitly invoked by a developer
- `--dry-run` shows what would be written before any files are touched

## Evidence

- Unit tests verify that preset output matches inline-write baseline
- `sicario verify` runs spec-compliance gates on CI

## Dependencies

- Task 1 (render.py) must complete before Tasks 3-4 (presets use _render)
- Tasks 3-4 (presets) must complete before Task 5 (refactor init)
- Task 5 (refactor init) is the final step before tests
