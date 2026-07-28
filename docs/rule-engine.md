# Declarative Rule Engine

SicarioSpec 0.5.1 moved `sicario verify` from hardcoded Python checks to a
declarative rule engine. The pass/fail verdict is still deterministic and owned
by code, but the checks are now data: `*.rule.json` files validated at load time
and dispatched to fixed evaluator kinds.

This matters for teams adopting the bundle because custom governance gates no
longer require a Python release. A platform or security team can add a project
rule, review it like any other policy file, and run the same halting gate in CI.

## Where Rules Live

`sicario verify` reads rules from two directories, in this order:

1. Shipped SicarioSpec rules in `presets/sicario-core/rules/` (loaded first).
2. `.sicario/rules/*.rule.json` in the target project (loaded second).

Precedence is deliberately simple: rules load in directory order, and **the
last rule file loaded wins for a given `id`**. The project directory loads
last, so a project rule overrides the shipped rule of the same id. Within one
directory, files load in sorted file-name order — so if two project rules
share an `id`, the one whose file name sorts later wins, deterministically,
regardless of filesystem enumeration order.

Use that behavior to disable or narrow a shipped rule without editing the
package:

```json
{
  "id": "SICARIO-HARDCODED-SECRET",
  "severity": "critical",
  "kind": "regex-forbidden",
  "path": "**/*",
  "params": {
    "pattern": "(?i)\\b(api[_-]?key|secret|token|password)\\b\\s*[:=]\\s*['\"][^'\"]{12,}['\"]"
  },
  "message": "Potential hardcoded secret",
  "enabled": false
}
```

That example keeps the same rule id and sets `enabled` to `false`, so the rule is
skipped. A real project should record the rationale in its risk or exception
register before disabling a gate. The override itself is also recorded
automatically in gate evidence (see below), so the change is visible in review
even when the register entry is missing.

### Override Evidence

Overriding a rule is a legitimate, supported action. An override never produces
a finding and never changes the verdict on its own. It is also how a project
could switch off the secret scan, so the control is **visibility**, not
prohibition: **every** `id` collision that changes the effective rule is
recorded in `scan_coverage.overrides` in
`generated/sicario/gate-summary.json`. A weakened policy shows up in the
evidence a reviewer reads, not only in a config diff.

That includes collisions that do not involve a shipped rule. The engine records
the replacement by `id`, not by which directory the files came from, so one
project rule superseding another project rule is recorded the same way — with
`superseded_origin` reading `project` rather than `shipped`. A rule quietly
neutralized by a second file in `.sicario/rules/` whose name sorts later is
exactly as visible as one that overrides the package.

Each override record carries:

| Field | Meaning |
|---|---|
| `rule_id` | The rule id that was overridden. |
| `winning_origin`, `winning_file` | Where the effective definition came from — `shipped` or `project`, plus the rule file name. |
| `superseded_origin`, `superseded_file` | Where the replaced definition came from. Also `shipped` or `project`: a project rule superseded by another project rule records `project` here. |
| `changed` | Every field whose value differs between the two definitions. |
| `material` | `true` when the change touches what the rule enforces (`enabled`, `severity`, `kind`, `path`, `params`); `false` for a cosmetic edit such as a reworded `message`. |
| `enabled` | `{"from": ..., "to": ...}` — effective enabled state before and after (a shipped rule that omits `enabled` counts as `true`). |
| `severity` | `{"from": ..., "to": ...}` — severity before and after. |
| `disables_rule` | `true` when the override turns an enabled rule off. |
| `impact` | `disables-<severity>-severity-rule` or `modifies-<severity>-severity-rule`. |

`impact` uses the **higher** of the two definitions' severities, so disabling a
shipped `critical` rule always reads `disables-critical-severity-rule` — even
if the same edit demotes the rule to `low` — and cannot be skimmed past as a
routine tweak.

One exemption: a rule identical in every field to the rule it replaces changes
nothing and is **not** recorded. `sicario init` copies every
shipped rule into `.sicario/rules/`, so without this exemption every
initialized project would carry ~21 meaningless override records, burying the
one a reviewer needs to see.

## Rule Contract

Every rule is valid JSON. Do not use JSON comments. Explain intent through
field names, clear messages, README text, or adjacent documentation.

