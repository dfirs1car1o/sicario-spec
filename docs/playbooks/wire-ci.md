---
title: "Playbook: Wire the Gate into CI"
sidebar_label: "Wire the gate into CI"
guide-slug: wire-ci
captured-version: 0.6.0
reference-run-repository: refrun-ci
reference-run-date: "2026-07-28"
---

# Playbook: Wire the Gate into CI

## Scenario and intended reader

Your repository passes `sicario verify` locally, and you want the same gate
to run on every pull request in GitHub Actions — red when a finding exists,
green after the fix — so governance stops depending on contributors
remembering to run it. This playbook wires the shipped workflow template
into a repository, walks one red-to-green cycle, and shows where the
evidence artifacts land in CI.

Intended reader: the engineer setting up CI for a SicarioSpec-governed
repository. For diagnosing an unfamiliar failure once CI is red, use the
[Investigate a failing gate](investigate-failing-gate.md) playbook in this section; this playbook stages
a known failure on purpose.

## Starting state

- A repository initialized with `sicario init` at SicarioSpec 0.6.0
  (captured with `--profile appsec`), committed to git, hosted on GitHub,
  with `sicario verify .` passing locally.
- A shell with Python 3.9+ and the SicarioSpec CLI installed. If `sicario`
  is not on your PATH, use `python3 -m sicario_cli.cli` — for example
  `python3 -m sicario_cli.cli verify .`.
- Permissions to push branches and open pull requests on the repository.

Assumed platform: macOS or Linux with a POSIX shell and git. GitHub Actions
behavior is platform-independent.

## Steps

### 1. Confirm the workflow is present — or wire it in

`sicario init` installs the CI workflow for you. Check:

```bash
cat .github/workflows/sicario-verify.yml
```

```yaml title="Verified output" sicario-output=verified sicario-block=wire-ci/step-1
name: sicario-verify

on:
  pull_request:
  merge_group:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  verify:
    name: SicarioSpec verify
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python -m pip install -e .
      - run: sicario verify .
```

If the file is absent — a brownfield repository that adopted SicarioSpec
without a full init, or a repo that pruned its workflows — copy the shipped
template from the SicarioSpec source, `workflow_templates/sicario-verify.yml`,
into place:

```bash
mkdir -p .github/workflows
cp <path-to-sicario-spec-checkout>/workflow_templates/sicario-verify.yml .github/workflows/
```

(Replace `<path-to-sicario-spec-checkout>` with wherever you cloned or
installed SicarioSpec from. The template is identical to the file shown
above.)

### 2. Read the workflow before trusting it

Four facts matter:

- **Triggers**: `pull_request`, `merge_group`, and `push` to `main` — the
  gate runs before merge, inside merge queues, and on what actually landed.
- **Permissions**: `contents: read` only. The job can read the checkout and
  nothing else — no token with write scope is exposed to the gate.
- **The gate step is `sicario verify .`** — the last `run:` line. It exits
  `0` on a clean repository and non-zero when any finding exists, and that
  exit code alone is what fails the job. There is no separate reporting
  layer to disagree with your local run: CI red means the same command you
  run locally would be red.
- **The install step assumes `sicario` becomes available.** As shipped,
  `python -m pip install -e .` installs *your* project; the `sicario` CLI
  is then present only if your project declares `sicario-spec` as a
  dependency (or the repo is SicarioSpec itself). If neither holds, pin
  the release the repository is governed by:

```yaml
      - run: python -m pip install "git+https://github.com/dfirs1car1o/sicario-spec.git@v0.6.0"
```

  Pinning matters: an unpinned install can pull a newer gate whose findings
  differ from the version your repository was authored against.

### 3. Commit, push, and watch the first green check

```bash
git add .github/workflows/sicario-verify.yml
git commit -m "ci: add sicario-verify gate"
git push
```

Open a pull request for any branch after this lands on your default branch.
The **Checks** panel on the PR shows `sicario-verify / SicarioSpec verify`.
This surface is graphical — the capture below comes from the reference
repository's Actions run.

:::info Tool capture pending
`docs/assets/guides/wire-ci/pr-checks-panel--v0.6.0.png` — capture class
**tool-captured** (FR-030b): the pull-request checks panel showing the
`sicario-verify` check. Awaits the hosted reference-run repository's real
Actions run; GitHub Actions cannot execute in the local capture
environment, and fabricating the surface is prohibited. The local-verify
equivalents below are the text-class captures from the same reference run.
:::

