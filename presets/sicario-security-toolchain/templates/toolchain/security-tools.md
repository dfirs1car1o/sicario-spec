# Security Tools Inventory

| Tool | Purpose | Required? | Version Pin | Evidence Path |
|---|---|---:|---|---|
| Gitleaks / detect-secrets | Secret scan | Yes | TBD | generated/security/secrets.json |
| Semgrep | SAST/static analysis | Yes | TBD | generated/security/sast.json |
| Syft | SBOM | Yes | TBD | generated/security/sbom.spdx.json |
| Grype / Trivy | Vulnerability scan | Yes | TBD | generated/security/vulnerabilities.json |
| Checkov / tfsec / Trivy | IaC scan | If IaC exists | TBD | generated/security/iac.json |
| OPA / Conftest | Policy-as-code | If policies exist | TBD | generated/security/policy.json |
