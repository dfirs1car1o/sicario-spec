# Risk Register — Customer Invoice Export API

| Risk ID | Status | Risk | Owner | Severity | Treatment | Evidence |
|---|---|---|---|---|---|---|
| R-001 | closed | IDOR on invoice export | @finance-platform | high | Server-side per-record authz + tests | generated/sicario/gate-summary.json |
| R-002 | closed | Sensitive billing data in logs | @finance-platform | medium | Exclude bodies; mask account numbers | generated/sicario/gate-summary.json |
