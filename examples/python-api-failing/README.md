# Example: the SAME feature, with one governance gap (proves the gate halts)

This directory is the deliberately-broken twin of
[`examples/python-api/`](../python-api/). It is the **exact same** governed
feature (the read-only invoice-export API) with **one** required artifact
removed: `docs/security/threat-model.md` is missing.

Its only job is to prove that `sicario verify` is a real **halting gate**: it
exits **non-zero** and names the failing finding code, so CI / a merge gate
actually blocks. A gate that never fails is not a gate.

## Reproduce the failure (from a clean clone)

From the repository root:

```bash
sicario verify examples/python-api-failing
# or, without installing:
python3 -m sicario_cli.cli verify examples/python-api-failing
```

Expected output (note the **non-zero exit**):

```
HIGH SICARIO-MISSING-THREAT-MODEL docs/security/threat-model.md: Missing docs/security/threat-model.md
sicario verify failed with 1 finding(s)
```

```bash
echo $?
# -> 1
```

The gate also writes evidence to
`examples/python-api-failing/generated/sicario/gate-summary.json` (gitignored),
which reports:

```json
{
  "status": "fail",
  "finding_count": 1,
  "findings": [
    {
      "severity": "high",
      "code": "SICARIO-MISSING-THREAT-MODEL",
      "message": "Missing docs/security/threat-model.md",
      "path": "docs/security/threat-model.md"
    }
  ]
}
```

## Side-by-side: pass and fail from the same clone

```bash
sicario verify examples/python-api          # -> sicario verify passed   (exit 0)
sicario verify examples/python-api-failing  # -> ... failed with 1 finding(s) (exit 1)
```

Same feature, same gate, opposite verdict — decided entirely by stdlib-only
code with no AI in the decision path. To fix the failing twin, restore
`docs/security/threat-model.md` (copy it from `../python-api/`) and the gate
returns to `pass`.

See [`USAGE.md`](../../USAGE.md) for the full finding-code reference.
