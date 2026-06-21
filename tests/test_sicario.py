from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from sicario_cli.cli import (
    CONTROL_MAPS_ROOT,
    PRESETS_ROOT,
    REQUIRED_TEMPLATES,
    SICARIO_OVERLAY_BEGIN,
    build_parser,
    detect_existing_governance,
    main,
    verify_project,
)


class SicarioSpecShapeTests(unittest.TestCase):
    def test_every_preset_has_metadata_and_templates(self) -> None:
        presets = sorted(path for path in PRESETS_ROOT.iterdir() if path.is_dir())
        self.assertGreaterEqual(len(presets), 8)
        for preset in presets:
            self.assertTrue((preset / "preset.yml").exists(), preset)
            templates = preset / "templates"
            self.assertTrue(templates.exists(), preset)
            for template in REQUIRED_TEMPLATES:
                self.assertTrue((templates / template).exists(), f"{preset.name}/{template}")

    def test_extension_commands_exist(self) -> None:
        root = Path(__file__).resolve().parents[1]
        commands = root / "extensions" / "sicario-guard" / "commands"
        expected = {
            "sicario.init.md",
            "sicario.assess.md",
            "sicario.threatmodel.md",
            "sicario.controls.md",
            "sicario.evidence.md",
            "sicario.verify.md",
            "sicario.review.md",
            "sicario.apply-findings.md",
        }
        self.assertEqual(expected, {path.name for path in commands.glob("*.md")})

    def test_cli_has_required_commands(self) -> None:
        parser = build_parser()
        help_text = parser.format_help()
        self.assertIn("init", help_text)
        self.assertIn("verify", help_text)
        self.assertIn("assess", help_text)

    def test_control_maps_are_valid_json(self) -> None:
        maps = sorted(CONTROL_MAPS_ROOT.glob("*.json"))
        self.assertGreaterEqual(len(maps), 2)
        names = {path.name for path in maps}
        self.assertIn("ccm-v4.1-sicario.json", names)
        self.assertIn("sox-404-itgc-sicario.json", names)
        for path in maps:
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("id", data)
            self.assertIn("framework", data)


