# Changelog

All notable changes to SicarioSpec are tracked here.

The project follows semantic versioning once the public API stabilizes. During
the `0.x` line, minor versions may introduce breaking changes when needed to
improve the security model.

## [Unreleased]

### Changed

- **Control maps are now tiered supported vs experimental.** The 14 shipped
  maps no longer present as peers. `pci-dss`, `ai-rmf`, and `owasp-asvs` are
  labeled EXPERIMENTAL: PCI DSS resolves roughly 29% of its evidence to bare
  directory names and covers 12 requirements against ~300 sub-requirements;
  AI RMF's `example_categories` are function labels rather than real
  subcategory identifiers; OWASP ASVS ships 3 entries covering about a fifth
  of the standard. Experimental maps remain fully installable and are still
  enforced by `sicario verify` when named explicitly on `--frameworks` — the
  only behavioral change is that they are excluded from every per-profile
  default, including `enterprise-strict`, which now defaults to the 11
  supported maps rather than all 14.

### Fixed

- **Backup ignore rule is now verified as effective, not merely present.** Git
  applies the last matching pattern, so a `.gitignore` containing
  `*.sicario-bak.*` followed by a negation re-included backups while a
  presence-only check reported them protected. `init` now re-asserts the rule so
  it is the deciding one, preserves CRLF line endings instead of rewriting every
  line, and refuses to write through a symlinked `.gitignore` (which would edit a
  file outside the project). A nested `.gitignore` negating the rule for a
  subtree remains a documented limitation.
- **`init` now reports the framework set it actually enforces.** On a re-run the
  existing `.sicario/frameworks.txt` is preserved, so the recomputed profile
  defaults may not be what is enforced; printing them stated the opposite of the
  truth. The preserved set is reported and any divergence is flagged.

- **Broken control-map evidence anchors.** Five references pointed at headings
  that exist in no shipped template. All 19 distinct anchors across all maps
  now resolve.
- **`fedramp-rev5` `control_family_count`** claimed 18 while shipping 13.
- **`ccm-v4.1` domain 12** was "Infrastructure Security" / "I&S"; the official
  CCM v4 domain is "Infrastructure and Virtualization Security" / "IVS".
- **`owasp-asvs` scope note** was the only map claiming to trace controls
  "directly" with no disclaimer; it now carries the same starter-mapping hedge
  as the other 13.

### Security

- **Backups are no longer committable.** `sicario init` now adds
  `*.sicario-bak.*` to the target repository's `.gitignore` before taking the
  first backup. Backups are verbatim copies of the adopting repo's existing
  constitution, instruction files, and Spec Kit templates, so they can carry
  secrets or internal content that was never meant to be committed. The rule is
  written idempotently and never clobbers an existing `.gitignore`. The same
  pattern was added to this repository's own `.gitignore`.

## [0.5.1] - 2026-06-25

### Added

- **Full Spec Kit bundle release path.** Added native release assets for all 11
  presets, `sicario-guard`, the `sicario-spec` bundle, and install-allowed
  preset, extension, and bundle catalogs.
- **Bundle walkthrough.** Added a plain-English walkthrough explaining what the
  bundle is, why it exists, when to use native Spec Kit versus the Python CLI,
  and how to operate the verify loop.
- **SOC 2, FedRAMP Rev. 5, and BSI C5:2026 control maps.** Expanded the shipped
  selectable framework set from 11 to 14 maps.
- **Custom rule example.** Added `examples/custom-rules/` with a Terraform
  `regex-required` rule and README showing how project-owned gates work without
  Python changes.
- **Interactive repo map.** Added a generated Docusaurus repo map for users,
  contributors, reviewers, and maintainers.
- **Declarative rule engine for `sicario verify`.** Replaced 210+ lines of
  hardcoded Python checks with a JSON Schema-driven `RuleEngine` that loads
  `.rule.json` files from `.sicario/rules/`. 10 evaluator kinds cover all
  previous checks: file-exists, file-glob, section-exists, keyword-exists,
  keyword-absent, regex-forbidden, regex-required, risk-rows-valid,
  classification-complete, tagging-complete. Users add custom gates by writing
  a rule file — no Python edits needed. (`specs/002-governance-rule-schema/`)
- **16 shipped rule files** in `presets/sicario-core/rules/` matching the
  previous check set exactly; rules are copied to `.sicario/rules/` during
  `sicario init`.
- **`--format {text,json,sarif}` flag** on `verify` for machine-readable
  output (SARIF 2.1.0, JSON, or human-readable text).
- **`--validate-rules` flag** on `verify` that validates all rule files against
  the schema without running checks.
- **Codex marketplace bundle** (`bundle.yml`) for IDE integration.

### Changed

