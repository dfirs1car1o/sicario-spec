"""SicarioCorePreset — baseline governance preset.

Ships every profile's mandatory governance files: constitution overlay, security
docs, governance docs, compliance docs, architecture docs, risk docs, agent
integration files, and CI/CD workflows.

Content-generator functions are defined here so each preset module is
self-contained.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Sequence


# ── Content generators ──────────────────────────────────────────────────


def _constitution_overlay(presets: Sequence[str], deferrals: Sequence[str]) -> str:
    """Build the additive constitution overlay that DEFERS to existing authority.

    Mirrors saas-assurance's pattern of adding governance as a brownfield overlay
    (e.g. "Principle VIII as an overlay that yields to mission.md") rather than
    replacing the host project's constitution.
    """
    from sicario_cli._render import SICARIO_OVERLAY_BEGIN, SICARIO_OVERLAY_END

    if deferrals:
        defer_line = (
            "This overlay is SUBORDINATE to the existing principles above and to "
            + ", ".join(f"`{d}`" for d in deferrals)
            + ". Where any conflict exists, the project's own principles and "
            "`mission.md` (or equivalent project-supremacy clause) WIN."
        )
    else:
        defer_line = (
            "This overlay is SUBORDINATE to the existing principles above. Where "
            "any conflict exists, the project's own principles WIN."
        )
    return f"""{SICARIO_OVERLAY_BEGIN}

## SicarioSpec Governance Overlay (Additive)

This section was appended by `sicario init`/`apply` as an ADDITIVE governance
overlay. Your existing constitution above is unchanged and remains authoritative.

{defer_line}

### Overlay Principle — Deterministic Authority Yields To Project Scope

Subject to the deferral clause above, SicarioSpec adds these guardrails:

- Anything that must be true (release status, compliance truth, approval status,
  security-gate status) is decided by code, tests, schemas, validators, or CI —
  not by an LLM. LLMs may draft, summarize, enrich, and review.
- External input, generated content, model output, file paths, and network data
  are untrusted until validated or sanitized.
- Secrets never enter version control, logs, stdout, generated artifacts, or LLM
  context.
- High-impact, irreversible, externally visible, or production-impacting changes
  require explicit human approval.
- Run `sicario verify` before handoff, pull request, release, or deployment.

Selected SicarioSpec presets: {", ".join(f"`{p}`" for p in presets)}.

The full SicarioSpec principles are staged for reference under
`.specify/presets/*/templates/constitution-template.md`; this overlay does not
import or override them onto your project — it points to them.

{SICARIO_OVERLAY_END}
"""


def _template_overlay(template_name: str) -> str:
    """Build the idempotent governance-impact gate block appended to templates."""
    from sicario_cli._render import SICARIO_OVERLAY_BEGIN, SICARIO_OVERLAY_END

    return f"""{SICARIO_OVERLAY_BEGIN}

## SicarioSpec Governance Impact (Additive Gate)

`sicario init`/`apply` appended this block to your existing `{template_name}`.
Your template content above is unchanged. Complete this gate for every feature;
`sicario verify` enforces the deterministic parts.

- **Data Classification**: highest level, owner, retention, residency, sharing,
  redaction.
- **Tagging Discipline**: owner, system, environment, data-classification,
  retention.
- **Trust Boundaries & Security Requirements**: untrusted inputs validated;
  authz explicit.
- **Abuse Cases**: misuse, privilege escalation, prompt/document injection.
- **AI/Agent guardrails** (if applicable): prompt injection, tool boundary,
  eval, memory, human approval.
- **Evidence**: tests, threat-model update, docs impact, `sicario verify`
  output.

