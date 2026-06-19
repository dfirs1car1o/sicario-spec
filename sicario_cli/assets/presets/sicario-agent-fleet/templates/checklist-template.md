# SicarioSpec Agent Fleet Checklist: [FEATURE NAME]

**Purpose**: Verify secure orchestration for multi-agent, workflow, queue, and worker systems.
**Created**: [DATE]
**Feature**: [link]

## Specification

- [ ] CHK001 Data classification is complete.
- [ ] CHK002 Trust boundaries are documented.
- [ ] CHK003 Abuse cases are documented.
- [ ] CHK004 Security acceptance criteria are measurable.
- [ ] CHK005 Evidence outputs are identified.
- [ ] CHK006 Fleet/orchestration risk section is complete.

## Orchestration

- [ ] CHK007 Workflow/state graph is documented.
- [ ] CHK008 State source of truth is identified.
- [ ] CHK009 Queue, topic, event, worker, and agent inventory is documented.
- [ ] CHK010 Retry, timeout, idempotency, and dead-letter behavior are defined.
- [ ] CHK011 Backpressure and concurrency limits are defined.

## Permission And Approval

- [ ] CHK012 Agent/worker identities are least privilege.
- [ ] CHK013 Tool/action allowlist is documented.
- [ ] CHK014 High-impact writes require human approval.
- [ ] CHK015 Emergency stop or pause mechanism exists.

## Verification

- [ ] CHK016 Secret scan passed.
- [ ] CHK017 Dependency/SCA scan passed.
- [ ] CHK018 SAST/static checks passed.
- [ ] CHK019 Retry/idempotency tests passed.
- [ ] CHK020 Poison-message/dead-letter tests passed.
- [ ] CHK021 Approval-gate tests passed.
- [ ] CHK022 `sicario verify` passed.
