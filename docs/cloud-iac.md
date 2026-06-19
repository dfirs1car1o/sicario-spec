# Cloud And Infrastructure As Code

SicarioSpec treats infrastructure as a first-class development surface.

The `cloud-iac` profile is provider-agnostic and includes starter material for:

- Terraform / OpenTofu
- Azure Verified Modules for Bicep and Terraform
- Azure Bicep
- Azure VM-oriented infrastructure
- AWS CloudFormation / CDK-style repositories
- GCP Terraform
- Kubernetes
- Containers
- Policy-as-code

Every infrastructure spec must address:

- provider and deployment model
- identity and access
- network exposure
- encryption
- secrets
- logging and monitoring
- policy-as-code
- CSA CCM shared-responsibility and cloud assurance traceability
- drift and change control
- rollback
- data residency
- data classification
- required resource tags and labels
- cost guardrails

Resource tagging must use the taxonomy in
`docs/governance/tagging-taxonomy.md`. At minimum, production-bound
infrastructure should carry `owner`, `system`, `environment`,
`data-classification`, `retention`, `compliance-scope`, `cost-center`,
`source-repo`, and `managed-by`; temporary resources also require `expires-on`.

## Azure Verified Modules

For Azure, prefer Azure Verified Modules (AVM) where a resource or pattern module
exists. AVM is Microsoft's standard for reusable Azure IaC modules across Bicep
and Terraform.

Bootstrap creates:

- `infra/azure-avm-bicep`
- `infra/azure-avm-terraform`

Reference indexes:

- AVM overview: https://azure.github.io/Azure-Verified-Modules/
- AVM Bicep index: https://azure.github.io/Azure-Verified-Modules/indexes/bicep/
- AVM Terraform resource index: https://azure.github.io/Azure-Verified-Modules/indexes/terraform/tf-resource-modules/
- Bicep AVM source repo: https://github.com/Azure/bicep-registry-modules
- Terraform Azure namespace: https://registry.terraform.io/namespaces/Azure

Default policy-as-code tools to consider:

- Checkov
- tfsec
- Trivy
- OPA / Conftest
- Azure Policy
- AWS Config
- GCP Organization Policy

The MVP includes starter templates, not production-ready infrastructure modules.
Production modules should be generated from the spec and validated by the
organization's preferred IaC and policy gates.