{SICARIO_OVERLAY_END}
"""


def _resolve_speckit_template_sources(
    presets: Sequence[str],
    presets_root: Path,
    speckit_template_files: Sequence[str],
) -> dict:
    """Pick the live Spec Kit template for each file.

    Presets are ordered least- to most-specialized (core first, the
    profile-specific preset last). The last preset that ships a given template
    wins, so the most specialized governance lands in `.specify/templates/`.
    """
    sources: dict = {}
    for preset in presets:
        templates_dir = presets_root / preset / "templates"
        for template in speckit_template_files:
            candidate = templates_dir / template
            if candidate.exists():
                sources[template] = candidate
    return sources


def _resolve_speckit_constitution(
    presets: Sequence[str],
    presets_root: Path,
) -> Optional[Path]:
    """Pick the live constitution: the most specialized preset that ships one."""
    chosen: Optional[Path] = None
    for preset in presets:
        candidate = presets_root / preset / "templates" / "constitution-template.md"
        if candidate.exists():
            chosen = candidate
    return chosen


def _apply_to_speckit(
    target: Path,
    presets: Sequence[str],
    *,
    force: bool,
    dry_run: bool,
    actions: List[str],
    reports: List,
    deferrals: Sequence[str],
    presets_root: Path,
    speckit_template_files: Sequence[str],
) -> None:
    from sicario_cli._render import FileReport, _overlay_text

    template_sources = _resolve_speckit_template_sources(presets, presets_root, speckit_template_files)
    for template, src in sorted(template_sources.items()):
        _overlay_text(
            target / ".specify" / "templates" / template,
            _template_overlay(template),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
            full_content=src.read_text(encoding="utf-8"),
        )

    constitution = _resolve_speckit_constitution(presets, presets_root)
    if constitution is not None:
        _overlay_text(
            target / ".specify" / "memory" / "constitution.md",
            _constitution_overlay(presets, deferrals),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
            full_content=constitution.read_text(encoding="utf-8"),
        )
    actions.append(
        "applied SicarioSpec governance to live Spec Kit paths "
        "(.specify/templates, .specify/memory/constitution.md)"
    )


def _sicario_project_readme(presets: Sequence[str]) -> str:
    return f"""# SicarioSpec Project Guardrails

SicarioSpec is installed for this project.

Installed presets:

{chr(10).join(f"- `{preset}`" for preset in presets)}

Run:

```bash
sicario verify
sicario assess
```

Principle: AI can draft and review, but deterministic gates decide whether the
work is complete enough to ship.
"""


def _claude_instructions() -> str:
    return """# Claude Project Instructions

Use SicarioSpec guardrails for all non-trivial changes.

- Start with the spec.
- Keep AI out of authoritative decisions.
- Add threat model and abuse cases for meaningful features.
- Add well-architected review for meaningful features.
- Add negative/security tests when risk applies.
- Run `sicario verify` before handoff.
- Keep security exceptions owned, approved, time-bound, and evidenced.
- Keep data classification and tags current for specs, evidence, resources, and releases.
- Do not place secrets in files, logs, artifacts, or LLM context.
"""


def _claude_overlay() -> str:
    """Delimited, idempotent SicarioSpec section appended to an existing CLAUDE.md."""
    from sicario_cli._render import SICARIO_OVERLAY_BEGIN, SICARIO_OVERLAY_END

    return f"""{SICARIO_OVERLAY_BEGIN}

## SicarioSpec Guardrails (Additive)

`sicario init`/`apply` appended this section to your existing `CLAUDE.md`. Your
instructions above are unchanged and take precedence. Apply these guardrails for
non-trivial changes, subject to your project's own rules and any `mission.md`:

- Start with the spec; keep AI out of authoritative pass/fail decisions.
- Add threat model, abuse cases, and well-architected review for meaningful
  features; add negative/security tests when risk applies.
- Run `sicario verify` before handoff.
- Keep data classification, tagging, and security exceptions current and owned.
- Do not place secrets in files, logs, artifacts, or LLM context.

{SICARIO_OVERLAY_END}
"""


def _agent_overlay() -> str:
    """Delimited, idempotent SicarioSpec section appended to an existing AGENTS.md."""
    from sicario_cli._render import SICARIO_OVERLAY_BEGIN, SICARIO_OVERLAY_END

    return f"""{SICARIO_OVERLAY_BEGIN}

