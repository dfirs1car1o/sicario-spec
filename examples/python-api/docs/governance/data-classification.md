# Data Classification — Customer Invoice Export API

The exported invoice payload is **confidential** customer billing data.

## Levels

| Level | Description | Examples | Minimum Handling |
|---|---|---|---|
| Public | Approved for public release | API docs | Source review before publication |
| Internal | Internal operational data | request metrics | Repository access controls |
| Confidential | Customer/business-sensitive data | invoice bodies, billing detail | Need-to-know access and redaction |
| Restricted | Secrets, tokens, credentials | datastore credentials | Do not commit; secret manager only |

## Register

| Asset / Flow | Owner | Classification | Regulated Data | Retention | Residency | Sharing / Egress | Redaction | Evidence |
|---|---|---|---|---|---|---|---|---|
| Invoice export payload | @finance-platform | Confidential | none | Not persisted | us-east | Authorized caller only | Account numbers masked in logs | generated/sicario/gate-summary.json |
| Export request logs | @finance-platform | Internal | none | 90d | us-east | Internal observability | No invoice bodies | generated/sicario/gate-summary.json |

## Rules

- Confidential payloads must not enter logs, traces, or error bodies.
- Datastore credentials are Restricted and live only in the runtime secret
  manager — never in git, logs, or LLM context.
