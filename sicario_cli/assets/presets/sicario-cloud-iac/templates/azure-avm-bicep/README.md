# Azure Verified Modules - Bicep Starter

Use Azure Verified Modules (AVM) for Azure Bicep deployments where an AVM
exists for the target resource or pattern.

Source indexes:

- https://azure.github.io/Azure-Verified-Modules/indexes/bicep/
- https://github.com/Azure/bicep-registry-modules

Rules:

- Prefer AVM modules over hand-rolled Bicep for common Azure resources.
- Pin module versions deliberately.
- Review module parameters, defaults, diagnostics, identity, private networking,
  encryption, and tags before production.
- Record module version and rationale in the feature plan.
- Run Bicep validation and policy-as-code checks before merge.

