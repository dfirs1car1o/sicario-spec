# Threat Model — Customer Invoice Export API

Status: complete (example)

## Scope

The read-only `GET /api/v1/invoices/{id}/export` endpoint that returns a single
customer invoice as PDF.

## Trust Boundaries

- Boundary 1: untrusted HTTP request -> API handler (authn + input validation)
- Boundary 2: API handler -> invoice service (validated id + authz context)
- Boundary 3: invoice service -> PDF renderer (no caller-supplied template)

## Threats

| Threat | Impact | Control | Status |
|---|---|---|---|
| Broken object-level authorization (IDOR) | High | Server-side per-record ownership check before render | Designed |
| Unauthenticated access | High | 401 at auth middleware | Designed |
| Sensitive billing data in logs | Medium | Exclude invoice bodies; mask account numbers | Designed |
| Invoice id enumeration | Medium | Opaque server-issued ids; deny == not-found | Designed |
| Malformed/oversized id triggering errors | Low | Strict id validation; safe 400 | Designed |

## Approval Boundaries

Production release of the endpoint requires maintainer approval.
