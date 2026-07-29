---
title: "Playbook: Override a Shipped Rule and Read the Evidence It Produces"
sidebar_label: "Override a shipped rule"
guide-slug: override-shipped-rule
captured-version: 0.6.0
reference-run-repository: refrun-rules/override-app
reference-run-date: "2026-07-28"
---

# Playbook: Override a Shipped Rule and Read the Evidence It Produces

## Scenario

A shipped rule fires on content your team has decided is acceptable — here,
the critical secret scan firing on a test fixture that carries a deliberately
fake, credential-shaped placeholder. You will override the shipped rule by
reusing its `id`: first narrowing its path, then (to see the evidence trail)
disabling it outright. After each change you will open
`generated/sicario/gate-summary.json` and read the override record the run
wrote, including the `disables-critical-severity-rule` impact string a
reviewer greps for.

One sentence to carry through the whole playbook: **overriding never changes
the verdict — the gate's control here is visibility, not prohibition.** An
override is a documented, legitimate action; performing one *invisibly* is
what the evidence exists to prevent.

**Intended reader**: a platform or security engineer tuning shipped rules,
and the reviewer who must later answer "was anything weakened?"

## Output conventions

Every quoted output block carries a machine-readable marker declaring it
`verified` or `illustrative`. Verified blocks come from the reference run in
this page's front matter and are re-executable as-is; the only rewrites
applied where marked are the documented normalizations `paths` (reference-run
directory shown as `~/refrun-rules/override-app`) and `line-numbers` (a line
number inside a grepped evidence file, which shifts with repository state).
Illustrative blocks are visibly labeled and representative rather than exact.

Every step is a terminal interaction, captured as text per the terminal-text
capture class; no step surfaces a graphical view, so this playbook carries no
screenshots (stated per the visual-asset policy).

## Prerequisites and starting state

- Python 3.9+ and SicarioSpec 0.6.0. Commands use the module form
  `python3 -m sicario_cli.cli`; if `sicario` is on your PATH it is equivalent.
- A POSIX shell (bash or zsh) on macOS or Linux; on Windows use WSL.
- Starting state: a repository freshly initialized with
  `python3 -m sicario_cli.cli init . --profile public-core`, where
  `python3 -m sicario_cli.cli verify .` passes.

How overriding works: rules load from the shipped directory first, then from
the project's `.sicario/rules/`, and **for a given `id` the last rule file
loaded wins**. `sicario init` copies every shipped rule verbatim into
`.sicario/rules/`, and a byte-equivalent copy is *not* an override — it
changes nothing, so it is not recorded. The moment you edit your copy so it
differs from the shipped definition, your definition wins and the run records
an override. Confirm the clean baseline:

```bash
python3 -c "
import json
d = json.load(open('generated/sicario/gate-summary.json'))
print(json.dumps(d['scan_coverage']['overrides']))
"
```

```text title="Verified output" sicario-output=verified sicario-block=override-shipped-rule/00-baseline
[]
```

## Steps

### 1. Reproduce the problem: a fixture trips the shipped secret scan

Create a fixture whose value is a placeholder, not a working credential —
built here with `printf` so the fake value is assembled at run time:

```bash
mkdir -p tests/fixtures
printf 'password = "%s"\n' "placeholder-fixture-value" > tests/fixtures/sample-config.yaml
python3 -m sicario_cli.cli verify .
```

```text title="Verified output" sicario-output=verified sicario-block=override-shipped-rule/01-red
CRITICAL SICARIO-HARDCODED-SECRET tests/fixtures/sample-config.yaml:1: Potential hardcoded secret
sicario verify failed with 1 finding(s)
```

Exit code `1`. The shipped rule `SICARIO-HARDCODED-SECRET`
(`.sicario/rules/040-secret-scan.rule.json`, severity `critical`, target
`**/*`) matches credential-shaped assignments anywhere in the tree —
including fixtures that are fake on purpose.

### 2. Narrow the rule by reusing its id

Edit your project copy, `.sicario/rules/040-secret-scan.rule.json`, changing
only the `path` so the scan covers first-party source instead of the whole
tree:

```json
"path": "src/**/*",
```

Leave `id`, `severity`, `kind`, `params`, and `message` exactly as shipped.
Re-run:

```bash
python3 -m sicario_cli.cli verify .
```

```text title="Verified output" sicario-output=verified sicario-block=override-shipped-rule/02-green
sicario verify passed
```

