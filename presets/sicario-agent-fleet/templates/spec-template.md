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
- Highest classification: Public / Internal / Confidential / Restricted / Regulated
- Classification owner:
- Regulated data involved: none / PII / PHI / PCI / SOX / export-controlled / customer confidential / other
- Data retention and deletion expectations:
- Data residency or sovereignty constraints:
- Sharing, egress, or third-party disclosure:
- Redaction or masking requirements:
- Agent memory, queue, trace, or transcript sensitivity:

## Tagging Discipline

- Required metadata tags: owner, system, environment, data-classification, retention, compliance-scope
- Fleet tags: workflow-id, agent-id, queue-topic, tenant, approval-boundary
- Evidence tags: feature-id, control-id, risk-id, exception-id where applicable
- Accepted values source: `docs/governance/tagging-taxonomy.md`
- Enforcement location: plan review / policy-as-code / CI / `sicario verify`

## Roles, Assets, And Abuse Actors

- Legitimate roles:
- Protected assets:
- Abuse actors:
- High-impact actions:
- Autonomous actors, workers, or agents:

## Trust Boundaries

- User/input boundary:
- Service/API boundary:
- External system boundary:
- Generated/model output boundary:
- Queue, event, or worker boundary:
- Orchestration state boundary:

## Security Requirements

- Authentication:
- Authorization:
- Input validation:
- Output handling:
- Audit logging:
- Rate limiting / abuse prevention:
- Secure error handling:

## Fleet / Orchestration Risk

Complete this section for LangGraph-style state graphs, Temporal-style durable
workflows, Ray/Celery-style distributed execution, queues, workers, MCP tool
fleets, SOAR playbooks, or multi-agent systems.

- Orchestration pattern:
- Workflow state source of truth:
- Agent/worker identity model:
- Tool and action allowlist:
- Queue/topic/event inputs:
- Retry policy:
- Idempotency controls:
- Dead-letter and poison-message handling:
- Backpressure and concurrency limits:
- Human approval boundaries:
- Production write boundaries:
- Rollback or compensation actions:
- Observability and trace correlation:
- Tenant, account, or environment isolation:

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
- **SA-004**: Orchestrated work MUST be idempotent or explicitly compensating.
- **SA-005**: High-impact autonomous actions MUST require human approval.

## Evidence To Produce

- Threat model update:
- Abuse-case update:
- Data classification record:
- Tagging taxonomy updates:
- Workflow/state graph:
- Queue and worker inventory:
- Tests:
- Gate summary:
- Control applicability:
- Reviewer approval:

## Success Criteria

- **SC-001**: [Measurable outcome]

## Assumptions

- [Assumption]
