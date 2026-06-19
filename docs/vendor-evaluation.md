# Vendor Evaluation

Status: initial desk review. Pin versions and review source before vendoring or
depending on external presets/extensions.

| Component | Source | License | Initial Decision | Notes |
|---|---|---|---|---|
| GitHub Spec Kit core | https://github.com/github/spec-kit | Project license | Use | Base SDD engine. Validate supported versions before release. |
| Security Governance preset | https://github.com/hindermath/spec-kit-preset-security-governance | MIT per catalog | Evaluate / borrow | Covers SSDF, ASVS, SBOM/AI-SBOM, NIS2, CRA, EU AI Act, DORA. |
| Architecture Governance preset | https://github.com/hindermath/spec-kit-preset-architecture-governance | MIT per catalog | Evaluate / borrow | Covers STRIDE/CAPEC, S-ADRs, Zero Trust, OWASP SAMM, cloud assurance. |
| Security Review extension | https://github.com/DyanGalih/spec-kit-security-review | MIT per catalog | Evaluate / maybe wrap | Useful review commands. Not directly installable from default community catalog. |
| Architecture Guard extension | https://github.com/DyanGalih/spec-kit-architecture-guard | MIT per catalog | Evaluate / maybe wrap | Useful architecture drift and governance checks. |
| IBM IaC Spec Kit | https://github.com/IBM/iac-spec-kit | Review before reuse | Reference | Useful IaC adaptation pattern. |

Review checklist before reuse:

- license compatibility
- tagged release or pinned commit
- install scripts
- network calls
- destructive writes
- secret handling
- dependency pinning
- source clarity

