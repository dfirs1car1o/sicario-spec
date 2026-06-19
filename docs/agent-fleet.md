# Agent Fleet And Orchestration

Use the `agent-fleet` profile when a project coordinates multiple agents,
workers, queues, workflows, SOAR playbooks, or distributed jobs.

This covers patterns such as:

- LangGraph-style state graphs
- Temporal-style durable workflows
- Ray/Celery-style distributed task execution
- queue and worker systems
- MCP tool fleets
- SOAR remediation playbooks
- multi-agent pipelines

The goal is not to standardize on one orchestrator. The goal is to make the
orchestration risk explicit before implementation.

Required design decisions:

- workflow/state graph
- durable state source of truth
- agent and worker identity model
- tool/action allowlist
- retry, timeout, idempotency, and dead-letter behavior
- backpressure and concurrency limits
- observability and trace correlation
- human approval boundaries
- emergency pause or kill switch
- rollback or compensation workflow

Recommended profile combinations:

```bash
sicario init my-agent-system --profile agent-fleet,supply-chain
sicario init my-soar-playbooks --profile agent-fleet,cloud-iac,compliance
sicario init my-ai-platform --profile appsec,ai-system,agent-fleet,supply-chain
```

For security automation, the important question is not only whether the agent can
act. It is whether the action is bounded, approved, observable, reversible, and
evidenced.
