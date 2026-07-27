from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from sicario_cli._render import (
    BACKUP_IGNORE_PATTERN,
    SICARIO_OVERLAY_BEGIN,
    _backup_rule_is_effective,
    _ensure_gitignore_rule,
)
from sicario_cli.cli import (
    CONTROL_MAPS_ROOT,
    EXPERIMENTAL_FRAMEWORKS,
    FRAMEWORK_IDS,
    FRAMEWORKS_CONFIG,
    PRESETS_ROOT,
    REQUIRED_TEMPLATES,
    SUPPORTED_FRAMEWORKS,
    _default_frameworks_for_profiles,
    _parse_frameworks,
    _read_selected_frameworks,
    build_parser,
    detect_existing_governance,
    main,
    verify_project,
)


class SicarioSpecShapeTests(unittest.TestCase):
    def test_every_preset_has_metadata_and_templates(self) -> None:
        presets = sorted(
            path for path in PRESETS_ROOT.iterdir() if path.is_dir() and path.name != "__pycache__"
        )
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
        self.assertIn("soc2-trust-services-sicario.json", names)
        self.assertIn("fedramp-rev5-sicario.json", names)
        self.assertIn("bsi-c5-2026-sicario.json", names)
        for path in maps:
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("id", data)
            self.assertIn("framework", data)

    def test_example_custom_rules_are_valid(self) -> None:
        from sicario_cli.rules import RuleEngine

        root = Path(__file__).resolve().parents[1]
        rule_dir = root / "examples" / "custom-rules"
        rules = sorted(rule_dir.glob("*.rule.json"))
        self.assertGreaterEqual(len(rules), 1)
        engine = RuleEngine()
        loaded = engine.load_rules([rule_dir])
        self.assertEqual(len(rules), len(loaded))


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


