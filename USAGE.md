# Using SicarioSpec

A copy-pasteable quickstart. If you read nothing else, read the mental model.

## The mental model (read this first)

**SicarioSpec does not give you a "threat-model command."** There is no
`sicario threatmodel` that does the modeling for you. Instead, security and
threat modeling are **enforced as mandatory sections** inside your Spec Kit
spec / plan / tasks templates, and a deterministic gate (`sicario verify`)
**fails the build** if those sections are missing or incomplete.

So the model is:

> **fill in the contract → run the gate.**
> You write the threat model, data classification, trust boundaries, AI/LLM
> risk, and secrets handling *into the spec and plan*. `sicario verify` is the
> non-AI judge that checks they are present and complete. An LLM never decides
> pass/fail.

That is the whole product. Everything below is mechanics.

---

## 1. Install

```bash
# From GitHub (no clone needed):
python3 -m pip install "git+https://github.com/dfirs1car1o/sicario-spec.git"

# Pin a release:
python3 -m pip install "git+https://github.com/dfirs1car1o/sicario-spec.git@v0.3.0"

# From a local checkout:
python3 -m pip install -e .
```

This puts a `sicario` command on your PATH. If it isn't, every command also
works as `python3 -m sicario_cli.cli <command>`.

---

## 2. Initialize

### New project (greenfield)

```bash
sicario init my-proj --profile appsec
cd my-proj
```

Pick the profile that matches the work (composable — comma-separate them):

| Profile | Use it for |
|---|---|
| `public-core` | Baseline governance, data classification, tagging, threat model, risk registers. |
| `appsec` | Application/API security: authn/authz, input validation, negative tests. |
| `saas` | SaaS-tenant work (Salesforce/Workday/ServiceNow/M365): read-only-SaaS + tenant-boundary invariants. |
| `cloud-iac` | Terraform / Bicep / AWS / GCP / Kubernetes + policy-as-code. |

(Other profiles: `ai-system`, `agent-fleet`, `security-toolchain`,
`supply-chain`, `compliance`, `enterprise-strict`. Run
`sicario init --help` for the full list.)

```bash
# Composable:
sicario init my-service --profile appsec,cloud-iac,compliance
```

### Existing Spec Kit repo (brownfield)

```bash
sicario init . --apply-to-speckit
```

This is **brownfield-safe by default**: it *overlays*, it never clobbers.

- Existing constitution → an **additive** SicarioSpec overlay is appended that
  explicitly **defers** to your own principles and any `mission.md`.
- Existing `spec/plan/tasks` templates → the governance-impact gate block is
  appended **idempotently** (re-running does not double-append).
- Existing `CLAUDE.md` / `AGENTS.md` → a delimited SicarioSpec section is
  appended; your content is never overwritten.
- Every modified file is backed up first to `*.sicario-bak.<UTC-timestamp>`.

Preview or override:

```bash
sicario init . --dry-run   # show the per-file plan (created/merged/preserved); write NOTHING
sicario init . --force     # full overwrite opt-in (still backs up first)
```

---

## 3. What `init` puts in place

The overlaid Spec Kit templates now **carry the governance sections**, so when
you write a spec/plan the contract is right there in front of you:

- **Data Classification** (level, owner, retention, residency, sharing, redaction)
- **Tagging Discipline** (owner, system, environment, data-classification, retention)
- **Trust Boundaries & Security Requirements**
- **Threat Model** (in the plan)
- **AI / LLM Risk** (prompt injection, tool boundary — when AI is in scope)
- **Secrets Handling**
- **Governance-impact gate** + **active-risk register**

Plus repo-level docs and a constitution overlay:
`docs/security/threat-model.md`, `docs/security/abuse-cases.md`,
`docs/governance/{data-classification,tagging-taxonomy}.md`,
`docs/compliance/control-maps/*`,
`docs/risk/{risk-register,security-exceptions,accepted-risk-log}.md`,
`docs/diagrams/`, `docs/docs-impact.md`, and
`.specify/memory/constitution.md`.

---

## 4. Write specs the normal Spec Kit way

Use Spec Kit exactly as you already do:

```
/speckit-specify   # writes specs/NNN-name/spec.md  (now with governance sections)
/speckit-plan      # writes specs/NNN-name/plan.md  (now with threat model, etc.)
/speckit-tasks     # writes specs/NNN-name/tasks.md (now with security/evidence tasks)
```

Because `init` overlaid the templates, **the templates force you to fill the
governance sections.** That is where threat/security modeling happens — you
model it into the spec and plan, in prose and tables, as part of writing the
feature. There is no separate tool to invoke.

---

## 5. `sicario verify` — the deterministic gate

```bash
sicario verify            # verify the current repo
sicario verify <dir>      # verify a specific directory (e.g. an example)
```

It exits non-zero on any finding, prints each finding, and writes evidence to
`generated/sicario/gate-summary.json` and `spec-run-evidence.json`. **No AI is
involved in the pass/fail decision.**

### Finding codes it emits

Repo-level governance docs:

| Code | Severity | Meaning |
|---|---|---|
| `SICARIO-MISSING-THREAT-MODEL` | high | `docs/security/threat-model.md` is missing. |
| `SICARIO-MISSING-DATA-CLASSIFICATION` | high | `docs/governance/data-classification.md` is missing. |
| `SICARIO-MISSING-TAGGING-TAXONOMY` | high | `docs/governance/tagging-taxonomy.md` is missing. |
| `SICARIO-MISSING-DOCS-IMPACT` | medium | `docs/docs-impact.md` is missing. |
| `SICARIO-MISSING-DIAGRAMS` | medium | `docs/diagrams/` directory is missing. |
| `SICARIO-MISSING-CONTROL-MAPS` | medium | No `docs/compliance/control-maps` (or `control_maps`) pack. |
| `SICARIO-MISSING-RISK-REGISTER` | medium | A `docs/risk/*` register file is missing. |

