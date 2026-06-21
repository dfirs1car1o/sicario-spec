# Control Applicability

| Domain | Applicable | Control Map | Evidence |
|---|---:|---|---|
| NIST SSDF (SP 800-218) | Yes | `control_maps/ssdf-800-218-sicario.json` | secure templates, verification, tests, supply-chain |
| NIST AI RMF (AI 100-1) | Partial | `control_maps/ai-rmf-sicario.json` | AI risk prompts, threat model, evals, approval gates |
| CSA CCM v4.1 | Partial | `control_maps/ccm-v4.1-sicario.json` | cloud/IaC profile, shared-responsibility evidence |
| SOX 404 / ICFR ITGC | Partial | `control_maps/sox-404-itgc-sicario.json` | change/access/operations evidence |
| OWASP ASVS | Yes | none (advisory) | appsec profile requirements |
| OWASP SAMM | Yes | none (advisory) | governance and review model |
| SLSA | Partial | none (advisory) | supply-chain profile, provenance readiness |
| OWASP LLM / Agentic AI risks | Yes | none (advisory) | AI-system profile |
| Docs-as-code | Yes | none | sicario-docs profile |
