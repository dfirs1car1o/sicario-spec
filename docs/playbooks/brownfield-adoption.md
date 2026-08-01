---
title: "Playbook: Adopt SicarioSpec in a Brownfield Repository"
sidebar_label: "Brownfield adoption"
guide-slug: brownfield-adoption
captured-version: 0.6.0
reference-run-repository: refrun-rules/brownfield-app
reference-run-date: "2026-07-28"
---

# Playbook: Adopt SicarioSpec in a Brownfield Repository

## Scenario

You maintain a repository that already has governance: a project constitution,
Spec Kit templates, and agent-instruction files such as `CLAUDE.md`. You want
SicarioSpec's gate and evidence without losing a line of what you already
wrote. This playbook walks the overlay-not-clobber contract end to end:
preview with `--dry-run`, adopt for real, inspect what was merged and what was
preserved, confirm the backups can never be committed, and re-run `init` to
see that adoption converges to a no-op.

**Intended reader**: an engineer adopting SicarioSpec into an existing
repository. No prior SicarioSpec experience is assumed beyond having the CLI
installed.

## Output conventions

Every quoted output block in this playbook carries a machine-readable marker
declaring it `verified` or `illustrative`:

- **verified** — captured from the reference run named in this page's front
  matter and re-executable as-is. The only rewrites applied are the documented
  normalizations listed in the marker: `paths` (the reference-run directory is
  shown as `~/refrun-rules/brownfield-app`, and the SicarioSpec install
  location as `<install-root>`).
- **illustrative** — representative of the shape you will see, visibly labeled
  as such, used where output contains environment-dependent values (absolute
  paths, backup timestamps, your `specify` version).

Every step in this playbook is a terminal interaction, captured as text per
the terminal-text capture class. No step surfaces a graphical view, so this
playbook carries no screenshots (stated per the visual-asset policy).

## Prerequisites and starting state

- Python 3.9+ and SicarioSpec 0.6.0. Commands below use the module form
  `python3 -m sicario_cli.cli`, which works on every install; if the `sicario`
  command is on your PATH, `sicario init` / `sicario verify` are equivalent.
- `git`, and a POSIX shell (bash or zsh) on macOS or Linux. On Windows, use
  WSL; native path separators and prompts will differ.

The starting state is a git repository with pre-existing governance. To
reconstruct it exactly, the reference run seeded a repository containing
`README.md`, `src/app.py`, a `.gitignore` (`__pycache__/`, `*.pyc`), and
these three governance files, all committed:

`.specify/memory/constitution.md` — the project's own constitution:

```markdown sicario-write=.specify/memory/constitution.md
# payments-api Constitution

## Principle I — Boring Technology
We choose proven components over novel ones.

## Principle II — Reviewed Changes
Every change lands through a reviewed pull request.
```

`.specify/templates/spec-template.md` — the project's own minimal template:

```markdown sicario-write=.specify/templates/spec-template.md
# Feature Spec: [NAME]

## Problem

## Approach

## Rollout
```

and `CLAUDE.md` — agent instructions:

```markdown sicario-write=CLAUDE.md
Prefer small, reviewable diffs. Never commit generated artifacts.
```

The remaining seed files (their content is not asserted by anything below):

```bash sicario-cmd=setup
printf '# payments-api\n' > README.md
mkdir -p src
printf 'def main():\n    pass\n' > src/app.py
printf '__pycache__/\n*.pyc\n' > .gitignore
```

## Steps

### 1. Preview the adoption with `--dry-run`

Always preview first. The dry run detects your existing governance, chooses a
per-file plan, and writes nothing.

```bash
python3 -m sicario_cli.cli init . --profile public-core --dry-run
```

*Illustrative output — excerpted; absolute paths and your `specify` version
vary by environment.*

