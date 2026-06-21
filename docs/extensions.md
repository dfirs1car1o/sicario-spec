# Extensions

The first extension is `sicario-guard`.

Commands:

- `/sicario.init`
- `/sicario.assess`
- `/sicario.threatmodel`
- `/sicario.controls`
- `/sicario.evidence`
- `/sicario.verify`
- `/sicario.review`
- `/sicario.apply-findings`

The extension is designed for Spec Kit command discovery. The deterministic
local implementation lives in the `sicario` CLI.

## Hooks: executed vs. agent guidance

`extension.yml` registers hooks on `after_specify`, `after_plan`, and
`after_tasks`. These commands split into two honestly-labeled kinds:

| Hook command | Kind | What runs |
|---|---|---|
| `/sicario.verify` | deterministic | `sicario verify` (the halting gate) |
| `/sicario.assess` | deterministic | `sicario assess` |
| `/sicario.evidence` | deterministic | evidence/assessment generation |
| `/sicario.threatmodel` | agent guidance | a coding agent drafts the threat model |
| `/sicario.review` | agent guidance | a coding agent reviews the change |
| `/sicario.controls` | agent guidance | a coding agent updates control applicability |
| `/sicario.apply-findings` | agent guidance | a coding agent turns findings into tasks |

`sicario hooks` reads `.specify/extensions.yml`, **executes the deterministic
hooks**, and **reports the agent-guidance hooks** (with a pointer to their command
doc) instead of pretending to run them:

```bash
sicario hooks                  # all events
sicario hooks --event after_tasks
```

The authoritative pass/fail decision is always the deterministic verify gate, not
the AI-authoring steps.

