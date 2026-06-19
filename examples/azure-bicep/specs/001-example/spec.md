# Feature Specification: Azure Bicep Example

## Data Classification
Infrastructure metadata.
## Trust Boundaries
CI runner to Azure Resource Manager.
## Security Requirements
Managed identity, least privilege RBAC, private networking where feasible, diagnostic settings.
## Abuse Cases
Public IP or broad role assignment is introduced without approval.
## Compliance / Control Applicability
Cloud/IaC and supply-chain controls apply.
## Evidence
Bicep validation, policy scan, deployment plan, and approval record.

