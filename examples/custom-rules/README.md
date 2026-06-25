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
before disabling a governance gate.