Required fields:

| Field | Purpose |
|---|---|
| `id` | Stable finding code or policy identifier, uppercase with hyphens. |
| `severity` | `critical`, `high`, `medium`, or `low`. |
| `kind` | Fixed evaluator kind. Rules cannot execute arbitrary code. |
| `path` | File path or glob pattern relative to the project root. |
| `message` | Human-readable failure message emitted by `sicario verify`. |

Optional fields:

| Field | Purpose |
|---|---|
| `params` | Kind-specific settings such as required headings, keywords, regex patterns, or minimum file count. |
| `enabled` | Boolean. Defaults to `true`; set to `false` to suppress a rule by id. |
| `fix` | Reserved for future auto-remediation metadata. |

### What Actually Validates A Rule

Rules are validated by `_validate_rule` in `sicario_cli/rules/engine.py`, a
hand-written function. It is the only validator in the code path. `sicario-spec`
declares no runtime dependencies (`pyproject.toml`: `dependencies = []`) and does
not import `jsonschema`.

`sicario_cli/rules/schema.json` ships with the package and is read into memory
when a `RuleEngine` is constructed, but nothing reads it back. **It is
documentation of intent, not an enforced contract.** Treat it as a reference for
what a rule is meant to look like; do not assume a rule that violates it will be
rejected.

`_validate_rule` checks:

- `id`, `severity`, `kind`, `path`, and `message` are present. If any is
  missing, validation stops there and reports only the missing fields — no
  further check runs on that rule.
- `id` is a string matching `^[A-Z][A-Z0-9-]+$`. (The schema does *not* express
  this; here the code is stricter.)
- `severity` is one of `critical`, `high`, `medium`, `low`.
- `kind` is one of the ten kinds listed below.
- `path` and `message` are strings.
- `enabled`, when present, is a boolean.
- `params`, when present, is an object.
- The kind's required `params` **keys are present**. `section-exists` needs
  `headings`; `keyword-exists` and `keyword-absent` need `keywords`;
  `regex-forbidden` and `regex-required` need `pattern`; `risk-rows-valid` needs
  `forbidden_values`. `classification-complete` and `tagging-complete` require a
  `params` object but no keys inside it — omitting `params` entirely is an error
  for those two. `file-exists` and `file-glob` have no `params` requirement.
- For `regex-forbidden` only, `max_findings_per_file` and
  `max_findings_per_rule` are positive integers (see the caps section below).

`_validate_rule` does **not** check:

- **Unknown top-level fields.** The schema sets `additionalProperties: false`;
  the code ignores extra keys entirely. A typo'd field name is silently accepted
  and silently has no effect.
- **Unknown or misspelled `params` keys.** Same failure mode, one level down: a
  misspelled parameter name is accepted and the evaluator falls back to its
  default.
- **The type or value of any `params` entry** other than the two
  `regex-forbidden` caps. Only key presence is checked. `"min_count": 0` passes
  validation even though the schema requires a minimum of 1 — and a `file-glob`
  rule with `min_count: 0` can never fail, because the match count is always
  `>= 0`. `"headings": "not-a-list"` passes too.
- **That `fix` is an object.** The schema requires one; the code accepts any
  value.
- **That a regex compiles.** An invalid `pattern` is not caught at load. It
  surfaces at evaluation time as a `high` finding reading
  `Invalid regex pattern: …`, under the rule's own id.

So: an invalid rule that `_validate_rule` rejects fails the gate loudly, as
documented in the caps section. An invalid rule that only `schema.json` would
have rejected loads and runs, possibly enforcing nothing. Review rule files on
their merits; the loader is not a substitute for that.

## Supported Kinds

| Kind | Use |
|---|---|
| `file-exists` | Require a single file to exist. |
| `file-glob` | Require at least one file matching a glob. |
| `section-exists` | Require headings or section text in a file. |
| `keyword-exists` | Require one or more keywords in each matching file. |
| `keyword-absent` | Require one or more keywords, but only in files that first match `condition_keywords`. Despite the name, it fails when the keywords are **absent** — see below. |
| `regex-forbidden` | Fail when a regex appears in matching text files. |
| `regex-required` | Fail when a regex is absent from a matching file. |
| `risk-rows-valid` | Validate active risk/exception rows for owner, expiry, rationale, approval, and evidence. |
| `classification-complete` | Validate data-classification documentation completeness. |
| `tagging-complete` | Validate tagging-taxonomy documentation completeness. |

