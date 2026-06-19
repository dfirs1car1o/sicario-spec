# Threat Model

## Scope

SicarioSpec bootstrap CLI, presets, extension command metadata, generated
governance artifacts, docs scaffold, and offline verification.

## Trust Boundaries

- User shell to `sicario` CLI.
- SicarioSpec source repo to generated target project.
- Generated model/agent guidance to developer tools.
- Target project files to deterministic verifier.

## Threats

| Threat | Impact | Control | Status |
|---|---|---|---|
| Bootstrap overwrites user files | High | Refuse overwrite unless `--force` | Implemented |
| Generated files escape target repo | High | Resolve target path and write only under selected target | Implemented |
| Hardcoded secrets in target repo | Critical | Pattern scan in `sicario verify` | Implemented |
| AI-sensitive spec omits prompt injection guardrails | High | Keyword and section validation | Implemented |
| Documentation drift hides behavior change | Medium | docs impact and docs/diagrams checks | Implemented |

## Human Approval Boundaries

Publishing releases, adding direct external writes, and enabling CI commits back
to protected branches require human approval.

