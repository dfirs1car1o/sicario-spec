---
title: "Playbook: Read Gate Evidence as a Reviewer"
sidebar_label: "Read evidence as a reviewer"
guide-slug: read-evidence-as-reviewer
captured-version: 0.6.0
reference-run-repository: refrun-reviewer
reference-run-date: "2026-07-28"
---

# Playbook: Read Gate Evidence as a Reviewer

## Scenario and intended reader

You are reviewing a change — or auditing a repository — and someone hands
you a green gate: `sicario verify passed`. Your job is to answer, **from
artifacts alone**, two questions: *what did this gate actually check*, and
*was anything weakened*. This playbook walks `gate-summary.json` field by
field: the verdict, the override records (including the one that disables a
critical rule), which rules did not run, where the shipped rules were loaded
from, and what was excluded from scanning.

Intended reader: a reviewer, security engineer, or auditor. You do not need
to run the gate, and you do not need the repository's toolchain — only the
evidence file. Commands below use `python3` and `grep` to read it; any JSON
viewer works.

## Starting state

- A `generated/sicario/gate-summary.json` produced by `sicario verify` at
  SicarioSpec 0.6.0. (Each verify run rewrites it in the scanned
  repository; in CI it lives in the runner workspace unless uploaded — see
  [Wire the gate into CI](./wire-ci.md).)
- The evidence quoted below comes from a reference repository containing
  exactly two reviewer-relevant facts, staged so you can see what each
  looks like: a project rule override that disables the shipped critical
  secret-scan rule, and one vendored directory (`node_modules/`) excluded
  from scanning by policy.
- A shell with `python3` and `grep`.

Reconstructed exactly (this is also what the docs verification runner does —
see FR-051): an `appsec`-profile init, one vendored file under
`node_modules/`, and a project rule reusing the shipped
`SICARIO-HARDCODED-SECRET` id with `"enabled": false`.

```bash sicario-cmd=setup
python3 -m sicario_cli.cli init . --profile appsec
mkdir -p node_modules/left-pad
printf 'module.exports = function leftPad() {};\n' > node_modules/left-pad/index.js
python3 - <<'PY'
import json

rule = {
    "id": "SICARIO-HARDCODED-SECRET",
    "severity": "critical",
    "kind": "regex-forbidden",
    "path": "**/*",
    "params": {
        "pattern": "(?i)\\b(api[_-]?key|secret|token|password)\\b\\s*[:=]\\s*['\"][^'\"]{12,}['\"]"
    },
    "message": "Potential hardcoded secret",
    "enabled": False,
}
with open(".sicario/rules/zzz-disable-secret-scan.rule.json", "w") as f:
    json.dump(rule, f, indent=2)
    f.write("\n")
PY
python3 -m sicario_cli.cli verify .
```

## Steps

### 1. Read the verdict — then distrust it politely

```bash sicario-cmd=read-evidence-as-reviewer/step-1
python3 -c "
import json
d = json.load(open('generated/sicario/gate-summary.json'))
print(d['status'], d['finding_count'])"
```

```text title="Verified output" sicario-output=verified sicario-block=read-evidence-as-reviewer/step-1
pass 0
```

The top-level fields are `generated_at_utc`, `status` (`pass`/`fail`),
`finding_count`, `findings`, and `scan_coverage`. Each entry in `findings`
carries `severity`, `code`, `message`, `path`, and — for content findings —
`line`. A failing run is easy to review: the findings are in front of you.
A **passing** run is where this playbook earns its keep, because
`status: pass` says only that no *enabled* rule fired on the files that
were *scanned*. Steps 2–5 establish both italicized qualifiers. Everything
you need is under `scan_coverage`; none of it feeds the verdict — it exists
so the verdict can be judged.

### 2. Hunt for weakened rules: the override records

A project may replace a shipped rule by reusing its `id` — legitimately, to
narrow a noisy rule, or illegitimately, to switch off the secret scan. The
gate does not forbid it; it records it, in `scan_coverage.overrides`. Start
with the one-line search a reviewer should run on any evidence file:

```bash sicario-cmd=read-evidence-as-reviewer/step-2a
grep -Hn "disables-critical" generated/sicario/gate-summary.json
```

```text title="Verified output" sicario-output=verified sicario-block=read-evidence-as-reviewer/step-2a sicario-normalize=line-numbers
generated/sicario/gate-summary.json:130:        "impact": "disables-critical-severity-rule",
```

A hit means a rule whose original severity is `critical` is now turned
off. (Across a fleet, run the same grep over every collected evidence file
— `grep -rn "disables-critical" <evidence-dir>` — it is cheap and it is
the needle that matters most.) Now read the full record:

```bash sicario-cmd=read-evidence-as-reviewer/step-2b
python3 -c "
import json
d = json.load(open('generated/sicario/gate-summary.json'))
print(json.dumps(d['scan_coverage']['overrides'], indent=2))"
```

