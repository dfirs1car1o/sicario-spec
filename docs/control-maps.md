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

## Selecting which frameworks apply (`--frameworks`)

You almost never owe evidence for all 10 frameworks. The **framework selector**
lets a project declare the subset it enforces, so `sicario verify` requires a
control map for exactly those frameworks — not all 10, and not none.

```bash
# Enforce only ISO 27001 and HIPAA for this project:
sicario init my-project --profile compliance --frameworks iso27001,hipaa

# Enforce every shipped framework:
sicario init my-project --profile enterprise-strict --frameworks all
```

This writes a plain-text project config, `.sicario/frameworks.txt` (one
framework key per line). `sicario verify` reads it and emits
`SICARIO-MISSING-FRAMEWORK-MAP` for any **selected** framework whose control map
is absent. Unselected frameworks are not required.

| Selector key | Framework | Control map |
|---|---|---|
| `ccm` | CSA CCM v4.1 | `ccm-v4.1-sicario.json` |
| `sox` | SOX 404 / ICFR ITGC | `sox-404-itgc-sicario.json` |
| `ssdf` | NIST SSDF (SP 800-218) | `ssdf-800-218-sicario.json` |
| `ai-rmf` | NIST AI RMF (AI 100-1) | `ai-rmf-sicario.json` |
| `iso27001` | ISO/IEC 27001:2022 | `iso-27001-2022-sicario.json` |
| `nist-800-53` | NIST SP 800-53 Rev 5 | `nist-800-53-r5-sicario.json` |
| `eu-ai-act` | EU AI Act (Reg. 2024/1689) | `eu-ai-act-sicario.json` |
| `gdpr` | GDPR (+ CPRA parallels) | `gdpr-cpra-sicario.json` |
| `pci-dss` | PCI DSS v4.0 | `pci-dss-v4.0-sicario.json` |
| `hipaa` | HIPAA Security Rule | `hipaa-security-rule-sicario.json` |

**Defaults.** If you omit `--frameworks`, the selection defaults to the
profile's natural framework set (e.g. `compliance` -> `ccm`, `sox`, `iso27001`,
`nist-800-53`; `ai-system` -> `ai-rmf`, `eu-ai-act`; `enterprise-strict` -> all
10). A bare `public-core` carries no compliance obligation, so it writes no
selector and `verify` keeps its prior coarse control-map check (the single
`SICARIO-MISSING-CONTROL-MAPS`). Delete `.sicario/frameworks.txt` to return to
that default behavior at any time.

## How To Use

1. Choose the frameworks you enforce with `--frameworks` (see above).
2. Select applicable domains in `docs/compliance/control-applicability.md`.
3. Link each applicable domain to concrete evidence in
   `docs/compliance/evidence-index.md`.
4. Record exceptions in `docs/risk/security-exceptions.md`.
5. Record accepted residual risk in `docs/risk/accepted-risk-log.md`.
6. Run `sicario verify` before handoff.

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