## SicarioSpec Guardrails (Additive)

`sicario init`/`apply` appended this section to your existing `AGENTS.md`. Your
instructions above are unchanged and take precedence. These apply to Codex,
Copilot coding agent, and other agents that read `AGENTS.md`, subject to your
project's own rules and any `mission.md`:

- Start with the spec for meaningful behavior changes; run `sicario verify`
  before handoff, pull request, release, or deployment.
- Keep AI out of authoritative security, compliance, legal, financial, or
  production-impacting decisions.
- Update threat model, abuse cases, data classification, and tagging when
  affected; add negative/security tests when risk applies.
- Keep security exceptions owned, approved, time-bound, and evidenced.
- Do not place secrets in files, logs, artifacts, prompts, generated output, or
  model context.

{SICARIO_OVERLAY_END}
"""


def _agent_instructions() -> str:
    return """# Agent Project Instructions

Use SicarioSpec guardrails for all non-trivial changes.

These instructions apply to Codex, GitHub Copilot coding agent, and other
agents that read `AGENTS.md`.

## Required Workflow

- Start with the spec before code for meaningful behavior changes.
- Run `sicario verify` before handoff, pull request, release, or deployment.
- Keep AI out of authoritative security, compliance, legal, financial, or
  production-impacting decisions.
- Add or update threat model and abuse cases for meaningful features.
- Add data classification and tagging updates when data, evidence, resources,
  release artifacts, or logs change.
- Add negative/security tests when risk applies.
- Keep security exceptions owned, approved, time-bound, and evidenced.
- Do not place secrets in files, logs, artifacts, prompts, generated output, or
  model context.

## Pull Requests

- Summarize security, governance, data classification, tagging, and release
  impact.
- Include verification commands and results.
- Use the machine-user PR flow when available; document fallback reason when it
  is not available.
- Do not merge failed checks or unresolved review comments.
"""


def _copilot_instructions() -> str:
    return """# GitHub Copilot Instructions

Follow SicarioSpec guardrails for every generated change.

- Prefer small, reviewable pull requests with clear evidence.
- Run `python3 -m sicario_cli.cli verify .` or `sicario verify` before handoff
  when the CLI is installed.
- Update specs, plans, tasks, threat models, abuse cases, data classification,
  tagging taxonomy, risk registers, and evidence paths when affected.
- Do not add secrets, tenant identifiers, customer data, private evidence, or
  unpublished vulnerability details to prompts, logs, docs, tests, artifacts, or
  release assets.
- Do not move or rewrite published release tags.
- For security, compliance, data, release, or production-impacting changes,
  require human approval and document the approval boundary.
- If Copilot cannot run a verification command, state exactly what was skipped
  and why in the pull request.
"""


def _copilot_governance_instructions() -> str:
    return """---
applyTo: "**"
---

# SicarioSpec Governance Instructions

Use these instructions for Copilot Chat, Copilot coding agent, and Copilot code
review when working in this repository.

- Treat `SICARIO.md`, `docs/governance/data-classification.md`, and
  `docs/governance/tagging-taxonomy.md` as required context.
- For AI, agent, RAG, MCP, or model-output changes, require prompt-injection,
  tool-boundary, memory, eval, and human-approval evidence.
- For multi-agent, queue, workflow, or SOAR changes, require retry,
  idempotency, dead-letter, observability, kill-switch, and approval-boundary
  evidence.
- For cloud/IaC changes, require least privilege, network exposure, encryption,
  secrets, logging, data residency, drift, policy-as-code, and tag evidence.
- For release changes, require version sync, immutable tags, workflow evidence,
  artifact classification, and provenance or attestation notes.
"""


def _copilot_setup_steps() -> str:
    return """name: "Copilot Setup Steps"

on:
  workflow_dispatch:
  push:
    paths:
      - .github/workflows/copilot-setup-steps.yml
  pull_request:
    paths:
      - .github/workflows/copilot-setup-steps.yml