```json title="Verified output" sicario-output=verified sicario-block=read-evidence-as-reviewer/step-2b
[
  {
    "rule_id": "SICARIO-HARDCODED-SECRET",
    "winning_origin": "project",
    "winning_file": "zzz-disable-secret-scan.rule.json",
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
```

How to read it, field by field:

- **`winning_origin` / `winning_file`** — where the definition now in
  effect lives. `project` + a file name means the winning definition is in
  the repository's own `.sicario/rules/` directory: open that exact file
  in the diff you are reviewing.
- **`superseded_origin` / `superseded_file`** — what it replaced; here the
  shipped `040-secret-scan.rule.json`.
- **`changed`** — every field whose value differs. **`material`** is
  `true` when any changed field alters what the rule enforces (`enabled`,
  `severity`, `kind`, `path`, `params`); a `material: false` record is a
  cosmetic edit (a reworded message) and needs no alarm.
- **`enabled` / `severity`** — from/to values, so a demote-and-disable
  cannot hide inside a one-word diff.
- **`original_severity`** — the anchor: the severity of the *first*
  definition ever loaded for this id (the shipped severity when a shipped
  rule exists). The `impact` string is ranked against it, so a chain of
  override files that demotes a rule in one file and disables it in
  another still reads `disables-critical-severity-rule`, never a laundered
  `disables-low-severity-rule`.
- **`impact`** — the greppable summary: `disables-` or `modifies-` plus
  the anchored severity.
- **`details`** — for `path`, `kind`, and `params` changes, the actual
  from/to values. Empty here because only `enabled` changed. When a
  `params.pattern` change appears, read it: the gate will not judge
  whether a regex change is a narrowing or a neutering, so the reviewer
  must.

What this record means for your review: this run's green verdict was
produced **with the critical secret scan turned off**. That is approvable
only with a recorded exception — an entry with an owner and an expiry in
the repository's exception register (`docs/risk/security-exceptions.md` in
initialized repositories) — never as an unexplained convenience. The
override workflow and its evidence trail are walked end-to-end in the
[Override a shipped rule](override-shipped-rule.md) playbook in this section.

### 3. See which rules did not run

```bash sicario-cmd=read-evidence-as-reviewer/step-3
python3 -c "
import json
d = json.load(open('generated/sicario/gate-summary.json'))
print(json.dumps(d['scan_coverage']['disabled_rules'], indent=2))"
```

```json title="Verified output" sicario-output=verified sicario-block=read-evidence-as-reviewer/step-3
[
  {
    "id": "SICARIO-HARDCODED-SECRET",
    "severity": "critical",
    "kind": "regex-forbidden"
  }
]
```

`disabled_rules` answers a different question than `overrides`:
*which rules did not run at all* (versus *who changed them and how*). The
`severity` shown is the **original** severity — anchored the same way as
`impact` — so a disabled critical rule reads `critical` here even if the
disabling definition also rewrote the severity field. Cross-check the two
lists: every disabled rule should be explained either by an override
record you have judged, or by a deliberate, documented project decision.

### 4. Check where the shipped rules came from: `asset_root`

```bash
python3 -c "
import json
d = json.load(open('generated/sicario/gate-summary.json'))
print(json.dumps(d['scan_coverage']['asset_root'], indent=2))"
```

```json title="Illustrative output (representative, not exact — paths are machine-specific)" sicario-output=illustrative sicario-block=read-evidence-as-reviewer/step-4
{
  "path": "~/tools/sicario-spec",
  "env_value": null,
  "env_override_set": false,
  "env_override_honored": false,
  "redirected_by_env": false,
  "shipped_rules_dir": "~/tools/sicario-spec/presets/sicario-core/rules",
  "shipped_rule_file_count": 21
}
```

(Your run shows real absolute paths; the values above have the
installation path normalized to `~/tools/sicario-spec`.)

Why this record exists: the shipped rule set can be redirected with the
`SICARIO_ASSET_ROOT` environment variable, and a decoy asset root with a
*partial* rule set weakens enforcement while looking populated. The record
makes that visible:

- **`path`** — the resolved root the shipped rules were loaded from. It
  should be the SicarioSpec installation you expect, not a directory
  inside the repository under review or an unfamiliar temp path.
- **`env_value` / `env_override_set` / `env_override_honored`** — the raw
  environment override as given, if any.
- **`redirected_by_env`** — `true` means the env var actually changed
  which root won. A redirected run also carries a
  `SICARIO-ASSET-ROOT-OVERRIDE` finding that fails the gate by design,
  precisely because a redirected rule source is indistinguishable from a
  tampered one until a human confirms it. So: a *green* run with
  `redirected_by_env: true` should not exist — treat one as evidence of
  tampering with the evidence.
