# Control Maps

SicarioSpec includes starter control maps for cloud assurance and audit evidence
readiness. These maps are traceability aids, not certification claims.

## Included Maps

SicarioSpec ships starter maps for 14 frameworks. Each is a coarse traceability
aid (theme / domain / family / practice-group / function / requirement / safeguard
level), not a control-by-control crosswalk and not a certification claim. Maps
are split into two tiers - **supported** and **experimental** - described in
[Map tiers](#map-tiers) below.

| Map | Tier | Granularity | Purpose | Source |
|---|---|---|---|---|
| CSA CCM v4.1 | supported | Domain-level (17 domains) | Cloud assurance, shared responsibility, cloud control evidence | `control_maps/ccm-v4.1-sicario.json` |
| SOX 404 / ICFR ITGC | supported | Control-area | Evidence readiness for financially relevant systems | `control_maps/sox-404-itgc-sicario.json` |
| SOC 2 Trust Services Criteria | supported | Criteria-family + trust-services category | Security, availability, confidentiality, processing integrity, and privacy evidence readiness | `control_maps/soc2-trust-services-sicario.json` |
| FedRAMP Rev. 5 | supported | Baseline + control-family | Federal cloud authorization and continuous-monitoring evidence readiness | `control_maps/fedramp-rev5-sicario.json` |
| BSI C5:2026 | supported | Criteria-area | Cloud service provider assurance evidence readiness | `control_maps/bsi-c5-2026-sicario.json` |
| NIST SSDF (SP 800-218) | supported | Practice-group (PO/PS/PW/RV) | Secure software development practice evidence | `control_maps/ssdf-800-218-sicario.json` |
| NIST AI RMF (AI 100-1) | experimental | Function-level (Govern/Map/Measure/Manage) | AI risk governance evidence | `control_maps/ai-rmf-sicario.json` |
| ISO/IEC 27001:2022 | supported | Theme + control-group (4 themes, 93 Annex A controls) | ISMS control evidence | `control_maps/iso-27001-2022-sicario.json` |
| NIST SP 800-53 Rev 5 | supported | Control-family (20 families) | Federal/enterprise control evidence | `control_maps/nist-800-53-r5-sicario.json` |
| EU AI Act (Reg. 2024/1689) | supported | Risk-tier + high-risk obligation (Art. 9-15) | AI regulatory governance evidence | `control_maps/eu-ai-act-sicario.json` |
| GDPR (+ CPRA parallels) | supported | Principle + duty (Art. 5 + DPIA/rights/breach) | Privacy program evidence | `control_maps/gdpr-cpra-sicario.json` |
| PCI DSS v4.0 | experimental | Requirement-level (12 requirements) | Cardholder-data-environment evidence | `control_maps/pci-dss-v4.0-sicario.json` |
| HIPAA Security Rule | supported | Safeguard (Administrative/Physical/Technical) | ePHI safeguard evidence | `control_maps/hipaa-security-rule-sicario.json` |
| OWASP ASVS | experimental | Verification area | Application security verification evidence | `control_maps/owasp-asvs-sicario.json` |

Frameworks named in templates and docs but **not yet shipped as a control map**
(treated as advisory until a map exists): SLSA, OWASP SAMM, OWASP LLM/Agentic
AI risks, NIS2, CRA, and DORA. Contributions adding these maps are welcome -
see the control-map issue form.

## Map Tiers

The 14 maps are not equally deep, so they are split into two tiers rather than
presented as peers.

**Supported** (11 selector keys): `ccm`, `sox`, `soc2`, `fedramp`, `bsi-c5`,
`ssdf`, `iso27001`, `nist-800-53`, `eu-ai-act`, `gdpr`, `hipaa`.

**Experimental** (3 selector keys): `pci-dss`, `ai-rmf`, `owasp-asvs`.

What "experimental" changes - and what it does not:

- Experimental maps remain fully installable. They ship exactly as before.
- `sicario verify` enforces them exactly like supported maps when they are
  explicitly selected via `--frameworks`. Selecting one and then deleting its
  map is still a `SICARIO-MISSING-FRAMEWORK-MAP` finding.
- The only behavioral difference: experimental maps are excluded from
  per-profile defaults. They are never selected implicitly - a team opts in by
  naming them on `--frameworks`. This includes `enterprise-strict`, which
  previously defaulted to all 14 and now defaults to the 11 supported maps.
- CLI output labels experimental selections, e.g. `owasp-asvs (experimental)`.

Upgrade note: a project initialized before tiering keeps whatever
`.sicario/frameworks.txt` already records, because `sicario init` preserves an
existing selector rather than clobbering it. If that file lists an experimental
key it stays enforced on an ordinary re-run. `init` reports the preserved set
rather than the recomputed defaults and flags the difference, so the output
always states what is actually enforced. Re-run with `--force`, or edit the file,
to adopt the new defaults.

Why these three are experimental:

- `pci-dss`: about 29% of its evidence references resolve to bare directory
  names, and it covers the 12 top-level requirements against roughly 300
  sub-requirements with no sub-requirement detail.
- `ai-rmf`: its `example_categories` values (e.g. "GOVERN 1") are
  function-level labels, not real AI RMF subcategory identifiers, so the
  apparent precision is cosmetic.
- `owasp-asvs`: 3 entries and 7 evidence references, covering roughly a fifth
  of the standard.

Tiering changes which maps a profile enforces by default. It does not make any
map deeper, and it does not make anything certifiable.

## Selecting which frameworks apply (`--frameworks`)

You almost never owe evidence for all 14 frameworks. The **framework selector**
lets a project declare the subset it enforces, so `sicario verify` requires a
control map for exactly those frameworks - not all 14, and not none.

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

| Selector key | Tier | Framework | Control map |
|---|---|---|---|
| `ccm` | supported | CSA CCM v4.1 | `ccm-v4.1-sicario.json` |
| `sox` | supported | SOX 404 / ICFR ITGC | `sox-404-itgc-sicario.json` |
| `soc2` | supported | SOC 2 Trust Services Criteria | `soc2-trust-services-sicario.json` |
| `fedramp` | supported | FedRAMP Rev. 5 | `fedramp-rev5-sicario.json` |
| `bsi-c5` | supported | BSI C5:2026 | `bsi-c5-2026-sicario.json` |
| `ssdf` | supported | NIST SSDF (SP 800-218) | `ssdf-800-218-sicario.json` |
| `ai-rmf` | experimental | NIST AI RMF (AI 100-1) | `ai-rmf-sicario.json` |
| `iso27001` | supported | ISO/IEC 27001:2022 | `iso-27001-2022-sicario.json` |
| `nist-800-53` | supported | NIST SP 800-53 Rev 5 | `nist-800-53-r5-sicario.json` |
| `eu-ai-act` | supported | EU AI Act (Reg. 2024/1689) | `eu-ai-act-sicario.json` |
| `gdpr` | supported | GDPR (+ CPRA parallels) | `gdpr-cpra-sicario.json` |
| `pci-dss` | experimental | PCI DSS v4.0 | `pci-dss-v4.0-sicario.json` |
| `hipaa` | supported | HIPAA Security Rule | `hipaa-security-rule-sicario.json` |
| `owasp-asvs` | experimental | OWASP ASVS | `owasp-asvs-sicario.json` |

**Defaults.** If you omit `--frameworks`, the selection defaults to the
profile's natural framework set (e.g. `compliance` -> `ccm`, `sox`, `soc2`,
`iso27001`, `nist-800-53`; `cloud-iac` -> `ccm`, `fedramp`, `bsi-c5`,
`nist-800-53`; `ai-system` -> `eu-ai-act`; `enterprise-strict` -> the 11
supported maps). Profile defaults contain only supported-tier maps: the
experimental keys (`pci-dss`, `ai-rmf`, `owasp-asvs`) are enforced only when
named explicitly. A bare `public-core` carries no compliance obligation, so it writes no
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
- SOC 2 mappings are Trust Services Criteria readiness starters. SOC 2 reports
  are attestation reports issued by qualified CPA firms; use the official AICPA
  criteria, your system description, control design, operating-effectiveness
  evidence, and auditor guidance.
