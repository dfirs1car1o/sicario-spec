---
title: "Playbook: Add a Custom Project Rule"
sidebar_label: "Add a Custom Project Rule"
guide-slug: custom-rule
captured-version: 0.6.0
reference-run-repository: refrun-rules/custom-rule-app
reference-run-date: "2026-07-28"
---

# Playbook: Add a Custom Project Rule

## Scenario

Your team has a policy the shipped rules do not cover — in this playbook, "no
internal staging hostname in committed files." You will write it as a
declarative project rule in `.sicario/rules/`, validate it, watch it fire and
then pass, learn the one loading rule that silently bites people
(subdirectories are ignored), and see what happens when a rule file is
malformed.

**Intended reader**: a platform or security engineer adding a project-owned
gate. No Python change and no SicarioSpec release is involved — a rule is a
reviewable JSON policy file.

## Output conventions

Every quoted output block carries a machine-readable marker declaring it
`verified` or `illustrative`. Verified blocks come from the reference run in
this page's front matter and are re-executable as-is; the only rewrite applied
is the documented `paths` normalization (the reference-run directory is shown
as `~/refrun-rules/custom-rule-app`). Illustrative blocks are visibly labeled
and representative rather than exact.

Every step is a terminal interaction, captured as text per the terminal-text
capture class; no step surfaces a graphical view, so this playbook carries no
screenshots (stated per the visual-asset policy).

## Prerequisites and starting state

- Python 3.9+ and SicarioSpec 0.6.0. Commands use the module form
  `python3 -m sicario_cli.cli`; if `sicario` is on your PATH it is equivalent.
- A POSIX shell (bash or zsh) on macOS or Linux; on Windows use WSL.
- Starting state: a repository freshly initialized with
  `python3 -m sicario_cli.cli init . --profile public-core`, where
  `python3 -m sicario_cli.cli verify .` already passes.

Two facts about where rules live, so the rest of the playbook makes sense.
`sicario verify` loads rules from two directories, in order: the shipped
rules, then the project's `.sicario/rules/`. For a given rule `id`, the last
file loaded wins — that is the override mechanism, covered in the
[override playbook](override-shipped-rule.md). And `sicario init` copies the
21 shipped rule files into `.sicario/rules/` so you can read exactly what
your gate enforces. Your custom rule will sit next to those copies.

## Steps

### 1. Write the rule

Create `.sicario/rules/200-no-staging-hostname.rule.json`. The file name must
end in `.rule.json`; the leading number only controls load order within the
directory.

```json
{
  "id": "ACME-NO-STAGING-HOSTNAME",
  "severity": "high",
  "kind": "regex-forbidden",
  "path": "**/*",
  "params": {
    "pattern": "staging\\.internal\\.example\\.com"
  },
  "message": "Internal staging hostname committed; use the service discovery name instead",
  "enabled": true
}
```

Field notes:

- `id` becomes the finding code (uppercase letters, digits, and hyphens;
  starts with a letter). Pick a project prefix so your codes are
  distinguishable from shipped `SICARIO-*` codes at a glance.
- `kind` must be one of the shipped evaluator kinds — `file-exists`,
  `file-glob`, `section-exists`, `keyword-exists`, `keyword-absent`,
  `regex-forbidden`, `regex-required`, `risk-rows-valid`,
  `classification-complete`, `tagging-complete`. This playbook uses
  `regex-forbidden`: the gate fails when the pattern matches. Patterns are
  compiled case-insensitively; see the
  [rule engine reference](../rule-engine.md) for each kind's parameters.
- `path` is a glob relative to the repository root. `**/*` scans everything
  except the fixed skipped-path set (`.git`, `node_modules`, `build`,
  `generated`, and friends).
- `severity` is one of `critical`, `high`, `medium`, `low`. Any finding fails
  the gate regardless of severity; severity is for readers and evidence.

### 2. Validate before running