## Rule Parameters

| Parameter | Kinds | Meaning |
|---|---|---|
| `headings` | `section-exists` | Required section headings. |
| `keywords` | `keyword-exists`, `keyword-absent` | Keywords to search for. Matched case-insensitively by both kinds. |
| `match_all` | `keyword-exists` **only** | `true` requires every keyword (AND); `false` requires any (OR). Defaults to `false`. `keyword-absent` does not read it. |
| `condition_keywords` | `keyword-absent` **only** | Gate on relevance: a file is only checked if it contains at least one of these. Files that match none are skipped. Omit to check every resolved file. Absent from `schema.json`. |
| `pattern` | `regex-forbidden`, `regex-required` | The regex, as a JSON string. Remember that backslashes must be escaped in JSON. |
| `case_insensitive` | `regex-required` **only** | Defaults to `true`. Set `false` for a case-sensitive match. Has no effect on `regex-forbidden`. |
| `forbidden_values` | `risk-rows-valid` | Cell values that are not acceptable in an active row. |
| `min_count` | `file-glob` | Minimum number of glob matches required. Defaults to `1`. |
| `max_findings_per_file`, `max_findings_per_rule` | `regex-forbidden` | Output caps; see below. |
| `required_columns` | `classification-complete`, `tagging-complete` | Required column headers. Each kind falls back to its own built-in list when omitted. |

### `keyword-absent` Is Conditionally Required, Not Forbidden

The name is misleading and worth stating plainly, because reading it the obvious
way inverts the rule. `keyword-absent` does **not** fail when a keyword appears.
It fails when **none** of `params.keywords` is found in a file — the finding
means "this keyword is absent and should not be". `params.match_all` is not read
by this kind at all, so a rule that sets it gets no effect from it (shipped rule
`090-ai-guardrails.rule.json` carries `"match_all": false` inertly).

What makes it distinct from `keyword-exists` is `condition_keywords`: only files
containing at least one of those are checked, so the requirement applies to
relevant files and no others. Shipped rule 090 reads: in any `specs/**/spec.md`
that mentions AI, LLM, RAG, an agent, MCP, a model, or prompts, require the text
`prompt injection` or `tool boundary`; leave every other spec alone.

All keyword matching in both kinds is case-insensitive substring matching, not
word matching — `token` matches inside `tokenizer`.

### Regex Case Sensitivity

**`regex-forbidden` patterns are always compiled with `re.IGNORECASE`.** This is
unconditional — `regex_forbidden.py` passes the flag with no parameter guarding
it, and there is no way to turn it off from a rule file. A `regex-forbidden`
rule cannot be made case-sensitive. Write patterns on that assumption: a pattern
intended to match only `AKIA` will also match `akia` and `AkIa`, and any
case-based precision you build into the pattern will not survive.

`regex-required` is different: it reads a `case_insensitive` parameter, which
defaults to `true` but can be set to `false` for a case-sensitive match. That
parameter is absent from `schema.json` and is honored by `regex-required` alone.

## `regex-forbidden` Findings and Caps

`regex-forbidden` emits one finding per distinct matching *line* in each
scanned file (multiple matches on one line are deduplicated — they are one
remediation action). The matched text itself is never carried in a finding.
Output is bounded by two cap parameters:

| Parameter | Default | Meaning |
|---|---|---|
| `max_findings_per_file` | 20 | Maximum findings reported from a single file. |
| `max_findings_per_rule` | 200 | Maximum findings the rule reports across all files. |

Both must be positive integers. The per-file cap is applied **before** the
per-rule cap. That ordering matters: a single flooded file cannot consume the
whole per-rule budget and hide findings in every other file.

Whenever either cap suppresses anything, the rule emits one additional
`SICARIO-FINDINGS-TRUNCATED` finding at the rule's own severity, carrying the
reported count, the suppressed count, and the true total. It is mandatory and
cannot itself be suppressed — it is appended after every cap has been applied.
Counting continues after emission stops, so those totals are exact rather than
lower bounds.

