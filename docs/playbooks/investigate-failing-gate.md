---
title: "Playbook: Investigate a Failing Gate"
sidebar_label: "Investigate a Failing Gate"
guide-slug: investigate-failing-gate
captured-version: 0.6.0
reference-run-repository: refrun-rules/failing-app
reference-run-date: "2026-07-28"
---

# Playbook: Investigate a Failing Gate

## Scenario

Your CI check just went red on `sicario verify`. This playbook walks the
whole investigation: read the human output, map each finding code to its
meaning, switch to machine output, open the evidence file
(`generated/sicario/gate-summary.json`), read `scan_coverage` to learn what
was and was not scanned — including the difference between a file the policy
*excluded* and a file the scanner *could not read*, and what a
`SICARIO-FINDINGS-TRUNCATED` overflow means — then fix each cause and re-run
to green.

**Intended reader**: an engineer with a red check who wants to fix the cause,
not silence the finding.

## Output conventions

Every quoted output block carries a machine-readable marker declaring it
`verified` or `illustrative`. Verified blocks come from the reference run in
this page's front matter and are re-executable as-is against the staged
repository below. Illustrative blocks are visibly labeled; they are used
where counts depend on repository state (for example, file totals that
include `.git` internals).

Every step is a terminal interaction, captured as text per the terminal-text
capture class; the CI check that turned red is only this playbook's premise,
and no step directs you to a rendered page or run view, so this playbook
carries no screenshots (stated per the visual-asset policy). For wiring and
reading the check in CI itself, see the [CI playbook](wire-ci.md).

## Prerequisites and starting state

- Python 3.9+ and SicarioSpec 0.6.0. Commands use the module form
  `python3 -m sicario_cli.cli`; if `sicario` is on your PATH it is
  equivalent. `git` and a POSIX shell (bash or zsh) on macOS or Linux; on
  Windows use WSL.

The starting state is a repository staged to fail with several distinct
codes. To reconstruct it exactly (this is also how the reference run built
it): initialize a git repository, run
`python3 -m sicario_cli.cli init . --profile public-core`, add `generated/`
to `.gitignore`, and then:

1. Create a first spec from the shipped template:
   `mkdir -p specs/001-payment-webhooks && cp .specify/templates/spec-template.md specs/001-payment-webhooks/spec.md`,
   plus a trivial `src/webhooks.py`.
2. Add a project rule `.sicario/rules/210-todo-security.rule.json` that
   forbids unresolved security TODO markers (deliberately small caps so this
   playbook can show truncation):

   ```json
   {
     "id": "ACME-TODO-SECURITY",
     "severity": "medium",
     "kind": "regex-forbidden",
     "path": "src/**/*.py",
     "params": {
       "pattern": "TODO\\(security\\)",
       "max_findings_per_file": 5,
       "max_findings_per_rule": 50
     },
     "message": "Unresolved security TODO; file a tracked issue or fix before merge",
     "enabled": true
   }
   ```

3. Add a small binary file `assets/diagram.png` (any non-UTF-8 bytes) and a
   `build/` directory with one file in it.
4. Commit this state — `sicario verify .` passes on it — then stage three
   defects as working-tree changes, as if a bad branch arrived:
   delete the `## Misuse / Abuse Cases` section from
   `specs/001-payment-webhooks/spec.md`; delete
   `docs/security/threat-model.md`; and write `src/jobs.py` containing a
   function with nine `# TODO(security): validate signer for step N` comment
   lines (N from 0 to 8).

## Steps

### 1. Run the gate locally and read the human output

```bash
python3 -m sicario_cli.cli verify .
```

```text title="Verified output" sicario-output=verified sicario-block=investigate-failing-gate/01-red
HIGH SICARIO-MISSING-THREAT-MODEL docs/security/threat-model.md: Missing docs/security/threat-model.md
HIGH SICARIO-SPEC-SECTION specs/001-payment-webhooks/spec.md: spec.md missing required section: Abuse Cases
MEDIUM ACME-TODO-SECURITY src/jobs.py:2: Unresolved security TODO; file a tracked issue or fix before merge
MEDIUM ACME-TODO-SECURITY src/jobs.py:3: Unresolved security TODO; file a tracked issue or fix before merge
MEDIUM ACME-TODO-SECURITY src/jobs.py:4: Unresolved security TODO; file a tracked issue or fix before merge
MEDIUM ACME-TODO-SECURITY src/jobs.py:5: Unresolved security TODO; file a tracked issue or fix before merge
MEDIUM ACME-TODO-SECURITY src/jobs.py:6: Unresolved security TODO; file a tracked issue or fix before merge
MEDIUM SICARIO-FINDINGS-TRUNCATED: Findings truncated for ACME-TODO-SECURITY: reported 5 of 9 occurrence(s) across 1 file(s); 4 suppressed (truncation-scope: per-file; caps: per-file=5, per-rule=50)
sicario verify failed with 8 finding(s)
```

