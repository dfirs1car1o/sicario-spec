---
title: "Start Here: Six Lessons"
sidebar_label: "Start here"
guide-slug: start-here
captured-version: 0.6.0
reference-run-repository: "(none — navigation page, no captured output)"
reference-run-date: "2026-07-31"
---

# Start Here: Six Lessons

Everything in this documentation set is real and verified — and there is a
lot of it. You do not need most of it on day one. **Take these six lessons
in order and you are good to go.** Each one builds on the last, states how
long it takes, and ends with something working.

Two notes before Lesson 1: do it in a **throwaway directory** — the real
profile decision is Lesson 2, and a scratch run is what makes deferring it
legitimate. And if you are here to *review* rather than adopt, Lesson 6
alone is your path — it needs only an evidence file, not the toolchain.

## The path

### Lesson 1 — Install it and reach a green gate

**[Getting started: zero to first passing gate](getting-started.md)** · ~30 minutes

Install the CLI, initialize a project, stage a real failure on purpose, read
the finding, fix it, finish green. When you are done you have a working
governed repository and you have seen the gate catch something.

### Lesson 2 — Choose the right profile for your repository

**[Choosing profiles, presets, and frameworks](../playbooks/initial-setup-selection.md)** · ~20 minutes

Lesson 1 used the `appsec` profile on faith. This lesson is the decision you
actually own: which profile fits your repository, what each one installs and
enforces, and which compliance frameworks it selects. Do this before
initializing anything real.

### Lesson 3 — Write your first spec

**[Your first spec](../playbooks/first-spec.md)** · ~30 minutes

The gate exists to judge specs. Copy the template, fill it section by
section, stage a defect so you see a finding fire, reach green. After this
you have done the core loop the whole product is about. Lesson 5 returns
here to teach what the gate *cannot* check about what you wrote.

### Lesson 4 — Put the gate in CI

**[Wire the gate into CI](../playbooks/wire-ci.md)** · ~30 minutes

Extra starting state for this lesson: a git repository hosted on GitHub
with push and pull-request rights — Lesson 1 deliberately did not create
one. Governance that depends on people remembering to run a command is not
governance. Wire the shipped workflow, watch a pull request go red on a
staged failure and green on the fix — with screenshots of exactly what you
should see.

### Lesson 5 — Write a spec worth reviewing

**[Spec authoring: every governance section](../playbooks/spec-authoring.md)** · ~60 minutes

The gate now has teeth, so this is the moment to learn what those teeth
cannot bite. Section by section: what each governance section is for, what
the rule literally checks, and the difference between analysis and
gate-passing filler — including the demonstration that a spec saying "we
did not do the work" passes every rule. The gate catches vocabulary; you
supply substance. This lesson is where that stops being a slogan.

### Lesson 6 — Review a gate you did not run

**[Read evidence as a reviewer](../playbooks/read-evidence-as-reviewer.md)** · ~20 minutes

Someone must be the reader the visibility controls were built for. Handed
only a stranger's `gate-summary.json`: which rules ran, what was disabled
or narrowed and by whom, where the rules were loaded from, what was never
scanned — and the six documented grounds to refuse an approval.

**That's it.** Six lessons, about three hours (a natural split: 1–3, then
4–6), and you can take a repository you own from nothing to a
merge-blocking gate, write a spec a reviewer would accept as analysis
rather than vocabulary, and read a green run's own evidence to say what it
actually checked — and whether anything was weakened.

After that, and strictly optional, there is one more path: the
[Advanced Track: graph and loop engineering](advanced-track.md) · two
playbooks, about two to three hours. It answers a different question from
the six lessons — not "what belongs in this section?" but "where does the
substance come from at all?" — by deriving spec content from a typed graph
of the feature and iterating that derivation until it stops producing new
findings. Its prerequisite is these six lessons, with **Lesson 5 as a hard
prerequisite**: every step states what the gate checks there, and the honest
answer is almost always "nothing", which only reads as a feature if you have
already done Lesson 5. Skip it entirely if you are here to adopt; come back
when the question above starts to bother you.

## When you need it

The remaining playbooks are task-shaped: go to them when their situation is
in front of you, not before. In particular, the first time the gate goes
red for a reason you did not stage, open
[Investigate a failing gate](../playbooks/investigate-failing-gate.md).

| When this happens | Go here |
|---|---|
| Adopting in a repo that already has a constitution or templates | [Brownfield adoption](../playbooks/brownfield-adoption.md) |
| The gate is red and you do not know why | [Investigate a failing gate](../playbooks/investigate-failing-gate.md) |
| You need a project-specific check the shipped rules do not cover | [Add a custom rule](../playbooks/custom-rule.md) |
| A shipped rule is too broad (or too noisy) for your repository | [Override a shipped rule](../playbooks/override-shipped-rule.md) |
| Choosing or changing compliance frameworks after setup | [Select frameworks](../playbooks/select-frameworks.md) |

Reference documentation (every finding code, every rule parameter, every
evidence field) lives in [USAGE.md](https://github.com/dfirs1car1o/sicario-spec/blob/main/USAGE.md)
and [the rule engine guide](../rule-engine.md) — for looking things up, not
for reading through.