jobs:
  copilot-setup-steps:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v6
        with:
          python-version: "3.11"
      - name: Install SicarioSpec project
        run: |
          if [ -f pyproject.toml ] || [ -f setup.py ]; then
            python -m pip install --upgrade pip
            python -m pip install -e .
          else
            echo "No Python package metadata found; Copilot will continue with repository checkout."
          fi
      - name: Verify SicarioSpec context
        run: |
          if python -m sicario_cli.cli --version >/dev/null 2>&1; then
            python -m sicario_cli.cli verify .
          elif command -v sicario >/dev/null 2>&1; then
            sicario verify .
          else
            echo "SicarioSpec CLI is not installed in this repository."
          fi
"""


def _skill_sicario_verify() -> str:
    return """---
name: sicario-verify
description: Run and interpret SicarioSpec verification gates before handoff, pull request, release, or when governance files change.
---

# SicarioSpec Verify

Use this skill when a change needs deterministic SicarioSpec validation.

1. Inspect the working tree and identify changed specs, plans, tasks, docs,
   workflows, release files, cloud/IaC files, and agent instructions.
2. Run the best available verifier:
   - `sicario verify .`
   - or `python3 -m sicario_cli.cli verify .`
3. If verification fails, summarize each finding by severity, code, path, and
   required remediation.
4. If verification passes, report the command and result.
5. Do not claim security or compliance approval from a passing verifier alone;
   human review is still required for high-impact changes.
"""


def _skill_governance_review() -> str:
    return """---
name: sicario-governance-review
description: Review a change for SicarioSpec security, data classification, tagging, evidence, risk, and approval gaps.
---

# SicarioSpec Governance Review

Use this skill before pull request handoff or when reviewing an AI-authored
change.

Check:

- Threat model and abuse cases are present and current.
- Data classification covers inputs, outputs, logs, evidence, artifacts, and
  release assets.
- Tagging discipline covers owner, system, environment, data classification,
  retention, evidence, risk, and exception records.
- Security exceptions are owned, approved, time-bound, and evidenced.
- AI/agent/tool-use changes include prompt injection, tool boundary, eval,
  memory, and human approval controls.
- Workflow/agent-fleet changes include retry, idempotency, dead-letter,
  observability, kill switch, and approval boundaries.
- PR summary includes verification commands and security/governance impact.
"""


def _skill_release_readiness() -> str:
    return """---
name: sicario-release-readiness
description: Check SicarioSpec version, changelog, immutable tag, artifact classification, and release evidence before publishing.
---

# SicarioSpec Release Readiness

Use this skill before tagging or publishing a release.

1. Confirm version metadata is synchronized across package metadata, CLI
   version, presets, extensions, and control maps.
2. Confirm `CHANGELOG.md` describes the release.
3. Confirm release artifacts are classified for public release and contain no
   secrets, private evidence, tenant identifiers, customer data, or unpublished
   vulnerability details.
4. Confirm release workflow, tests, verifier, artifact upload, and provenance or
   attestation evidence are green.
5. Do not move, delete, or rewrite a published tag. Ship a new patch release
   instead.
"""


def _claude_security_reviewer_agent() -> str:
    return """---
name: sicario-security-reviewer
description: Reviews changes for SicarioSpec security, data classification, tagging, threat-model, and evidence gaps.
tools: Read, Glob, Grep, Bash
model: inherit
---

You are a read-first SicarioSpec security reviewer. Review the repository and
diff for missing or stale threat models, abuse cases, data classification,
tagging taxonomy, evidence, risk entries, exception ownership, and approval
boundaries.

Prefer read-only commands. Do not edit files unless explicitly asked. Report
findings with file paths, concrete risk, and recommended remediation.
"""


def _claude_release_manager_agent() -> str:
    return """---
name: sicario-release-manager
description: Checks release readiness, version synchronization, changelog, immutable tags, artifacts, and provenance evidence.
tools: Read, Glob, Grep, Bash
model: inherit
---