class FrameworkSelectorTests(unittest.TestCase):
    """#18 — projects enforce only the frameworks they chose."""

    def test_parse_frameworks_validates_and_dedupes(self) -> None:
        self.assertEqual(["iso27001", "hipaa"], _parse_frameworks("iso27001, hipaa, ISO27001"))

    def test_parse_frameworks_all_expands_to_every_framework(self) -> None:
        self.assertEqual(list(FRAMEWORK_IDS), _parse_frameworks("all"))

    def test_parse_frameworks_rejects_unknown(self) -> None:
        with self.assertRaises(SystemExit):
            _parse_frameworks("iso27001,not-a-framework")

    def test_default_frameworks_follow_profile_set(self) -> None:
        # public-core carries no compliance obligation -> no default frameworks.
        self.assertEqual([], _default_frameworks_for_profiles(["public-core"]))
        # compliance carries a concrete default set.
        self.assertEqual(
            ["ccm", "sox", "soc2", "iso27001", "nist-800-53"],
            _default_frameworks_for_profiles(["compliance"]),
        )
        # enterprise-strict enforces every SUPPORTED framework. Experimental maps
        # are excluded from every profile default, including this one — enforcing
        # them requires naming them explicitly on --frameworks.
        self.assertEqual(
            SUPPORTED_FRAMEWORKS, _default_frameworks_for_profiles(["enterprise-strict"])
        )

    def test_init_explicit_frameworks_writes_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(
                0,
                main(
                    [
                        "init",
                        str(target),
                        "--profile",
                        "compliance",
                        "--frameworks",
                        "iso27001,hipaa",
                    ]
                ),
            )
            config = target / FRAMEWORKS_CONFIG
            self.assertTrue(config.exists())
            self.assertEqual(["iso27001", "hipaa"], _read_selected_frameworks(target))

    def test_init_default_frameworks_match_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target), "--profile", "compliance"]))
            self.assertEqual(
                ["ccm", "sox", "soc2", "iso27001", "nist-800-53"],
                _read_selected_frameworks(target),
            )

    def test_tiers_partition_every_shipped_framework(self) -> None:
        self.assertEqual(
            set(FRAMEWORK_IDS),
            set(SUPPORTED_FRAMEWORKS) | EXPERIMENTAL_FRAMEWORKS,
            "every shipped framework must be assigned exactly one tier",
        )
        self.assertFalse(set(SUPPORTED_FRAMEWORKS) & EXPERIMENTAL_FRAMEWORKS)
        self.assertEqual({"pci-dss", "ai-rmf", "owasp-asvs"}, EXPERIMENTAL_FRAMEWORKS)

    def test_experimental_frameworks_never_appear_in_profile_defaults(self) -> None:
        """Experimental maps must require an explicit opt-in, never a profile default."""
        from sicario_cli.cli import PROFILE_FRAMEWORKS

        for profile in PROFILE_FRAMEWORKS:
            defaults = _default_frameworks_for_profiles([profile])
            leaked = set(defaults) & EXPERIMENTAL_FRAMEWORKS
            self.assertFalse(leaked, f"profile {profile} defaults leak experimental {leaked}")

    def test_appsec_default_drops_experimental_but_keeps_supported(self) -> None:
        # appsec is the sharpest case: its table entry names owasp-asvs, which is
        # experimental, so the supported entries must survive and it must not.
        defaults = _default_frameworks_for_profiles(["appsec"])
        self.assertIn("ssdf", defaults)
        self.assertIn("iso27001", defaults)
        self.assertNotIn("owasp-asvs", defaults)

    def test_experimental_framework_still_enforced_when_explicitly_selected(self) -> None:
        """Experimental stays installable and stays gated — it just is not implicit."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(
                0,
                main(
                    [
                        "init",
                        str(target),
                        "--profile",
                        "appsec",
                        "--frameworks",
                        "owasp-asvs,pci-dss",
                    ]
                ),
            )
            self.assertEqual(["owasp-asvs", "pci-dss"], _read_selected_frameworks(target))
            # Selected experimental maps are enforced exactly like supported ones.
            self.assertEqual([], verify_project(target, write=False))

            # Removing a selected experimental map must still be a finding.
            (target / "docs" / "compliance" / "control-maps" / FRAMEWORK_IDS["owasp-asvs"]).unlink()
            codes = [f.code for f in verify_project(target, write=False)]
            self.assertIn("SICARIO-MISSING-FRAMEWORK-MAP", codes)

    def test_frameworks_config_header_flags_experimental_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(
                0,
                main(["init", str(target), "--profile", "appsec", "--frameworks", "pci-dss"]),
            )
            content = (target / FRAMEWORKS_CONFIG).read_text(encoding="utf-8")
            self.assertIn("Experimental keys:", content)
            self.assertIn("explicitly enforces experimental: pci-dss", content)
            # The key line itself stays bare so the parser is unaffected.
            self.assertEqual(["pci-dss"], _read_selected_frameworks(target))

    def test_rerun_reports_preserved_selection_not_recomputed_defaults(self) -> None:
        """A preserved selector is what is enforced, so it is what must be reported.

        A project that selected an experimental framework before tiering keeps
        enforcing it on an ordinary re-run, because the existing
        .sicario/frameworks.txt is preserved rather than clobbered. Printing the
        newly-computed defaults would tell the user the opposite of the truth.
        """
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(
                0,
                main(
                    [
                        "init",
                        str(target),
                        "--profile",
                        "appsec",
                        "--frameworks",
                        "ssdf,owasp-asvs",
                    ]
                ),
            )

            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                self.assertEqual(0, main(["init", str(target), "--profile", "appsec"]))
            output = buffer.getvalue()

            # The stale experimental selection is still enforced...
            self.assertIn("owasp-asvs", _read_selected_frameworks(target))
            # ...so the run must say so, and must flag the divergence.
            self.assertIn("owasp-asvs (experimental)", output)
            self.assertIn("preserved", output)

    def test_public_core_writes_no_framework_config_and_verifies(self) -> None:
        # Default behavior is unchanged: bare public-core writes no selector and
        # verify keeps the legacy coarse control-map check (which passes since
        # init copies the control-map pack).
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target), "--profile", "public-core"]))
            self.assertFalse((target / FRAMEWORKS_CONFIG).exists())
            self.assertIsNone(_read_selected_frameworks(target))
            self.assertEqual([], verify_project(target, write=False))

    def test_verify_honors_selected_subset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(
                0,
                main(["init", str(target), "--profile", "compliance", "--frameworks", "iso27001"]),
            )
            # All maps were copied, so the selected subset verifies clean.
            self.assertEqual([], verify_project(target, write=False))
            # Remove the selected framework's map -> a precise finding fires.
            (target / "docs" / "compliance" / "control-maps" / FRAMEWORK_IDS["iso27001"]).unlink()
            findings = verify_project(target, write=False)
            codes = {finding.code for finding in findings}
            self.assertIn("SICARIO-MISSING-FRAMEWORK-MAP", codes)

    def test_verify_does_not_require_unselected_frameworks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(
                0,
                main(["init", str(target), "--profile", "compliance", "--frameworks", "iso27001"]),
            )
            # Removing a NON-selected framework's map must not fail the gate.
            (target / "docs" / "compliance" / "control-maps" / FRAMEWORK_IDS["hipaa"]).unlink()
            findings = verify_project(target, write=False)
            codes = {finding.code for finding in findings}
            self.assertNotIn("SICARIO-MISSING-FRAMEWORK-MAP", codes)
            self.assertNotIn("SICARIO-MISSING-CONTROL-MAPS", codes)


class WorkedExampleGateProofTests(unittest.TestCase):
    """#2 — the worked example proves the halting gate passes AND fails."""

    REPO_ROOT = Path(__file__).resolve().parents[1]

    def test_python_api_example_passes(self) -> None:
        example = self.REPO_ROOT / "examples" / "python-api"
        self.assertEqual([], verify_project(example, write=False))

    def test_python_api_failing_example_halts_with_expected_code(self) -> None:
        example = self.REPO_ROOT / "examples" / "python-api-failing"
        findings = verify_project(example, write=False)
        codes = {finding.code for finding in findings}
        # The only seeded gap is the missing threat model.
        self.assertEqual({"SICARIO-MISSING-THREAT-MODEL"}, codes)

    def test_failing_example_verify_command_returns_nonzero(self) -> None:
        # verify_command is the actual CLI entrypoint; it must exit non-zero so a
        # CI/merge gate halts.
        import argparse
        import io
        from contextlib import redirect_stdout

        from sicario_cli.cli import verify_command

        example = self.REPO_ROOT / "examples" / "python-api-failing"
        with redirect_stdout(io.StringIO()):
            code = verify_command(argparse.Namespace(path=str(example)))
        self.assertEqual(1, code)


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

    def test_init_ignores_backups_in_target_gitignore(self) -> None:
        """Backups are verbatim copies of the target's files, so they must be unstageable."""
        import fnmatch

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self._seed_brownfield(target)
            self.assertEqual(
                0, main(["init", str(target), "--profile", "appsec", "--integration", "claude"])
            )

            gitignore = target / ".gitignore"
            self.assertTrue(gitignore.exists())
            rules = [line.strip() for line in gitignore.read_text(encoding="utf-8").splitlines()]
            self.assertIn("*.sicario-bak.*", rules)

            # The rule must actually match the backups this run produced — a pattern
            # that is present but non-matching would be worse than none at all.
            backups = list(target.glob("*.sicario-bak.*")) + list(
                target.glob(".specify/memory/*.sicario-bak.*")
            )
            self.assertTrue(backups, "expected brownfield init to create backups")
            for backup in backups:
                self.assertTrue(
                    fnmatch.fnmatch(backup.name, "*.sicario-bak.*"),
                    f"ignore rule does not match real backup {backup.name}",
                )

    def test_init_preserves_existing_target_gitignore(self) -> None:
        """An existing .gitignore is appended to, never clobbered."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self._seed_brownfield(target)
            gitignore = target / ".gitignore"
            gitignore.write_text("node_modules/\n*.env\n", encoding="utf-8")

            self.assertEqual(
                0, main(["init", str(target), "--profile", "appsec", "--integration", "claude"])
            )

            content = gitignore.read_text(encoding="utf-8")
            self.assertIn("node_modules/", content)
            self.assertIn("*.env", content)
            self.assertIn("*.sicario-bak.*", content)

    def test_init_gitignore_rule_is_idempotent(self) -> None:
        """Re-running init must not append the ignore rule twice."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self._seed_brownfield(target)
            args = ["init", str(target), "--profile", "appsec", "--integration", "claude"]

            self.assertEqual(0, main(args))
            first = (target / ".gitignore").read_text(encoding="utf-8")
            self.assertEqual(0, main(args))
            second = (target / ".gitignore").read_text(encoding="utf-8")

            self.assertEqual(first, second)
            self.assertEqual(1, second.count("*.sicario-bak.*"))

    def test_init_dry_run_writes_no_gitignore(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self._seed_brownfield(target)
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
            self.assertFalse((target / ".gitignore").exists())

    def test_gitignore_rule_effectiveness_accounts_for_negations(self) -> None:
        """Presence is not protection: git applies the LAST matching pattern."""
        p = BACKUP_IGNORE_PATTERN
        self.assertTrue(_backup_rule_is_effective(f"{p}\n", p))
        # A negation AFTER the rule re-includes backups, so the rule is not effective.
        self.assertFalse(_backup_rule_is_effective(f"{p}\n!keep.sicario-bak.20260101\n", p))
        # A negation BEFORE the rule is overridden by it.
        self.assertTrue(_backup_rule_is_effective(f"!keep.sicario-bak.20260101\n{p}\n", p))
        # Comments and blank lines are not rules.
        self.assertTrue(_backup_rule_is_effective(f"# !{p}\n\n{p}\n", p))

    def test_ensure_gitignore_reasserts_rule_after_a_negation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            gitignore = target / ".gitignore"
            gitignore.write_text(
                f"{BACKUP_IGNORE_PATTERN}\n!keep.sicario-bak.20260101T000000Z\n",
                encoding="utf-8",
            )
            actions: list = []
            _ensure_gitignore_rule(target, dry_run=False, actions=actions)

            lines = [
                ln.strip()
                for ln in gitignore.read_text(encoding="utf-8").splitlines()
                if ln.strip()
            ]
            # Our rule must now be the last decisive rule, so it wins.
            self.assertEqual(BACKUP_IGNORE_PATTERN, lines[-1])
            self.assertTrue(
                _backup_rule_is_effective(
                    gitignore.read_text(encoding="utf-8"), BACKUP_IGNORE_PATTERN
                )
            )
            # And a second run is a no-op now that the rule is effective.
            before = gitignore.read_text(encoding="utf-8")
            _ensure_gitignore_rule(target, dry_run=False, actions=actions)
            self.assertEqual(before, gitignore.read_text(encoding="utf-8"))

    def test_ensure_gitignore_preserves_crlf_line_endings(self) -> None:
        """Appending one rule must not rewrite every existing line."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            gitignore = target / ".gitignore"
            gitignore.write_bytes(b"node_modules/\r\n*.env\r\n")
            _ensure_gitignore_rule(target, dry_run=False, actions=[])

            raw = gitignore.read_bytes()
            # Original lines survive byte-for-byte with their CRLF endings.
            self.assertIn(b"node_modules/\r\n", raw)
            self.assertIn(b"*.env\r\n", raw)
            # The appended rule uses the file's own ending, not a bare LF.
            self.assertIn(BACKUP_IGNORE_PATTERN.encode() + b"\r\n", raw)
            self.assertNotIn(b"\r\r", raw)

    def test_ensure_gitignore_preserves_lf_line_endings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            gitignore = target / ".gitignore"
            gitignore.write_bytes(b"node_modules/\n")
            _ensure_gitignore_rule(target, dry_run=False, actions=[])
            raw = gitignore.read_bytes()
            self.assertNotIn(b"\r", raw)
            self.assertIn(BACKUP_IGNORE_PATTERN.encode() + b"\n", raw)

    def test_ensure_gitignore_refuses_to_write_through_a_symlink(self) -> None:
        """A symlinked .gitignore points outside the project; never write through it."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            outside = base / "outside.txt"
            outside.write_text("ORIGINAL\n", encoding="utf-8")
            project = base / "project"
            project.mkdir()
            (project / ".gitignore").symlink_to(outside)

            actions: list = []
            _ensure_gitignore_rule(project, dry_run=False, actions=actions)

            self.assertEqual("ORIGINAL\n", outside.read_text(encoding="utf-8"))
            self.assertTrue(any("symlink" in a for a in actions))

    def test_secret_scan_detects_all_four_documented_patterns(self) -> None:
        """The three patterns that were dead code must actually be enforced.

        Until rules 041-043 shipped, only the assignment pattern was enforced.
        `SECRET_PATTERNS` in cli.py still listed AWS key ids, `sk-` provider
        tokens and private key blocks, but nothing referenced it, so those three
        were detected by nothing while USAGE.md claimed coverage. This test is the
        regression guard: it plants one of each and asserts each is caught.
        """
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target), "--profile", "appsec"]))

            # Built at runtime so this test file never itself contains a secret.
            (target / "leak_assign.txt").write_text(
                "api_key = " + '"' + "z" * 20 + '"' + "\n", encoding="utf-8"
            )
            (target / "leak_aws.txt").write_text(
                "AKIA" + "A1B2C3D4E5F6G7H8" + "\n", encoding="utf-8"
            )
            (target / "leak_token.txt").write_text("sk-" + "a" * 30 + "\n", encoding="utf-8")
            (target / "leak_key.pem").write_text(
                "-----BEGIN RSA PRIVATE" + " KEY-----\n", encoding="utf-8"
            )

            codes = {f.code for f in verify_project(target, write=False)}
            for expected in (
                "SICARIO-HARDCODED-SECRET",
                "SICARIO-HARDCODED-AWS-KEY",
                "SICARIO-HARDCODED-PROVIDER-TOKEN",
                "SICARIO-PRIVATE-KEY-MATERIAL",
            ):
                self.assertIn(expected, codes, f"{expected} did not fire on a planted secret")

    def test_generated_files_contain_no_placeholder_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.assertEqual(0, main(["init", str(target), "--profile", "appsec"]))
            parts = [
                ("api", "_", "key ="),
                ("api", "key:"),
                ("secret", "_", "key ="),
                ("pass", "word ="),
                ("bear", "er "),
                ("AK", "IA"),
                ("ghp", "_"),
            ]
            secret_patterns = ["".join(p).lower() for p in parts]
            for path in target.rglob("*"):
                if not path.is_file() or path.suffix not in (
                    ".md",
                    ".yml",
                    ".yaml",
                    ".json",
                    ".txt",
                ):
                    continue
                # Detection rules necessarily contain the patterns they detect —
                # `041-secret-aws-access-key.rule.json` holds the AWS key regex as
                # its own data. Scanning them for those strings is a guaranteed
                # false positive. Rule files are copied to more than one location
                # (`.sicario/rules/` and `.specify/presets/*/rules/`), so key off
                # the file itself rather than any one directory prefix.
                if path.name.endswith(".rule.json"):
                    continue
                content = path.read_text(encoding="utf-8", errors="ignore").lower()
                for pattern in secret_patterns:
                    self.assertNotIn(
                        pattern,
                        content,
                        f"Potential leaked pattern '{pattern}' found in {path}",
                    )


if __name__ == "__main__":
    unittest.main()
