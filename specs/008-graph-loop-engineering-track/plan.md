# Implementation Plan: Advanced Track — Graph Engineering and Loop Engineering

**Feature Branch**: `008-graph-loop-engineering-track`
**Spec**: `spec.md` (same directory)
**Date**: 2026-08-04

## Approach

Two-stage build on one branch: (1) the `examples/spec-graph/` package —
stdlib-only checklist helper implementing traversal rules R1–R13, JSON
schema, two example graphs, and the SEC-002/003/005 invariant tests;
(2) the two playbooks, track index, `start-here` link, sidebar category with
the FR-003 exclusion, docs-site Mermaid rendering, and the FR-003/SEC-006
docs tests, with every quoted helper output captured from real runs as
verified blocks. A fresh-context adversarial audit against every FR/SEC/SR
preceded merge; its five findings were fixed on-branch.

## Recorded Decisions And Deviations

- **FR-042: option (i) taken** — `@docusaurus/theme-mermaid@3.10.2` added to
  `docs-site/package.json` (pinned to match the docusaurus core version).
  Build-time, docs-site only; `pyproject.toml` dependencies remain empty and
  nothing under `docs/` or `docs-site/` ships in the wheel.
- **Transitive requirement discovered and verified**:
  `@mermaid-js/layout-elk@^0.1.9` is declared an *optional* peer by the
  theme, but the theme's client module imports it statically and the webpack
  client bundle fails to resolve without it ("Module not found … further
  build is impossible" — reproduced independently by deleting the package
  and rebuilding). It is the unavoidable cost of the FR-042(i) choice, not a
  discretionary addition; ruled within FR-052's intent by the audit because
  the clause's purpose (nothing new ships in the Python package) is
  preserved with a zero-byte `pyproject.toml` diff.
- **FR-013 deviation: `tags` is schema-optional.** Requiring the five tag
  keys in `graph.schema.json` would make the deliberately untagged example
  node schema-invalid, while the teaching point is that an untagged node is
  a *traversal finding* (R9) and a gap-list entry, not a parse error. The
  requirement is enforced by R9 and taught in both lessons; documented in
  `examples/spec-graph/README.md`.
- **Audit fixes applied before merge**: corrected a false gate-fact in the
  loop lesson (`Rollback` and `Threat Model` ARE `SICARIO-PLAN-SECTION`
  substrings); `UnicodeDecodeError` now caught so the helper exits 0 on
  non-UTF-8 input (with regression test); SEC-002 severity-token assertion
  added (permitting `high` only inside `high-impact`); SR-007
  absolute-tool-boundary sentence added to the loop lesson's AI-drafting
  passage; this plan records the above.

## Threat Model

The feature's threats are documentation-supply-chain shaped and are handled
in the spec's Misuse / Abuse Cases: coverage laundering (mitigated by SR-005
literal sentences plus closing drills), verdict creep in the helper
(SEC-002 tests), secret-shaped example values (SEC-005 negative scan reusing
the shipped rule patterns), and real-graph publication by readers (SR-006
warning and private-location guidance). The plan-level residual is the new
docs-site dependency pair, mitigated by exact version pinning, the
lockfile, and the existing scripts-disabled npm install in CI.

## Data Classification

All committed artifacts are Public by design (public repo and docs-site);
the classification table and the real-graph sensitivity rule live in the
spec. No new data classes are introduced by implementation.

## Tagging

Documentation artifacts follow the spec's Tagging Discipline section; the
cloud example graph carries the five tag keys on every tagged node, with
one deliberately untagged node as the R9 teaching fixture.

## Well-Architected Review

Operational excellence: verified blocks make the lessons self-testing in CI.
Security: all MUST NOTs are enforced by tests, not convention. Reliability:
the helper is deterministic (byte-identical repeat runs, tested).
Cost/performance: no runtime dependencies; docs build cost grows only by
the mermaid render step.

## Supply Chain

Two new npm packages (`@docusaurus/theme-mermaid`, `@mermaid-js/layout-elk`),
docs-site only, exactly pinned / caret-pinned respectively, resolved through
the committed lockfile and installed in CI with lifecycle scripts disabled.
Zero new Python dependencies. No new GitHub Actions.

## Rollback

The feature is additive: rollback is reverting the squash commit. No
migration, no state, no generated artifacts change shape. If only the
mermaid rendering regresses, FR-042 option (ii) (screenshot fallback) is
the documented degraded mode without touching lesson content.

## Human Approval

The dependency addition and the FR-013 deviation recorded here were the two
judgment calls; both passed the adversarial audit and the standard reviewed
PR flow (NHI submits, human account approves) applies as the approval point.

## Evidence

Gate runs on the branch head: 249 unit tests green; docs runner 99 verified
re-executed / 0 mismatches across 15 guides; `sicario verify` passed;
docs-site build success with all three new routes generated. Audit report
retained in session records; findings list and fixes summarized above.
