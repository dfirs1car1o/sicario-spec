#!/usr/bin/env bash
# Demo scenario played back inside the asciinema recording.
#
# This is the *driver* that types the commands during the recording. It assumes:
#   - `sicario` is on PATH (installed via `pip install -e .` into a venv)
#   - the current working directory is a clean scratch dir that contains a copy
#     of the repo's examples/ tree at ./examples (record.sh sets this up).
#
# It captures the real, unmodified behaviour of the gate:
#   sicario init demo-proj --profile appsec   -> scaffolds a governed repo
#   sicario verify examples/python-api        -> PASS, exit 0
#   sicario verify examples/python-api-failing-> FAIL (SICARIO-MISSING-THREAT-MODEL), exit 1
#
# Nothing here fabricates output; every line is produced by the installed CLI.
set -u

# A tiny "type it like a human" helper so the cast reads naturally.
typed() {
  printf '$ %s\n' "$*"
  "$@"
}

note() { printf '\n# %s\n' "$*"; }

note "SicarioSpec demo — a HALTING governance gate, verdict owned by stdlib-only code (no LLM)."
note "sicario --version"
sicario --version
sleep 1

note "1) Scaffold a governed project from the appsec profile."
typed sicario init demo-proj --profile appsec
sleep 1

note "2) Verify a fully-governed feature -> PASS (exit 0)."
typed sicario verify examples/python-api
printf '$ echo $?\n%s\n' "$?"
sleep 1

note "3) The SAME feature with docs/security/threat-model.md removed -> the gate HALTS."
note "   It exits non-zero and names the finding code, so CI/merge is blocked."
set +e
typed sicario verify examples/python-api-failing
rc=$?
set -e 2>/dev/null || true
printf '$ echo $?\n%s\n' "$rc"
sleep 1

note "Same gate, opposite verdict, decided by non-AI code. A gate that can only pass is not a gate."