An invalid cap — zero, negative, or a non-integer — is **rejected at rule
load**, and the rule then does not run. That gap is not silent: a rule that
fails validation is reported as a critical `SICARIO-RULE-INVALID` finding (a
rule file that cannot be read or parsed as a JSON object as
`SICARIO-RULE-UNREADABLE`), so the gate fails rather than silently enforcing
less than it appears to. This is the difference between a typo being caught
and a typo silently disabling your secret scan.

Because findings are per matching line, `finding_count` in
`generated/sicario/gate-summary.json` will be larger than before spec 006 for
affected repositories. Existing keys keep their names, types, and meanings —
`finding_count` still means "number of findings"; there are simply more of
them.

## Scan Coverage Evidence

`sicario verify` writes a `scan_coverage` object into
`generated/sicario/gate-summary.json`. It is evidence only — nothing in it
feeds the pass/fail verdict. It carries the effective skip-directory set
(`skipped_path_set`), rules loaded but disabled (`disabled_rules`), every
override of a shipped rule (`overrides`, above), and one record per
`regex-forbidden` rule under `rules`. Each per-rule record includes:

| Field | Meaning |
|---|---|
| `files_scanned` | Files read and evaluated. |
| `files_skipped`, `skipped_files` | Count and paths of files that could not be read or decoded. |
| `files_excluded`, `excluded_dirs`, `excluded_dirs_total`, `excluded_dirs_truncated` | Files excluded because a path component matched the fixed skip-directory policy, attributed to the directory that triggered the exclusion. |

The record also carries match and truncation counters (`files_matched`,
`total_occurrences`, `findings_reported`, `occurrences_suppressed`,
`truncated`, `truncation_scopes`) and the effective cap values.

The distinction between skipped and excluded matters: "could not be read" is a
scanner limitation to investigate, "excluded by policy" is a policy decision to
review, and neither may be indistinguishable from "clean". That is why both
are counted separately instead of being folded into the scanned total.

The `excluded_dirs` itemisation is bounded at 50 directories; when the list is
shortened, `excluded_dirs_truncated` is `true` and `excluded_dirs_total`
carries the real directory count. The file **count** (`files_excluded`) is
always exact and never capped.

## Validation Workflow

Validate rules without running the full project checks:

```bash
sicario verify --validate-rules
```

This validates exactly the files a real run would load, from the same two
directories, using the same `_validate_rule` described above. It prints one line
per error and exits `1`, or `all rules valid (N file(s))` and exits `0`.

Two properties are worth knowing:

- **It is non-recursive**, matching the engine. Both `--validate-rules` and
  `load_rules` glob `*.rule.json` at the top level of a rules directory only.
- **Rule files in subdirectories are named as ignored.** A file at
  `.sicario/rules/team-a/foo.rule.json` is never loaded by the gate. Rather than
  say nothing about it, `--validate-rules` prints it as
  `ignored — rule files load only from the top level of a rules directory, not
  from subdirectories`, and the success line reports how many were ignored.
  Ignored files do not fail validation; they are reported so a rule that will
  never run cannot sit unnoticed in a subdirectory looking installed.

Because the two paths share `_rule_sources`, validation never clears a set of
files different from the set the gate loads.

Run the full gate:

```bash
sicario verify
```

Machine-readable output is available for automation:

```bash
sicario verify --format json
sicario verify --format sarif
```

With `--format json` or `--format sarif`, stdout carries **only** the
artifact; the human summary line goes to stderr, so
`sicario verify --format sarif | jq` works. Text format keeps the summary on
stdout. In every format, the exit code is the authoritative verdict.

## Example Rule

The `examples/custom-rules/` directory contains a community-facing Terraform
example:

- `terraform-pinned-version.rule.json` uses `regex-required` to require
  `required_version` in matching `main.tf` files.
- `README.md` explains how to copy the rule into `.sicario/rules/`, validate it
  with `sicario verify --validate-rules`, and suppress it only with a documented
  risk or exception rationale.

Use this shape for future project-owned gates: one small JSON rule, one adjacent
README, a precise stable rule ID, and a deterministic evaluator kind.
