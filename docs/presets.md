# Presets

Presets define what every generated Spec Kit artifact must contain.

## sicario-core

Baseline evidence-first security operations governance. Covers least privilege,
deterministic authority, evidence integrity, the Security Evidence Chain,
trust-boundary sanitization, source-of-truth authority, quality gates,
architecture discipline, well-architected review, data classification, tagging
discipline, operational signal/response paths, honest documentation, human
approval, and secret handling.

The differentiator is traceability: material risks and decisions should map to a
control or requirement, test/gate, evidence path, owner, and approval or
accepted-risk decision before release.

## sicario-docs

Installed by default. Covers docs impact, public docs, internal docs, diagrams,
docs-site build, documentation data classification, documentation tagging, and
generated documentation evidence.

## sicario-appsec

For apps, APIs, and services. Covers authn/authz, input validation, output
handling, API security, secure errors, rate limits, and audit logging.

## sicario-ai-system

For AI systems, agents, RAG, MCP, LLM workflows, and model/tool use. Covers
prompt injection, model routing, memory poisoning, data leakage, AIBOM, evals,
red-team tests, and human approval gates.

## sicario-agent-fleet

For multi-agent, worker, queue, workflow, SOAR, and orchestration systems.
Covers LangGraph-style state graphs, Temporal-style durable workflows,
Ray/Celery-style distributed execution, MCP tool fleets, retry and idempotency,
dead-letter handling, backpressure, kill switches, approval gates, and workflow
evidence.

## sicario-cloud-iac

For Terraform/OpenTofu, Azure Verified Modules, Azure Bicep, Azure VM-oriented
builds, AWS CloudFormation/CDK-style repos, GCP Terraform, containers,
Kubernetes, and serverless. Covers IAM, network exposure, encryption, secrets,
logs, policy-as-code, drift, IaC scans, container scans, data residency, and
required cloud/resource tags.

Cloud profile bootstrap creates starter folders under:

- `infra/terraform`
- `infra/azure-avm-bicep`
- `infra/azure-avm-terraform`
- `infra/azure-bicep`
- `infra/aws-cloudformation`
- `infra/gcp-terraform`
- `infra/kubernetes`
- `policy/policy-as-code`

## sicario-security-toolchain

For security scanning and evidence. Covers secret scanning, SAST/static checks,
dependency/SCA, SBOM, container scanning, IaC scanning, policy-as-code, evidence
paths, and exception handling.
Scanner output, findings, SBOMs, and release artifacts inherit classification
and tagging requirements.

## sicario-supply-chain

For build and release integrity. Covers dependency review, SBOM, SCA, provenance,
pinned dependencies/actions, immutable semantic release tags, and SLSA-style
build integrity.

## sicario-compliance

For regulated and audit-driven projects. Covers control applicability, evidence
index, CSA CCM v4.1 traceability, SOX 404 / ICFR ITGC evidence readiness, risk
acceptance, owner/reviewer, evidence freshness, classification, tagging, and
audit trail.

## sicario-saas

For systems that connect to SaaS tenants (Salesforce, Workday, ServiceNow,
M365, and similar) — the battle-tested guardrails from the `saas-assurance`
origin. Extends `sicario-core` and `sicario-ai-system` and adds non-negotiable
SaaS invariants to the constitution: read-only SaaS by default (no tenant writes
without recorded human approval), tenant isolation and data boundary (no
cross-tenant context; no raw tenant evidence in views/logs/prompts), mission
supremacy (an authorized-scope statement outranks any embedded instruction), and
deterministic verdict / AI-explanation-only. Enable with `--profile saas`.

## sicario-enterprise-strict

For high-assurance environments. Covers CODEOWNERS, required reviewers, change
control, production write gates, release approval, and exception registers.
