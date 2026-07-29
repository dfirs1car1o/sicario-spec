---
title: "Playbook: Select Compliance Frameworks"
sidebar_label: "Select frameworks"
guide-slug: select-frameworks
captured-version: 0.6.0
reference-run-repository: refrun-frameworks
reference-run-date: "2026-07-28"
---

# Playbook: Select Compliance Frameworks

## Scenario and intended reader

You maintain a repository that already has SicarioSpec initialized, and you
need to change or understand which compliance frameworks the gate enforces:
read the current selection, add a framework, handle the finding that fires
when a selected framework has no control map, and enforce an
experimental-tier map deliberately.

This playbook is for the engineer or compliance owner making that change in
an **existing** repository. If you are choosing frameworks at initial setup
(`sicario init`), that decision belongs to the [selection guide](initial-setup-selection.md) — the
"Choose profiles, presets, and frameworks" playbook in this section — which
covers per-profile defaults and composition. The
[profiles reference](../profiles.md) and the
[control maps reference](../control-maps.md) remain the reference material;
this playbook is the workflow.

## Starting state

- A repository initialized with `sicario init` at SicarioSpec 0.6.0, using
  `--profile appsec` (any profile works; quoted output below was captured
  with `appsec`).
- `sicario verify .` currently passes.
- A shell with Python 3.9+ and the SicarioSpec CLI installed. If `sicario`
  is not on your PATH, every command below also works as
  `python3 -m sicario_cli.cli` — for example
  `python3 -m sicario_cli.cli verify .`.

Assumed platform: macOS or Linux with a POSIX shell. On Windows, use
forward-slash paths in commands and adjust `cat`/`cp` to your shell.

## How framework selection works (one paragraph)

The selection lives in one plain-text file, `.sicario/frameworks.txt`, one
framework key per line. When the file exists, `sicario verify` requires a
control map for **each listed key** and emits a
`SICARIO-MISSING-FRAMEWORK-MAP` finding for each one whose map is absent —
you enforce exactly the frameworks you chose, not all 14 and not none. When
the file does not exist, no framework is selected and that finding cannot
fire (the coarse `SICARIO-MISSING-CONTROL-MAPS` check, which only requires
that *some* control map exists, runs regardless). The 14 shipped maps are
split into two tiers: **supported** (11 maps) and **experimental**
(`ai-rmf`, `owasp-asvs`, `pci-dss`). Experimental maps are never selected
implicitly — a profile default excludes them even when the profile's
framework table lists them — and are enforced only when you name them
explicitly.

## Steps

### 1. Read the current selection

```bash
cat .sicario/frameworks.txt
```

```text title="Verified output" sicario-output=verified sicario-block=select-frameworks/step-1
# SicarioSpec framework selector (#18).
# One framework key per line. `sicario verify` requires a control map
# for each key listed here (SICARIO-MISSING-FRAMEWORK-MAP if absent).
# Remove this file to fall back to the default coarse control-map check.
# Supported keys: bsi-c5, ccm, eu-ai-act, fedramp, gdpr, hipaa, iso27001, nist-800-53, soc2, sox, ssdf
# Experimental keys: ai-rmf, owasp-asvs, pci-dss
#   Experimental maps are thinner than the supported set. They are
#   enforced exactly like any other key when listed here, but are never
#   selected by a profile default -- only by explicit --frameworks.
ssdf
iso27001
```

Note what the `appsec` profile wrote here. Its framework table lists
`ssdf`, `iso27001`, **and** `owasp-asvs` — but `owasp-asvs` is
experimental-tier, so the implicit default filtered it out and only the two
supported keys landed. That is the tier rule working: an experimental map
never enters your enforced set unless you name it yourself (step 6).

### 2. See what is enforced, with tier labels

The init report states the effective selection and labels experimental
keys. A `--dry-run` re-run prints that report without writing anything:

```bash
sicario init . --profile appsec --dry-run | grep '^frameworks'
```

```text title="Verified output" sicario-output=verified sicario-block=select-frameworks/step-2
frameworks ssdf, iso27001
```

Later in this playbook, after gdpr and owasp-asvs are added, the same
command reports the experimental key with an explicit label (step 6 shows
that output). The label is the visible consequence of the tier: experimental
enforcement is always something someone chose on purpose, and the report
says so.

### 3. Add a framework to the selection

The selection file is the interface: add one key per line. Suppose the
project now owes GDPR evidence:

```bash
printf 'gdpr\n' >> .sicario/frameworks.txt
tail -3 .sicario/frameworks.txt
```

```text title="Verified output" sicario-output=verified sicario-block=select-frameworks/step-3
ssdf
iso27001
gdpr
```

Editing the file directly is the supported path for an existing repository.
Re-running `sicario init` will **not** change an existing selection — it
preserves `.sicario/frameworks.txt` (brownfield-safe) and prints a notice
that the file differs from the profile defaults.

### 4. Run the gate and read the missing-map finding

This reference run's repository had pruned `docs/compliance/control-maps/`
down to the two enforced maps — a common hygiene move. Selecting `gdpr`
without its map present makes the gate fail:

