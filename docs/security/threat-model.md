# Threat Model

## Scope

SicarioSpec bootstrap CLI, presets, extension command metadata, generated
governance artifacts, docs scaffold, and offline verification.

## Trust Boundaries

- User shell to `sicario` CLI.
- SicarioSpec source repo to generated target project.
- Generated model/agent guidance to developer tools.
- Target project files to deterministic verifier.

## Methodology

Threats are categorized by STRIDE (Spoofing, Tampering, Repudiation, Information
Disclosure, Denial of Service, Elevation of Privilege).

## Threats

| Threat | STRIDE Category | Impact | Control | Status |
|---|---|---|---|---|
| Bootstrap overwrites user files without consent | Tampering | High | Brownfield-safe default: existing files are additively merged/overlaid or preserved, never fully overwritten; full overwrite requires explicit `--force`; a timestamped `*.sicario-bak.*` backup is taken before any overwrite; `--dry-run` previews every decision without writing | Implemented |
| Generated files escape target repo directory | Tampering | High | Resolve target path to absolute; restrict all writes to under selected target | Implemented |
| Hardcoded secrets in target repo pass undetected | Information Disclosure | Critical | Pattern-based secret scan in `sicario verify`; extendable via custom rule files | Implemented |
| AI-sensitive spec omits prompt-injection guardrails | Tampering | High | Keyword and section validation in verify gate; non-zero exit on missing sections | Implemented |
| Documentation drift hides behavior change | Repudiation | Medium | docs-impact tracking and docs/diagrams existence checks in verify | Implemented |
| Unauthenticated user modifies `.rule.json` files to weaken gates | Tampering | High | Rule files are under version control and changes are visible in PR diff; every override of a rule `id` is additionally recorded in `scan_coverage.overrides` in gate evidence with an `impact` string (e.g. `disables-critical-severity-rule`); a rule file that fails validation or cannot be read surfaces as a critical `SICARIO-RULE-INVALID` / `SICARIO-RULE-UNREADABLE` finding; `sicario verify --validate-rules` checks rule files pre-run; a run that loads zero rules fails closed with `SICARIO-NO-RULES-LOADED`, and a `SICARIO_ASSET_ROOT` redirect of the shipped rule source fails the run with `SICARIO-ASSET-ROOT-OVERRIDE` (see [rule-engine.md](../rule-engine.md)) | Implemented |
| CI pipeline bypasses verify by exiting early or masking exit code | Spoofing | High | CI workflow enforces `sicario verify` as a required step; branch protection requires passing status check | Implemented |
| Concurrent CI jobs race on shared gate-summary output | Denial of Service | Low | CI runners are single-threaded per job; not exploitable in current architecture | Accepted |
| Preset output injection via malicious template or content generator | Tampering | High | Preset classes are version-controlled Python modules; generated paths are fixed relative paths under the selected target; no runtime fetching of external content; content generators use only stdlib and hardcoded templates | Implemented |

## Human Approval Boundaries

Publishing releases, adding direct external writes, and enabling CI commits back
to protected branches require human approval.
