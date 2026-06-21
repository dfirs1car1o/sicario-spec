# Tasks: Customer Invoice Export API

Each task maps to a requirement or governance gate. The security, negative,
data-classification, tagging, docs-impact, evidence, and threat-model tasks are
what `sicario verify` requires to be present.

## Implementation

- [ ] Add the `GET /api/v1/invoices/{id}/export` route (FR-001).
- [ ] Implement `authorize_export(principal, invoice)` with deny-by-default.
- [ ] Wire structured audit logging that excludes invoice bodies.

## Testing

- [ ] Add a functional test for a successful authorized export (FR-001).
- [ ] Add a negative/security test for cross-org denial — 403 (SA-001).
- [ ] Add a security test for anonymous access — 401 (SA-002).
- [ ] Add a negative test for a malformed id — 400 (SA-003).

## Governance & Evidence

- [ ] Update the threat model with the IDOR and id-enumeration entries.
- [ ] Record the data classification (confidential) for the export payload.
- [ ] Apply the standard tagging set to artifacts and evidence.
- [ ] Record the docs impact entry for the new endpoint.
- [ ] Generate evidence by running `sicario verify` and committing the gate
      summary.
- [ ] Run `sicario verify` and confirm `status: pass` before handoff.
