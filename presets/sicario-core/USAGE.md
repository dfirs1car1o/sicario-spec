# SicarioSpec Core Usage

This guide is the second step after installing `sicario-core`. The README is the
landing page; this document explains how to use the preset in day-to-day
Spec Kit work.

## Workflow

1. Write the feature spec with classification, trust boundaries, abuse cases,
   operational signal paths, security acceptance criteria, and evidence outputs.
2. Build the implementation plan by mapping risks and decisions to controls,
   gates, owners, rollback, and evidence paths.
3. Generate tasks that make tests, scans, evidence production, documentation,
   and human review explicit work items.
4. Use the checklist before merge or release to verify the evidence chain is
   complete.
5. Record approval or accepted risk when a control is not implemented, a gate is
   waived, or a high-impact change needs human authorization.

## Template Impact

| Template | What It Adds |
| --- | --- |
| `spec-template` | Data classification, tagging, roles/assets/abuse actors, trust boundaries, security requirements, control applicability, AI/tool risk, external access, secrets handling, audit/logging requirements, operational signal paths, misuse cases, and evidence expectations. |
| `plan-template` | Threat model, Security Evidence Chain, security decision record, Well-Architected Review, authn/authz design, data flow, supply chain, cloud/IaC risk, AI/tool boundary, operational readiness, CI/security gates, rollback, evidence outputs, and human approval points. |
| `tasks-template` | Security foundation tasks, negative/security tests, authorization boundary tests, audit logging tasks, operational signal tasks, evidence generation, verification gates, documentation impact, and human review. |
| `checklist-template` | Review checks for classification, tagging, trust boundaries, abuse cases, evidence chain quality, threat model, rollback, approval, scans, static checks, and verification. |
| `constitution-template` | Project principles for least privilege, deterministic authority, evidence integrity, trust-boundary sanitization, source-of-truth authority, quality gates, architecture discipline, operability, documentation integrity, and human-gated high-impact changes. |

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

## Operating Model

Every meaningful security concern should resolve to:

- a risk or decision
- a control or requirement
- a test or gate
- an evidence path
- an owner or reviewer
- an approval or accepted-risk state

That gives product, engineering, security, compliance, and operations teams the
same handoff record without requiring a custom command surface.
