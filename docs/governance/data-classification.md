# Data Classification

SicarioSpec treats data classification as a release and review gate. Specs,
plans, logs, evidence, examples, diagrams, scanner output, model prompts, model
outputs, queues, traces, and packaged artifacts must identify the highest
classification they carry.

## Levels

| Level | Description | Examples | Minimum Handling |
|---|---|---|---|
| Public | Approved for public release | README, public docs, synthetic examples | Source review before publication |
| Internal | Internal project or operational data | backlog notes, generated evidence summaries | Repository access controls |
| Confidential | Business, customer, or security-sensitive data | private architecture, customer config | Need-to-know access and redaction |
| Restricted | Highly sensitive security, credential, or vulnerability data | secrets, tokens, private vuln details | Do not commit; approved secure storage only |
| Regulated | Data under legal, contractual, or audit scope | PII, PHI, PCI, SOX evidence | Control mapping, retention, and reviewer approval |

## Repository Register

| Asset / Flow | Owner | Classification | Regulated Data | Retention | Residency | Sharing / Egress | Redaction | Evidence |
|---|---|---|---|---|---|---|---|---|
| Source code and templates | Maintainers | Public | none | Per release | N/A | Public GitHub release | Secrets excluded | Git history |
| Generated gate evidence | Maintainers | Internal | none by default | Per run | N/A | Repository collaborators | Findings reviewed before publication | generated/sicario/gate-summary.json |
| Security reports and scanner output | Security owner | Internal or higher | vulnerability metadata possible | Per finding | N/A | Maintainers / advisory flow | Private details redacted publicly | GitHub Security / Actions |
| Release distributions | Maintainers | Public | none | Per release | N/A | Public GitHub release | Built from reviewed source | GitHub release assets |

## Rules

- Restricted data and secrets must not enter git, logs, generated artifacts, or
  LLM context.
- Public examples must use synthetic values only.
- Evidence carries the same or higher classification as the source data it
  summarizes.
- Any feature that handles customer, tenant, vulnerability, credential, model
  context, audit, or regulated data needs explicit owner, retention, residency,
  sharing, and redaction decisions.