### 4. Stage a failing finding and watch the check go red

On a branch, deliberately break one governed invariant — delete the threat
model (`git` restores it in step 5, and nothing secret-shaped is involved):

```bash
git checkout -b demo/red-gate
rm docs/security/threat-model.md
git commit -am "demo: stage a failing gate"
git push -u origin demo/red-gate
```

Open a pull request from `demo/red-gate`. The `sicario-verify` check fails.
What CI ran is exactly what you can run locally; the job log's final step
shows:

```bash
sicario verify .
```

```text title="Verified output" sicario-output=verified sicario-block=wire-ci/step-4
HIGH SICARIO-MISSING-THREAT-MODEL docs/security/threat-model.md: Missing docs/security/threat-model.md
sicario verify failed with 1 finding(s)
```

The command exits `1`, the step fails, and the job — therefore the check —
goes red. Each finding line reads: severity, finding code, path, message.

:::info Tool capture pending
`docs/assets/guides/wire-ci/ci-run-failing--v0.6.0.png` — capture class
**tool-captured**: the Actions run view of the failing `SicarioSpec verify`
job with the finding line visible in the log. Awaits the hosted
reference-run repository's real Actions run (same reason as step 3's
capture).
:::

### 5. Fix and re-run to green

Restore the file and push; the check re-runs automatically:

```bash
git checkout main -- docs/security/threat-model.md
git commit -am "demo: restore threat model"
git push
```

The local equivalent of what CI now runs:

```bash
sicario verify .
```

```text title="Verified output" sicario-output=verified sicario-block=wire-ci/step-5
sicario verify passed
```

Exit code `0`; the `sicario-verify` check on the pull request turns green.

:::info Tool capture pending
`docs/assets/guides/wire-ci/ci-run-passing--v0.6.0.png` — capture class
**tool-captured**: the Actions run view of the passing `SicarioSpec verify`
job. Awaits the hosted reference-run repository's real Actions run.
:::

### 6. Know where the evidence artifacts land in CI

Every `sicario verify .` run — in CI exactly as locally — writes two
evidence files into the checkout it verified:

- `generated/sicario/gate-summary.json` — verdict, findings, and the
  `scan_coverage` record (see
  [Read gate evidence as a reviewer](./read-evidence-as-reviewer.md)).
- `generated/sicario/spec-run-evidence.json` — the evidence-path index.

In CI these land in the **runner's workspace** and disappear with it: the
shipped template deliberately does not upload them, because the check's
verdict is the exit code and the log carries the finding lines. If your
review process wants the evidence retained per run, add an upload step —
an optional addition to the template, not shipped behavior:

```yaml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: sicario-evidence
          path: generated/sicario/
```

`if: always()` matters — the evidence of a *failing* run is the copy
reviewers most need.

### 7. Make the check required

A green check that can be ignored is advisory, not a gate. In the
repository settings, add `SicarioSpec verify` to the required status checks
for your protected branch, so merging is blocked while the gate is red.
See [repository settings](../repository-settings.md) for the repository's
recommended protection posture.

## Success check

You are done when all of the following hold:

1. `.github/workflows/sicario-verify.yml` exists on the default branch and
   its final step is `sicario verify .`.
2. A pull request that deletes `docs/security/threat-model.md` shows the
   `sicario-verify` check red, and the job log contains the
   `SICARIO-MISSING-THREAT-MODEL` finding line.
3. Restoring the file turns the same check green without any workflow
   change.
4. The check is listed as required on the protected branch.

## About the output quoted in this playbook

Every quoted block above is labeled `verified` (re-executable and compared
against a real run) or `illustrative` (representative). Terminal output was
captured from a reference run on a net-new repository (`refrun-ci`, run
date 2026-07-28, SicarioSpec 0.6.0, module form `python3 -m sicario_cli.cli`
from the source checkout), with working-directory paths normalized to
`~/work/<repo>`. The three GitHub Actions surfaces are graphical and carry
pending tool-captured asset slots (named above per the asset convention)
until the hosted reference-run repository's real Actions run supplies them;
no step depends on those images.
