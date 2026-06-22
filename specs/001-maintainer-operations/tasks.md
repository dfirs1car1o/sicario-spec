---
description: "SicarioSpec secure task list for maintainer operations hardening"
---

# Tasks: Maintainer Operations Hardening

**Input**: `spec.md`, `plan.md`

## Phase 1: Setup

- [x] T001 Initialize Spec Kit in the repository with Codex integration.
- [x] T002 Install the local `sicario-core` preset as a Spec Kit development preset.
- [x] T003 Create feature branch and `specs/001-maintainer-operations/` via Spec Kit scripts.
- [x] T004 Add this feature's spec and implementation plan.

## Phase 2: Security Foundation

- [x] T005 Update threat model in `specs/001-maintainer-operations/spec.md` for public issue input, GitHub Actions, and agent-assisted PR boundaries.
- [x] T006 Add misuse and abuse cases for malicious issue text, accidental sensitive data, and unsafe workflow expansion.
- [x] T007 Define public data classification and untrusted issue-input boundary.
- [x] T008 Record tagging impact: feature-id `001-maintainer-operations` and control-id `SEC-001..SEC-004`; no taxonomy file change required.
- [x] T009 Record docs impact: README, CONTRIBUTING, repository settings, maintainer operations, changelog, and Spec Kit artifacts changed.
- [x] T010 Populate the Security Evidence Chain with risks, controls, gates, evidence, owner, and approval entries.
- [x] T011 Document the automation boundary: issues may trigger labels/comments, not commits, PRs, releases, or tag movement.
- [x] T012 Document agent-assisted work as PR-only with non-author maintainer review.

## Phase 3: Implementation

- [x] T013 Add `MAINTAINERS.md` with maintainer roles, triage outcomes, merge authority, and automation limits.
- [x] T014 Add `.github/CODEOWNERS` for default and release-critical ownership.
- [x] T015 Add `.github/ISSUE_TEMPLATE/maintenance_task.yml`.
- [x] T016 Add `.github/workflows/issue-triage.yml` with least-privilege issue labeling/commenting behavior.
- [x] T017 Add `docs/maintainer-operations.md` as the issue-to-PR runbook.
- [x] T018 Update contributor, repository-settings, README, and changelog references.
- [x] T019 Add security test coverage through `actionlint`, YAML parsing, and workflow permission review.
- [x] T020 Add negative test review for issue text not becoming executable code or direct repository mutation.

## Phase 4: Evidence And Verification

- [x] T021 Run `specify preset info sicario-core`.
- [x] T022 Run `python3 -m unittest discover -s tests`.
- [x] T023 Run `python3 -m sicario_cli.cli verify .`.
- [x] T024 Inspect `git diff` for accidental secrets, unsafe permissions, or generated noise.
- [ ] T025 Open machine-user pull request with Spec Kit evidence and verification output.

## Dependencies

- T001-T003 block all dogfood evidence.
- T005-T012 block workflow merge readiness.
- T013-T020 block documentation updates and verification.
- T021-T024 block PR publication.
