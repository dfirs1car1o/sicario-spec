# Implementation Plan: Customer Invoice Export API

## Threat Model

Primary threats and controls for the export path:

| Threat | Impact | Control | Status |
|---|---|---|---|
| Broken object-level authorization (IDOR) | High | Server-side per-record ownership check before render | Planned |
| Unauthenticated access | High | Reject anonymous requests with 401 at the auth middleware | Planned |
| Sensitive data in logs | Medium | Structured logging that excludes invoice bodies; account-number masking | Planned |
| Id enumeration / probing | Medium | Opaque server-issued ids; deny is indistinguishable from not-found | Planned |

Trust boundaries are inherited from the spec: untrusted HTTP request -> handler
-> invoice service -> PDF renderer.

## Architecture / Security Decision Record

Authorization is enforced in a single, testable `authorize_export(principal,
invoice)` function called before any record is read for rendering. The PDF
renderer takes no caller-supplied template input, removing server-side template
injection as a class.

## Authn / Authz Design

- Authentication: bearer token validated by existing platform middleware.
- Authorization: per-record ownership check; client-supplied org claims are
  never trusted — entitlement is resolved server-side from the principal.

## Data Flow And Trust Boundaries

client -> API handler (authn + input validation) -> authorize_export ->
invoice service (read-only) -> PDF renderer -> response.

## Data Classification

The exported payload is **confidential** (customer billing detail). The handling
rules (owner, retention, residency, sharing, redaction) are defined in the
spec's Data Classification section and recorded in
`docs/governance/data-classification.md`. No data is reclassified by this plan.

## Tagging

Implementation artifacts and evidence carry the standard tags: `owner`,
`system`, `environment`, `data-classification`, `retention`, and `feature-id`,
per `docs/governance/tagging-taxonomy.md`.

## Well-Architected

- **Operational excellence**: structured audit logs for every export decision.
- **Security**: least privilege read-only datastore role; deny-by-default authz.
- **Reliability**: renderer failures return 5xx without leaking internals.
- **Performance efficiency**: single-record export; no N+1 reads.
- **Cost optimization**: no caching of confidential PDFs at the edge.
- **Sustainability**: no background re-rendering; render on demand only.

## Supply Chain

No new third-party dependency is introduced. The PDF renderer is an existing,
pinned internal library; its version is unchanged.

## Cloud / IaC Risk

No infrastructure change. The endpoint runs in the existing service with its
existing least-privilege datastore role.

## AI / Tool Boundary

Not applicable: no AI, model, or tool-calling path. Prompt injection and tool
boundary controls are out of scope for this read-only export endpoint.

## Test Strategy

Unit tests for `authorize_export`, plus negative/security tests for the 401,
403, and 400 paths (see Security Acceptance Criteria SA-001..SA-003).

## CI / Security Gates

`sicario verify` runs in CI and must pass. Negative-path tests are required to
merge.

## Rollback

Revert the endpoint route registration; the change is additive and read-only,
so rollback is a single revert with no data migration.

## Evidence Outputs

`sicario verify` gate summary (`generated/sicario/gate-summary.json`), updated
threat model, and the passing test report.

## Human Approval Points

Production release of the new endpoint requires maintainer approval.
