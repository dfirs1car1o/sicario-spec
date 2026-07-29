---
title: "Playbook: Running The First Spec From A Fresh Init"
sidebar_label: "Your first spec"
guide-slug: first-spec
captured-version: 0.6.0
reference-run-repository: payments-api
reference-run-date: "2026-07-28"
---

# Playbook: Running The First Spec From A Fresh Init

## Scenario And Intended Reader

You have a freshly initialized SicarioSpec repository and have never written
a governed spec. This playbook walks the full first-spec loop: create the
feature directory, copy the governed template, fill its sections in order,
run the gate at checkpoints, read real findings once — deliberately, in a
staged step — and end at `sicario verify passed`, with the passing spec
reflected in the evidence artifact reviewers will read.

This playbook covers the *loop*. What a complete section should *contain*,
section by section, is the depth companion — the spec-authoring playbook
planned for this guide set (not yet published) — which you do not need in
order to finish here.

## Prerequisites

The baseline path requires exactly this, and nothing else:

- a POSIX shell (bash or zsh; on Windows, substitute `py -3 -m` for the
  `python3 -m` forms and `copy` for `cp`);
- Python 3.9+ and the SicarioSpec CLI 0.6.0
  (`sicario --version` → `sicario 0.6.0`; use
  `python3 -m sicario_cli.cli` everywhere if `sicario` is not on `PATH`);
- a repository initialized by `sicario init` (the walkthrough's end state:
  `sicario verify .` exits `0`).

No coding-agent environment, no Spec Kit CLI, and no scripts directory are
required — and no step below assumes them.

## How Output Is Quoted In This Playbook

Quoted output blocks carry a machine-readable `verified` or `illustrative`
marker; verified blocks are exact at the captured version, illustrative
blocks are visibly labeled and representative. All quoted output comes from
a reference run: a net-new repository `payments-api`, initialized with
`--profile appsec`, run date 2026-07-28, SicarioSpec 0.6.0.

## Starting State

An initialized repository at its root, gate green:

```bash
sicario verify .
```

```text title="Verified output" sicario-output=verified sicario-block=first-spec/fs-01
sicario verify passed
```

## Step 1 — Create The Feature Directory

Feature directories live under `specs/`, named `<NNN-short-name>` — a
three-digit sequence number and a short kebab-case name. The worked example
is a refund-export feature:

```bash
mkdir -p specs/001-refund-export
```

No output on success.

## Step 2 — Copy The Governed Spec Template (The Baseline Path)

Copy the shipped spec template into the feature directory as `spec.md`:

```bash
cp .specify/templates/spec-template.md specs/001-refund-export/spec.md
```

No output on success. This manual copy is the **universal floor**: it works
on every adoption path, because `sicario init` installs the governed
templates into `.specify/templates/` and requires nothing beyond a shell.

Two conveniences exist that this playbook deliberately does **not** rely
on:

- **The feature-creation script** (`.specify/scripts/bash/create-new-feature.sh`)
  exists only where Spec Kit's own scaffolding is present — repositories
  adopted through native Spec Kit tooling (`specify init` + the bundle
  path). Targets initialized by `sicario init` do **not** receive a
  `.specify/scripts/` directory, so this playbook cannot and does not
  promise it there.
- **The slash-command flow** (the `/speckit-specify` family, through
  `/speckit-plan` and `/speckit-tasks`) exists as agent skills: prompt
  documents that a coding-agent environment surfaces as slash commands.
  Inside such an environment, `/speckit-specify` creates the feature
  directory and spec for you, and is a legitimate variant of this step.
  Outside one, these commands do not exist as anything you can run — they
  are unavailable in a plain shell, and no later step here depends on
  them.

## Step 3 — Checkpoint 1: The Fresh Template Already Passes, And Why

Run the gate before writing a single word:

```bash
sicario verify .
```

```text title="Verified output" sicario-output=verified sicario-block=first-spec/fs-02
sicario verify passed
```

This is worth being honest about: the shipped template starts
**complete-in-form**. It already contains every section heading and phrase
the gate's presence and completeness checks require — on both adoption
paths, greenfield init and brownfield overlay — so a freshly copied
template passes before any real content exists. The gate enforces the
*form* of a governed spec; the *substance* of each section remains a human
obligation, which is exactly why the next step stages a defect on purpose:
so the first findings you ever read are ones you created knowingly.

## Step 4 — Stage A Spec-Contract Defect, On Purpose

Make the two edits a half-finished spec most often exhibits. In
`specs/001-refund-export/spec.md`:

1. delete the entire `## Trust Boundaries` section (the heading and its
   bullets);
2. delete the `- Classification owner:` line from the
   `## Data Classification` section.

Then run the gate:

```bash
sicario verify .
```

```text title="Verified output" sicario-output=verified sicario-block=first-spec/fs-03
HIGH SICARIO-SPEC-SECTION specs/001-refund-export/spec.md: spec.md missing required section: Trust Boundaries
HIGH SICARIO-DATA-CLASSIFICATION-INCOMPLETE specs/001-refund-export/spec.md: Data classification must include owner, level, retention, residency, sharing, and redaction fields
sicario verify failed with 2 finding(s)
```

The command exits `1`. The two codes, as they first appear:

- **`SICARIO-SPEC-SECTION`** — a required spec section heading is absent.
  The gate requires six: Data Classification, Tagging Discipline, Trust
  Boundaries, Security Requirements, Abuse Cases, and Evidence. The
  message names the missing one.