Secrets:

| Code | Severity | Meaning |
|---|---|---|
| `SICARIO-HARDCODED-SECRET` | critical | A secret-shaped string (API key / token / `AKIA…` / `sk-…` / private key) was found in a scanned text file. |

Spec contract (`specs/**/spec.md`):

| Code | Severity | Meaning |
|---|---|---|
| `SICARIO-SPEC-SECTION` | high | A required heading is missing (Data Classification, Tagging Discipline, Trust Boundaries, Security Requirements, Abuse Cases, Evidence). |
| `SICARIO-DATA-CLASSIFICATION-INCOMPLETE` | high | The Data Classification section lacks owner, level, retention, residency, sharing, or redaction. |
| `SICARIO-TAGGING-DISCIPLINE-INCOMPLETE` | high | The Tagging Discipline section lacks owner, system, environment, data-classification, or retention. |
| `SICARIO-AI-GUARDRAIL-MISSING` | high | The spec mentions AI/LLM/agent/RAG/MCP/model/prompt but has no `prompt injection` or `tool boundary` guardrail. |
| `SICARIO-FLEET-GUARDRAIL-MISSING` | high | An orchestration spec (LangGraph/queue/worker/multi-agent/SOAR…) lacks retry, idempotency, dead-letter, workflow state, or human-approval guardrails. |

Plan / tasks contract:

| Code | Severity | Meaning |
|---|---|---|
| `SICARIO-PLAN-SECTION` | high | `plan.md` is missing a required heading (Threat Model, Data Classification, Tagging, Well-Architected, Supply Chain, Rollback, Human Approval, Evidence). |
| `SICARIO-TASKS-SECTION` | high | `tasks.md` is missing a required task (security test, negative, classification, tagging, docs impact, evidence, threat model). |

Risk register hygiene:

| Code | Severity | Meaning |
|---|---|---|
| `SICARIO-INCOMPLETE-ACTIVE-RISK` | high | A row marked `\| active \|` has a blank / `TBD` / `N/A` / `none` / `never` / `permanent` cell — an active risk or exception must name an owner, expiration, approval/rationale, compensating control, and evidence. |

A clean run prints `sicario verify passed` and the gate summary shows
`"status": "pass"`.

---

## 6. `sicario hooks` — Spec Kit hook runner

```bash
sicario hooks                      # run all events
sicario hooks --event after_tasks  # run one event
```

It reads `.specify/extensions.yml` and treats hooks honestly by kind:

- **Deterministic (it actually runs them):** `sicario.verify`,
  `sicario.assess`, `sicario.evidence`. These are backed by the CLI and produce
  pass/fail + evidence.
- **Agent-guidance (it only reports them):** `sicario.threatmodel`,
  `sicario.review`, `sicario.controls`, `sicario.apply-findings`,
  `sicario.init`. A coding agent performs these; the runner prints a pointer to
  the command doc instead of pretending to execute an AI step.

This split is deliberate: SicarioSpec never lets an AI step masquerade as a
deterministic gate.

---

## Where does X live?

| You want to... | It lives in... | Enforced by |
|---|---|---|
| Threat model a feature | `plan.md` "Threat Model" section + `docs/security/threat-model.md` | `SICARIO-PLAN-SECTION`, `SICARIO-MISSING-THREAT-MODEL` |
| Classify data | `spec.md` "Data Classification" section + `docs/governance/data-classification.md` | `SICARIO-SPEC-SECTION`, `SICARIO-DATA-CLASSIFICATION-INCOMPLETE`, `SICARIO-MISSING-DATA-CLASSIFICATION` |
| Tag artifacts | `spec.md` "Tagging Discipline" + `docs/governance/tagging-taxonomy.md` | `SICARIO-TAGGING-DISCIPLINE-INCOMPLETE`, `SICARIO-MISSING-TAGGING-TAXONOMY` |
| Define trust boundaries / abuse cases | `spec.md` "Trust Boundaries", "Abuse Cases" | `SICARIO-SPEC-SECTION` |
| Add AI/LLM guardrails | `spec.md` "AI / LLM Risk" (say "prompt injection" + "tool boundary") | `SICARIO-AI-GUARDRAIL-MISSING` |
| Keep secrets out of the repo | (don't commit them) | `SICARIO-HARDCODED-SECRET` (scan) |
| Track an active risk/exception | `docs/risk/*.md` (owner, expiry, approval, compensating control, evidence) | `SICARIO-INCOMPLETE-ACTIVE-RISK` |
| See a passing end-state | [`examples/python-api/`](examples/python-api/) | run `sicario verify examples/python-api` |

---

## A fully-worked example

[`examples/python-api/`](examples/python-api/) is a complete governed feature
(a read-only invoice-export API) with every section filled in. Run:

```bash
sicario verify examples/python-api
# -> sicario verify passed
```

Open its [`spec.md`](examples/python-api/specs/001-example/spec.md),
[`plan.md`](examples/python-api/specs/001-example/plan.md), and
[`tasks.md`](examples/python-api/specs/001-example/tasks.md) to see exactly what
"complete" looks like for the gate.