```bash
python3 -m sicario_cli.cli verify . --validate-rules
```

```text title="Verified output" sicario-output=verified sicario-block=custom-rule/02-validate
all rules valid (43 file(s))
```

Exit code `0`. The count is every rule file the gate would load: 21 shipped
files plus the 22 now in `.sicario/rules/` (the 21 copies plus your new one).
`--validate-rules` checks exactly the files a real run would load — same
directories, same top-level-only glob — so "valid" here means "will actually
be enforced", not merely "parses".

### 3. See it fire

Stage a violation the way it would really arrive — a runbook that names the
staging host. Create `docs/runbooks/deploy.md`:

```markdown
# Deploy runbook

1. Push the image.
2. Smoke-test against staging.internal.example.com before promoting.
```

Run the gate:

```bash
python3 -m sicario_cli.cli verify .
```

```text title="Verified output" sicario-output=verified sicario-block=custom-rule/03-firing
HIGH ACME-NO-STAGING-HOSTNAME docs/runbooks/deploy.md:4: Internal staging hostname committed; use the service discovery name instead
sicario verify failed with 1 finding(s)
```

Exit code `1`. The finding line is `SEVERITY CODE path:line: message` — your
`id`, your `message`, and the exact line of the match. `regex-forbidden`
findings never echo the matched text itself into output or evidence, so a
rule that matches sensitive content cannot leak it.

### 4. Fix and pass

