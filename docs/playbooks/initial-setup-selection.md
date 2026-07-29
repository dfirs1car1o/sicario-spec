---
title: "Playbook: Choosing Profiles, Presets, And Frameworks At Initial Setup"
sidebar_label: "Choosing profiles & presets"
guide-slug: initial-setup-selection
captured-version: 0.6.0
reference-run-repository: platform-infra
reference-run-date: "2026-07-28"
---

# Playbook: Choosing Profiles, Presets, And Frameworks At Initial Setup

## Scenario And Intended Reader

You are about to run `sicario init` for the first time and must choose a
`--profile` value (and possibly `--frameworks`). This playbook turns that
flag into a decision: for every shipped profile it states what kind of
repository it fits, what it concretely installs, what the gate will then
demand of every future feature, and which compliance frameworks it enforces
by default. It is the document the
[getting-started walkthrough](../guides/getting-started.md) links at its
init step; you need no other playbook to complete it.

Pick wrong in either direction and you pay for it: a too-heavy profile
drowns a small repository in obligations that do not apply; a too-light one
ships a service without the obligations that do.

## Starting State

- SicarioSpec CLI 0.6.0 installed (either install path from the
  walkthrough); `sicario --version` prints `sicario 0.6.0`.
- A target repository (new or existing — init is brownfield-safe either
  way), not yet initialized.
- If `sicario` is not on your `PATH`, substitute
  `python3 -m sicario_cli.cli` for `sicario` in every command here.

## How Output Is Quoted In This Playbook

Quoted output blocks carry a machine-readable `verified` or `illustrative`
marker. Verified blocks are exact at the captured version; illustrative
blocks are visibly labeled and representative rather than exact. Absolute
paths are normalized to `/work/<repo-name>`. All quoted output comes from a
reference run: net-new repository `platform-infra`, run date 2026-07-28,
SicarioSpec 0.6.0.

**Staleness note**: the tables below are derived from the shipped
composition metadata at captured-version 0.6.0 — the CLI's
profile-to-preset and profile-to-framework tables and each preset's
manifest — not from CLI output. Composition can change in a release without
any output string changing, so these tables are re-checked against the
shipped metadata at every release under the release checklist discipline.

## Step 1 — Know What A Profile Does

A profile is a named composition of **presets**. Every preset layers onto
the five governed Spec Kit templates (spec, plan, tasks, checklist,
constitution); `sicario-core` replaces the stock templates with governed
ones, and every other preset **appends** its domain's sections and guidance
onto them. Two consequences before you choose:

1. **Every profile includes the baseline.** All profiles compose
   `sicario-core` + `sicario-docs`, so every choice lands: the governed
   templates, the shipped rule pack (21 rule files) in `.sicario/rules/`,
   the baseline security docs (threat model, abuse cases, data
   classification, tagging taxonomy, risk registers, evidence index,
   control applicability), the full control-map pack under
   `docs/compliance/control-maps/`, the `sicario-guard` extension, CI
   workflows (`sicario-verify.yml`, `docs-site.yml`), and a Docusaurus
   docs-site scaffold.
2. **Enforcement comes from the core rules; depth comes from the presets.**
   Only `sicario-core` ships gate rules. Specialty presets deepen what the
   templates ask of you; they do not add new finding codes. So the
   *enforced floor* is the same for every profile, and the profile decides
   how much domain-specific substance the templates demand within it.

What the core rules will demand of every future feature (the
choice-to-enforcement link):

| Template artifact | Sections the gate requires | Finding code that enforces it |
|---|---|---|
| `specs/**/spec.md` | Data Classification, Tagging Discipline, Trust Boundaries, Security Requirements, Abuse Cases, Evidence | `SICARIO-SPEC-SECTION` (high) |
| `specs/**/spec.md` | Data Classification completeness: owner, level, retention, residency, sharing, redaction | `SICARIO-DATA-CLASSIFICATION-INCOMPLETE` (high) |
| `specs/**/spec.md` | Tagging completeness: owner, system, environment, data-classification, retention | `SICARIO-TAGGING-DISCIPLINE-INCOMPLETE` (high) |
| `specs/**/spec.md` (AI-shaped features) | Prompt-injection and tool-boundary guardrails | `SICARIO-AI-GUARDRAIL-MISSING` (high) |
| `specs/**/spec.md` (orchestration-shaped features) | Retry, idempotency, workflow-state, dead-letter, approval guardrails | `SICARIO-FLEET-GUARDRAIL-MISSING` (high) |
| `specs/**/plan.md` | Required plan sections | `SICARIO-PLAN-SECTION` (high) |
| `specs/**/tasks.md` | Required task phrases | `SICARIO-TASKS-SECTION` (high) |

