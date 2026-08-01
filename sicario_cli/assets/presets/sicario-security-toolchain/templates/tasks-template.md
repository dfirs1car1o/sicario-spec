---
description: "SicarioSpec security toolchain task list template"
---

# Tasks: [FEATURE NAME]

**Input**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, contracts

## Phase 1: Setup

- [ ] T001 Configure local test command
- [ ] T002 Add or update docs impact tracking
- [ ] T003 Identify required security tools and versions

## Phase 2: Security Foundation

- [ ] T004 Update threat model in `docs/security/threat-model.md`
- [ ] T005 Update abuse cases in `docs/security/abuse-cases.md`
- [ ] T006 Update control applicability in `docs/compliance/control-applicability.md`
- [ ] T007 Update evidence index in `docs/compliance/evidence-index.md`
- [ ] T008 Update data classification register in `docs/governance/data-classification.md`
- [ ] T009 Update tagging taxonomy in `docs/governance/tagging-taxonomy.md`

## Phase 3: Toolchain

- [ ] T010 Run secret scan
- [ ] T011 Run SAST/static checks
- [ ] T012 Run dependency/SCA scan
- [ ] T013 Generate or update SBOM
- [ ] T014 Run container scan if applicable
- [ ] T015 Run IaC scan if applicable
- [ ] T016 Run policy-as-code checks if applicable
- [ ] T017 Store evidence under documented paths

## Phase 4: Tests First

- [ ] T018 Add functional tests for the primary story
- [ ] T019 Add negative/security tests for misuse and abuse cases
- [ ] T020 Verify tests fail before implementation where practical

## Phase 5: Implementation

- [ ] T021 Implement the smallest independently testable slice
- [ ] T022 Add audit logging without sensitive data
- [ ] T023 Keep external systems read-only unless explicit approval is documented

## Phase 6: Evidence And Verification

- [ ] T024 Populate the Security Evidence Chain with risk, control, gate, evidence, owner, and approval entries
- [ ] T025 Run the configured project verification gate
- [ ] T026 Run `sicario verify` if SicarioSpec CLI is installed for this project
- [ ] T027 Record docs impact or no-docs-impact decision
- [ ] T028 Obtain human review for high-risk changes

## Dependencies

- Security foundation blocks implementation.
- Classification and tagging decisions block evidence storage and release packaging.
- Toolchain evidence blocks release.
- Negative/security tests must exist before final verification.
- Human approval blocks high-impact write, release, and exception tasks.
