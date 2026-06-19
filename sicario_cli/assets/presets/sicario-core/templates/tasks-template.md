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

## Phase 3: Tests First

- [ ] T012 Add functional tests for the primary story
- [ ] T013 Add negative/security tests for misuse and abuse cases
- [ ] T014 Add authorization or privilege-boundary tests
- [ ] T015 Add regression tests for prior related issues
- [ ] T016 Verify tests fail before implementation where practical

## Phase 4: Implementation

- [ ] T017 Implement the smallest independently testable slice
- [ ] T018 Add audit logging without sensitive data
- [ ] T019 Preserve deterministic authority for authoritative outcomes
- [ ] T020 Keep external systems read-only unless explicit approval is documented

## Phase 5: Evidence And Verification

- [ ] T021 Run secret scan
- [ ] T022 Run dependency/SCA scan
- [ ] T023 Run SAST/static checks
- [ ] T024 Run IaC/container scan if applicable
- [ ] T025 Generate evidence artifacts
- [ ] T026 Run `sicario verify`
- [ ] T027 Record docs impact or no-docs-impact decision
- [ ] T028 Obtain human review for high-risk changes

## Dependencies

- Security foundation blocks implementation.
- Classification and tagging decisions block data handling and infrastructure work.
- Negative/security tests must exist before final verification.
- Human approval blocks high-impact write, release, and exception tasks.
