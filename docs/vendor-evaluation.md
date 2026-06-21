# Vendor Evaluation

Status: initial desk review. Pin versions and review source before vendoring or
depending on external presets/extensions.

This is a capability/license desk-review of ecosystem components we may reuse,
borrow from, or reference. It is **not** a competitive comparison or positioning
claim; it intentionally describes components by capability rather than by vendor.

| Component | Source | License | Initial Decision | Notes |
|---|---|---|---|---|
| GitHub Spec Kit core | https://github.com/github/spec-kit | Project license | Use | Base SDD engine. Validate supported versions before release. |
| Community security-governance preset | Public Spec Kit catalog | MIT per catalog | Evaluate / borrow | Advisory-append pattern covering SSDF, ASVS, SBOM/AI-SBOM, NIS2, CRA, EU AI Act, DORA. |
| Community architecture-governance preset | Public Spec Kit catalog | MIT per catalog | Evaluate / borrow | Covers STRIDE/CAPEC, S-ADRs, Zero Trust, OWASP SAMM, cloud assurance. |
| Community security-review extension | Public Spec Kit catalog | MIT per catalog | Evaluate / maybe wrap | Useful review commands. Not directly installable from default community catalog. |
| Community architecture-guard extension | Public Spec Kit catalog | MIT per catalog | Evaluate / maybe wrap | Useful architecture drift and governance checks. |
| Vendor IaC Spec Kit pattern | Public catalog | Review before reuse | Reference | Useful IaC adaptation pattern. |

Review checklist before reuse:

- license compatibility
- tagged release or pinned commit
- install scripts
- network calls
- destructive writes
- secret handling
- dependency pinning
- source clarity

