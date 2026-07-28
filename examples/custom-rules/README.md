# Custom Rule Example

This directory contains a community-facing example rule for SicarioSpec's
declarative rule engine. The example checks Terraform root modules and requires
each matching `main.tf` file to include `required_version`.

Rule files must be valid JSON, so they do not use JSON comments. Keep custom
rules self-documenting through stable rule IDs, precise messages, narrow paths,
and adjacent README text like this file.

## Use The Rule

Copy the example into a project's local rule directory:

```bash
mkdir -p .sicario/rules
cp examples/custom-rules/terraform-pinned-version.rule.json \
  .sicario/rules/terraform-pinned-version.rule.json
```

Keep the file at the top level of `.sicario/rules/`. Rules are loaded
non-recursively, so a rule in a subdirectory never runs; `--validate-rules`
prints such files as ignored rather than validating them.

Then validate the rule file:

```bash
sicario verify --validate-rules
```

Run the full governance gate:

```bash
sicario verify
```

The rule uses:

- `id`: `SICARIO-TERRAFORM-REQUIRED-VERSION`, the stable finding code.
- `kind`: `regex-required`, which fails when a regex is absent from a matching
  file.
- `path`: `**/main.tf`, so every Terraform `main.tf` is evaluated.
- `params.pattern`: `\brequired_version\b`, the required Terraform version pin
  marker.
- `message`: the finding text emitted when a matching file omits the marker.
- `enabled`: `true`, so the rule runs by default.

## Suppress The Rule

To suppress a local rule, set `enabled` to `false` in the copy under
`.sicario/rules/`:

```json
{
  "id": "SICARIO-TERRAFORM-REQUIRED-VERSION",
  "severity": "medium",
  "kind": "regex-required",
  "path": "**/main.tf",
  "params": {
    "pattern": "\\brequired_version\\b"
  },
  "message": "Terraform root module main.tf must pin required_version.",
  "enabled": false
}
```

Record the reason in the project's risk register or security exception register
before disabling a governance gate. Disabling is also visible in gate evidence:
every disabled rule is listed in `scan_coverage.disabled_rules` in
`generated/sicario/gate-summary.json`, and whenever one rule supersedes another
by reusing its `id`, the override is recorded in `scan_coverage.overrides` with
what changed and its impact. That applies to any `id` collision, not only to a
project rule overriding a shipped one: a second file in `.sicario/rules/` whose
name sorts later supersedes the first, and is recorded with
`superseded_origin: "project"`.
