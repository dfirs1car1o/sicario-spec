# [PROJECT_NAME] Security Toolchain Constitution

This constitution extends the SicarioSpec core constitution for repositories
that enforce security scanning, SBOM, policy-as-code, and release evidence.

## Core Principles

### 1. Security Checks Run Before Handoff

Secret scanning, SAST/static checks, dependency review, SBOM generation, IaC
scans, container scans, and policy-as-code checks are part of delivery, not
post-release cleanup.

### 2. Findings Must Become Work

Every material finding must be fixed, linked to remediation work, or recorded as
an approved, time-bound exception with compensating controls.

### 3. Evidence Is Generated And Indexed

Tool output must be reproducible, stored in documented locations, and indexed in
`docs/compliance/evidence-index.md`.

### 4. Tool Configuration Is Source-Controlled

Scanner configuration, ignores, baselines, custom policies, and versions must be
reviewed like code.

### 5. Releases Require Green Gates Or Approved Exceptions

Security gates must pass before release unless a human-approved exception exists
with an owner, expiration date, rationale, and compensating control.
