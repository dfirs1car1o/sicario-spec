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

## Tagging Plan

- Required tags:
- Accepted values source: `docs/governance/tagging-taxonomy.md`
- Cloud/IaC tagging enforcement:
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

## Security Evidence Chain

Use this table as the delivery handoff between engineering, security, and
operations. Every high-impact decision, accepted risk, or material control should
have a chain entry.

| Chain ID | Risk / Decision | Control / Requirement | Test / Gate | Evidence Path | Owner | Approval / Accepted Risk |
|---|---|---|---|---|---|---|
| SEC-001 | TBD | TBD | TBD | TBD | TBD | TBD |

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

## Authn / Authz Design

- Identity source:
- Authorization checks:
- Privilege boundaries:
- Negative tests:

## Data Flow And Trust Boundaries

```text
actor -> boundary -> component -> boundary -> data/evidence/output
```

## Supply Chain

- New dependencies:
- Dependency review:
- SBOM impact:
- Pinned actions/images:
- Build provenance:

## Cloud / IaC Risk

- IAM:
- Network exposure:
- Encryption:
- Secrets:
- Logging:
- Drift/policy checks:

## AI / Tool Boundary

- Prompt injection controls:
- Tool allowlist:
- Model routing:
- Memory controls:
- Human approval gates:
- Evals/red-team tests:

## Operational Readiness

- Required telemetry:
- Detection or alert rule:
- Triage and response owner:
- Runbook or rollback link:
- Evidence retention:

## Test Strategy

- Unit tests:
- Integration tests:
- Negative/security tests:
- Regression tests:
- Offline test constraints:

## CI / Security Gates

- Lint/type gates:
- Secret scan:
- SAST:
- Dependency/SCA:
- IaC/container scan:
- Project verification gate:
- Optional SicarioSpec verification if installed:

## Rollback

- Rollback trigger:
- Revert steps:
- Data migration rollback:
- Evidence of rollback readiness:

## Evidence Outputs

- Threat model:
- Abuse cases:
- Data classification register:
- Tagging taxonomy:
- Control applicability:
- Evidence index:
- Security Evidence Chain:
- Gate summary:
- Reviewer approval:

## Human Approval Points

- Production write:
- External system write:
- Security exception:
- Release:

## Constitution Check

| Principle | Status | Evidence |
|---|---|---|
| Least privilege | TBD | TBD |
| Deterministic authority | TBD | TBD |
| Evidence integrity | TBD | TBD |
| Security Evidence Chain | TBD | TBD |
| Trust-boundary sanitization | TBD | TBD |
| Source-of-truth authority | TBD | TBD |
| Quality gates | TBD | TBD |
| Architecture discipline | TBD | TBD |
| Well-architected review | TBD | TBD |
| Operability and resilience | TBD | TBD |
| Honest documentation | TBD | TBD |

## Project Structure

[Describe real files and directories.]