You are a SicarioSpec release manager. Verify version metadata, changelog,
release workflow, artifact classification, immutable tag discipline, and
provenance or attestation evidence.

Prefer read-only commands. Do not move, delete, or rewrite published tags.
Report blockers and exact verification commands.
"""


def _write_agent_integrations(
    target: Path,
    integration: str,
    *,
    force: bool,
    dry_run: bool,
    actions: List[str],
    reports: List,
) -> None:
    from sicario_cli._render import FileReport, _overlay_text, _write_text

    if integration in {"claude", "all"}:
        _overlay_text(
            target / "CLAUDE.md",
            _claude_overlay(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
            full_content=_claude_instructions(),
        )
        _write_text(
            target / ".claude" / "skills" / "sicario-verify" / "SKILL.md",
            _skill_sicario_verify(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / ".claude" / "skills" / "sicario-governance-review" / "SKILL.md",
            _skill_governance_review(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / ".claude" / "skills" / "sicario-release-readiness" / "SKILL.md",
            _skill_release_readiness(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / ".claude" / "agents" / "sicario-security-reviewer.md",
            _claude_security_reviewer_agent(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / ".claude" / "agents" / "sicario-release-manager.md",
            _claude_release_manager_agent(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )

    if integration in {"codex", "copilot", "all"}:
        _overlay_text(
            target / "AGENTS.md",
            _agent_overlay(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
            full_content=_agent_instructions(),
        )

    if integration in {"codex", "all"}:
        _write_text(
            target / ".agents" / "skills" / "sicario-verify" / "SKILL.md",
            _skill_sicario_verify(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / ".agents" / "skills" / "sicario-governance-review" / "SKILL.md",
            _skill_governance_review(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / ".agents" / "skills" / "sicario-release-readiness" / "SKILL.md",
            _skill_release_readiness(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )

    if integration in {"copilot", "all"}:
        _write_text(
            target / ".github" / "copilot-instructions.md",
            _copilot_instructions(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / ".github" / "instructions" / "sicario-governance.instructions.md",
            _copilot_governance_instructions(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / ".github" / "workflows" / "copilot-setup-steps.yml",
            _copilot_setup_steps(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )


# ── Preset class ─────────────────────────────────────────────────────────


class SicarioCorePreset:
    """Baseline governance preset for SicarioSpec.

    Call ``write()`` to emit all core governance files into a target project.
    """

    ALWAYS_WORKFLOWS = ["sicario-verify.yml", "docs-site.yml"]

    TOOLCHAIN_WORKFLOW = "security-toolchain.yml"

    def write(
        self,
        target: Path,
        presets_root: Path,
        workflows_root: Path,
        selected_presets: Sequence[str],
        integration: str,
        apply_to_speckit: bool,
        deferrals: Sequence[str],
        speckit_template_files: Sequence[str],
        *,
        force: bool,
        dry_run: bool,
        actions: List[str],
        reports: List,
    ) -> None:
        from sicario_cli._render import _write_text
        from sicario_cli.cli import (
            _default_abuse_cases,
            _default_accepted_risk_log,
            _default_control_applicability,
            _default_data_classification,
            _default_docs_impact,
            _default_evidence_index,
            _default_risk_register,
            _default_security_exceptions,
            _default_system_context,
            _default_system_context_diagram,
            _default_tagging_taxonomy,
            _default_threat_model,
        )

        # 1. Apply governance to live Spec Kit paths.
        if apply_to_speckit:
            _apply_to_speckit(
                target,
                selected_presets,
                force=force,
                dry_run=dry_run,
                actions=actions,
                reports=reports,
                deferrals=deferrals,
                presets_root=presets_root,
                speckit_template_files=speckit_template_files,
            )

        # 2. SICARIO.md
        _write_text(
            target / "SICARIO.md",
            _sicario_project_readme(selected_presets),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )

        # 3. Security docs
        _write_text(
            target / "docs" / "security" / "threat-model.md",
            _default_threat_model(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / "docs" / "security" / "abuse-cases.md",
            _default_abuse_cases(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )

        # 4. Governance docs
        _write_text(
            target / "docs" / "governance" / "data-classification.md",
            _default_data_classification(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / "docs" / "governance" / "tagging-taxonomy.md",
            _default_tagging_taxonomy(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )

        # 5. Compliance docs
        _write_text(
            target / "docs" / "compliance" / "control-applicability.md",
            _default_control_applicability(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / "docs" / "compliance" / "evidence-index.md",
            _default_evidence_index(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )

        # 6. Architecture docs
        _write_text(
            target / "docs" / "architecture" / "system-context.md",
            _default_system_context(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / "docs" / "diagrams" / "system-context.mmd",
            _default_system_context_diagram(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / "docs" / "docs-impact.md",
            _default_docs_impact(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )

        # 7. Risk docs
        _write_text(
            target / "docs" / "risk" / "risk-register.md",
            _default_risk_register(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / "docs" / "risk" / "security-exceptions.md",
            _default_security_exceptions(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / "docs" / "risk" / "accepted-risk-log.md",
            _default_accepted_risk_log(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )

        # 8. Agent integrations
        _write_agent_integrations(
            target,
            integration,
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )

        # 9. Workflows — always-shipped pair
        for workflow_name in self.ALWAYS_WORKFLOWS:
            workflow_src = workflows_root / workflow_name
            if not workflow_src.exists():
                continue
            _write_text(
                target / ".github" / "workflows" / workflow_name,
                workflow_src.read_text(encoding="utf-8"),
                force=force,
                dry_run=dry_run,
                actions=actions,
                reports=reports,
            )

        # 10. Security-toolchain workflow (conditional)
        if "sicario-security-toolchain" in selected_presets:
            workflow_src = workflows_root / self.TOOLCHAIN_WORKFLOW
            if workflow_src.exists():
                _write_text(
                    target / ".github" / "workflows" / self.TOOLCHAIN_WORKFLOW,
                    workflow_src.read_text(encoding="utf-8"),
                    force=force,
                    dry_run=dry_run,
                    actions=actions,
                    reports=reports,
                )

        # 11. Cloud-IaC starters (conditional)
        if "sicario-cloud-iac" in selected_presets:
            self._write_cloud_iac_starters(target, presets_root, force, dry_run, actions, reports)

        # 12. Security-toolchain starters (conditional)
        if "sicario-security-toolchain" in selected_presets:
            self._write_toolchain_starters(target, presets_root, force, dry_run, actions, reports)

    @staticmethod
    def _write_cloud_iac_starters(
        target: Path,
        presets_root: Path,
        force: bool,
        dry_run: bool,
        actions: List[str],
        reports: List,
    ) -> None:
        from sicario_cli._render import _copy_tree

        starters = [
            ("terraform", "infra/terraform"),
            ("azure-bicep", "infra/azure-bicep"),
            ("azure-avm-bicep", "infra/azure-avm-bicep"),
            ("azure-avm-terraform", "infra/azure-avm-terraform"),
            ("aws-cloudformation", "infra/aws-cloudformation"),
            ("gcp", "infra/gcp-terraform"),
            ("kubernetes", "infra/kubernetes"),
            ("policy-as-code", "policy/policy-as-code"),
        ]
        src_base = presets_root / "sicario-cloud-iac" / "templates"
        for src_name, dst_rel in starters:
            _copy_tree(
                src_base / src_name,
                target / dst_rel,
                force=force,
                dry_run=dry_run,
                actions=actions,
                reports=reports,
            )

    @staticmethod
    def _write_toolchain_starters(
        target: Path,
        presets_root: Path,
        force: bool,
        dry_run: bool,
        actions: List[str],
        reports: List,
    ) -> None:
        from sicario_cli._render import _copy_tree

        _copy_tree(
            presets_root / "sicario-security-toolchain" / "templates" / "toolchain",
            target / "security" / "toolchain",
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
