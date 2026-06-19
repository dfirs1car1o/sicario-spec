# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`
**Created**: [DATE]
**Status**: Draft
**Input**: User description: "$ARGUMENTS"

## User Scenarios & Testing

### User Story 1 - [Brief Title] (Priority: P1)

[Describe the independently testable user journey.]

**Why this priority**: [Business/security value]

**Independent Test**: [How this story can be tested alone]

## Data Classification

- Data types processed:
- Highest classification: Public / Internal / Confidential / Restricted / Regulated
- Classification owner:
- Regulated data involved: none / PII / PHI / PCI / SOX / export-controlled / customer confidential / other
- Data retention and deletion expectations:
- Data residency or sovereignty constraints:
- Scanner output, SBOM, finding, and evidence sensitivity:
- Redaction or masking requirements:

## Tagging Discipline

- Required metadata tags: owner, system, environment, data-classification, retention, compliance-scope
- Toolchain tags: scanner, scan-type, artifact-type, evidence-path, control-id
- Finding tags: severity, risk-id, exception-id, remediation-owner, due-date
- Accepted values source: `docs/governance/tagging-taxonomy.md`
- Enforcement location: plan review / policy-as-code / CI / `sicario verify`

## Trust Boundaries

- User/input boundary:
- Service/API boundary:
- External system boundary:
- Generated/model output boundary:

## Security Requirements

- Authentication:
- Authorization:
- Input validation:
- Output handling:
- Audit logging:
- Secure error handling:

## Toolchain Requirements

- Secret scanning:
- SAST/static checks:
- Dependency/SCA:
- SBOM:
- Container scan:
- IaC scan:
- Policy-as-code:
- Evidence artifact locations:

## Misuse / Abuse Cases

- Abuse case 1:
- Abuse case 2:
- Abuse case 3:

## Evidence To Produce

- Threat model update:
- Abuse-case update:
- Data classification record:
- Tagging taxonomy updates:
- Toolchain results:
- Gate summary:
- Reviewer approval:
