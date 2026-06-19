---
description: "SicarioSpec security toolchain task list template"
---

# Tasks: [FEATURE NAME]

## Phase 1: Setup

- [ ] T001 Configure local test command
- [ ] T002 Add or update docs impact tracking
- [ ] T003 Identify required security tools and versions

## Phase 2: Security Foundation

- [ ] T004 Update threat model in `docs/security/threat-model.md`
- [ ] T005 Update abuse cases in `docs/security/abuse-cases.md`
- [ ] T006 Update control applicability in `docs/compliance/control-applicability.md`
- [ ] T007 Update evidence index in `docs/compliance/evidence-index.md`

## Phase 3: Toolchain

- [ ] T008 Run secret scan
- [ ] T009 Run SAST/static checks
- [ ] T010 Run dependency/SCA scan
- [ ] T011 Generate or update SBOM
- [ ] T012 Run container scan if applicable
- [ ] T013 Run IaC scan if applicable
- [ ] T014 Run policy-as-code checks if applicable
- [ ] T015 Store evidence under documented paths

## Phase 4: Tests And Verification

- [ ] T016 Add functional tests
- [ ] T017 Add negative/security tests
- [ ] T018 Run `sicario verify`
- [ ] T019 Obtain human review for high-risk changes

## Dependencies

- Toolchain evidence blocks release.
- Human approval blocks high-impact write, release, and exception tasks.
