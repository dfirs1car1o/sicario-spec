# SicarioSpec Security Toolchain Checklist: [FEATURE NAME]

**Purpose**: Verify security scanning and evidence readiness.
**Created**: [DATE]
**Feature**: [link]

## Toolchain

- [ ] CHK001 Secret scan passed.
- [ ] CHK002 SAST/static checks passed.
- [ ] CHK003 Dependency/SCA scan passed.
- [ ] CHK004 SBOM generated or no-impact decision recorded.
- [ ] CHK005 Container scan passed where applicable.
- [ ] CHK006 IaC scan passed where applicable.
- [ ] CHK007 Policy-as-code checks passed where applicable.
- [ ] CHK008 Findings are linked to tickets, accepted risk, or remediation.

## Evidence

- [ ] CHK009 Evidence index is updated.
- [ ] CHK010 Gate summary is generated.
- [ ] CHK011 Security exceptions are time-bound and approved.
- [ ] CHK012 `sicario verify` passed.
