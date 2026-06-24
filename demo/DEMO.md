# SicarioSpec Verify Demo

This demo shows the core SicarioSpec invariant: the gate can pass and it can
halt. The verdict is owned by deterministic Python code, not by an LLM.

## Exact Commands

From the repository root:

```bash
python3 -m pip install -e .
sicario --version
sicario verify examples/python-api
echo $?
sicario verify examples/python-api-failing
echo $?
```

Expected shape:

```text
$ sicario --version
sicario 0.5.0

$ sicario verify examples/python-api
sicario verify passed
$ echo $?
0

$ sicario verify examples/python-api-failing
HIGH SICARIO-MISSING-THREAT-MODEL docs/security/threat-model.md: Missing docs/security/threat-model.md
sicario verify failed with 1 finding(s)
$ echo $?
1
```

The exact finding count can grow as the rule set becomes stricter. The invariant
is the important part: a governed example passes, the deliberately broken twin
fails, and the failure is a non-zero exit with a named finding code.

## Reproduce In A Throwaway Workspace

Run:

```bash
demo/run.sh
```

The script creates a temporary virtual environment, installs this checkout in
editable mode, and runs the pass/fail pair against the bundled examples.
