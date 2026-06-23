# Security Exceptions

Exceptions must be explicit, owned, time-bound, approved, and backed by a
compensating control. Permanent exceptions are not allowed.

| Exception ID | Status | Control / Gate | Owner | Expires | Approval | Compensating Control | Evidence |
|---|---|---|---|---|---|---|---|
| EXC-001 | open | `SICARIO-MISSING-THREAT-MODEL` — threat-model section required on every feature | Maintainers | 2027-01-01 | TBD | External threat-modeling process documented in project wiki; verify still enforces abuse-cases and data-classification | generated/sicario/gate-summary.json |
| EXC-002 | open | `SICARIO-MISSING-DIAGRAMS` — system-context diagram required | Maintainers | 2026-09-01 | TBD | Architecture decision records (ADRs) capture the same structural information in prose | generated/sicario/gate-summary.json |
