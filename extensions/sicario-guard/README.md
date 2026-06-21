# SicarioSpec Guard Extension

`sicario-guard` adds review, verification, threat-modeling, control mapping,
and evidence generation commands to Spec Kit.

The extension is intentionally deterministic-first. Commands may ask an AI agent
to draft or review, but authoritative pass/fail state comes from repository
files, validators, tests, and `sicario verify`.

## How the hooks actually run

The `after_specify` / `after_plan` / `after_tasks` entries in `extension.yml`
and the generated `.specify/extensions.yml` are of two kinds, and SicarioSpec is
explicit about which is which:

- **Deterministic hooks** (`sicario.verify`, `sicario.assess`, `sicario.evidence`)
  are backed by the `sicario` CLI and are executed by `sicario hooks`.
- **Agent-guidance hooks** (`sicario.threatmodel`, `sicario.review`,
  `sicario.controls`, `sicario.apply-findings`) are prompt instructions for a
  coding agent. SicarioSpec does **not** execute these; `sicario hooks` reports
  them and points to the command doc so a human or agent performs the work.

Run the wired hooks for a project:

```bash
sicario hooks                 # run all events
sicario hooks --event after_tasks
```

This keeps the contract honest: the gate that decides pass/fail is code, and the
AI-authoring steps are clearly labeled as agent guidance rather than silently
unexecuted automation.

