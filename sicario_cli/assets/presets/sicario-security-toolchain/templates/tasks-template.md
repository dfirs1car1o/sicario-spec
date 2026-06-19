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

## Phase 4: Tests And Verification

- [ ] T018 Add functional tests
- [ ] T019 Add negative/security tests
- [ ] T020 Run `sicario verify`
- [ ] T021 Obtain human review for high-risk changes

## Dependencies

- Classification and tagging decisions block evidence storage and release packaging.
- Toolchain evidence blocks release.
- Human approval blocks high-impact write, release, and exception tasks.