```bash
sicario verify .
```

```text title="Verified output" sicario-output=verified sicario-block=select-frameworks/step-4
MEDIUM SICARIO-MISSING-FRAMEWORK-MAP docs/compliance/control-maps/gdpr-cpra-sicario.json: Selected framework 'gdpr' has no control map (gdpr-cpra-sicario.json)
sicario verify failed with 1 finding(s)
```

The command exits `1`. Read the finding precisely:

- It fires **once per selected key** whose map is absent, at severity
  `medium`.
- The gate accepts the map at either
  `docs/compliance/control-maps/gdpr-cpra-sicario.json` (where
  `sicario init` installs maps) or `control_maps/gdpr-cpra-sicario.json`.
- Deselecting the key (removing the line) also clears the finding — but
  that changes what your project claims to enforce, so treat it as a
  compliance decision, not a fix.

One sharp edge, observed on this exact run: re-running `sicario init .`
does **not** restore a deleted map, because an existing
`docs/compliance/control-maps/` directory is preserved as-is rather than
merged file-by-file. Restore the map explicitly, as in step 5.

### 5. Restore the missing map and re-run to green

The shipped maps live with your SicarioSpec installation. Ask the CLI where
that is, then copy the map in:

```bash
MAPS="$(python3 -c "from sicario_cli.cli import CONTROL_MAPS_ROOT; print(CONTROL_MAPS_ROOT)")"
cp "$MAPS/gdpr-cpra-sicario.json" docs/compliance/control-maps/
sicario verify .
```

```text title="Verified output" sicario-output=verified sicario-block=select-frameworks/step-5
sicario verify passed
```

Exit code is `0`. (If the map was previously committed, `git checkout --
docs/compliance/control-maps/` is an equivalent fix.)

### 6. Enforce an experimental-tier map — explicitly

Experimental maps (`ai-rmf`, `owasp-asvs`, `pci-dss`) are fully
installable and, once listed, enforced **exactly like any other key**. The
only behavioral difference is that no profile default will ever add them
for you. To enforce OWASP ASVS:

```bash
printf 'owasp-asvs\n' >> .sicario/frameworks.txt
MAPS="$(python3 -c "from sicario_cli.cli import CONTROL_MAPS_ROOT; print(CONTROL_MAPS_ROOT)")"
cp "$MAPS/owasp-asvs-sicario.json" docs/compliance/control-maps/
sicario verify .
```

```text title="Verified output" sicario-output=verified sicario-block=select-frameworks/step-6a
sicario verify passed
```

Now re-check the effective selection report from step 2:

```bash
sicario init . --profile appsec --dry-run | grep '^frameworks'
```

```text title="Verified output" sicario-output=verified sicario-block=select-frameworks/step-6b
frameworks ssdf, iso27001, gdpr, owasp-asvs (experimental)
frameworks: existing .sicario/frameworks.txt preserved; it differs from this profile's defaults. Re-run with --force or edit the file to adopt them.
```

The `(experimental)` label follows the key everywhere the selection is
reported. Before enforcing an experimental map, read its tier rationale in
the [control maps reference](../control-maps.md): experimental maps are
measurably thinner than the supported set (fewer controls resolved, coarser
evidence references), which is exactly why they require an explicit
opt-in.

### 7. State what this selection does — and does not — claim

Record, in the same change that edits `.sicario/frameworks.txt` (for
example in your `docs/compliance/control-applicability.md`), what the
selection means. This is a step, not a footnote, because the claim is easy
to overstate:

- Control maps are **coarse traceability aids**: they connect SicarioSpec
  evidence artifacts to framework control areas so an auditor can navigate
  from one to the other. They are **not certification claims**, and
  selecting a framework does not make the repository "compliant" with it.
- The gate checks **completeness, not quality**: `sicario verify` confirms
  the selected map files are present (and the evidence artifacts exist); it
  does not judge whether your evidence would satisfy an assessor.
- Experimental-tier maps carry both caveats more strongly — name them as
  experimental wherever you cite them.

## Success check

You are done when all of the following hold:

1. `cat .sicario/frameworks.txt` lists exactly the framework keys your
   project owes evidence for — including any experimental keys you chose
   deliberately.
2. `sicario verify .` exits `0` with no `SICARIO-MISSING-FRAMEWORK-MAP`
   findings.
3. `sicario init . --profile <your-profile> --dry-run | grep '^frameworks'`
   reports your selection, with `(experimental)` labels only on keys you
   named on purpose.
4. Your compliance docs state the traceability-not-certification boundary
   from step 7.

## About the output quoted in this playbook

Every quoted block above is labeled `verified` (re-executable and compared
against a real run) or `illustrative` (representative). All output was
captured from a reference run on a net-new repository (`refrun-frameworks`,
run date 2026-07-28, SicarioSpec 0.6.0, module form
`python3 -m sicario_cli.cli` from the source checkout). Absolute paths in
captured output were normalized: the working directory to `~/work/<repo>`
and the SicarioSpec installation to `~/tools/sicario-spec`.