- Version synced to `0.5.1` for the full bundle release.
- **Positioning reframed to a neutral capability statement.** Removed the named
  competitor call-out from the README, docs-site landing page, and supporting
  docs. The differentiator now leads with the survey-validated moat: a *halting*
  verify gate (non-zero exit blocks the merge, with finding codes) whose verdict
  is owned by stdlib-only code with no LLM in the decision path — versus
  advisory-append patterns generally. No multi-framework-breadth superiority is
  claimed.
- **docs-site swept** to reflect current capabilities: turnkey
  `--apply-to-speckit` wiring, brownfield-safe adoption, the 14 frameworks and
  the new selector, the USAGE flow, and the pass+fail worked example.
- **Spec Kit catalog readiness.** Reworked `sicario-core` around the Security
  Evidence Chain: risk or decision to control, test/gate, evidence path, owner,
  and approval or accepted-risk state.
- **Maintainer operations hardening.** Added `MAINTAINERS.md`,
  `.github/CODEOWNERS`, a maintainer-task issue form, a safe issue-triage
  workflow, and `docs/maintainer-operations.md` so public issues move through
  triage, Spec Kit feature artifacts, reviewed PRs, checks, and non-author
  approval instead of direct issue-to-code automation.
- **Spec Kit dogfood artifacts.** Initialized the repo with Spec Kit Codex
  infrastructure, installed `sicario-core` as a local development preset, and
  added `specs/001-maintainer-operations/` with spec, plan, and tasks for this
  maintainer-ops change.
- **Framework selector (#18).** `sicario init --frameworks <keys>` records which
  of the 14 control-map frameworks a project enforces in
  `.sicario/frameworks.txt`. `sicario verify` honors the subset: each selected
  framework's control map must be present (`SICARIO-MISSING-FRAMEWORK-MAP`),
  while unselected frameworks are not required. Default selection follows the
  profile's framework set; `enterprise-strict` enforces all 14. With no config
  file, `verify` keeps its prior coarse control-map behavior unchanged.
- **Failing worked example** (`examples/python-api-failing/`) — the same governed
  feature as `examples/python-api/` with one required artifact removed, proving
  `sicario verify` is a real halting gate (exit 1 + finding code) reproducible
  from a clean clone.

## [0.4.0] - 2026-06-21

### Added

- **Six new compliance control maps** (10 frameworks total), making the
  `compliance` and `enterprise-strict` profiles credible for regulated
  enterprises. All are starter / domain-level crosswalks, not certification or
  conformity claims:
  - `iso-27001-2022-sicario.json` — ISO/IEC 27001:2022 Annex A, theme +
    control-group level (4 themes, 93 controls).
  - `nist-800-53-r5-sicario.json` — NIST SP 800-53 Rev 5, all 20 control families.
  - `eu-ai-act-sicario.json` — EU AI Act risk tiers + high-risk obligations
    (Articles 9-15).
  - `gdpr-cpra-sicario.json` — GDPR Article 5 principles and duties (DPIA,
    data-subject rights, breach notification) with CPRA/CCPA parallels.
  - `pci-dss-v4.0-sicario.json` — PCI DSS v4.0, all 12 requirements.
  - `hipaa-security-rule-sicario.json` — HIPAA Security Rule Administrative,
    Physical, and Technical safeguards.

### Changed

- `control_maps/README.md`, `docs/control-maps.md`, the docs-site landing page,
  the `/sicario.controls` command, and README "frameworks covered" claims now
  list all 10 frameworks with honest starter / non-certification framing.
- Version synced to `0.4.0` across `VERSION`, `version.py`, `pyproject.toml`,
  preset and extension manifests, and all control maps.

## [0.3.0] - 2026-06-21

Brownfield-safe adoption: `sicario init`/apply no longer silently clobbers an
existing constitution, Spec Kit templates, or agent-instruction files.

### Added

- **Brownfield-safe adoption is now the default.** `sicario init` detects an
  existing setup (`.specify/memory/constitution.md`, `.specify/templates/*`,
  `CLAUDE.md`/`AGENTS.md`, and `mission.md`/project-supremacy files) before
  writing, and merges/overlays instead of skipping or clobbering:
  - **Constitution:** appends a clearly-marked ADDITIVE SicarioSpec overlay that
    explicitly DEFERS to the project's own principles and any `mission.md`
    (a brownfield overlay that yields to `mission.md`).
    The existing constitution is never replaced.
  - **Templates:** appends the SicarioSpec governance-impact gate block to an
    existing `spec/plan/tasks` template — idempotently (no double-append on
    re-run) — rather than overwriting the whole file.
  - **Instructions (`CLAUDE.md`/`AGENTS.md`):** never overwritten; a delimited,
    idempotent SicarioSpec section is appended.
- Every modified file is **backed up first** to a timestamped
  `*.sicario-bak.<UTC>` file.
- A clear per-file **adoption report** prints at the end of every run: each file
  is reported as `created` / `merged-overlaid` / `preserved` / `overwritten`,
  with a summary line.
- `--dry-run` now previews the full per-file adoption report and writes nothing.
- **`USAGE.md` quickstart.** A copy-pasteable usage guide (install → init →
  write specs → `sicario verify` → `sicario hooks`) that makes the mental model
  explicit: SicarioSpec has no "threat-model command" — security/threat modeling
  is enforced as mandatory spec/plan sections checked by `sicario verify`. Linked
  prominently from the README; includes the full finding-code reference and a
  "where does X live?" table.
- **Fully-worked example.** `examples/python-api/` is now a complete governed
  feature (a read-only invoice-export API) with every required section filled in
  and the repo-level governance docs present, so `sicario verify
  examples/python-api` returns `status: pass`. Its `README.md` shows how to
  reproduce the passing gate.

### Changed

- `--force` remains the explicit FULL-OVERWRITE opt-in, but now takes a
  timestamped backup before overwriting any pre-existing file.
- A non-empty target directory is no longer an error: brownfield-safe adoption
  is the default, so `--force` is not required to initialize into an existing
  repository.

## [0.2.0] - 2026-06-21

Spec Kit wiring, honest positioning, expanded control maps, executable hooks, and
a SaaS-hardened profile.

### Added

- `sicario init` now applies the selected governance to the **live Spec Kit
  paths** so `/speckit-*` commands actually pick it up: templates land in
  `.specify/templates/{spec,plan,tasks}-template.md` and the constitution in
  `.specify/memory/constitution.md`. Opt out with `--no-apply-to-speckit`.
- `sicario hooks` command: executes the deterministic Spec Kit hooks
  (`sicario.verify`/`assess`/`evidence`) from `.specify/extensions.yml` and
  honestly reports the agent-guidance hooks instead of pretending to run them.
- New control maps: NIST SSDF (SP 800-218) practice-group map and NIST AI RMF
  (AI 100-1) function-level map, alongside the existing CSA CCM v4.1 and SOX 404
  maps.
- New `sicario-saas` preset and `--profile saas`: read-only-SaaS, tenant/data
  boundary, and mission-supremacy invariants.

### Changed

- README and docs-site positioning: dropped any implication of being the first or
  only Spec Kit security-governance preset; lead with deterministic, code-owned
  verdicts (AI is explanation-only) plus a mandatory governance contract, a
  halting gate, and control maps; added a precise definition of "deterministic";
  differentiated from advisory-append security-governance presets generally.
- Reconciled control-map docs to what is actually shipped (SSDF/AI RMF now mapped;
  SLSA/OWASP ASVS/SAMM/LLM labeled advisory until a map exists).
- Extension docs now clearly distinguish deterministic hooks from agent-guidance
  hooks.

## [0.1.2] - 2026-06-19

Release for agent-native environments, the public documentation site, and
clearer launch positioning.

### Added

- Agent-native bootstrap outputs for Claude Code, Codex, and GitHub Copilot
  coding agent through `--integration codex`, `--integration copilot`, and
  `--integration all`.
- Repo-scoped SicarioSpec skills for verification, governance review, and
  release readiness.
- Copilot instructions and setup workflow for cloud-agent environments.
- Public GitHub Pages documentation site backed by the repository `docs/`
  content.
- Adoption and launch guide for positioning, proof points, and first outreach
  messages.

### Changed

- README positioning, badges, quickstart, generated artifact list, and
  agent-native delivery guidance.

## [0.1.1] - 2026-06-19

Patch release for repository hardening after the initial public release.

### Added

- Machine-user pull request workflow with an audited maintainer fallback for
  environments that cannot provision a machine account.
- Data classification and tagging evidence requirements in the public
  contribution and repository governance workflow.

### Fixed

- Release workflow now builds, smoke-tests, uploads the workflow artifact,
  emits provenance attestations, and treats existing GitHub releases as
  immutable.
- Release reruns no longer attempt to add, replace, delete, or rename assets on
  an existing immutable release.

## [0.1.0] - 2026-06-19

Initial public release.

### Added

- `sicario` CLI with `init`, `verify`, and `assess` commands.
- Composable profiles for core governance, AppSec, AI systems, agent fleets,
  cloud/IaC, security toolchains, supply chain, compliance, docs, and
  enterprise controls.
- Spec Kit presets, templates, and Sicario guard extension commands.
- CCM v4.1 and SOX 404 / ICFR starter control maps.
- Terraform, Azure Bicep, Azure Verified Modules, AWS CloudFormation, GCP
  Terraform, Kubernetes, container, and policy-as-code starters.
- Docusaurus docs-site scaffold and docs impact tracking.
- Risk register, security exceptions, accepted risk log, threat model, abuse
  cases, evidence index, and system context defaults.
- Deterministic verification gates for missing threat models, docs impact,
  control maps, risk registers, spec sections, plan sections, AI guardrails,
  orchestration guardrails, and hardcoded secret patterns.
- Package assets so GitHub installs include presets, extensions, workflows, and
  control maps.
- Public repository health files, issue forms, PR template, CodeQL, Dependabot,
  and OpenSSF Scorecard workflow.
