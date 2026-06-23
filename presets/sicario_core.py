"""SicarioCorePreset — baseline governance preset.

Ships every profile's mandatory governance files: constitution overlay, security
docs, governance docs, compliance docs, architecture docs, risk docs, agent
integration files, and CI/CD workflows.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Sequence


class SicarioCorePreset:
    """Baseline governance preset for SicarioSpec.

    Call ``write()`` to emit all core governance files into a target project.
    Content-generator functions are imported lazily to avoid circular imports
    from ``cli.py``.
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
        *,
        force: bool,
        dry_run: bool,
        actions: List[str],
        reports: List,
    ) -> None:
        from sicario_cli._render import _write_text
        from sicario_cli.cli import (
            _apply_to_speckit,
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
            _sicario_project_readme,
            _write_agent_integrations,
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
