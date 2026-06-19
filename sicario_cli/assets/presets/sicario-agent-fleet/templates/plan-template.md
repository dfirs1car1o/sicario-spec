# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

## Summary

[Extract primary requirement and implementation approach.]

## Technical Context

**Language/Version**: [TBD]
**Primary Dependencies**: [TBD]
**Storage**: [TBD]
**Testing**: [TBD]
**Target Platform**: [TBD]
**Project Type**: [TBD]

## Data Classification And Handling

- Highest classification:
- Classification owner:
- Regulated data:
- Retention and deletion:
- Residency constraints:
- Sharing and third-party disclosure:
- Redaction, masking, or tokenization:
- Agent memory, queue, trace, or transcript controls:

## Tagging Plan

- Required tags:
- Accepted values source: `docs/governance/tagging-taxonomy.md`
- Workflow, agent, queue, tenant, and approval-boundary tags:
- Evidence, risk, and exception tag mapping:
- Temporary resource expiration tags:

## Threat Model

- Assets:
- Entry points:
- Trust boundaries:
- Threat actors:
- Abuse cases:
- Required controls:
- Residual risks:

## Architecture / Security Decision Record

- Decision:
- Alternatives:
- Security tradeoffs:
- Approval needed:

## Well-Architected Review

- Operational excellence:
- Security:
- Reliability:
- Performance efficiency:
- Cost optimization:
- Sustainability:
- Tradeoffs accepted:

## Orchestration Design

- Orchestrator or framework:
- Workflow topology:
- State graph or process definition:
- Durable state store:
- Queue, topic, or event sources:
- Worker pools:
- Concurrency limits:
- Timeout policy:
- Retry policy:
- Dead-letter handling:
- Idempotency key strategy:
- Compensation or rollback steps:

## Fleet Identity And Permissions

- Agent/worker identities:
- Tool/action allowlist:
- External write permissions:
- Environment and tenant isolation:
- Credential injection:
- Credential rotation:
- Least-privilege tests:

## Human Approval And Break-Glass

- Actions requiring approval:
- Approval evidence location:
- Emergency stop or kill switch:
- Break-glass owner:
- Audit trail:

## Data Flow And Trust Boundaries

```text
event -> queue/state -> orchestrator -> worker/agent -> tool/action -> evidence
```

## Supply Chain

- New dependencies:
- Dependency review:
- SBOM impact:
- Pinned actions/images:
- Build provenance:

## AI / Tool Boundary

- Prompt injection controls:
- Tool allowlist:
- Model routing:
- Memory controls:
- Human approval gates:
- Evals/red-team tests:

## Test Strategy

- Unit tests:
- Integration tests:
- Negative/security tests:
- Retry/idempotency tests:
- Poison-message/dead-letter tests:
- Concurrency/backpressure tests:
- Approval-gate tests:
- Regression tests:
- Offline test constraints:

## CI / Security Gates

- Lint/type gates:
- Secret scan:
- SAST:
- Dependency/SCA:
- IaC/container scan:
- SicarioSpec verification:

## Rollback

- Rollback trigger:
- Revert steps:
- Compensation workflow:
- Data migration rollback:
- Evidence of rollback readiness:

## Evidence Outputs

- Threat model:
- Abuse cases:
- Data classification register:
- Tagging taxonomy:
- Workflow/state graph:
- Queue and worker inventory:
- Control applicability:
- Evidence index:
- Gate summary:
- Reviewer approval:

## Human Approval Points

- Production write:
- External system write:
- Security exception:
- Autonomous remediation:
- Release:

## Constitution Check

| Principle | Status | Evidence |
|---|---|---|
| Least privilege | TBD | TBD |
| Deterministic authority | TBD | TBD |
| Evidence integrity | TBD | TBD |
| Trust-boundary sanitization | TBD | TBD |
| Source-of-truth authority | TBD | TBD |
| Quality gates | TBD | TBD |
| Architecture discipline | TBD | TBD |
| Well-architected review | TBD | TBD |
| Operability and resilience | TBD | TBD |
| Honest documentation | TBD | TBD |

## Project Structure

[Describe real files and directories.]