The governed templates already contain every required section and phrase,
so a spec created from your initialized template passes these checks in
form; the substance is yours to supply (the
[first-spec playbook](first-spec.md) demonstrates this honestly).

## Step 2 — Look Up The Shipped Profiles

Composition table at captured-version 0.6.0 (`core` and `docs` are aliases
of the `public-core` composition):

| Profile | Repository kind it fits | Presets composed | Framework defaults (effective) |
|---|---|---|---|
| `public-core` (aliases: `core`, `docs`) | Libraries, docs repositories, small tools, any undecided case | sicario-core, sicario-docs | none (coarse control-map check only) |
| `appsec` | Applications, APIs, services | + sicario-appsec | ssdf, iso27001 |
| `ai-system` | AI/LLM apps, RAG, MCP servers, tool-using systems | + sicario-ai-system | eu-ai-act |
| `agent-fleet` | Multi-agent, worker/queue, workflow, SOAR, orchestration systems | + sicario-ai-system, sicario-agent-fleet | eu-ai-act |
| `cloud-iac` | Terraform/OpenTofu, Bicep/AVM, AWS/GCP, Kubernetes, policy-as-code | + sicario-cloud-iac | ccm, fedramp, bsi-c5, nist-800-53 |
| `supply-chain` | Build/release pipelines, SBOM, provenance, SLSA-shaped work | + sicario-supply-chain | ssdf |
| `compliance` | Regulated, audit-driven, evidence-heavy environments | + sicario-compliance | ccm, sox, soc2, iso27001, nist-800-53 |
| `saas` | Systems that connect to SaaS tenants (SSPM-adjacent, read-only-SaaS posture) | + sicario-ai-system, sicario-saas | ccm, soc2, iso27001 |
| `security-toolchain` | Security scanning/tooling repositories (SAST, SCA, secrets, IaC scanning) | + sicario-security-toolchain | none (coarse control-map check only) |
| `enterprise-strict` | High-assurance enterprise: approval, release, and exception governance | sicario-core, sicario-docs, sicario-appsec, sicario-ai-system, sicario-agent-fleet, sicario-security-toolchain, sicario-supply-chain, sicario-compliance, sicario-enterprise-strict | the 11 supported maps (see Step 4) |

What each composed preset concretely adds (all append to the five governed
templates unless noted):

| Preset | What it adds to the target |
|---|---|
| `sicario-core` | Replaces the five Spec Kit templates with governed ones; ships the entire rule pack into `.sicario/rules/`; writes `SICARIO.md`, the baseline docs set (`docs/security/`, `docs/governance/`, `docs/risk/`, `docs/compliance/` including control maps, `docs/architecture/`, `docs/diagrams/`, `docs/docs-impact.md`), agent-integration files, and the `sicario-verify.yml` / `docs-site.yml` workflows |
| `sicario-docs` | Docs-as-code governance appended to all five templates (docs-impact, diagram source control, generated-docs drift, ADRs); Docusaurus docs-site scaffold (`docs-site/`) |
| `sicario-appsec` | AppSec sections: authn/authz, session and token handling, input validation, API security, secure errors, audit logging |
| `sicario-ai-system` | AI security sections: prompt injection, tool boundaries, model routing, memory poisoning, data leakage, AIBOM, AI evals |
| `sicario-agent-fleet` | Orchestration sections: workflow state, durable execution, queue/worker safety, idempotency, retry and dead-letter, distributed permissions |
| `sicario-cloud-iac` | Cloud/IaC sections plus an additional cloud-risk template: Terraform/OpenTofu, Azure AVM/Bicep, AWS, GCP, Kubernetes, containers, policy-as-code |
| `sicario-supply-chain` | Build/release integrity sections: dependency review, SBOM, pinned dependencies, GitHub Actions hardening, provenance, artifact-signing readiness |
| `sicario-compliance` | Evidence-readiness sections: control applicability, evidence index, risk acceptance, control owners, reviewers, evidence freshness |
| `sicario-saas` | SaaS-tenant invariants: read-only-SaaS, tenant isolation, data boundary, mission supremacy, OAuth/integration risk, no raw tenant evidence |
| `sicario-security-toolchain` | Scanner-pipeline sections: secret scanning, SAST, SCA, SBOM, container and IaC scanning, policy-as-code; adds a toolchain CI workflow |
| `sicario-enterprise-strict` | Approval-governance sections: CODEOWNERS, required reviewers, change control, production write gates, release approval, exception register |

