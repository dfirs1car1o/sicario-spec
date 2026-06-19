# Policy As Code Starter

Use this folder to keep cloud, Kubernetes, and IaC policies source-controlled.

Included starters:

- `checkov.yml`: Checkov scan configuration.
- `opa/conftest/iac.rego`: OPA/Conftest policy starter.
- `azure-policy/deny-public-storage.json`: Azure Policy starter.
- `kubernetes/kyverno-require-non-root.yaml`: Kubernetes admission policy starter.

These are examples, not production policy libraries. Validate against your cloud
platform, tenancy model, and exception process before enforcement.
