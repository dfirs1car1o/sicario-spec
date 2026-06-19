# Documentation Requirements Addendum

Every feature must state whether it changes user-facing behavior, internal
operations, architecture, threat boundaries, controls, or generated artifacts.

Required sections in the resolved feature spec:

- Data classification and tagging impact
- Documentation impact
- Public docs impact
- Contributor/operator docs impact
- Diagram impact
- Evidence impact

## Documentation Data Classification

- Highest classification represented in docs, diagrams, examples, screenshots, logs, or evidence:
- Classification owner:
- Redaction or masking requirements:
- Retention and deletion expectations:
- External publication or sharing constraints:

## Documentation Tagging Discipline

- Required tags: owner, system, audience, data-classification, doc-type, lifecycle
- Evidence tags: feature-id, control-id, risk-id, exception-id where applicable
- Accepted values source: `docs/governance/tagging-taxonomy.md`
- Enforcement location: docs review / CI / `sicario verify`
