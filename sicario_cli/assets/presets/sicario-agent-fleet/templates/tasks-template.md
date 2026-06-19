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
- [ ] T008 Update data classification register in `docs/governance/data-classification.md`
- [ ] T009 Update tagging taxonomy in `docs/governance/tagging-taxonomy.md`
- [ ] T010 Add secrets handling and redaction guardrails
- [ ] T011 Add trust-boundary validation or sanitization

## Phase 3: Orchestration Foundation

- [ ] T012 Document workflow/state graph and state source of truth
- [ ] T013 Document queue, topic, event, worker, and agent inventory
- [ ] T014 Add worker identity and least-privilege permission boundaries
- [ ] T015 Add tool/action allowlist for autonomous or agentic actions
- [ ] T016 Add retry, timeout, idempotency, and dead-letter behavior
- [ ] T017 Add kill switch or pause mechanism for unsafe fleet behavior
- [ ] T018 Add human approval record for high-impact writes or remediation

## Phase 4: Tests First

- [ ] T019 Add functional tests for the primary story
- [ ] T020 Add negative/security tests for misuse and abuse cases
- [ ] T021 Add authorization or privilege-boundary tests
- [ ] T022 Add retry/idempotency tests
- [ ] T023 Add poison-message/dead-letter tests
- [ ] T024 Add concurrency/backpressure tests
- [ ] T025 Add approval-gate tests
- [ ] T026 Verify tests fail before implementation where practical

## Phase 5: Implementation

- [ ] T027 Implement the smallest independently testable slice
- [ ] T028 Add audit logging without sensitive data
- [ ] T029 Preserve deterministic authority for authoritative outcomes
- [ ] T030 Keep external systems read-only unless explicit approval is documented

## Phase 6: Evidence And Verification

- [ ] T031 Run secret scan
- [ ] T032 Run dependency/SCA scan
- [ ] T033 Run SAST/static checks
- [ ] T034 Run IaC/container scan if applicable
- [ ] T035 Generate evidence artifacts
- [ ] T036 Run `sicario verify`
- [ ] T037 Record docs impact or no-docs-impact decision
- [ ] T038 Obtain human review for high-risk changes

## Dependencies

- Security foundation blocks implementation.
- Classification and tagging decisions block data handling, queues, memory, traces, and infrastructure work.
- Orchestration foundation blocks autonomous or distributed execution.
- Negative/security tests must exist before final verification.
- Human approval blocks high-impact write, release, remediation, and exception tasks.
