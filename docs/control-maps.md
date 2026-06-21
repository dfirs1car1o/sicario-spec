# Control Maps

SicarioSpec includes starter control maps for cloud assurance and audit evidence
readiness. These maps are traceability aids, not certification claims.

## Included Maps

| Map | Granularity | Purpose | Source |
|---|---|---|---|
| CSA CCM v4.1 | Domain-level | Cloud assurance, shared responsibility, cloud control evidence | `control_maps/ccm-v4.1-sicario.json` |
| SOX 404 / ICFR ITGC | Control-area | Evidence readiness for financially relevant systems | `control_maps/sox-404-itgc-sicario.json` |
| NIST SSDF (SP 800-218) | Practice-group (PO/PS/PW/RV) | Secure software development practice evidence | `control_maps/ssdf-800-218-sicario.json` |
| NIST AI RMF (AI 100-1) | Function-level (Govern/Map/Measure/Manage) | AI risk governance evidence | `control_maps/ai-rmf-sicario.json` |

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
