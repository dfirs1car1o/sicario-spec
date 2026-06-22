---
description: "SicarioSpec secure task list template"
---

# Tasks: [FEATURE NAME]

**Input**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, contracts

## Phase 1: Setup

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Configure linting, formatting, and local test command
- [ ] T003 Add or update docs impact tracking

## Phase 2: Security Foundation

- [ ] T004 Update threat model in `docs/security/threat-model.md`
- [ ] T005 Update abuse cases in `docs/security/abuse-cases.md`
- [ ] T006 Update control applicability in `docs/compliance/control-applicability.md`
- [ ] T007 Update evidence index in `docs/compliance/evidence-index.md`
- [ ] T008 Update data classification register in `docs/governance/data-classification.md`
- [ ] T009 Update tagging taxonomy in `docs/governance/tagging-taxonomy.md`
- [ ] T010 Add secrets handling and redaction guardrails
- [ ] T011 Add trust-boundary validation or sanitization
- [ ] T012 Populate the Security Evidence Chain with risk, control, gate, evidence, owner, and approval entries

## Phase 3: Tests First

- [ ] T013 Add functional tests for the primary story
- [ ] T014 Add negative/security tests for misuse and abuse cases
- [ ] T015 Add authorization or privilege-boundary tests
- [ ] T016 Add regression tests for prior related issues
- [ ] T017 Verify tests fail before implementation where practical

## Phase 4: Implementation

- [ ] T018 Implement the smallest independently testable slice
- [ ] T019 Add audit logging without sensitive data
- [ ] T020 Add operational signals, detection hooks, or runbook updates where required
- [ ] T021 Preserve deterministic authority for authoritative outcomes
- [ ] T022 Keep external systems read-only unless explicit approval is documented

## Phase 5: Evidence And Verification

- [ ] T023 Run secret scan
- [ ] T024 Run dependency/SCA scan
- [ ] T025 Run SAST/static checks
- [ ] T026 Run IaC/container scan if applicable
- [ ] T027 Generate evidence artifacts and update evidence paths in the Security Evidence Chain
- [ ] T028 Run the configured project verification gate
- [ ] T029 Run `sicario verify` if SicarioSpec CLI is installed for this project
- [ ] T030 Record docs impact or no-docs-impact decision
- [ ] T031 Obtain human review for high-risk changes

## Dependencies

- Security foundation blocks implementation.
- Classification and tagging decisions block data handling and infrastructure work.
- Security Evidence Chain entries block final verification.
- Negative/security tests must exist before final verification.
- Human approval blocks high-impact write, release, and exception tasks.
