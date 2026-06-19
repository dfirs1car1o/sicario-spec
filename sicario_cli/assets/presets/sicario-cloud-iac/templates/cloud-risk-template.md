# Cloud / Infrastructure Risk Template

Complete this for every infrastructure spec.

## Provider And Deployment Model

- Provider(s): Azure / AWS / GCP / Kubernetes / hybrid / local
- IaC technology: Terraform / OpenTofu / Bicep / CloudFormation / CDK / other
- Environment: dev / test / staging / prod
- Region(s):
- Data residency:
- Data classification:

## Identity And Access

- Managed identities / service principals / roles:
- Least-privilege scope:
- Privileged operations:
- Break-glass path:

## Network Exposure

- Public ingress:
- Private endpoints:
- Egress controls:
- DNS/TLS:

## Data Protection

- Encryption at rest:
- Encryption in transit:
- Key ownership:
- Backup/restore:

## Secrets

- Secret store:
- Runtime injection:
- Rotation:
- Redaction:

## Logging And Monitoring

- Activity logs:
- Resource logs:
- Security telemetry:
- Alerts:

## Policy As Code

- Tools: Checkov / tfsec / Trivy / OPA / Conftest / Azure Policy / AWS Config / GCP Org Policy
- Required policies:
- Exception process:

## Drift And Change Control

- Drift detection:
- Terraform/Bicep plan review:
- Approval gate:
- Rollback:

## Cost Guardrails

- SKU/instance restrictions:
- Budget threshold:
- Auto-shutdown:
- Required tags/labels:
- Temporary resource expiration:

## Tagging Discipline

Required tags/labels should follow `docs/governance/tagging-taxonomy.md`:

- owner
- system
- environment
- data-classification
- retention
- compliance-scope
- cost-center
- source-repo
- managed-by
- expires-on for temporary resources
