# Security Toolchain Starter

This folder documents the expected security tools and evidence paths for a
project using the `security-toolchain` profile.

Recommended tools:

- Secret scanning: Gitleaks or detect-secrets
- SAST/static checks: Semgrep or language-native analyzers
- Dependency/SCA: pip-audit, npm audit, osv-scanner, Grype
- SBOM: Syft or language-native SBOM generation
- Container scanning: Trivy or Grype
- IaC scanning: Checkov, tfsec, Trivy
- Policy-as-code: OPA/Conftest, Azure Policy, Kubernetes admission policies

Pin versions before production use and record evidence paths in
`docs/compliance/evidence-index.md`.
