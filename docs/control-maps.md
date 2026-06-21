# Control Maps

SicarioSpec includes starter control maps for cloud assurance and audit evidence
readiness. These maps are traceability aids, not certification claims.

## Included Maps

SicarioSpec ships starter maps for 10 frameworks. Each is a coarse traceability
aid (theme / domain / family / practice-group / function / requirement / safeguard
level), not a control-by-control crosswalk and not a certification claim.

| Map | Granularity | Purpose | Source |
|---|---|---|---|
| CSA CCM v4.1 | Domain-level (17 domains) | Cloud assurance, shared responsibility, cloud control evidence | `control_maps/ccm-v4.1-sicario.json` |
| SOX 404 / ICFR ITGC | Control-area | Evidence readiness for financially relevant systems | `control_maps/sox-404-itgc-sicario.json` |
| NIST SSDF (SP 800-218) | Practice-group (PO/PS/PW/RV) | Secure software development practice evidence | `control_maps/ssdf-800-218-sicario.json` |
| NIST AI RMF (AI 100-1) | Function-level (Govern/Map/Measure/Manage) | AI risk governance evidence | `control_maps/ai-rmf-sicario.json` |
| ISO/IEC 27001:2022 | Theme + control-group (4 themes, 93 Annex A controls) | ISMS control evidence | `control_maps/iso-27001-2022-sicario.json` |
| NIST SP 800-53 Rev 5 | Control-family (20 families) | Federal/enterprise control evidence | `control_maps/nist-800-53-r5-sicario.json` |
| EU AI Act (Reg. 2024/1689) | Risk-tier + high-risk obligation (Art. 9-15) | AI regulatory governance evidence | `control_maps/eu-ai-act-sicario.json` |
| GDPR (+ CPRA parallels) | Principle + duty (Art. 5 + DPIA/rights/breach) | Privacy program evidence | `control_maps/gdpr-cpra-sicario.json` |
| PCI DSS v4.0 | Requirement-level (12 requirements) | Cardholder-data-environment evidence | `control_maps/pci-dss-v4.0-sicario.json` |
| HIPAA Security Rule | Safeguard (Administrative/Physical/Technical) | ePHI safeguard evidence | `control_maps/hipaa-security-rule-sicario.json` |

Frameworks named in templates and docs but **not yet shipped as a control map**
(treated as advisory until a map exists): SLSA, OWASP ASVS, OWASP SAMM, and
OWASP LLM/Agentic AI risks. Contributions adding these maps are welcome — see the
control-map issue form.

## How To Use

1. Select applicable domains in `docs/compliance/control-applicability.md`.
2. Link each applicable domain to concrete evidence in
   `docs/compliance/evidence-index.md`.
3. Record exceptions in `docs/risk/security-exceptions.md`.
4. Record accepted residual risk in `docs/risk/accepted-risk-log.md`.
5. Run `sicario verify` before handoff.

## Important Boundaries

- CCM mappings are domain-level starters. Use CSA's official artifact for
  authoritative control text, CAIQ questions, shared-responsibility details, and
  audit guidance.
- SOX mappings are ITGC evidence starters. SOX Section 404 focuses on internal
  control over financial reporting, so final scoping must be performed with the
  finance, audit, and legal stakeholders for systems that affect financial
  reporting.
- ISO/IEC 27001 and NIST SP 800-53 maps are theme-/family-level. Authoritative
  control text lives in ISO/IEC 27002:2022 and NIST SP 800-53 Rev 5; selection
  and tailoring (Statement of Applicability, 800-53B baselines) are yours.
- EU AI Act, GDPR/CPRA, PCI DSS, and HIPAA maps are regulatory- and audit-shaped
  guidance, **not legal advice or a conformity/compliance assessment**. Confirm
  classification, lawful basis, CDE scope, ePHI scope, and conformity with
  qualified counsel, a DPO, a QSA, or a notified body as applicable.
