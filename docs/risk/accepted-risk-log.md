# Accepted Risk Log

Accepted risk requires a business owner, security reviewer, expiration date, and
revalidation evidence.

| Risk ID | Status | Risk | Business Owner | Security Reviewer | Expires | Rationale | Evidence |
|---|---|---|---|---|---|---|---|
| AR-001 | open | Verify gate depends on file-system state at time of run; race condition possible during concurrent CI jobs | Maintainers | Maintainers | 2026-12-31 | CI runners are single-threaded per job; true concurrent writes to the same workspace are outside the threat model for `0.x` line | generated/sicario/gate-summary.json |
