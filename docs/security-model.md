# Security Model

SicarioSpec follows these principles.

1. **Deterministic gates decide.** AI may draft, explain, and review, but pass/fail
   state comes from code, validators, tests, and CI.
2. **Fail closed.** Missing threat models, security tasks, required evidence, or
   docs impact records fail verification.
3. **No secrets.** Secrets must not enter repo files, logs, generated artifacts,
   or LLM context.
4. **No blind writes.** High-impact writes and external system writes require
   explicit human approval.
5. **Docs are evidence.** Documentation, diagrams, and evidence indexes are part
   of the release gate.
6. **Orchestration is bounded.** Agent fleets, workflow engines, queues, and
   SOAR playbooks need explicit state, retry, idempotency, dead-letter,
   observability, and approval boundaries.
7. **Architecture is governed.** Meaningful changes require ADRs, data-flow and
   trust-boundary clarity, well-architected review, rollback, operability, and
   cost/performance tradeoff notes.
8. **Exceptions expire.** Active risk or security exceptions require ownership,
   approval, expiration, compensating controls, and evidence.

Deterministic does not mean unbypassable. A project can override or disable any
shipped rule — including the secret scan — by reusing its `id` in
`.sicario/rules/`. The control is visibility, not prohibition: every effective
override is recorded in `scan_coverage.overrides` in
`generated/sicario/gate-summary.json`, with `impact` and `original_severity`
fields, so disabling a shipped critical rule always reads
`disables-critical-severity-rule` and is grep-able in review. See
[Rule Engine](./rule-engine.md#override-evidence).

SicarioSpec is not a compliance certification engine. It is a development
governance system that helps create evidence for review.