Exit code `1`. Eight findings across four distinct codes. Each finding line
has one anatomy:

```text title="Illustrative output (representative, not exact)" sicario-output=illustrative sicario-block=investigate-failing-gate/01-anatomy
SEVERITY CODE path:line: message
```

- `SEVERITY` (`CRITICAL`/`HIGH`/`MEDIUM`/`LOW`) ranks the finding for
  readers; **any** finding fails the gate regardless of severity.
- `CODE` is the stable identifier you map in step 2.
- `path:line` locates the cause; findings with no line concept (a missing
  file, a missing section) carry just the path, and the truncation finding
  carries no path at all.
- The message is the rule's static text — for `regex-forbidden` rules it
  never echoes the matched content, so output and evidence cannot leak what
  was matched.

Four distinct codes are in play: two shipped (`SICARIO-MISSING-THREAT-MODEL`,
`SICARIO-SPEC-SECTION`), one project-defined (`ACME-TODO-SECURITY`), and one
engine-emitted overflow (`SICARIO-FINDINGS-TRUNCATED`).

### 2. Map each code to its meaning

- **Shipped `SICARIO-*` codes** are documented in the finding-code tables of
  `USAGE.md` (repository root of SicarioSpec) and in the
  [rule engine reference](../rule-engine.md). Here:
  `SICARIO-MISSING-THREAT-MODEL` means `docs/security/threat-model.md` is
  missing; `SICARIO-SPEC-SECTION` means a spec lacks a required section — and
  the message names which (`Abuse Cases`).
- **Project codes** (anything not `SICARIO-*`, here `ACME-TODO-SECURITY`)
  are defined by your own repository. Find the defining rule file — the code
  is the rule's `id`:

  ```bash
  grep -rl "ACME-TODO-SECURITY" .sicario/rules/
  ```

  ```text title="Verified output" sicario-output=verified sicario-block=investigate-failing-gate/02-grep-rule
  .sicario/rules/210-todo-security.rule.json
  ```

  The rule file gives you the pattern, the target glob, the severity, and
  the caps — everything the finding meant.
- **`SICARIO-FINDINGS-TRUNCATED`** is not a defect of its own: it is the
  engine telling you a findings cap suppressed output. Step 5 reads it
  properly.

### 3. Switch to machine output when you need it

```bash
python3 -m sicario_cli.cli verify . --format json | head -20
```

```json title="Verified output" sicario-output=verified sicario-block=investigate-failing-gate/03-json
[
  {
    "severity": "high",
    "code": "SICARIO-MISSING-THREAT-MODEL",
    "message": "Missing docs/security/threat-model.md",
    "path": "docs/security/threat-model.md"
  },
  {
    "severity": "high",
    "code": "SICARIO-SPEC-SECTION",
    "message": "spec.md missing required section: Abuse Cases",
    "path": "specs/001-payment-webhooks/spec.md"
  },
  {
    "severity": "medium",
    "code": "ACME-TODO-SECURITY",
    "message": "Unresolved security TODO; file a tracked issue or fix before merge",
    "path": "src/jobs.py",
    "line": 2
  },
```

(`head -20` shows the first three of the eight entries; drop it to see the
full document.) Three things to know about the machine formats
(`--format json`, `--format sarif`):

- stdout carries **only** the document, so you can pipe it straight into
  `jq` or an uploader; the human summary line goes to stderr:

  ```text title="Verified output" sicario-output=verified sicario-block=investigate-failing-gate/03-stderr
  sicario verify failed with 8 finding(s)
  ```

- the exit code (`1` failing, `0` passing) is the authoritative verdict in
  every format — CI should gate on it, not on parsing text;
- `path` and `line` are separate fields, so paths stay resolvable file
  references for SARIF consumers.

### 4. Open the evidence file: findings versus scan coverage

Every run (any format) writes `generated/sicario/gate-summary.json`:

```bash
python3 -c "
import json
d = json.load(open('generated/sicario/gate-summary.json'))
print('status:', d['status']); print('finding_count:', d['finding_count'])
print('keys:', list(d.keys()))
print('scan_coverage keys:', list(d['scan_coverage'].keys()))
"
```

