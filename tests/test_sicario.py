from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from sicario_cli.cli import (
    CONTROL_MAPS_ROOT,
    PRESETS_ROOT,
    REQUIRED_TEMPLATES,
    build_parser,
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
            summary = json.loads((target / "generated" / "sicario" / "gate-summary.json").read_text())
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
            self.assertEqual(0, main(["init", str(target), "--integration", "all", "--profile", "ai-system"]))

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
            self.assertIn("copilot-setup-steps", (target / ".github" / "workflows" / "copilot-setup-steps.yml").read_text(encoding="utf-8"))
            self.assertIn("sicario verify", (target / ".agents" / "skills" / "sicario-verify" / "SKILL.md").read_text(encoding="utf-8"))

    def test_codex_integration_generates_agents_md_and_codex_skills_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target), "--integration", "codex"]))
            self.assertTrue((target / "AGENTS.md").exists())
            self.assertTrue((target / ".agents" / "skills" / "sicario-verify" / "SKILL.md").exists())
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
            self.assertFalse((target / ".agents" / "skills" / "sicario-verify" / "SKILL.md").exists())

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

    def test_agent_fleet_profile_installs_preset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "fleet-project"
            self.assertEqual(0, main(["init", str(target), "--profile", "agent-fleet"]))
            self.assertTrue((target / ".specify" / "presets" / "sicario-agent-fleet").exists())
            self.assertTrue((target / ".specify" / "presets" / "sicario-ai-system").exists())
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
            self.assertTrue((target / "policy" / "policy-as-code" / "opa" / "conftest" / "iac.rego").exists())
            findings = verify_project(target, write=False)
            self.assertEqual([], findings)

    def test_security_toolchain_profile_installs_toolchain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "toolchain-project"
            self.assertEqual(0, main(["init", str(target), "--profile", "security-toolchain"]))
            self.assertTrue((target / ".specify" / "presets" / "sicario-security-toolchain").exists())
            self.assertTrue((target / "security" / "toolchain" / "security-tools.md").exists())
            self.assertTrue((target / ".github" / "workflows" / "security-toolchain.yml").exists())
            findings = verify_project(target, write=False)
            self.assertEqual([], findings)

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


if __name__ == "__main__":
    unittest.main()