## Step 3 — Follow The Decision Path

Start from the kind of work in the repository:

1. **Application, API, or service code?** → `appsec`.
2. **Does it call models, run agents, or expose/consume MCP or tools?**
   → `ai-system`; if it orchestrates *multiple* agents or workers (queues,
   workflows, SOAR) → `agent-fleet` (which already includes the ai-system
   preset).
3. **Is it Terraform/OpenTofu, Bicep, Kubernetes, or other IaC?**
   → `cloud-iac`.
4. **Is its product the build/release pipeline itself (SBOM, provenance,
   signing)?** → `supply-chain`. A repository *of security scanners and
   their configs* → `security-toolchain`.
5. **Does it connect to customer SaaS tenants?** → `saas`.
6. **Is it audit-driven with named frameworks to evidence?**
   → `compliance`, alone or composed with the technical profile from
   above.
7. **High-assurance enterprise repository that needs approval and
   exception governance at maximum depth?** → `enterprise-strict`
   (it composes nearly everything; expect the heaviest templates).
8. **None of the above, a library or docs repository, or you are genuinely
   undecided?** → **`public-core`** — the baseline recommendation and the
   default when `--profile` is omitted. It is the cheapest to satisfy and
   you can re-run init later with a bigger profile; init is idempotent and
   brownfield-safe, so upgrading a profile is an overlay, not a rewrite.

**When the repository spans kinds, compose profiles** with the
comma-separated form. Composition merges the profiles' preset lists (in
order, deduplicated) and unions their framework defaults. An API service
that also owns its Terraform:

```bash
sicario init . --profile appsec,cloud-iac --dry-run
```

*Illustrative output — the dry run's composition lines shown, other plan
lines elided, paths normalized to `/work/platform-infra`.*

```text title="Illustrative output (representative, not exact)" sicario-output=illustrative sicario-block=initial-setup-selection/sel-01
target /work/platform-infra
presets sicario-core, sicario-docs, sicario-appsec, sicario-cloud-iac
mode: greenfield (no existing governance detected)
frameworks ssdf, iso27001, ccm, fedramp, bsi-c5, nist-800-53
```

The `presets` line is the merged preset list; the `frameworks` line is the
union of `appsec` (ssdf, iso27001) and `cloud-iac` (ccm, fedramp, bsi-c5,
nist-800-53) effective defaults.

A typo in the profile name is a hard error, never a silent fallback:

```bash
sicario init . --profile web
```

```text title="Verified output" sicario-output=verified sicario-block=initial-setup-selection/sel-02
Unknown profile(s): web. Known profiles: agent-fleet, ai-system, appsec, cloud-iac, compliance, core, docs, enterprise-strict, public-core, saas, security-toolchain, supply-chain
```

The command exits `1`.

## Step 4 — Understand The Framework Defaults And Tiers

SicarioSpec ships 14 control-map frameworks in two tiers: 11 **supported**
(`bsi-c5`, `ccm`, `eu-ai-act`, `fedramp`, `gdpr`, `hipaa`, `iso27001`,
`nist-800-53`, `soc2`, `sox`, `ssdf`) and 3 **experimental** (`ai-rmf`,
`owasp-asvs`, `pci-dss`), which are measurably thinner than the rest.

The tier default rule, precisely:

- **Experimental maps are never selected implicitly.** They are excluded
  from every profile's effective defaults *even where the profile's
  framework table lists them*: `appsec` lists `owasp-asvs`, `saas` and the
  AI profiles list `ai-rmf` — those maps state what the profile is about,
  but none of them lands in `.sicario/frameworks.txt` unless you name it
  yourself on `--frameworks`.
- **`enterprise-strict` is the deliberate exception in what it lists, not
  in what it defaults.** Its table explicitly selects all 14 shipped
  frameworks — and the experimental filter still applies, so its
  *effective* default is the 11 supported maps. To enforce all 14 you must
  say so: `--frameworks all`.
- When named explicitly, an experimental map is enforced exactly like any
  other selection.

The selection is recorded in `.sicario/frameworks.txt`, one key per line;
`sicario verify` then fails with `SICARIO-MISSING-FRAMEWORK-MAP` for any
selected framework whose control map is absent. The file init wrote for the
`appsec,cloud-iac` composition above:

```bash
cat .sicario/frameworks.txt
```

```text title="Verified output" sicario-output=verified sicario-block=initial-setup-selection/sel-03
# SicarioSpec framework selector (#18).
# One framework key per line. `sicario verify` requires a control map
# for each key listed here (SICARIO-MISSING-FRAMEWORK-MAP if absent).
# Remove this file to fall back to the default coarse control-map check.
# Supported keys: bsi-c5, ccm, eu-ai-act, fedramp, gdpr, hipaa, iso27001, nist-800-53, soc2, sox, ssdf
# Experimental keys: ai-rmf, owasp-asvs, pci-dss
#   Experimental maps are thinner than the supported set. They are
#   enforced exactly like any other key when listed here, but are never
#   selected by a profile default -- only by explicit --frameworks.
ssdf
iso27001
ccm
fedramp
bsi-c5
nist-800-53
```

Two accuracy statements that apply to every tier: control maps are coarse
traceability aids, **not certification claims** — selecting `soc2` does not
make you SOC 2 ready, it makes your evidence traceable to SOC 2 criteria —
and the gate checks the *completeness* of governance artifacts, not the
quality of their content.

To choose a subset deliberately instead of taking the profile default, pass
`--frameworks` yourself, for example
`sicario init . --profile saas --frameworks soc2,iso27001`.

## Step 5 — Prefer Prompts? Use The Interactive Wizard

`sicario init <dir> --interactive` replaces flag-composing with a
three-step prompt-driven wizard:

1. **Framework selection** — lists all 14 framework keys with their map
   files; enter numbers, `all`, or nothing for none.
2. **Data classification boundary** — the maximum classification level the
   project handles (`public`, `internal`, `confidential`, `restricted`,
   `regulated`; default `confidential`).
3. **Cloud provider targets** — AWS, Azure, GCP, Kubernetes, or none.
   Selecting any provider automatically adds the `cloud-iac` profile to
   your composition.

What it writes: your framework selection into `.sicario/frameworks.txt`
(explicit wizard selections behave like `--frameworks` — experimental keys
you pick are enforced), and the three answers into `.sicario/config.json`;
the init then proceeds as usual with the resulting profile composition.

Prefer the wizard when you can answer "which frameworks, what data, which
clouds" but do not yet know the flag vocabulary; prefer flags once you want
reproducible, scripted init commands.

## Step 6 — Commit The Decision

Run the dry-run preview with your chosen profile and read the per-file
plan — `[created]` marks files init will write fresh, `[merged-overlaid]`
marks existing files it will additively overlay rather than replace, and
`[preserved]` marks existing files it will not touch (the
[walkthrough](../guides/getting-started.md) shows a full plan). Then init
for real and verify.
Shown with this playbook's worked composition — substitute your own
`--profile` value:

```bash
sicario init . --profile appsec,cloud-iac --dry-run
sicario init . --profile appsec,cloud-iac
sicario verify .
```

```text title="Verified output" sicario-output=verified sicario-block=initial-setup-selection/sel-04
sicario verify passed
```

The final command exits `0`.

## Success Check

You have completed this playbook when, for your repository, you can state
without looking anything else up:

1. the profile (or composition) you chose and the kind-of-work reasoning
   behind it;
2. the presets that profile composes and what each adds to your templates;
3. the framework defaults it selects — and which frameworks in its table
   are experimental-tier and therefore absent from the defaults;
4. and `sicario verify .` exits `0` on your initialized repository.

## Visual Assets Note

Every surface in this playbook is a terminal, captured as text blocks
(capture-class `terminal-text`); no step surfaces a graphical view, which
is the stated reason this playbook carries no screenshots.

## About This Playbook's Captures

Reference run: repository `platform-infra`, run date 2026-07-28, captured
against SicarioSpec 0.6.0; the repository contains nothing but what these
steps create. Tables derive from the shipped composition metadata at the
same version, as stated in the staleness note above.
