# SicarioSpec Core

SicarioSpec Core is an evidence-first security operations preset for Spec Kit.
It turns a feature idea into a traceable chain of security decisions, controls,
tests, gates, evidence, owners, and human approval points.

Use it when a project needs to prove what changed, what could go wrong, what
control covers the risk, what gate verifies the control, where the evidence
lives, and who owns the decision before release.

## Security Evidence Chain

The core concept is a lightweight evidence chain:

```text
feature intent
-> data classification
-> trust boundary
-> abuse case
-> control or requirement
-> test or gate
-> evidence artifact
-> owner / reviewer
-> approval or accepted risk
```

This gives security, engineering, and operations teams a shared handoff record.
The preset does not claim compliance or certification. It creates the traceable
artifact structure a team can use to support review, assurance, incident
readiness, and audit conversations.

## What Makes It Different

Other security and architecture presets tend to focus on secure coding
standards, regulatory applicability, threat-modeling methods, architecture
decision records, or supply-chain transparency. SicarioSpec Core is narrower:
it focuses on operational proof. Every major security concern should resolve to
a control, test/gate, evidence path, owner, and approval or accepted-risk state.

## What It Provides

- Feature specification template with data classification, tagging, abuse-case,
  security requirement, operational signal, and evidence-chain sections.
- Implementation plan template with threat model, rollback, control mapping, and
  well-architected review sections.
- Task template that turns security, compliance, documentation, evidence, and
  verification work into explicit delivery tasks.
- Checklist template for spec, plan, task, and verification review.
- Constitution template for least privilege, deterministic authority, evidence
  integrity, trust-boundary sanitization, quality gates, and human approval.

## Use It When

- Security work keeps getting discussed but not traced to delivery evidence.
- Teams need a common handoff between product, engineering, security, and
  operations.
- Reviews need to answer "what proves this control worked?" before merge or
  release.
- Incident-response readiness matters and features need logging, detection,
  alerting, ownership, and rollback decisions captured early.

## Do Not Use It When

- You only need secure coding language profiles, SBOM/VEX detail, or regulatory
  applicability templates.
- You only need deep architecture methods such as STRIDE/CAPEC matrices,
  security ADRs, or Zero Trust applicability.
- You are building a throwaway prototype and do not intend to maintain evidence.

## Local Development Install

From a Spec Kit project root:

```bash
specify preset add --dev /path/to/sicario-spec/presets/sicario-core
specify preset resolve spec-template
specify preset info sicario-core
```

## Catalog Install

After a release publishes the preset ZIP asset:

```bash
specify preset add --from https://github.com/dfirs1car1o/sicario-spec/releases/download/vX.Y.Z/sicario-core-X.Y.Z.zip
```

## Notes

This preset is the baseline governance layer. The broader SicarioSpec repository
also includes optional profiles for AppSec, AI systems, agent fleets, cloud IaC,
security tooling, supply chain, compliance, docs, and enterprise change control.
Those profiles remain separate so teams can compose only the controls they need.
