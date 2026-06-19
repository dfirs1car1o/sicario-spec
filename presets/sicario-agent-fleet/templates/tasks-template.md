---
description: "SicarioSpec agent fleet and orchestration task list template"
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

## Phase 3: Orchestration Foundation

- [ ] T010 Document workflow/state graph and state source of truth
- [ ] T011 Document queue, topic, event, worker, and agent inventory
- [ ] T012 Add worker identity and least-privilege permission boundaries
- [ ] T013 Add tool/action allowlist for autonomous or agentic actions
- [ ] T014 Add retry, timeout, idempotency, and dead-letter behavior
- [ ] T015 Add kill switch or pause mechanism for unsafe fleet behavior
- [ ] T016 Add human approval record for high-impact writes or remediation

## Phase 4: Tests First

- [ ] T017 Add functional tests for the primary story
- [ ] T018 Add negative/security tests for misuse and abuse cases
- [ ] T019 Add authorization or privilege-boundary tests
- [ ] T020 Add retry/idempotency tests
- [ ] T021 Add poison-message/dead-letter tests
- [ ] T022 Add concurrency/backpressure tests
- [ ] T023 Add approval-gate tests
- [ ] T024 Verify tests fail before implementation where practical

## Phase 5: Implementation

- [ ] T025 Implement the smallest independently testable slice
- [ ] T026 Add audit logging without sensitive data
- [ ] T027 Preserve deterministic authority for authoritative outcomes
- [ ] T028 Keep external systems read-only unless explicit approval is documented

## Phase 6: Evidence And Verification

- [ ] T029 Run secret scan
- [ ] T030 Run dependency/SCA scan
- [ ] T031 Run SAST/static checks
- [ ] T032 Run IaC/container scan if applicable
- [ ] T033 Generate evidence artifacts
- [ ] T034 Run `sicario verify`
- [ ] T035 Record docs impact or no-docs-impact decision
- [ ] T036 Obtain human review for high-risk changes

## Dependencies

- Security foundation blocks implementation.
- Orchestration foundation blocks autonomous or distributed execution.
- Negative/security tests must exist before final verification.
- Human approval blocks high-impact write, release, remediation, and exception tasks.