class SicarioCliBehaviorTests(unittest.TestCase):
    def test_init_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            code = main(["init", str(target), "--dry-run", "--profile", "public-core"])
            self.assertEqual(0, code)
            self.assertFalse(target.exists())

    def test_init_generates_project_that_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target), "--profile", "ai-system"]))
            findings = verify_project(target, write=True)
            self.assertEqual([], findings)
            summary = json.loads(
                (target / "generated" / "sicario" / "gate-summary.json").read_text()
            )
            self.assertEqual("pass", summary["status"])
            self.assertTrue((target / "docs-site" / "package.json").exists())
            self.assertTrue((target / "docs" / "diagrams" / "system-context.mmd").exists())
            self.assertTrue((target / "docs" / "governance" / "data-classification.md").exists())
            self.assertTrue((target / "docs" / "governance" / "tagging-taxonomy.md").exists())
            self.assertTrue((target / "docs" / "compliance" / "control-maps").exists())
            self.assertTrue((target / "docs" / "risk" / "risk-register.md").exists())

    def test_all_integration_generates_agent_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(
                0, main(["init", str(target), "--integration", "all", "--profile", "ai-system"])
            )

            expected = [
                "CLAUDE.md",
                "AGENTS.md",
                ".claude/skills/sicario-verify/SKILL.md",
                ".claude/skills/sicario-governance-review/SKILL.md",
                ".claude/skills/sicario-release-readiness/SKILL.md",
                ".claude/agents/sicario-security-reviewer.md",
                ".claude/agents/sicario-release-manager.md",
                ".agents/skills/sicario-verify/SKILL.md",
                ".agents/skills/sicario-governance-review/SKILL.md",
                ".agents/skills/sicario-release-readiness/SKILL.md",
                ".github/copilot-instructions.md",
                ".github/instructions/sicario-governance.instructions.md",
                ".github/workflows/copilot-setup-steps.yml",
            ]
            for relative in expected:
                self.assertTrue((target / relative).exists(), relative)

            self.assertIn("AGENTS.md", (target / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertIn(
                "copilot-setup-steps",
                (target / ".github" / "workflows" / "copilot-setup-steps.yml").read_text(
                    encoding="utf-8"
                ),
            )
            self.assertIn(
                "sicario verify",
                (target / ".agents" / "skills" / "sicario-verify" / "SKILL.md").read_text(
                    encoding="utf-8"
                ),
            )

    def test_codex_integration_generates_agents_md_and_codex_skills_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target), "--integration", "codex"]))
            self.assertTrue((target / "AGENTS.md").exists())
            self.assertTrue(
                (target / ".agents" / "skills" / "sicario-verify" / "SKILL.md").exists()
            )
            self.assertFalse((target / "CLAUDE.md").exists())
            self.assertFalse((target / ".github" / "copilot-instructions.md").exists())

    def test_copilot_integration_generates_copilot_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target), "--integration", "copilot"]))
            self.assertTrue((target / "AGENTS.md").exists())
            self.assertTrue((target / ".github" / "copilot-instructions.md").exists())
            self.assertTrue((target / ".github" / "workflows" / "copilot-setup-steps.yml").exists())
            self.assertFalse((target / "CLAUDE.md").exists())
            self.assertFalse(
                (target / ".agents" / "skills" / "sicario-verify" / "SKILL.md").exists()
            )

    def test_missing_threat_model_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target)]))
            (target / "docs" / "security" / "threat-model.md").unlink()
            findings = verify_project(target, write=False)
            codes = {finding.code for finding in findings}
            self.assertIn("SICARIO-MISSING-THREAT-MODEL", codes)

    def test_hardcoded_secret_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target)]))
            secret = "x" * 24
            (target / "bad.py").write_text(f"api_key = '{secret}'\n", encoding="utf-8")
            findings = verify_project(target, write=False)
            codes = {finding.code for finding in findings}
            self.assertIn("SICARIO-HARDCODED-SECRET", codes)

    def test_incomplete_active_exception_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target)]))
            (target / "docs" / "risk" / "security-exceptions.md").write_text(
                "\n".join(
                    [
                        "# Security Exceptions",
                        "",
                        "| Exception ID | Status | Control / Gate | Owner | Expires | Approval | Compensating Control | Evidence |",
                        "|---|---|---|---|---|---|---|---|",
                        "| EX-001 | active | secret scan | TBD | never | TBD | TBD | TBD |",
                    ]
                ),
                encoding="utf-8",
            )
            findings = verify_project(target, write=False)
            codes = {finding.code for finding in findings}
            self.assertIn("SICARIO-INCOMPLETE-ACTIVE-RISK", codes)

    def test_missing_data_classification_register_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target)]))
            (target / "docs" / "governance" / "data-classification.md").unlink()
            findings = verify_project(target, write=False)
            codes = {finding.code for finding in findings}
            self.assertIn("SICARIO-MISSING-DATA-CLASSIFICATION", codes)

    def test_shallow_data_classification_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target)]))
            spec_dir = target / "specs" / "001-classification"
            spec_dir.mkdir(parents=True)
            (spec_dir / "spec.md").write_text(
                "\n".join(
                    [
                        "# Feature Specification: customer export",
                        "## Data Classification",
                        "Internal.",
                        "## Tagging Discipline",
                        "- owner, system, environment, data-classification, retention",
                        "## Trust Boundaries",
                        "User to service.",
                        "## Security Requirements",
                        "Validate input.",
                        "## Abuse Cases",
                        "Misuse.",
                        "## Evidence",
                        "Tests.",
                    ]
                ),
                encoding="utf-8",
            )
            findings = verify_project(target, write=False)
            codes = {finding.code for finding in findings}
            self.assertIn("SICARIO-DATA-CLASSIFICATION-INCOMPLETE", codes)

    def test_ai_spec_without_guardrails_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target)]))
            spec_dir = target / "specs" / "001-ai"
            spec_dir.mkdir(parents=True)
            (spec_dir / "spec.md").write_text(
                "\n".join(
                    [
                        "# Feature Specification: AI helper",
                        "## Data Classification",
                        "- Highest classification: Internal",
                        "- Classification owner: Maintainers",
                        "- Data retention and deletion expectations: Per release",
                        "- Data residency or sovereignty constraints: N/A",
                        "- Sharing, egress, or third-party disclosure: None",
                        "- Redaction or masking requirements: Secrets redacted",
                        "## Tagging Discipline",
                        "- owner, system, environment, data-classification, retention",
                        "## Trust Boundaries",
                        "User to model.",
                        "## Security Requirements",
                        "Validate input.",
                        "## Abuse Cases",
                        "Misuse.",
                        "## Evidence",
                        "Tests.",
                        "This feature uses an LLM agent.",
                    ]
                ),
                encoding="utf-8",
            )
            findings = verify_project(target, write=False)
            codes = {finding.code for finding in findings}
            self.assertIn("SICARIO-AI-GUARDRAIL-MISSING", codes)

    def test_agent_fleet_spec_without_orchestration_guardrails_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target), "--profile", "agent-fleet"]))
            spec_dir = target / "specs" / "001-orchestration"
            spec_dir.mkdir(parents=True)
            (spec_dir / "spec.md").write_text(
                "\n".join(
                    [
                        "# Feature Specification: LangGraph remediation workflow",
                        "## Data Classification",
                        "- Highest classification: Internal",
                        "- Classification owner: Maintainers",
                        "- Data retention and deletion expectations: Per release",
                        "- Data residency or sovereignty constraints: N/A",
                        "- Sharing, egress, or third-party disclosure: None",
                        "- Redaction or masking requirements: Secrets redacted",
                        "## Tagging Discipline",
                        "- owner, system, environment, data-classification, retention",
                        "## Trust Boundaries",
                        "User to orchestrator to workers.",
                        "## Security Requirements",
                        "Validate input.",
                        "## Abuse Cases",
                        "Misuse.",
                        "## Evidence",
                        "Tests.",
                        "This feature uses LangGraph orchestration and worker queues.",
                        "Prompt injection and tool boundary controls are documented.",
                    ]
                ),
                encoding="utf-8",
            )
            findings = verify_project(target, write=False)
            codes = {finding.code for finding in findings}
            self.assertIn("SICARIO-FLEET-GUARDRAIL-MISSING", codes)

    def test_init_applies_governance_to_live_speckit_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target), "--profile", "appsec"]))
            # Spec Kit reads templates from .specify/templates/ and the
            # constitution from .specify/memory/constitution.md.
            for template in ("spec-template.md", "plan-template.md", "tasks-template.md"):
                self.assertTrue(
                    (target / ".specify" / "templates" / template).exists(),
                    f".specify/templates/{template}",
                )
            constitution = target / ".specify" / "memory" / "constitution.md"
            self.assertTrue(constitution.exists(), ".specify/memory/constitution.md")
            self.assertIn("Constitution", constitution.read_text(encoding="utf-8"))
            # The most specialized selected preset (sicario-appsec) supplies the
            # live spec template, not bare core.
            from sicario_cli.cli import PRESETS_ROOT

            appsec_spec = (
                PRESETS_ROOT / "sicario-appsec" / "templates" / "spec-template.md"
            ).read_text(encoding="utf-8")
            self.assertEqual(
                appsec_spec,
                (target / ".specify" / "templates" / "spec-template.md").read_text(
                    encoding="utf-8"
                ),
            )

    def test_init_no_apply_to_speckit_skips_live_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(
                0, main(["init", str(target), "--profile", "appsec", "--no-apply-to-speckit"])
            )
            self.assertFalse((target / ".specify" / "templates" / "spec-template.md").exists())
            self.assertFalse((target / ".specify" / "memory" / "constitution.md").exists())
            # Presets are still staged for reference.
            self.assertTrue((target / ".specify" / "presets" / "sicario-appsec").exists())

    def test_agent_fleet_profile_installs_preset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "fleet-project"
            self.assertEqual(0, main(["init", str(target), "--profile", "agent-fleet"]))
            self.assertTrue((target / ".specify" / "presets" / "sicario-agent-fleet").exists())
            self.assertTrue((target / ".specify" / "presets" / "sicario-ai-system").exists())
            findings = verify_project(target, write=False)
            self.assertEqual([], findings)

    def test_saas_profile_installs_preset_and_invariants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "saas-project"
            self.assertEqual(0, main(["init", str(target), "--profile", "saas"]))
            self.assertTrue((target / ".specify" / "presets" / "sicario-saas").exists())
            self.assertTrue((target / ".specify" / "presets" / "sicario-ai-system").exists())
            # The live constitution carries the SaaS invariants.
            constitution = (target / ".specify" / "memory" / "constitution.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Read-Only SaaS By Default", constitution)
            self.assertIn("Tenant Isolation And Data Boundary", constitution)
            self.assertIn("Mission Supremacy", constitution)
            findings = verify_project(target, write=False)
            self.assertEqual([], findings)

    def test_cloud_profile_installs_avm_starters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "cloud-project"
            self.assertEqual(0, main(["init", str(target), "--profile", "cloud-iac"]))
            self.assertTrue((target / "infra" / "azure-avm-bicep" / "main.bicep").exists())
            self.assertTrue((target / "infra" / "azure-avm-terraform" / "main.tf").exists())
            self.assertTrue((target / "infra" / "azure-bicep" / "main.bicep").exists())
            self.assertTrue((target / "infra" / "terraform" / "main.tf").exists())
            self.assertTrue((target / "policy" / "policy-as-code" / "README.md").exists())
            self.assertTrue(
                (target / "policy" / "policy-as-code" / "opa" / "conftest" / "iac.rego").exists()
            )
            findings = verify_project(target, write=False)
            self.assertEqual([], findings)

    def test_security_toolchain_profile_installs_toolchain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "toolchain-project"
            self.assertEqual(0, main(["init", str(target), "--profile", "security-toolchain"]))
            self.assertTrue(
                (target / ".specify" / "presets" / "sicario-security-toolchain").exists()
            )
            self.assertTrue((target / "security" / "toolchain" / "security-tools.md").exists())
            self.assertTrue((target / ".github" / "workflows" / "security-toolchain.yml").exists())
            findings = verify_project(target, write=False)
            self.assertEqual([], findings)

    def test_hooks_runner_executes_deterministic_and_reports_agent_hooks(self) -> None:
        import io
        from contextlib import redirect_stdout

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target), "--profile", "public-core"]))
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["hooks", str(target)])
            output = buffer.getvalue()
            # A freshly initialized project passes the deterministic verify hook.
            self.assertEqual(0, code)
            # after_tasks -> sicario.verify is deterministic and actually runs.
            self.assertIn("run sicario.verify (deterministic)", output)
            # after_specify -> sicario.threatmodel is agent guidance, reported not executed.
            self.assertIn("sicario.threatmodel (agent guidance)", output)
            self.assertTrue((target / "generated" / "sicario" / "gate-summary.json").exists())

    def test_hooks_runner_single_event_filter(self) -> None:
        import io
        from contextlib import redirect_stdout

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target), "--profile", "public-core"]))
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["hooks", str(target), "--event", "after_tasks"])
            output = buffer.getvalue()
            self.assertEqual(0, code)
            self.assertIn("[after_tasks]", output)
            self.assertNotIn("[after_specify]", output)

    def test_plan_without_well_architected_review_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target)]))
            spec_dir = target / "specs" / "001-plan"
            spec_dir.mkdir(parents=True)
            (spec_dir / "plan.md").write_text(
                "\n".join(
                    [
                        "# Implementation Plan",
                        "## Threat Model",
                        "## Supply Chain",
                        "## Rollback",
                        "## Human Approval",
                        "## Evidence",
                    ]
                ),
                encoding="utf-8",
            )
            findings = verify_project(target, write=False)
            codes = {finding.code for finding in findings}
            self.assertIn("SICARIO-PLAN-SECTION", codes)