Replace the hostname in the runbook with the service-discovery name (line 4
becomes "Smoke-test against the staging service name from service discovery
before promoting."), then re-run:

```bash
python3 -m sicario_cli.cli verify .
```

```text title="Verified output" sicario-output=verified sicario-block=custom-rule/04-green
sicario verify passed
```

The run also wrote evidence. Your rule's per-run coverage record is in
`generated/sicario/gate-summary.json` under `scan_coverage.rules`:

```bash
python3 -c "
import json
d = json.load(open('generated/sicario/gate-summary.json'))
rec = [r for r in d['scan_coverage']['rules'] if r['rule_id'] == 'ACME-NO-STAGING-HOSTNAME'][0]
print(json.dumps({k: rec[k] for k in ('rule_id','kind','target','files_scanned','files_matched','findings_reported')}, indent=2))
"
```

*Illustrative output — file counts vary with repository contents.*

```json title="Illustrative output (representative, not exact)" sicario-output=illustrative sicario-block=custom-rule/04-coverage
{
  "rule_id": "ACME-NO-STAGING-HOSTNAME",
  "kind": "regex-forbidden",
  "target": "**/*",
  "files_scanned": 117,
  "files_matched": 0,
  "findings_reported": 0
}
```

A passing rule leaves proof of what it scanned, not just silence.

### 5. The top-level-only loading rule

Rule files load **only from the top level of a rules directory** —
subdirectories are never loaded. This is the mistake that fails silently, so
stage it deliberately. Move the rule into a subdirectory:

```bash
mkdir -p .sicario/rules/drafts
mv .sicario/rules/200-no-staging-hostname.rule.json .sicario/rules/drafts/
python3 -m sicario_cli.cli verify . --validate-rules
```

```text title="Verified output" sicario-output=verified sicario-block=custom-rule/05-subdir sicario-normalize=paths
~/refrun-rules/custom-rule-app/.sicario/rules/drafts/200-no-staging-hostname.rule.json: ignored — rule files load only from the top level of a rules directory, not from subdirectories
all rules valid (42 file(s); 1 ignored in subdirectories)
```

`--validate-rules` names the unreachable file. A plain `verify` run gives you
no such warning — the rule simply does not run, and a violation sails
through. Prove it: re-add the hostname while the rule is parked in `drafts/`:

```bash
printf '\nTest note: staging.internal.example.com\n' >> docs/runbooks/deploy.md
python3 -m sicario_cli.cli verify .
```

```text title="Verified output" sicario-output=verified sicario-block=custom-rule/05-silent-pass
sicario verify passed
```

A green gate, with the violation sitting in the tree — silent
non-enforcement, which is why validating after any rules-directory change is
worth the habit. Move the rule back and enforcement returns immediately:

```bash
mv .sicario/rules/drafts/200-no-staging-hostname.rule.json .sicario/rules/
rmdir .sicario/rules/drafts
python3 -m sicario_cli.cli verify .
```

```text title="Verified output" sicario-output=verified sicario-block=custom-rule/05-back
HIGH ACME-NO-STAGING-HOSTNAME docs/runbooks/deploy.md:6: Internal staging hostname committed; use the service discovery name instead
sicario verify failed with 1 finding(s)
```

Delete the test note line from the runbook to get back to green.

### 6. What a malformed rule does

Create a deliberately broken rule,
`.sicario/rules/201-block-debug-flag.rule.json`, with an invalid severity and
a zero findings cap:

```json
{
  "id": "ACME-NO-DEBUG-FLAG",
  "severity": "blocker",
  "kind": "regex-forbidden",
  "path": "src/**/*.py",
  "params": {
    "pattern": "DEBUG\\s*=\\s*True",
    "max_findings_per_file": 0
  },
  "message": "Debug mode enabled in source"
}
```

```bash
python3 -m sicario_cli.cli verify . --validate-rules
```

```text title="Verified output" sicario-output=verified sicario-block=custom-rule/06-invalid sicario-normalize=paths
~/refrun-rules/custom-rule-app/.sicario/rules/201-block-debug-flag.rule.json: severity 'blocker' must be one of ['critical', 'high', 'low', 'medium']
~/refrun-rules/custom-rule-app/.sicario/rules/201-block-debug-flag.rule.json: params.max_findings_per_file must be a positive integer (got 0)
rule validation failed with 2 error(s) across 44 file(s)
```

Exit code `1`, with every error named per file. And if you skip validation
and run the gate anyway, the gate fails closed rather than silently
enforcing less:

```bash
python3 -m sicario_cli.cli verify .
```

```text title="Verified output" sicario-output=verified sicario-block=custom-rule/06-fail-closed
CRITICAL SICARIO-RULE-INVALID .sicario/rules/201-block-debug-flag.rule.json: Rule 'ACME-NO-DEBUG-FLAG' did not run: severity 'blocker' must be one of ['critical', 'high', 'low', 'medium']; params.max_findings_per_file must be a positive integer (got 0)
sicario verify failed with 1 finding(s)
```

A rule that cannot run is a gap in enforcement, so it is a critical finding —
a cap of `0` on a scan rule must never quietly turn into "scan nothing and
pass". Fix the file (severity `high`, `max_findings_per_file` of `20`) and
both commands go green:

```bash
python3 -m sicario_cli.cli verify . --validate-rules
python3 -m sicario_cli.cli verify .
```

```text title="Verified output" sicario-output=verified sicario-block=custom-rule/06-fixed
all rules valid (44 file(s))
sicario verify passed
```

## Success check

You are done when:

1. `python3 -m sicario_cli.cli verify . --validate-rules` reports
   `all rules valid` including your new file's count, with nothing
   `ignored in subdirectories`.
2. A staged violation of your policy fails the gate with **your** finding
   code and exits `1`; removing it returns `sicario verify passed`, exit `0`.
3. `scan_coverage.rules` in `generated/sicario/gate-summary.json` contains a
   record for your rule id, proving it ran.

## Further reading

- [Declarative rule engine](../rule-engine.md) — every kind, every parameter,
  caps and truncation behavior for `regex-forbidden`.
- [Playbook: override a shipped rule](override-shipped-rule.md) — reusing a
  shipped rule's `id` to narrow or disable it, and the evidence that records
  the override.
- [Playbook: investigate a failing gate](investigate-failing-gate.md) — for
  reading the findings your new rule will produce in anger.
