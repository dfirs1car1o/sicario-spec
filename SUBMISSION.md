# Spec Kit Community Catalog Submission — SicarioSpec

This document is the maintainer-facing package for listing **SicarioSpec** in the
GitHub Spec Kit community preset catalog
(`presets/catalog.community.json`). It contains (a) the ready-to-paste catalog
entry, (b) a cover note for the submission PR, and (c) the pre-submission
checklist mapped to `presets/PUBLISHING.md`.

> Scope note for the maintainer doing the outward action: this file lives on the
> SicarioSpec repo. The actual catalog PR is opened **against
> `github/spec-kit`** (one preset per PR, alphabetical by id), per
> [issue #2362](https://github.com/github/spec-kit/issues/2362) where a Spec Kit
> collaborator wrote: *"Please submit each of them (one per PR) to our community
> catalog and we will get them in."*

---

## (a) Catalog entry (paste into `github/spec-kit` → `presets/catalog.community.json`)

Insert this object into the top-level `presets` map, keyed by id and kept in
**alphabetical order by id** (`sicario-spec` sorts after the `s…` entries such as
`spec-kit-…`/`secure-…` and before `t…`). Field order matches the existing
entries (`name`, `id`, `version`, `description`, `author`, `repository`,
`download_url`, `homepage`, `documentation`, `license`, `requires`, `provides`,
`tags`, `created_at`, `updated_at`).

```json
"sicario-spec": {
  "name": "SicarioSpec",
  "id": "sicario-spec",
  "version": "0.4.0",
  "description": "Security, governance, and evidence bundle whose pass/fail verdict is owned by a halting, stdlib-only verify gate (non-zero exit + finding codes) with no LLM in the decision path. Enforces mandatory governance sections in spec/plan/tasks and ships selectable starter control maps for 10 frameworks (CSA CCM v4.1, SOX 404 ITGC, NIST SSDF, NIST AI RMF, ISO/IEC 27001:2022, NIST SP 800-53 Rev 5, EU AI Act, GDPR/CPRA, PCI DSS v4.0, HIPAA Security Rule).",
  "author": "SicarioSpec Contributors",
  "repository": "https://github.com/dfirs1car1o/sicario-spec",
  "download_url": "https://github.com/dfirs1car1o/sicario-spec/archive/refs/tags/v0.4.0.zip",
  "homepage": "https://github.com/dfirs1car1o/sicario-spec",
  "documentation": "https://github.com/dfirs1car1o/sicario-spec/blob/main/README.md",
  "license": "MIT",
  "requires": {
    "speckit_version": ">=0.9.0"
  },
  "provides": {
    "templates": 11,
    "commands": 8
  },
  "tags": [
    "security",
    "governance",
    "devsecops",
    "deterministic-gate",
    "evidence",
    "compliance",
    "ai-security"
  ],
  "created_at": "2026-06-21T00:00:00Z",
  "updated_at": "2026-06-21T00:00:00Z"
}
```

Also add a row to `docs/community/presets.md` (alphabetical by name):

```markdown
| SicarioSpec | Halting, code-owned security/governance gate (non-zero exit + finding codes, no LLM in the decision path) with mandatory spec/plan/tasks governance sections and selectable starter control maps for 10 frameworks. | [dfirs1car1o/sicario-spec](https://github.com/dfirs1car1o/sicario-spec) |
```

> **`provides` counts** reflect the 11 preset bundles
> (`presets/sicario-*/preset.yml`) and the 8 guard commands declared in
> `extensions/sicario-guard/extension.yml` (init, assess, threatmodel, controls,
> evidence, verify, review, apply-findings). Confirm against the repo at release
> time and adjust if a preset/command is added or removed.

---

## (b) Cover note for the catalog PR

**TL;DR — the defensible differentiator:** SicarioSpec is the Spec Kit
governance preset whose `verify` is a **halting gate** — it exits non-zero with a
specific finding code, and that pass/fail verdict is produced by **stdlib-only
Python with no model call, no network, and no AI import**. An LLM is structurally
barred from the decision path, not merely instructed to stay out. (We do **not**
claim to be the first or only security-governance preset.)

### The gate-halt proof (reproducible from a clean clone)

The repo ships a passing example and its deliberately-broken twin so the gate can
be seen passing *and* failing:

```text
$ sicario verify examples/python-api
sicario verify passed
$ echo $?
0

$ sicario verify examples/python-api-failing
HIGH SICARIO-MISSING-THREAT-MODEL docs/security/threat-model.md: Missing docs/security/threat-model.md
sicario verify failed with 1 finding(s)
$ echo $?
1
```

Same feature, same gate, opposite verdict — decided entirely by non-AI code. A
gate that can only pass is not a gate. A short recording of this exact session is
in [`demo/`](demo/) (`demo/verify-demo.gif`, regenerable via `demo/record.sh`).

### Honest contrast with the existing Security Governance preset

The ecosystem already has a strong security-governance preset —
[`hindermath/spec-kit-preset-security-governance`](https://github.com/hindermath/spec-kit-preset-security-governance)
— and the proposal that seeded the preset direction is
[issue #2362](https://github.com/github/spec-kit/issues/2362). That preset does
real, useful work: it **appends** secure-development governance to the
constitution/spec/plan/tasks templates and **wraps** `speckit.specify/plan/tasks`
with shared security guidance, covering NIST SSDF, CWE Top 25, OWASP ASVS,
SBOM/VEX/SLSA, OpenSSF Scorecard, and EU CRA/NIS2/DORA applicability. Its
mechanism is **advisory**: it enriches the documents an agent and a human
reviewer then act on; there is no blocking verification step.

SicarioSpec operates at a **different layer** and is **complementary**, not a
replacement:

| | Advisory-append preset (e.g. Security Governance) | SicarioSpec |
|---|---|---|
| Mechanism | Append guidance / wrap commands | Append the governance contract **+ a verify gate** |
| Verdict | Advisory; reviewer decides | **Halting**: non-zero exit + finding code |
| Decision owner | Agent + human judgement | **stdlib-only code; no LLM in the path** |
| Breadth | Broad standards/regulatory applicability (ASVS, CRA, NIS2, DORA, SLSA, …) | Narrower; enforces presence/completeness of what it does cover |
| CI behavior | Produces evidence to read | **Blocks merge/release** when a required artifact is absent |

You can keep any advisory preset and **stack** SicarioSpec behind it: adopt the
advice you like, then gate the result behind a deterministic, code-owned verdict.
SicarioSpec is intentionally narrower on regulatory breadth (no ASVS/NIS2/CRA/DORA
control maps yet) — it trades breadth for an enforced verdict.

### Where the verdict comes from

`sicario verify` reads repository files and applies fixed rules. It checks for
required governance docs (threat model, data classification, tagging taxonomy,
diagrams, control maps, risk registers), hardcoded-secret patterns, required
spec/plan/tasks sections, AI-sensitive specs missing prompt-injection / tool-
boundary guardrails, orchestration specs missing retry/idempotency/dead-letter/
approval guardrails, and active risk/exception rows missing owner/expiry/approval/
compensating-control/evidence. Each violation emits a documented finding code
(e.g. `SICARIO-MISSING-THREAT-MODEL`, `SICARIO-SPEC-SECTION`,
`SICARIO-AI-GUARDRAIL-MISSING`) and forces a non-zero exit. The full finding-code
reference is in [`USAGE.md`](USAGE.md).

### Provenance — extracted from a system that runs this model in anger

The deterministic-verdict model is not aspirational. It was **extracted and
generalized from a production multi-agent SaaS security-assessment system**
(`saas-assurance`) where the same invariant holds: a non-AI rules engine
(`skills/oscal_assess`) owns every pass/fail verdict, and the LLM layer is
structurally import-banned from that path. SicarioSpec ports that
"calculator-and-consultant" separation — *AI explains, code decides* — into a
Spec Kit preset so any team can adopt the pattern without the full pipeline.

### Framing: the opt-in preset that #2362 called for

Issue #2362 explicitly framed security governance as *"optional… not a mandatory
heavier workflow for all Spec Kit users"*, and a collaborator confirmed *"This is
exactly what presets are designed for… create those presets and publish them to
a GitHub repository and then we can link them in the community catalog."*
SicarioSpec is exactly that: a public, opt-in preset repository. It does not push
any policy into Spec Kit core — it is adopted only when a project selects it, and
it is brownfield-safe (overlays, never clobbers existing constitutions/templates).

### What we explicitly do **not** claim

- Not the "first" or "only" governance preset.
- No multi-framework breadth claim beyond the 10 starter maps shipped; maps are
  coarse traceability aids, not certification or legal/conformity assessments.
- Does not guarantee secure code, certify compliance, or replace human review.

---

## (c) Pre-submission checklist (mapped to `presets/PUBLISHING.md`)

| PUBLISHING.md requirement | Status | Note |
|---|---|---|
| Valid preset(s) with valid `preset.yml` manifest | ✅ | 11 presets under `presets/sicario-*/preset.yml`. |
| Semantic versioning | ✅ | `0.4.0` across `VERSION`, `pyproject.toml`, presets, control maps (version-sync test enforces). |
| Preset id lowercase-with-hyphens | ✅ | `sicario-spec`. |
| Public GitHub repository | ✅ | `github.com/dfirs1car1o/sicario-spec` (MIT). |
| `README.md` and `LICENSE` present | ✅ | Both at repo root. |
| All files referenced in manifest exist | ✅ | Templates/toolchain referenced by presets are present (test suite covers). |
| Tested on real projects (`specify preset add --dev` / `--from`) | ⚠️ **action needed** | We tested the **package CLI** (`pip install -e .`, real `sicario init`/`verify` pass+fail captured in `demo/`). We have **not** yet run the upstream `specify preset add --from <zip>` flow against this repo's preset layout. Do this before opening the catalog PR and paste the result into the PR checklist. |
| GitHub release with matching semver tag + `download_url` resolves | ⚠️ **blocker** | Latest published release is **v0.1.2**; code is at **v0.4.0**. The `download_url` in the entry points to `…/tags/v0.4.0.zip`, which **does not exist yet**. Cut a `v0.4.0` release (the `release.yml` workflow already builds + attests) before submitting, or change the entry to the actual released version. |
| `requires.speckit_version` is accurate | ⚠️ verify | Entry says `>=0.9.0` (matches `presets/sicario-*/preset.yml` `requires.spec-kit`). The neighbouring catalog entries use `>=0.8.0`; confirm SicarioSpec actually needs 0.9.0 (e.g. for the prepend/append/wrap stacking) or relax to match what was smoke-tested. |
| `provides` counts accurate | ✅ | 11 presets; 8 commands declared in `extensions/sicario-guard/extension.yml`. Re-confirm at release time if presets/commands change. |
| Verification checklist (manifest, template quality, command coherence, security, docs) | ✅ ready | Covered by repo tests, CodeQL, Scorecard, and the worked examples. |

### Open items for JJ before the real (outward) submission

1. **Cut a `v0.4.0` GitHub release** so `download_url` resolves (or retarget the
   entry to the released tag). This is the one hard blocker.
2. **Run `specify preset add --from <v0.4.0 zip>`** (or `--dev`) against a real
   Spec Kit checkout and record the result for the PR checklist — PUBLISHING.md
   asks for this explicitly and the catalog reviewers validate it.
3. **Confirm `requires.speckit_version`** (0.9.0 vs 0.8.0) against the version you
   actually smoke-test on.
4. Open the catalog PR **against `github/spec-kit`**, one preset, alphabetical
   insertion, with the verification checklist filled in. (Not done here by
   design — that is the maintainer's outward action.)