```text title="Verified output" sicario-output=verified sicario-block=investigate-failing-gate/04-summary-keys
status: fail
finding_count: 8
keys: ['generated_at_utc', 'status', 'finding_count', 'findings', 'scan_coverage']
scan_coverage keys: ['skipped_path_set', 'rules', 'disabled_rules', 'overrides', 'asset_root']
```

Two different kinds of content live here, and keeping them straight is the
core reading skill:

- **`findings`** is what the verdict is computed from — the same entries the
  CLI printed, as data. `status` and `finding_count` summarize it.
- **`scan_coverage`** is evidence about *how* the run scanned: per-rule
  coverage records, the fixed skipped-path policy, rules that were disabled,
  overrides of shipped rules, and where the shipped rules were loaded from
  (`asset_root`). Nothing in `scan_coverage` ever changes the verdict — it
  exists so a reviewer can see what a green or red verdict actually covered.

### 5. Read the truncation record: what a cap suppressed

The overflow finding said `reported 5 of 9`. The coverage record for the
truncated rule carries the exact accounting:

```bash
python3 -c "
import json
d = json.load(open('generated/sicario/gate-summary.json'))
recs = {r['rule_id']: r for r in d['scan_coverage']['rules']}
print(json.dumps(recs['ACME-TODO-SECURITY'], indent=2))
"
```

```json title="Verified output" sicario-output=verified sicario-block=investigate-failing-gate/05-truncation
{
  "rule_id": "ACME-TODO-SECURITY",
  "kind": "regex-forbidden",
  "target": "src/**/*.py",
  "files_scanned": 2,
  "files_skipped": 0,
  "skipped_files": [],
  "files_excluded": 0,
  "excluded_dirs": [],
  "excluded_dirs_total": 0,
  "excluded_dirs_truncated": false,
  "max_excluded_dirs_recorded": 50,
  "files_matched": 1,
  "total_occurrences": 9,
  "total_matches": 9,
  "findings_reported": 5,
  "occurrences_suppressed": 4,
  "truncated": true,
  "truncation_scopes": [
    "per-file"
  ],
  "max_findings_per_file": 5,
  "max_findings_per_rule": 50
}
```

How to read a `SICARIO-FINDINGS-TRUNCATED` situation:

- The caps (`max_findings_per_file`, `max_findings_per_rule` — defaults 20
  and 200; this rule sets 5 and 50) bound how many findings are *printed*,
  never how many are *counted*: `total_occurrences: 9` and
  `occurrences_suppressed: 4` are exact, because counting continues after
  emission stops.
- The overflow finding is mandatory and unsuppressible whenever anything was
  suppressed, and it inherits the truncated rule's severity — a cap can
  shorten output, but it cannot make suppression invisible or the run
  greener.
- Practically: do not fix five TODOs and expect green. The record says nine
  exist; fix the file, not the printed subset.

### 6. Excluded is a decision; skipped is a limitation

Now the coverage question a red (or green) gate always raises: what was
*not* scanned? Look at the record for the shipped secret-scan rule, whose
target is the whole tree:

```bash
python3 -c "
import json
d = json.load(open('generated/sicario/gate-summary.json'))
recs = {r['rule_id']: r for r in d['scan_coverage']['rules']}
r = recs['SICARIO-HARDCODED-SECRET']
keep = ('rule_id','target','files_scanned','files_skipped','skipped_files',
        'files_excluded','excluded_dirs','excluded_dirs_total')
print(json.dumps({k: r[k] for k in keep}, indent=2))
"
```

*Illustrative output — the shape and the named paths are exact for the staged
repository; file counts vary with repository state (the `.git` total in
particular).*

```json title="Illustrative output (representative, not exact)" sicario-output=illustrative sicario-block=investigate-failing-gate/06-coverage
{
  "rule_id": "SICARIO-HARDCODED-SECRET",
  "target": "**/*",
  "files_scanned": 118,
  "files_skipped": 1,
  "skipped_files": [
    "assets/diagram.png"
  ],
  "files_excluded": 161,
  "excluded_dirs": [
    {
      "path": ".git",
      "files": 158
    },
    {
      "path": "build",
      "files": 1
    },
    {
      "path": "generated",
      "files": 2
    }
  ],
  "excluded_dirs_total": 3
}
```

These are two different facts, kept deliberately separate:

- **`files_excluded` / `excluded_dirs` — a policy decision.** The fixed
  skipped-path set (recorded once per run as
  `scan_coverage.skipped_path_set`: `.git`, `.venv`, `node_modules`,
  `build`, `dist`, `generated`, and similar) excludes these directories
  before any read is attempted. Attribution is per excluded directory root
  with a file count, so you can *review* the decision: here `build/` and
  `generated/` are build products, exactly what the policy is for.
