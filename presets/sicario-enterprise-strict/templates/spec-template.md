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

**Acceptance Scenarios**:

1. **Given** [state], **When** [action], **Then** [outcome]

## Data Classification

- Data types processed:
- Sensitivity level:
- Regulated data involved:
- Data retention and deletion expectations:

## Roles, Assets, And Abuse Actors

- Legitimate roles:
- Protected assets:
- Abuse actors:
- High-impact actions:

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
- Rate limiting / abuse prevention:
- Secure error handling:

## Privacy Requirements

- Data minimization:
- Purpose limitation:
- Consent or notice requirements:
- Redaction requirements:

## Compliance / Control Applicability

Map applicable requirements without claiming certification.

| Domain | Applicable? | Rationale | Evidence |
|---|---:|---|---|
| AppSec / ASVS | TBD | TBD | TBD |
| NIST SSDF | TBD | TBD | TBD |
| Supply Chain / SLSA | TBD | TBD | TBD |
| AI Risk / NIST AI RMF | TBD | TBD | TBD |
| Cloud/IaC | TBD | TBD | TBD |

## AI / LLM Risk

Complete this section if the feature uses AI, agents, RAG, model output, MCP,
tool calling, autonomous workflows, or generated code.

- Prompt injection exposure:
- Tool boundary controls:
- Model routing:
- Memory poisoning risk:
- Data leakage risk:
- Human approval boundaries:
- AI evals / red-team tests:

## External System Access

- External systems:
- Read/write permissions:
- Production impact:
- Human approval needed:

## Secrets / Credential Handling

- Secret sources:
- Runtime injection method:
- Redaction requirements:
- Rotation owner:

## Audit / Logging Requirements

- Events to log:
- Fields to exclude:
- Retention:
- Alerting:

## Misuse / Abuse Cases

- Abuse case 1:
- Abuse case 2:
- Abuse case 3:

## Functional Requirements

- **FR-001**: System MUST [specific capability]
- **FR-002**: System MUST [specific capability]

## Security Acceptance Criteria

- **SA-001**: [Measurable security outcome]
- **SA-002**: [Negative test outcome]
- **SA-003**: [Evidence outcome]

## Evidence To Produce

- Threat model update:
- Abuse-case update:
- Tests:
- Gate summary:
- Control applicability:
- Reviewer approval:

## Success Criteria

- **SC-001**: [Measurable outcome]

## Assumptions

- [Assumption]