Understand what you traded before moving on: `src/**/*` stops scanning
`docs/`, configuration, and everything else outside `src/` — narrowing a
critical rule is a real reduction in coverage, which is exactly why the next
step exists.

### 3. Read the override record

```bash
python3 -c "
import json
d = json.load(open('generated/sicario/gate-summary.json'))
print(json.dumps(d['scan_coverage']['overrides'], indent=2))
"
```

```json title="Verified output" sicario-output=verified sicario-block=override-shipped-rule/03-record
[
  {
    "rule_id": "SICARIO-HARDCODED-SECRET",
    "winning_origin": "project",
    "winning_file": "040-secret-scan.rule.json",
    "superseded_origin": "shipped",
    "superseded_file": "040-secret-scan.rule.json",
    "changed": [
      "path"
    ],
    "material": true,
    "enabled": {
      "from": true,
      "to": true
    },
    "severity": {
      "from": "critical",
      "to": "critical"
    },
    "original_severity": "critical",
    "disables_rule": false,
    "impact": "modifies-critical-severity-rule",
    "details": {
      "path": {
        "from": "**/*",
        "to": "src/**/*"
      }
    }
  }
]
```

Field by field, the way a reviewer reads it:

- **`winning_origin` / `winning_file`** — where the definition now in effect
  lives (`project`, your `.sicario/rules/` file). **`superseded_origin` /
  `superseded_file`** — what it replaced (`shipped`). The verbatim init
  copies are exempt from recording, so `superseded_origin` correctly says
  `shipped`, not "the project's own copy".
- **`changed`** — the fields whose values differ; here only `path`.
- **`material`** — `true` because `path` changes what the rule *enforces*. A
  reworded `message` alone would be `material: false`, so cosmetic edits are
  distinguishable from policy changes without diffing rule files by hand.
- **`details`** — the actual change, from/to, for the fields names alone
  cannot convey. `"**/*"` → `"src/**/*"` is the whole story of this override;
  a params/pattern change would be shown the same way.
- **`original_severity`** — the severity this id was *first* defined with
  (the shipped severity). `impact` is ranked against it, so a chain of
  overrides that demotes a rule before changing it cannot launder the impact
  string.
- **`impact`** — the one-glance summary: `modifies-critical-severity-rule`.
  Grep-friendly by design.

Note the verdict: the run **passed** with this record present. The override
did not fail the gate and never will — it is evidence for review, not a
finding.

### 4. Confirm the narrowed rule still enforces its remaining scope

```bash
printf 'password = "%s"\n' "placeholder-not-a-real-value" > src/settings.py
python3 -m sicario_cli.cli verify .
```

```text title="Verified output" sicario-output=verified sicario-block=override-shipped-rule/04-src-covered
CRITICAL SICARIO-HARDCODED-SECRET src/settings.py:1: Potential hardcoded secret
sicario verify failed with 1 finding(s)
```

The rule is alive inside `src/**/*`. Remove the probe file
(`rm src/settings.py`) before continuing.

### 5. The disable case — and the reviewer's grep

Now the version of this action a reviewer most needs to catch: turning the
rule off. Restore your copy to the shipped content first (the pristine copy
is staged in your own repository), then set `"enabled": false` in it:

```bash
cp .specify/presets/sicario-core/rules/040-secret-scan.rule.json .sicario/rules/040-secret-scan.rule.json
```

Edit `.sicario/rules/040-secret-scan.rule.json` so `"enabled": false`, then:

```bash
python3 -m sicario_cli.cli verify .
```

```text title="Verified output" sicario-output=verified sicario-block=override-shipped-rule/05-disabled-green
sicario verify passed
```

Look at what just happened: the credential-shaped fixture from step 1 is
still in the tree, and the gate is green — a red gate made green by turning
the check off. Nothing in the verdict distinguishes this from a clean
repository. The evidence does:

```bash
python3 -c "
import json
d = json.load(open('generated/sicario/gate-summary.json'))
print(json.dumps(d['scan_coverage']['overrides'], indent=2))
print('disabled_rules:', json.dumps(d['scan_coverage']['disabled_rules']))
"
```

```json title="Verified output" sicario-output=verified sicario-block=override-shipped-rule/05-disable-record
[
  {
    "rule_id": "SICARIO-HARDCODED-SECRET",
    "winning_origin": "project",
    "winning_file": "040-secret-scan.rule.json",
    "superseded_origin": "shipped",
    "superseded_file": "040-secret-scan.rule.json",
    "changed": [
      "enabled"
    ],
    "material": true,
    "enabled": {
      "from": true,
      "to": false
    },
    "severity": {
      "from": "critical",
      "to": "critical"
    },
    "original_severity": "critical",
    "disables_rule": true,
    "impact": "disables-critical-severity-rule",
    "details": {}
  }
]
disabled_rules: [{"id": "SICARIO-HARDCODED-SECRET", "severity": "critical", "kind": "regex-forbidden"}]
```

`disables_rule: true`, and the impact string is now
`disables-critical-severity-rule` — disabling never reads like narrowing.
The rule also appears in `disabled_rules`, the list of loaded-but-not-run
rules, carrying its *original* severity. This is the one-line search a
reviewer (or CI annotation) runs across evidence:

```bash
grep -rn "disables-critical" generated/
```

```text title="Verified output" sicario-output=verified sicario-block=override-shipped-rule/05-grep sicario-normalize=line-numbers
generated/sicario/gate-summary.json:130:        "impact": "disables-critical-severity-rule",
```

One command, one answer to "was anything weakened".

### 6. If an override is to stay, it needs an exception record

Because overrides never fail the gate, the accountability lives in review and
in the exception register — not in the verdict. A narrowing or disable that
remains in the repository should be recorded in
`docs/risk/security-exceptions.md` (created by `init`), which requires an
owner, an expiry, an approval, and a compensating control:

```bash
grep -A2 "| Exception ID" docs/risk/security-exceptions.md
```

```text title="Verified output" sicario-output=verified sicario-block=override-shipped-rule/06-register
| Exception ID | Status | Control / Gate | Owner | Expires | Approval | Compensating Control | Evidence |
|---|---|---|---|---|---|---|---|
| EXC-001 | open | SICARIO-MISSING-THREAT-MODEL — threat-model section required | Maintainers | 2027-01-01 | TBD | External threat-modeling process documented | generated/sicario/gate-summary.json |
```

Add a row for your override on the same pattern, pointing its Evidence cell
at `generated/sicario/gate-summary.json` — the file that carries the override
record you just read. Disablement presented without this trail is not a
remedy; it is the anti-pattern the evidence exists to expose.

### 7. End state for this walkthrough: restore and fix properly

For this playbook's fixture there is a better fix than any override: make the
placeholder not credential-shaped at all. Restore the shipped rule and
replace the fixture value with a short angle-bracket placeholder:

```bash
cp .specify/presets/sicario-core/rules/040-secret-scan.rule.json .sicario/rules/040-secret-scan.rule.json
printf 'password = "%s"\n' "<from-env>" > tests/fixtures/sample-config.yaml
python3 -m sicario_cli.cli verify .
python3 -c "
import json
d = json.load(open('generated/sicario/gate-summary.json'))
print('overrides:', json.dumps(d['scan_coverage']['overrides']))
print('disabled_rules:', json.dumps(d['scan_coverage']['disabled_rules']))
print('status:', d['status'])
"
```

```text title="Verified output" sicario-output=verified sicario-block=override-shipped-rule/07-end
sicario verify passed
overrides: []
disabled_rules: []
status: pass
```

Full scan coverage restored, no overrides in effect, and the fixture now
teaches the safe habit: real values belong in the environment or a secret
store, never in the file.

## Success check

You have completed this playbook when:

1. You produced (and read) both override records: `changed: ["path"]` with
   `impact: modifies-critical-severity-rule`, and `changed: ["enabled"]`
   with `disables_rule: true` and
   `impact: disables-critical-severity-rule`.
2. `grep -rn "disables-critical" generated/` found the disable record while
   it was in effect.
3. You can state, without hedging, that every one of those runs **passed** —
   overrides are visible in `scan_coverage.overrides`, never in the verdict.
4. The end state is green with `overrides: []` and `disabled_rules: []`.

## Further reading

- [Declarative rule engine](../rule-engine.md) — the precedence contract,
  override evidence fields, and the no-op exemption in full.
- [Playbook: add a custom project rule](custom-rule.md) — new rules rather
  than modified shipped ones.
- [Playbook: investigate a failing gate](investigate-failing-gate.md) — the
  fix-first path this playbook's evidence discipline backs up.
