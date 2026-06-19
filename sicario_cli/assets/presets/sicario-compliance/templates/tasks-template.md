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
- [ ] T008 Add secrets handling and redaction guardrails
- [ ] T009 Add trust-boundary validation or sanitization

## Phase 3: Tests First

- [ ] T010 Add functional tests for the primary story
- [ ] T011 Add negative/security tests for misuse and abuse cases
- [ ] T012 Add authorization or privilege-boundary tests
- [ ] T013 Add regression tests for prior related issues
- [ ] T014 Verify tests fail before implementation where practical

## Phase 4: Implementation

- [ ] T015 Implement the smallest independently testable slice
- [ ] T016 Add audit logging without sensitive data
- [ ] T017 Preserve deterministic authority for authoritative outcomes
- [ ] T018 Keep external systems read-only unless explicit approval is documented

## Phase 5: Evidence And Verification

- [ ] T019 Run secret scan
- [ ] T020 Run dependency/SCA scan
- [ ] T021 Run SAST/static checks
- [ ] T022 Run IaC/container scan if applicable
- [ ] T023 Generate evidence artifacts
- [ ] T024 Run `sicario verify`
- [ ] T025 Record docs impact or no-docs-impact decision
- [ ] T026 Obtain human review for high-risk changes

## Dependencies

- Security foundation blocks implementation.
- Negative/security tests must exist before final verification.
- Human approval blocks high-impact write, release, and exception tasks.