- **`SICARIO-DATA-CLASSIFICATION-INCOMPLETE`** — the Data Classification
  section no longer covers all required fields (owner, level, retention,
  residency, sharing, redaction). Removing the owner line was enough.

This is the shape of every finding you will meet later unplanned:
severity, stable code, repository-relative location, message — and a
non-zero exit code that CI gates on.

## Step 5 — Fix And Re-Run To Green

Nothing real has been written yet, so the fix is to restore the complete
form — re-copy the template:

```bash
cp .specify/templates/spec-template.md specs/001-refund-export/spec.md
sicario verify .
```

```text title="Verified output" sicario-output=verified sicario-block=first-spec/fs-04
sicario verify passed
```

(Later, when a spec has real content, the fix is the targeted one: restore
the missing section or field, never the whole file.)

## Step 6 — Fill The Sections In Order, Gate At Checkpoints

Now write the spec, in this order — it front-loads the decisions every
later section depends on:

1. Title, overview, and user scenarios — what the feature is;
2. **Data Classification** — what data it touches, owner, level,
   retention, residency, sharing, redaction;
3. **Tagging Discipline** — owner, system, environment,
   data-classification, retention tags;
4. Roles, assets, and abuse actors;
5. **Trust Boundaries** — where untrusted input crosses into your system;
6. **Security Requirements** and privacy requirements;
7. **Abuse Cases** — how the feature gets misused, detection, mitigation;
8. Functional requirements, acceptance criteria, and **Evidence** to
   produce.

Replace the template's blank bullets with your feature's real analysis,
keeping the section headings and the field labels: the completeness checks
key on those labels, so `- Classification owner:` becomes
`- Classification owner: payments data owner` — label kept, value added.
The worked example's Data Classification fill, from the reference run:

*Illustrative content — your feature's real values belong here, not
these.*

```text title="Illustrative output (representative, not exact)" sicario-output=illustrative sicario-block=first-spec/fs-05
- Data types processed: refund ids, amounts, currency codes, order ids
- Highest classification: Confidential
- Classification owner: payments data owner
- Data retention and deletion expectations: exports retained 30 days, then deleted
- Data residency or sovereignty constraints: exports stay in the primary region
- Sharing, egress, or third-party disclosure: finance team only; no third parties
- Redaction or masking requirements: card numbers never exported; last-4 only
```

Run `sicario verify .` as a checkpoint after step 2 (classification
filled) and again after step 8 (all sections filled). What each checkpoint
honestly reports: **green, both times** — because you started from a
complete-in-form template and kept the headings and labels while adding
substance. The checkpoints are not there to catch you; they are there so
that *if* an edit accidentally breaks the form — a deleted heading, a
dropped field label, a section pasted over — you learn at the checkpoint,
seconds after the edit, instead of in CI. Two cautions with real teeth:

- if your feature involves AI, agents, models, or tool use, the gate
  additionally requires the prompt-injection and tool-boundary guardrail
  content to be present (`SICARIO-AI-GUARDRAIL-MISSING`) — the template's
  AI / LLM Risk section carries it; do not delete that section, fill it;
- likewise orchestration-shaped features (queues, workers, multi-agent)
  must keep retry/idempotency/dead-letter/workflow-state/approval content
  (`SICARIO-FLEET-GUARDRAIL-MISSING`).

Checkpoint after the final section:

```bash
sicario verify .
```

```text title="Verified output" sicario-output=verified sicario-block=first-spec/fs-06
sicario verify passed
```

## Step 7 — Read The Green Run In The Evidence

The loop ends at the artifact reviewers will read, not at your terminal.
Every verify run rewrites `generated/sicario/gate-summary.json`; confirm
the passing spec is reflected there:

```bash
python3 -c "import json; d = json.load(open('generated/sicario/gate-summary.json')); print(json.dumps({'status': d['status'], 'finding_count': d['finding_count']}, indent=2))"
```

```text title="Verified output" sicario-output=verified sicario-block=first-spec/fs-07
{
  "status": "pass",
  "finding_count": 0
}
```

During Step 4's staged failure this same file carried `"status": "fail"`,
`"finding_count": 2`, and both finding records — the evidence trail is
written on red runs too, which is what makes it evidence.

## Success Check

You have completed the loop when all of the following hold:

1. `specs/001-refund-export/spec.md` (or your feature's equivalent) exists
   and every governed section carries your real content, not template
   blanks;
2. `sicario verify .` prints `sicario verify passed` and exits `0`;
3. `generated/sicario/gate-summary.json` shows `"status": "pass"` and
   `"finding_count": 0`;
4. you have read the two staged finding codes and can say what each one
   polices.

## Visual Assets Note

Every surface in this playbook is a terminal or a text file, captured as
text blocks (capture-class `terminal-text`); no step surfaces a graphical
view, which is the stated reason this playbook carries no screenshots.

## About This Playbook's Captures

Reference run: repository `payments-api`, run date 2026-07-28, captured
against SicarioSpec 0.6.0. The repository contains nothing but what this
playbook's steps create; absolute paths do not appear in quoted output, and
the module-form/`PATH` note from the prerequisites applies to every quoted
command. This playbook's first-run acceptance evaluation is performed
without a coding-agent environment, so the path validated cold is the
baseline path every reader has.