class BrownfieldSafeAdoptionTests(unittest.TestCase):
    """`sicario init`/apply must never silently clobber existing governance."""

    def _seed_brownfield(self, target: Path) -> dict:
        """Create a target that already has constitution, templates, CLAUDE.md, mission.md."""
        (target / ".specify" / "memory").mkdir(parents=True)
        (target / ".specify" / "templates").mkdir(parents=True)
        constitution = target / ".specify" / "memory" / "constitution.md"
        constitution.write_text(
            "# MyProject Constitution\n\n## Core Principles\n### 1. Ship fast\nWe move quickly.\n",
            encoding="utf-8",
        )
        spec_template = target / ".specify" / "templates" / "spec-template.md"
        spec_template.write_text(
            "# My existing spec template\nCustom content here.\n", encoding="utf-8"
        )
        claude = target / "CLAUDE.md"
        claude.write_text("# My CLAUDE instructions\nDo the thing.\n", encoding="utf-8")
        mission = target / "mission.md"
        mission.write_text("# Mission\nRead-only against tenants.\n", encoding="utf-8")
        return {
            "constitution": constitution,
            "spec_template": spec_template,
            "claude": claude,
            "mission": mission,
        }

    def test_detect_existing_governance_finds_setup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self._seed_brownfield(target)
            found = detect_existing_governance(target)
            self.assertIn(".specify/memory/constitution.md", found["constitution"])
            self.assertIn(".specify/templates/spec-template.md", found["templates"])
            self.assertIn("CLAUDE.md", found["instructions"])
            self.assertIn("mission.md", found["mission"])

    def test_brownfield_default_overlays_and_preserves(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            seeded = self._seed_brownfield(target)
            original_constitution = seeded["constitution"].read_text(encoding="utf-8")
            original_template = seeded["spec_template"].read_text(encoding="utf-8")
            original_claude = seeded["claude"].read_text(encoding="utf-8")

            self.assertEqual(
                0, main(["init", str(target), "--profile", "appsec", "--integration", "claude"])
            )

            # Existing content is preserved verbatim (not clobbered)...
            new_constitution = seeded["constitution"].read_text(encoding="utf-8")
            self.assertIn(original_constitution.strip(), new_constitution)
            self.assertIn("Ship fast", new_constitution)
            # ...and the SicarioSpec overlay is appended additively, deferring to mission.md.
            self.assertIn(SICARIO_OVERLAY_BEGIN, new_constitution)
            self.assertIn("SUBORDINATE", new_constitution)
            self.assertIn("mission.md", new_constitution)

            new_template = seeded["spec_template"].read_text(encoding="utf-8")
            self.assertIn(original_template.strip(), new_template)
            self.assertIn(SICARIO_OVERLAY_BEGIN, new_template)

            new_claude = seeded["claude"].read_text(encoding="utf-8")
            self.assertIn(original_claude.strip(), new_claude)
            self.assertIn(SICARIO_OVERLAY_BEGIN, new_claude)

            # Backups were taken for every modified file.
            self.assertTrue(list(target.glob(".specify/memory/constitution.md.sicario-bak.*")))
            self.assertTrue(list(target.glob("CLAUDE.md.sicario-bak.*")))

    def test_brownfield_rerun_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            seeded = self._seed_brownfield(target)
            self.assertEqual(
                0, main(["init", str(target), "--profile", "appsec", "--integration", "claude"])
            )
            after_first = seeded["constitution"].read_text(encoding="utf-8")
            claude_first = seeded["claude"].read_text(encoding="utf-8")

            # Second run must not double-append the overlay.
            self.assertEqual(
                0, main(["init", str(target), "--profile", "appsec", "--integration", "claude"])
            )
            after_second = seeded["constitution"].read_text(encoding="utf-8")
            claude_second = seeded["claude"].read_text(encoding="utf-8")

            self.assertEqual(after_first, after_second)
            self.assertEqual(claude_first, claude_second)
            self.assertEqual(1, after_second.count(SICARIO_OVERLAY_BEGIN))
            self.assertEqual(1, claude_second.count(SICARIO_OVERLAY_BEGIN))

    def test_brownfield_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            seeded = self._seed_brownfield(target)
            before = seeded["constitution"].read_text(encoding="utf-8")
            self.assertEqual(
                0,
                main(
                    [
                        "init",
                        str(target),
                        "--profile",
                        "appsec",
                        "--integration",
                        "claude",
                        "--dry-run",
                    ]
                ),
            )
            after = seeded["constitution"].read_text(encoding="utf-8")
            self.assertEqual(before, after)
            self.assertEqual(before.count(SICARIO_OVERLAY_BEGIN), 0)
            # No backups, no new generated docs.
            self.assertFalse(list(target.glob(".specify/memory/constitution.md.sicario-bak.*")))
            self.assertFalse((target / "docs" / "security" / "threat-model.md").exists())

    def test_force_overwrites_constitution_after_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            seeded = self._seed_brownfield(target)
            original = seeded["constitution"].read_text(encoding="utf-8")
            self.assertEqual(
                0,
                main(
                    [
                        "init",
                        str(target),
                        "--profile",
                        "appsec",
                        "--integration",
                        "claude",
                        "--force",
                    ]
                ),
            )
            overwritten = seeded["constitution"].read_text(encoding="utf-8")
            # --force replaces with the full SicarioSpec constitution template.
            self.assertNotIn("Ship fast", overwritten)
            self.assertIn("Constitution", overwritten)
            # The original is preserved in a backup.
            backups = list(target.glob(".specify/memory/constitution.md.sicario-bak.*"))
            self.assertTrue(backups)
            self.assertEqual(original, backups[0].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
