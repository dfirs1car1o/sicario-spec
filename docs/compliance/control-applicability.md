# Control Applicability

| Domain | Applicable | Control Map | Evidence |
|---|---:|---|---|
| NIST SSDF (SP 800-218) | Yes | `control_maps/ssdf-800-218-sicario.json` | secure templates, verification, tests, supply-chain |
| NIST AI RMF (AI 100-1) | Partial | `control_maps/ai-rmf-sicario.json` | AI risk prompts, threat model, evals, approval gates |
| CSA CCM v4.1 | Partial | `control_maps/ccm-v4.1-sicario.json` | cloud/IaC profile, shared-responsibility evidence |
| SOX 404 / ICFR ITGC | Partial | `control_maps/sox-404-itgc-sicario.json` | change/access/operations evidence |
| SOC 2 Trust Services Criteria | Partial | `control_maps/soc2-trust-services-sicario.json` | security, availability, confidentiality, processing-integrity, and privacy evidence |
| FedRAMP Rev. 5 | Partial | `control_maps/fedramp-rev5-sicario.json` | federal cloud baseline, authorization, continuous monitoring evidence |
| BSI C5:2026 | Partial | `control_maps/bsi-c5-2026-sicario.json` | cloud service provider assurance, operations, supplier, continuity evidence |
| OWASP ASVS | Yes | `control_maps/owasp-asvs-sicario.json` | appsec profile requirements, threat model, abuse cases, tests |
| OWASP SAMM | Yes | none (advisory) | governance and review model |
| SLSA | Partial | none (advisory) | supply-chain profile, provenance readiness |
| OWASP LLM / Agentic AI risks | Yes | none (advisory) | AI-system profile |
| Docs-as-code | Yes | none | sicario-docs profile |
