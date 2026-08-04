---
title: "Advanced Track: Graph And Loop Engineering"
sidebar_label: "Advanced Track"
guide-slug: advanced-track
captured-version: 0.6.0
reference-run-repository: "(in-repo: examples/spec-graph helper runs)"
reference-run-date: "2026-08-04"
---

# Advanced Track: Graph And Loop Engineering

The [six lessons](start-here.md) take you from nothing to a merge-blocking
gate, a spec a reviewer would accept as analysis, and the ability to read a
green run's own evidence. That is the whole adoption path, and for most
readers it is enough.

This track is what comes after, and it is **optional**. It answers a
different question: not "what belongs in this section?" but **"where does the
substance come from at all?"** Instead of walking the template and asking
what to write, you build a typed graph of the feature and apply fixed
traversal rules that mechanically emit obligations — abuse cases, control
requirements, classification rows, evidence rows, owners — and then iterate
that traversal until it stops producing new ones.

**Two playbooks, about two to three hours.** Take them in order.

## Before You Start

**Prerequisite: Lessons 1–6, with Lesson 5 as a hard prerequisite.**

Both playbooks name spec sections by the names
[Lesson 5](../playbooks/spec-authoring.md) teaches, and both lean on the
thing Lesson 5 exists to establish: that `sicario verify` checks
**completeness of form, not quality of thinking**, on purpose. Every step in
this track states what the gate checks there, and for almost all of them the
honest answer is **nothing**. If you have not internalized why that is a
feature rather than a defect, the track will read as a critique of the tool
instead of as the work the tool deliberately leaves to you.

You will also want [Lesson 3](../playbooks/first-spec.md) fresh, because the
loop playbook mirrors its gate-as-checkpoint rhythm at a different altitude.

Everything in this track is on the **authoring** side. It changes nothing
about `sicario verify`, adds no rule, no finding code, and no required
section, and introduces no Python dependency. The helper it uses is standard
library only, renders no verdict, and always exits `0`.

## The Path

### Lesson A1 — Graph engineering

**[Deriving a spec from a model of the system](../playbooks/graph-engineering.md)**
· 60–90 minutes

Build a typed graph — nodes with a kind, a zone, and attributes; directed
labelled edges — starting from the `docs/diagrams/system-context.mmd` your
own `sicario init` already shipped. Learn the load-bearing idea: a trust
boundary is not a node, it is the `zone` attribute, and a boundary crossing
is the computed predicate `crosses(edge) ⟺ zone(src) ≠ zone(dst)` — which
turns a judgement call into a set operation. Then run the traversal rules
R1–R13 as a repeatable procedure, build the **obligation ledger** (element →
rule → abuse case → requirement → negative test → evidence → owner, no blank
cells), and read the **gap list** — the class of omission a deterministic
gate structurally cannot compute.

Worked in full on a SaaS-to-SaaS connector, motivated by the Salesloft Drift
compromise; the cloud scenario appears in outline. Includes the
tenant-substitution drill, the commonly-omitted-nodes list, and the
cycle-blindness drill that shows one missing edge silently deleting an entire
abuse case.

### Lesson A2 — Loop engineering

**[Iterating a graph until it stops producing findings](../playbooks/loop-engineering.md)**
· 60–90 minutes

One traversal is a snapshot, and the interesting findings change the graph.
This playbook is the discipline around that: three nested loops — **L1**,
four fixed questions per crossing edge; **L2**, adversarial one-hop
propagation that is *allowed to mutate the graph*; **L3**, the outer
convergence loop — with a mechanical stopping rule (a pass that adds no node,
no edge, and no spec line is **dry**), two guards against stopping too early
and never stopping, and a **traversal log** committed as reviewer-facing
evidence with its Tier-2 status stated plainly.

Worked in full on a regulated cloud export path — the reverse-path rule, the
`can_assume` escalation cycle into the control plane, and the deploy-closure
blast radius — and revisits the connector's webhook cycle.

## A Note About The Name

"Graph engineering" as a term of art is a few weeks old and began as a joke:
it surfaced in a tweet in mid-July 2026 and was satirized the same day
("Loop Engineering Is Dead. Enter Graph Engineering"), itself a riff on "loop
engineering", which had been popularized only that June. This track uses both
names because they are what people are currently searching for, and says
plainly that the names are new, faintly silly, and not the point.

The substance is decades old. John Lambert's "defenders think in lists,
attackers think in graphs" is from 2015 and carries a worked credential-graph
traversal that predates BloodHound. Threagile walks a model's communication
links across trust boundaries and fires rules identified by the path that
produced them. MITRE D3FEND publishes fourteen thousand verb-typed mapping
rows joining defensive techniques to artifacts to attack techniques. DO-178C
has mandated bidirectional traceability since 2011. When the vocabulary is
renamed again in six months, nothing in these two playbooks changes — which
is the main reason to learn the substance under the label rather than the
label.

## What This Track Is Not

It is not a completeness claim, and both playbooks say so in the same words:

> A graph-derived spec is not thereby complete, verified, or certified: the
> graph determines relevance and depth, never the gate's required form, and
> an inapplicable concern still receives an explicit rationale.

The graph bounds the analysis, and the graph is something a human drew.
Neither playbook introduces a second authority: `sicario verify` remains the
sole authority on pass and fail, and the helper you run in both is an
authoring aid that emits a checklist and a gap list, never a judgement.

It is also not an invitation to publish your model:

> A graph of a real system is a map of its attack surface: treat it as
> sensitive, keep it out of public repositories, and publish only synthetic
> examples.

The two example graphs shipped at `examples/spec-graph/` are synthetic and
every credential-ish value in them is an angle-bracketed placeholder. Yours
will not be.

## Where To Go Back To

- [Start here: six lessons](start-here.md) — the adoption path this track
  sits after. If you have not finished it, finish it first.
- [Lesson 5 · Write a spec worth reviewing](../playbooks/spec-authoring.md) —
  the hard prerequisite.
- `examples/spec-graph/README.md` in the SicarioSpec repository — the graph
  schema, the helper's contract, and both example graphs in full.
