# SicarioSpec Agent Fleet Checklist: [FEATURE NAME]

**Purpose**: Verify secure orchestration for multi-agent, workflow, queue, and worker systems.
**Created**: [DATE]
**Feature**: [link]

## Specification

- [ ] CHK001 Data classification is complete, including owner, retention, residency, disclosure, memory, queue, and trace handling.
- [ ] CHK002 Tagging discipline is defined for data, resources, workflows, agents, queues, evidence, risk, and exceptions.
- [ ] CHK003 Trust boundaries are documented.
- [ ] CHK004 Abuse cases are documented.
- [ ] CHK005 Security acceptance criteria are measurable.
- [ ] CHK006 Evidence outputs are identified.
- [ ] CHK007 Fleet/orchestration risk section is complete.

## Orchestration

- [ ] CHK008 Workflow/state graph is documented.
- [ ] CHK009 State source of truth is identified.
- [ ] CHK010 Queue, topic, event, worker, and agent inventory is documented.
- [ ] CHK011 Retry, timeout, idempotency, and dead-letter behavior are defined.
- [ ] CHK012 Backpressure and concurrency limits are defined.

## Permission And Approval

- [ ] CHK013 Agent/worker identities are least privilege.
- [ ] CHK014 Tool/action allowlist is documented.
- [ ] CHK015 High-impact writes require human approval.
- [ ] CHK016 Emergency stop or pause mechanism exists.

## Verification

- [ ] CHK017 Secret scan passed.
- [ ] CHK018 Dependency/SCA scan passed.
- [ ] CHK019 SAST/static checks passed.
- [ ] CHK020 Classification and tagging tasks are present.
- [ ] CHK021 Retry/idempotency tests passed.
- [ ] CHK022 Poison-message/dead-letter tests passed.
- [ ] CHK023 Approval-gate tests passed.
- [ ] CHK024 `sicario verify` passed.
