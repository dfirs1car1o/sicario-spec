# Control Applicability

Tier reflects the shipped control-map tier (see
[docs/control-maps.md](../control-maps.md#map-tiers)): supported maps can be
enforced by profile defaults; experimental maps are enforced only when named
explicitly on `--frameworks`. Advisory rows have no shipped map.

| Domain | Tier | Applicable | Control Map | Evidence |
|---|---|---:|---|---|
| NIST SSDF (SP 800-218) | supported | Yes | `control_maps/ssdf-800-218-sicario.json` | secure templates, verification, tests, supply-chain |
| NIST AI RMF (AI 100-1) | experimental | Partial | `control_maps/ai-rmf-sicario.json` | AI risk prompts, threat model, evals, approval gates |
| CSA CCM v4.1 | supported | Partial | `control_maps/ccm-v4.1-sicario.json` | cloud/IaC profile, shared-responsibility evidence |
| SOX 404 / ICFR ITGC | supported | Partial | `control_maps/sox-404-itgc-sicario.json` | change/access/operations evidence |
| SOC 2 Trust Services Criteria | supported | Partial | `control_maps/soc2-trust-services-sicario.json` | security, availability, confidentiality, processing-integrity, and privacy evidence |
| FedRAMP Rev. 5 | supported | Partial | `control_maps/fedramp-rev5-sicario.json` | federal cloud baseline, authorization, continuous monitoring evidence |
| BSI C5:2026 | supported | Partial | `control_maps/bsi-c5-2026-sicario.json` | cloud service provider assurance, operations, supplier, continuity evidence |
| ISO/IEC 27001:2022 | supported | Partial | `control_maps/iso-27001-2022-sicario.json` | ISMS-shaped evidence: policies, risk registers, exceptions, accepted-risk log |
| NIST SP 800-53 Rev 5 | supported | Partial | `control_maps/nist-800-53-r5-sicario.json` | control-family evidence via compliance and cloud/IaC profiles |
| EU AI Act (Reg. 2024/1689) | supported | Partial | `control_maps/eu-ai-act-sicario.json` | AI-system profile prompts, risk-tier classification, high-risk obligation evidence |
| GDPR (+ CPRA parallels) | supported | No | `control_maps/gdpr-cpra-sicario.json` | this repo processes no personal data; map ships for downstream projects |
| PCI DSS v4.0 | experimental | No | `control_maps/pci-dss-v4.0-sicario.json` | no cardholder data environment; map ships for downstream projects |
| HIPAA Security Rule | supported | No | `control_maps/hipaa-security-rule-sicario.json` | no ePHI; map ships for downstream projects |
| OWASP ASVS | experimental | Yes | `control_maps/owasp-asvs-sicario.json` | appsec profile requirements, threat model, abuse cases, tests |
| OWASP SAMM | advisory | Yes | none (advisory) | governance and review model |
| SLSA | advisory | Partial | none (advisory) | supply-chain profile, provenance readiness |
| OWASP LLM / Agentic AI risks | advisory | Yes | none (advisory) | AI-system profile |
| Docs-as-code | n/a | Yes | none | sicario-docs profile |
