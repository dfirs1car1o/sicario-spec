# Azure Verified Modules - Terraform Starter

Use Azure Verified Modules (AVM) for Azure Terraform deployments where an AVM
exists for the target resource or pattern.

Source indexes:

- https://azure.github.io/Azure-Verified-Modules/indexes/terraform/tf-resource-modules/
- https://registry.terraform.io/namespaces/Azure

Rules:

- Prefer `Azure/avm-*` modules over ad hoc modules for common Azure resources.
- Pin module versions deliberately.
- Review module parameters, defaults, diagnostics, identity, private networking,
  encryption, and tags before production.
- Record module version and rationale in the feature plan.
- Run `terraform validate`, plan review, and policy-as-code checks before merge.