```text title="Illustrative output (representative, not exact)" sicario-output=illustrative sicario-block=brownfield-adoption/01-dry-run
target ~/refrun-rules/brownfield-app
specify specify 0.11.8
integration claude
presets sicario-core, sicario-docs
detected existing governance: constitution=['.specify/memory/constitution.md']; templates=['.specify/templates/spec-template.md']; instructions=['CLAUDE.md']
mode: brownfield-safe (merge/overlay/preserve)
append ignore rule *.sicario-bak.* to ~/refrun-rules/brownfield-app/.gitignore
copy <install-root>/presets/sicario-core -> ~/refrun-rules/brownfield-app/.specify/presets/sicario-core
...
overlay ~/refrun-rules/brownfield-app/.specify/memory/constitution.md

SicarioSpec adoption report (dry-run preview — nothing written)
---------------------------------------------------------------
  [merged-overlaid] ~/refrun-rules/brownfield-app/.gitignore — appended ignore rule *.sicario-bak.*
  [created] ~/refrun-rules/brownfield-app/.specify/presets/sicario-core
  [merged-overlaid] ~/refrun-rules/brownfield-app/.specify/templates/spec-template.md — appended overlay
  [merged-overlaid] ~/refrun-rules/brownfield-app/.specify/memory/constitution.md — appended overlay
  [merged-overlaid] ~/refrun-rules/brownfield-app/CLAUDE.md — appended overlay
  ...
  summary: 33 created, 4 merged-overlaid
dry-run complete; no files written
```

Read the plan through the three per-file states:

- **created** — the file does not exist in your repository; SicarioSpec will
  write it new. Nothing of yours is involved.
- **merged-overlaid** — the file exists and SicarioSpec knows how to extend it
  additively: your content stays verbatim, a clearly delimited overlay block
  is appended, and a backup is taken first.
- **preserved** — the file exists and SicarioSpec cannot safely merge it, so
  it is left untouched and reported. (You will see this state on re-runs in
  step 5; `--force` is the explicit opt-in to full overwrite instead, and it
  still takes backups first.)

Note the detection line: your constitution, your template, and `CLAUDE.md`
were all found, and the mode switched to `brownfield-safe
(merge/overlay/preserve)`. In an empty directory the same command reports
`mode: greenfield (no existing governance detected)`.

### 2. Adopt for real

```bash sicario-cmd=setup
python3 -m sicario_cli.cli init . --profile public-core
```

*Illustrative output — final lines shown; the full report matches the dry-run
plan.*

```text title="Illustrative output (representative, not exact)" sicario-output=illustrative sicario-block=brownfield-adoption/02-init
  summary: 33 created, 4 merged-overlaid
SicarioSpec initialized at ~/refrun-rules/brownfield-app
Next: cd into the project and run `sicario verify`.
```

### 3. Inspect the overlay: your content is untouched above the markers

```bash sicario-cmd=brownfield-adoption/03-overlay
sed -n '1,16p' .specify/memory/constitution.md
```

```text title="Verified output" sicario-output=verified sicario-block=brownfield-adoption/03-overlay
# payments-api Constitution

## Principle I — Boring Technology
We choose proven components over novel ones.

## Principle II — Reviewed Changes
Every change lands through a reviewed pull request.

<!-- BEGIN SICARIO-SPEC OVERLAY (additive; do not edit by hand) -->

## SicarioSpec Governance Overlay (Additive)

This section was appended by `sicario init`/`apply` as an ADDITIVE governance
overlay. Your existing constitution above is unchanged and remains authoritative.

This overlay is SUBORDINATE to the existing principles above and to `CLAUDE.md`. Where any conflict exists, the project's own principles and `mission.md` (or equivalent project-supremacy clause) WIN.
```

Your constitution is byte-for-byte intact above the
`BEGIN SICARIO-SPEC OVERLAY` marker, and the overlay itself states that it is
subordinate to your existing principles and to the instruction files it
detected (`CLAUDE.md` here). The overlay ends with an
`<!-- END SICARIO-SPEC OVERLAY -->` marker:

```bash sicario-cmd=brownfield-adoption/03-markers
grep -n "SICARIO-SPEC OVERLAY" .specify/memory/constitution.md
```

```text title="Verified output" sicario-output=verified sicario-block=brownfield-adoption/03-markers
9:<!-- BEGIN SICARIO-SPEC OVERLAY (additive; do not edit by hand) -->
39:<!-- END SICARIO-SPEC OVERLAY -->
```

The same marker pair delimits the overlays appended to `CLAUDE.md` and
`.specify/templates/spec-template.md` — run the same `grep -n` against each
to see them.

### 4. Backups exist — and cannot be committed

Every merged file was backed up first, as a timestamped sibling:

```bash
ls .specify/memory/
```

*Illustrative output — the UTC timestamp in the backup name is taken at run
time.*

```text title="Illustrative output (representative, not exact)" sicario-output=illustrative sicario-block=brownfield-adoption/04-backups
constitution.md
constitution.md.sicario-bak.20260728T204506Z
```

Backups are verbatim copies of your pre-existing files, which may contain
things that were never meant to be committed. So before the first backup was
taken, `init` appended an ignore rule to your `.gitignore` (your existing
entries untouched):