- FedRAMP mappings are Rev. 5 baseline and control-family starters. A real
  package requires official FedRAMP templates or OSCAL artifacts, control
  implementation statements, assessor evidence, agency authorization review,
  and continuous monitoring.
- BSI C5 mappings are cloud criteria-area starters. A real attestation depends
  on the official BSI C5 catalogue, the scoped cloud service description,
  independent audit evidence, and provider/customer responsibility boundaries.
- SSDF mappings are practice-group (PO/PS/PW/RV) starters. Authoritative
  practices, tasks, and implementation examples live in NIST SP 800-218;
  demonstrating actual practice implementation is yours.
- AI RMF mappings (experimental) are function-level starters. The category
  labels they cite are function-level, not official AI RMF subcategory
  identifiers; use the official NIST AI RMF and its Playbook for
  subcategory-level work.
- OWASP ASVS mappings (experimental) cover only a small slice of the standard
  (roughly a fifth). Use the official ASVS for the full verification
  requirements and level definitions.
- ISO/IEC 27001 and NIST SP 800-53 maps are theme-/family-level. Authoritative
  control text lives in ISO/IEC 27002:2022 and NIST SP 800-53 Rev 5; selection
  and tailoring (Statement of Applicability, 800-53B baselines) are yours.
- EU AI Act, GDPR/CPRA, PCI DSS, and HIPAA maps are regulatory- and audit-shaped
  guidance, **not legal advice or a conformity/compliance assessment**. Confirm
  classification, lawful basis, CDE scope, ePHI scope, and conformity with
  qualified counsel, a DPO, a QSA, or a notified body as applicable.
