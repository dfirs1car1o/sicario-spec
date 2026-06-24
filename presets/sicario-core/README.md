# SicarioSpec Core

SicarioSpec Core is an evidence-first security operations preset for Spec Kit.
It adds secure-by-default governance templates that make feature work show
what changed, what can go wrong, what control covers the risk, what gate proves
the control worked, where the evidence lives, and who approved the decision.

This is the baseline SicarioSpec preset. It provides templates only: no custom
commands, no scripts, and no runtime dependency on the broader SicarioSpec CLI.

## Quick Start

Install the released preset from any Spec Kit project root:

```bash
specify preset add --from https://github.com/dfirs1car1o/sicario-spec/releases/download/v0.5.0/sicario-core-0.5.0.zip
specify preset info sicario-core
specify preset resolve spec-template
```

If you are developing the preset locally:

```bash
specify preset add --dev /path/to/sicario-spec/presets/sicario-core
specify preset info sicario-core
specify preset resolve plan-template
```

If `specify` reports that the directory is not a Spec Kit project, initialize
the project first with `specify init`, then rerun the preset install command.

## What This Preset Changes

SicarioSpec Core replaces the default Spec Kit templates with a security
operations workflow:

| Template | What It Adds |
| --- | --- |
| `spec-template` | Data classification, tagging, roles/assets/abuse actors, trust boundaries, security requirements, control applicability, AI/tool risk, external access, secrets handling, audit/logging requirements, operational signal paths, misuse cases, and evidence expectations. |
| `plan-template` | Threat model, Security Evidence Chain, security decision record, Well-Architected Review, authn/authz design, data flow, supply chain, cloud/IaC risk, AI/tool boundary, operational readiness, CI/security gates, rollback, evidence outputs, and human approval points. |
| `tasks-template` | Security foundation tasks, negative/security tests, authorization boundary tests, audit logging tasks, operational signal tasks, evidence generation, verification gates, documentation impact, and human review. |
| `checklist-template` | Review checks for classification, tagging, trust boundaries, abuse cases, evidence chain quality, threat model, rollback, approval, scans, static checks, and verification. |
| `constitution-template` | Project principles for least privilege, deterministic authority, evidence integrity, trust-boundary sanitization, source-of-truth authority, quality gates, architecture discipline, operability, documentation integrity, and human-gated high-impact changes. |

## What Makes It Different

Most security presets focus on secure coding rules, compliance mappings,
threat-modeling technique, architecture records, or supply-chain transparency.
Those are useful, but they do not always prove that a feature was operated
safely.

SicarioSpec Core is narrower and more operational. It focuses on operational proof:
each meaningful risk or decision should map to a control, a test or gate, an
evidence path, an owner, and an approval or accepted-risk state.

## Security Evidence Chain

The core operating model is the Security Evidence Chain:

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

Every meaningful security concern should resolve to a control, a gate, an
evidence path, an owner, and an approval or accepted-risk state. That gives
product, engineering, security, compliance, and operations teams the same
handoff record.

## Workflow

1. Write the feature spec with classification, trust boundaries, abuse cases,
   operational signal paths, security acceptance criteria, and evidence outputs.
2. Build the implementation plan by mapping risks and decisions to controls,
   gates, owners, rollback, and evidence paths.
3. Generate tasks that make tests, scans, evidence production, documentation,
   and human review explicit work items.
4. Use the checklist before merge or release to verify the chain is complete.
5. Record approval or accepted risk when a control is not implemented, a gate
   is waived, or a high-impact change needs human authorization.

## Use It When

- Security work keeps getting discussed but not traced to delivery evidence.
- Teams need a shared handoff between product, engineering, security, and
  operations.
- Reviews need to answer "what proves this control worked?" before merge or
  release.
- Incident-response readiness matters and features need logging, detection,
  alerting, ownership, and rollback decisions captured early.
- A project needs better governance without adding a custom command surface.

## Do Not Use It When

- You only need secure coding language profiles, SBOM/VEX detail, or regulatory
  applicability templates.
- You only need deep architecture methods such as STRIDE/CAPEC matrices,
  security ADRs, or Zero Trust applicability.
- You need a fully automated compliance engine. This preset creates structured
  evidence prompts; it does not certify compliance.
- You are building a throwaway prototype and do not intend to maintain evidence.

## Verify Installation

After installing, these commands should show that the SicarioSpec templates are
active:

```bash
specify preset info sicario-core
specify preset resolve spec-template
specify preset resolve plan-template
specify preset resolve tasks-template
specify preset resolve checklist-template
specify preset resolve constitution-template
```

The resolved templates should point to `.specify/presets/sicario-core/`.

## Relationship To The Broader SicarioSpec Repo

The broader SicarioSpec repository includes optional governance material for
application security, AI systems, agent fleets, cloud IaC, security tooling,
supply chain, compliance, documentation, and enterprise change control.

Those materials are intentionally separate from this preset. `sicario-core` is
the small, reviewable Spec Kit preset that installs cleanly through
`specify preset add` and provides the baseline evidence workflow.