```bash sicario-cmd=brownfield-adoption/04-gitignore
cat .gitignore
```

```text title="Verified output" sicario-output=verified sicario-block=brownfield-adoption/04-gitignore
__pycache__/
*.pyc

# SicarioSpec timestamped backups (may contain pre-existing secrets)
*.sicario-bak.*
```

Confirm git actually ignores them — `git check-ignore -v` names the deciding
rule, and no backup appears in `git status`:

```bash
git check-ignore -v .specify/memory/constitution.md.sicario-bak.*
git status --short | grep sicario-bak
```

*Illustrative output — timestamped file name varies; the second command prints
nothing (and exits 1) because no backup is unignored.*

```text title="Illustrative output (representative, not exact)" sicario-output=illustrative sicario-block=brownfield-adoption/04-check-ignore
.gitignore:5:*.sicario-bak.*	.specify/memory/constitution.md.sicario-bak.20260728T204506Z
```

`init` is careful here: if your `.gitignore` already contains the rule it is
left alone, and if a later negation (`!something.sicario-bak...`) re-includes
backups, the rule is re-appended so the last matching pattern wins again.

### 5. Re-run to confirm adoption converges

Run the same `init` command again:

```bash
python3 -m sicario_cli.cli init . --profile public-core
```

*Illustrative output — summary lines shown.*

```text title="Illustrative output (representative, not exact)" sicario-output=illustrative sicario-block=brownfield-adoption/05-rerun
gitignore already ignores *.sicario-bak.*
overlay already present in ~/refrun-rules/brownfield-app/.specify/templates/plan-template.md
overlay already present in ~/refrun-rules/brownfield-app/.specify/templates/spec-template.md
overlay already present in ~/refrun-rules/brownfield-app/.specify/templates/tasks-template.md
overlay already present in ~/refrun-rules/brownfield-app/.specify/memory/constitution.md
...
  summary: 37 preserved
```

Nothing you own is touched again, and nothing SicarioSpec wrote is touched
again either: files with the overlay marker report `overlay already present`,
directories report `skip existing`, and generated files report `preserve
existing`. The re-run converges immediately — the very first re-run after
adoption reports `37 preserved` with zero new backups, and every run after
that reports exactly the same thing:

*Illustrative output — third run's summary line, identical to the second.*

```text title="Illustrative output (representative, not exact)" sicario-output=illustrative sicario-block=brownfield-adoption/05-third-run
  summary: 37 preserved
```

No new backups are taken on any re-run after adoption.

> **Pre-0.6.1 adopters**: before this fix, `init` wrote `plan-template.md` and
> `tasks-template.md` (and, on a greenfield init, every Spec Kit template and
> the constitution) without stamping the overlay marker onto them, so the
> *first* re-run mistook those files for pre-existing content, appended the
> overlay block on top, and took a backup — reporting `2 merged-overlaid, 35
> preserved` instead of `37 preserved`. Only the *second* re-run (the
> project's third `init`) was a true no-op. If you adopted before 0.6.1, your
> next re-run will do that one-time overlay-and-backup pass; every run after
> that converges like the one shown above.

### 6. Run the gate

```bash sicario-cmd=brownfield-adoption/06-verify
python3 -m sicario_cli.cli verify .
```

```text title="Verified output" sicario-output=verified sicario-block=brownfield-adoption/06-verify
sicario verify passed
```

Exit code `0`. The adopted repository passes because `init` created every
document the shipped rules require (threat model, risk registers, data
classification, control maps, and the rest) while preserving yours.

## Success check

You are done when all of the following hold:

1. `python3 -m sicario_cli.cli verify .` prints `sicario verify passed` and
   exits `0`.
2. `git diff` on `.specify/memory/constitution.md`, `CLAUDE.md`, and
   `.specify/templates/spec-template.md` shows only appended
   `SICARIO-SPEC OVERLAY` blocks (plus the `.gitignore` rule) — none of your
   original lines changed.
3. `git status --short | grep sicario-bak` prints nothing: every backup
   exists on disk but is uncommittable.
4. Re-running `init` reports `preserved` / `overlay already present` rather
   than taking new backups.

## Further reading

- [Playbook: add a custom project rule](custom-rule.md) — your first
  project-owned gate in the adopted repository.
- [Playbook: override a shipped rule](override-shipped-rule.md) — narrowing
  shipped rules to fit a brownfield layout, with the evidence that records it.
- [Declarative rule engine](../rule-engine.md) — reference for everything the
  gate enforces.