- **`files_skipped` / `skipped_files` — a scanner limitation.** These files
  were targeted and could not be read or decoded — here
  `assets/diagram.png`, a binary. Each one is listed by name so you can
  *investigate* it: a binary image is expected; your `.env`-style file
  appearing here would mean the scan you are relying on did not actually
  read it.

A file that was not scanned is never reported as if it had been cleared —
if either number is nonzero, you know precisely which files a green verdict
would say nothing about.

### 7. Fix each cause and watch the count fall

Fix in any order; re-run after each to see the finding disappear. The
reference run went:

Restore the deleted threat model (it is tracked, so restore from git — or
recreate it):

```bash
git restore docs/security/threat-model.md
python3 -m sicario_cli.cli verify . | tail -2
```

```text title="Verified output" sicario-output=verified sicario-block=investigate-failing-gate/07-fix1
MEDIUM SICARIO-FINDINGS-TRUNCATED: Findings truncated for ACME-TODO-SECURITY: reported 5 of 9 occurrence(s) across 1 file(s); 4 suppressed (truncation-scope: per-file; caps: per-file=5, per-rule=50)
sicario verify failed with 7 finding(s)
```

Restore the spec's deleted section (again from git; when writing a spec for
real, put the section back with real content):

```bash
git restore specs/001-payment-webhooks/spec.md
python3 -m sicario_cli.cli verify . | tail -2
```

```text title="Verified output" sicario-output=verified sicario-block=investigate-failing-gate/07-fix2
MEDIUM SICARIO-FINDINGS-TRUNCATED: Findings truncated for ACME-TODO-SECURITY: reported 5 of 9 occurrence(s) across 1 file(s); 4 suppressed (truncation-scope: per-file; caps: per-file=5, per-rule=50)
sicario verify failed with 6 finding(s)
```

Resolve the TODO markers — actually resolve them (do the work or file a
tracked issue and reference it), don't reword them into a spelling the
pattern misses. The reference run replaced `src/jobs.py` with a version
whose docstring references the tracking issue and contains no
`TODO(security)` markers. Then:

```bash
python3 -m sicario_cli.cli verify .
```

```text title="Verified output" sicario-output=verified sicario-block=investigate-failing-gate/07-green
sicario verify passed
```

Exit code `0`, and the evidence agrees:

```bash
python3 -c "
import json
d = json.load(open('generated/sicario/gate-summary.json'))
print('status:', d['status'], '| finding_count:', d['finding_count'])
"
```

```text title="Verified output" sicario-output=verified sicario-block=investigate-failing-gate/07-evidence
status: pass | finding_count: 0
```

### 8. If you cannot fix it now: the legitimate paths

Tempted to silence a finding instead? There are exactly two legitimate
paths, and "quietly disable the rule" is not one of them:

1. **Fix the cause** — everything above.
2. **Record an exception** — a row in `docs/risk/security-exceptions.md`
   with an owner, an expiry, an approval, and a compensating control, plus
   the rule change that implements it. Rule overrides and disables are
   *visible by construction*: every one is recorded in
   `scan_coverage.overrides` in the evidence file, disabled critical rules
   carry a `disables-critical-severity-rule` impact string reviewers grep
   for, and none of it changes the verdict in your favor invisibly. The
   [override playbook](override-shipped-rule.md) walks that evidence trail
   end to end — read it before narrowing or disabling anything.

## Success check

You have completed this playbook when:

1. You can name all four staged finding codes and where each was defined
   (shipped rule, project rule, or engine overflow).
2. `python3 -m sicario_cli.cli verify .` exits `0` and prints
   `sicario verify passed`, and `generated/sicario/gate-summary.json` shows
   `status: pass`, `finding_count: 0`.
3. From the evidence file alone you can state: how many occurrences the
   truncated rule really found (9), which file the scanner could not read
   (`assets/diagram.png`), and which directories policy excluded (`.git`,
   `build`, `generated`).

## Further reading

- [Declarative rule engine](../rule-engine.md) — finding-code semantics,
  caps and truncation, and the full coverage-record schema; the shipped
  finding-code tables are in `USAGE.md` at the SicarioSpec repository root.
- [Playbook: override a shipped rule](override-shipped-rule.md) — the
  evidence trail for narrowing or disabling a rule.
- [Playbook: add a custom project rule](custom-rule.md) — where project
  codes like `ACME-TODO-SECURITY` come from.
