# SicarioSpec Security Toolchain Checklist: [FEATURE NAME]

**Purpose**: Verify security scanning and evidence readiness.
**Created**: [DATE]
**Feature**: [link]

## Classification And Tagging

- [ ] CHK001 Data classification covers scanner output, SBOMs, findings, evidence, and release artifacts.
- [ ] CHK002 Tagging discipline covers scanners, artifact types, evidence paths, findings, risks, and exceptions.

## Toolchain

- [ ] CHK003 Secret scan passed.
- [ ] CHK004 SAST/static checks passed.
- [ ] CHK005 Dependency/SCA scan passed.
- [ ] CHK006 SBOM generated or no-impact decision recorded.
- [ ] CHK007 Container scan passed where applicable.
- [ ] CHK008 IaC scan passed where applicable.
- [ ] CHK009 Policy-as-code checks passed where applicable.
- [ ] CHK010 Findings are linked to tickets, accepted risk, or remediation.

## Evidence

- [ ] CHK011 Evidence index is updated.
- [ ] CHK012 Gate summary is generated.
- [ ] CHK013 Security exceptions are time-bound and approved.
- [ ] CHK014 `sicario verify` passed.
