# Feature Specification: Customer Invoice Export API

A small, fully-worked SicarioSpec example. This spec is intentionally complete:
every governance section the deterministic gate requires is filled in with
realistic content. Running `sicario verify examples/python-api` against this
directory returns `status: pass`.

## User Scenarios & Testing

An authenticated finance user calls `GET /api/v1/invoices/{id}/export` to
download a single customer invoice as PDF. Admins may export any invoice; a
standard user may only export invoices owned by their own organization. The
endpoint is read-only: it never creates, mutates, or deletes invoice records.

- **Primary**: finance user exports an invoice they are authorized to see.
- **Authz boundary**: standard user is denied an invoice from another org.
- **Anonymous**: unauthenticated request is rejected with 401.

## Data Classification

The export payload contains customer billing detail (names, amounts, line
items) and is therefore handled as **confidential**.

- **Classification level**: confidential.
- **Classification owner**: Finance Platform team (owner: `@finance-platform`).
- **Regulated data**: none (no PII beyond business contact; no PHI/PCI/SOX
  evidence is produced by this endpoint).
- **Retention**: export request logs retained 90 days; no invoice bodies are
  persisted by the export path.
- **Residency**: data stays in the primary region (`us-east`); no cross-region
  copy or egress.
- **Sharing**: response is returned only to the authenticated, authorized
  caller; no third-party sharing.
- **Redaction**: account numbers are masked in logs and error messages;
  invoice bodies are never written to logs.

## Tagging Discipline

Every artifact and evidence record for this feature carries the standard tag
set so handling, ownership, and traceability are enforceable:

- **owner**: `@finance-platform`
- **system**: `invoice-export-api`
- **environment**: `prod`
- **data-classification**: `confidential`
- **retention**: `90d`
- **feature-id**: `specs/001-example`

## Trust Boundaries

- HTTP request (untrusted) -> API handler: validate path params and the
  authenticated principal before any data access.
- API handler -> invoice service: pass only the validated invoice id and the
  caller's authorization context.
- Invoice service -> PDF renderer: render from validated, owned records only;
  the renderer receives no caller-supplied template input.

## Security Requirements

- Authenticate every request; reject anonymous callers with 401.
- Authorize per-record: a caller may export an invoice only if it belongs to an
  organization they are entitled to, enforced server-side (no trust in client
  claims).
- Validate `{id}` as an opaque, server-issued identifier; reject malformed ids.
- No invoice content, account numbers, or tokens in logs, error bodies, or
  traces.

## Privacy Requirements

Do not log invoice line items or customer billing detail. Log only the request
id, caller id, target invoice id, and authorization outcome.

## Compliance / Control Applicability

- AppSec (authn/authz, input validation, negative tests) applies.
- CSA CCM v4.1 IAM and logging domains apply at the evidence level.

## AI / LLM Risk

Not applicable to this feature: there is no AI, LLM, agent, RAG, MCP, or
model-driven path in the export flow, and no caller-supplied content is ever
placed into a prompt or tool call. There is no prompt injection or tool
boundary exposure today. If an AI-assisted summarization feature is added
later, this section must add explicit prompt injection and tool boundary
guardrails and re-run `sicario verify`.

## External System Access

The endpoint performs no external writes. It reads from the internal invoice
datastore and the internal PDF renderer only.

## Secrets / Credential Handling

Datastore credentials are injected from the runtime secret manager at startup;
they are never read from files committed to the repo, never logged, and never
returned in responses.

## Audit / Logging Requirements

Log every export attempt with: request id, caller id, target invoice id, and
allow/deny outcome. Authorization denials are logged at WARN. No payload bodies
are logged.

## Misuse / Abuse Cases

- A standard user requests an invoice id belonging to another organization.
- An anonymous client calls the endpoint directly.
- A caller enumerates sequential ids to probe for accessible invoices.
- A caller submits a malformed or oversized id to trigger an unhandled error.

## Functional Requirements

- **FR-001**: Return the requested invoice as a PDF for an authorized caller.
- **FR-002**: Deny export of invoices the caller does not own (403).
- **FR-003**: Reject unauthenticated requests (401).

## Security Acceptance Criteria

- **SA-001**: A standard user is denied (403) an invoice from another org.
- **SA-002**: An anonymous request is rejected (401).
- **SA-003**: A malformed id is rejected (400) without leaking internals.

## Evidence To Produce

Threat model update, functional + negative/security tests, data classification
record, tagging record, docs-impact entry, and the `sicario verify` gate
summary (`generated/sicario/gate-summary.json`).