- **`shipped_rules_dir` / `shipped_rule_file_count`** — the shipped rules
  directory and how many top-level rule files it held (21 at 0.6.0). A
  count far below the release's shipped set is the decoy-root signature.

### 5. Read coverage: scanned, skipped, excluded — and who decided

Each content-scanning rule gets a per-rule record in
`scan_coverage.rules`. Pull one:

```bash sicario-cmd=read-evidence-as-reviewer/step-5
python3 -c "
import json
d = json.load(open('generated/sicario/gate-summary.json'))
rec = [r for r in d['scan_coverage']['rules']
       if r['rule_id'] == 'SICARIO-HARDCODED-AWS-KEY'][0]
print(json.dumps(rec, indent=2))"
```

```json title="Verified output" sicario-output=verified sicario-block=read-evidence-as-reviewer/step-5
{
  "rule_id": "SICARIO-HARDCODED-AWS-KEY",
  "kind": "regex-forbidden",
  "target": "**/*",
  "files_scanned": 123,
  "files_skipped": 0,
  "skipped_files": [],
  "files_excluded": 1,
  "excluded_dirs": [
    {
      "path": "node_modules",
      "files": 1
    }
  ],
  "excluded_dirs_total": 1,
  "excluded_dirs_truncated": false,
  "max_excluded_dirs_recorded": 50,
  "files_matched": 0,
  "total_occurrences": 0,
  "total_matches": 0,
  "findings_reported": 0,
  "occurrences_suppressed": 0,
  "truncated": false,
  "truncation_scopes": [],
  "max_findings_per_file": 20,
  "max_findings_per_rule": 200
}
```

The distinction that matters:

- **`files_skipped` / `skipped_files`** — files the scanner **could not
  read** (permissions, encoding). A scanner limitation: each one is a file
  the rule silently did not check, and the list names them. Non-empty
  means investigate.
- **`files_excluded` / `excluded_dirs`** — files a **policy decision**
  removed from scope: the standing skipped-path set
  (`scan_coverage.skipped_path_set` — `.git`, `node_modules`, `build`,
  virtualenvs, and so on). The per-directory attribution tells you *where*
  the exclusions were: here, 1 file under `node_modules`. That is
  expected. `123` files excluded under a directory named `src/` would not
  be.
- **Truncation honesty** — `excluded_dirs` lists at most
  `max_excluded_dirs_recorded` directories, but `files_excluded` and
  `excluded_dirs_total` are always exact, and `excluded_dirs_truncated`
  says whether the list was cut. Likewise `truncated` /
  `truncation_scopes` on findings: `findings_reported` can be capped
  (`max_findings_per_file`, `max_findings_per_rule`) while
  `total_occurrences` stays exact — so a capped report never silently
  understates how much was found.

### 6. The refuse-to-approve list

From artifacts alone, do not approve a change or accept a green run when:

1. **There is no evidence file** for the run being claimed — a verdict
   without `gate-summary.json` is an anecdote.
2. **`scan_coverage.overrides` contains a `material` record** — above all
   any `impact: "disables-critical-severity-rule"` — **without a matching
   exception-register entry naming an owner and an expiry.** A fix or a
   recorded exception are the legitimate outcomes; a silent disable is
   neither.
3. **A `params` override changes a pattern you have not read** — the
   `details` from/to is in the record precisely so you can.
4. **`redirected_by_env` is `true` on a green run**, or `asset_root.path`
   / `shipped_rule_file_count` do not match the expected installation and
   release.
5. **`skipped_files` is non-empty** with no explanation of why those files
   could not be read.
6. **Exclusion attribution surprises you** — `excluded_dirs` charging
   files to directories that should be in scope, or exclusion counts that
   jumped since the last review.

## Success check

Using only the evidence file, you can now state — for the reference
evidence above, and for any run you review: which rule was weakened
(`SICARIO-HARDCODED-SECRET`, disabled), where the winning definition lives
(project file `zzz-disable-secret-scan.rule.json`, superseding shipped
`040-secret-scan.rule.json`), what the run's `asset_root` resolution says
about the shipped rules (loaded from the expected installation, 21 rule
files, not redirected), and what was excluded from scanning and why
(1 file, attributed to `node_modules`, by standing policy). If you can
answer those four for a real run, the playbook did its job.

## About the output quoted in this playbook

Every quoted block above is labeled `verified` (re-executable and compared
against a real run) or `illustrative` (representative). All evidence was
captured from a reference run on a net-new repository (`refrun-reviewer`,
run date 2026-07-28, SicarioSpec 0.6.0, module form
`python3 -m sicario_cli.cli` from the source checkout): an `appsec`-profile
init, one vendored file under `node_modules/`, and one project override
rule disabling the shipped secret scan — staged exactly so this playbook
could show real records rather than asserted ones. Machine-specific
absolute paths were normalized to `~/tools/sicario-spec`; the one block
containing them is labeled illustrative.
