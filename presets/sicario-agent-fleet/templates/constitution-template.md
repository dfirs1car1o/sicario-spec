# [PROJECT_NAME] Agent Fleet Constitution

This constitution extends the SicarioSpec core constitution for systems that run
multi-agent workflows, distributed workers, queues, SOAR playbooks, or durable
process orchestration.

## Core Principles

### 1. Workflow State Is Authoritative

Workflow state must live in a durable, auditable source of truth. Model memory,
chat history, logs, and transient worker memory are not authoritative state.

### 2. Every Worker Has A Bounded Identity

Agents, workers, and workflow steps must use distinct identities where practical,
least-privilege permissions, and explicit tool/action allowlists.

### 3. Autonomous Writes Are Human-Gated

Production-impacting writes, external system writes, customer-impacting changes,
security exceptions, and automated remediation require documented approval unless
a pre-approved playbook explicitly covers the action.

### 4. Distributed Work Must Be Idempotent

Retries, duplicate events, partial failures, and replayed workflow steps must not
create unsafe side effects. If idempotency is impossible, compensation steps are
required.

### 5. Failures Must Be Contained And Observable

Retries, dead-letter queues, poison messages, backpressure, timeout behavior,
worker crashes, and orphaned workflow state must be observable and tested.

### 6. Kill Switches Are Required

Operators must be able to pause, disable, or roll back unsafe automated behavior
without editing code under emergency conditions.

## Governance

Amendments require human approval, a pull request, and a changelog entry.
