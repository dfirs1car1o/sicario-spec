from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from sicario_cli import __version__


ROOT = Path(__file__).resolve().parents[1]


class ReleaseMetadataTests(unittest.TestCase):
    def test_package_version_metadata_is_synchronized(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        self.assertEqual(version, __version__)

        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        match = re.search(r'^version = "([^"]+)"$', pyproject, flags=re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertEqual(version, match.group(1))

        for preset in sorted((ROOT / "presets").glob("sicario-*/preset.yml")):
            text = preset.read_text(encoding="utf-8")
            self.assertRegex(text, rf'version:\s*"?{re.escape(version)}"?', str(preset))

        extension = ROOT / "extensions" / "sicario-guard" / "extension.yml"
        self.assertRegex(
            extension.read_text(encoding="utf-8"),
            rf'version:\s*"?{re.escape(version)}"?',
        )

        for control_map in sorted((ROOT / "control_maps").glob("*.json")):
            data = json.loads(control_map.read_text(encoding="utf-8"))
            self.assertEqual(version, data["version"], control_map)

    def test_public_repo_health_files_exist(self) -> None:
        expected = [
            "CODE_OF_CONDUCT.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "SUPPORT.md",
            "CHANGELOG.md",
            "LICENSE",
            "docs/governance/data-classification.md",
            "docs/governance/tagging-taxonomy.md",
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            ".github/ISSUE_TEMPLATE/control_map.yml",
            ".github/ISSUE_TEMPLATE/security_hardening.yml",
            ".github/workflows/test.yml",
            ".github/workflows/codeql.yml",
            ".github/workflows/scorecard.yml",
            ".github/workflows/release.yml",
            ".github/workflows/publish-pypi.yml",
            ".github/dependabot.yml",
            ".github/release.yml",
            "catalogs/presets.json",
            "catalogs/extensions.json",
            "catalogs/bundles.json",
            "scripts/build_release_assets.py",
            "scripts/smoke_bundle_install.sh",
            "docs/release-process.md",
            "docs/openssf.md",
            "docs/repository-settings.md",
            "docs/machine-user-pr-flow.md",
            "docs/assets/sicario-spec-mark.svg",
        ]
        for relative in expected:
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_readme_has_release_badges_and_honest_openssf_language(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("actions/workflows/test.yml/badge.svg", readme)
        self.assertIn("actions/workflows/codeql.yml/badge.svg", readme)
        self.assertIn("actions/workflows/release.yml/badge.svg", readme)
        self.assertIn(
            "api.scorecard.dev/projects/github.com/dfirs1car1o/sicario-spec/badge", readme
        )
        self.assertIn("img.shields.io/github/v/release/dfirs1car1o/sicario-spec", readme)
        self.assertIn("OpenSSF Best Practices status is not claimed yet", readme)

    def test_release_workflow_builds_and_attests_distributions(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
        self.assertRegex(workflow, r"actions/upload-artifact@[0-9a-f]{40} # v7")
        self.assertRegex(workflow, r"actions/attest-build-provenance@[0-9a-f]{40} # v4")
        self.assertIn("--require-hashes -r .github/requirements/release-build.txt", workflow)
        self.assertIn("attestations: write", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("Build Spec Kit release assets", workflow)
        self.assertIn("Validate Spec Kit release assets", workflow)
        self.assertIn("Smoke test Spec Kit bundle install", workflow)
        self.assertIn("scripts/build_release_assets.py", workflow)
        self.assertIn("scripts/smoke_bundle_install.sh", workflow)
        self.assertIn('f"sicario-guard-{version}.zip"', workflow)
        self.assertIn('f"sicario-spec-{version}.zip"', workflow)
        self.assertIn("catalogs/*.json", workflow)
        self.assertIn(
            "Release $RELEASE_TAG already exists; immutable release assets will not be modified.",
            workflow,
        )
        self.assertNotIn("--clobber", workflow)
        self.assertNotIn("gh release upload", workflow)

    def test_pypi_publish_workflow_uses_trusted_publishing(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "publish-pypi.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("environment:", workflow)
        self.assertIn("name: pypi", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("--require-hashes -r .github/requirements/release-build.txt", workflow)
        # Assert the action is SHA-pinned with a version comment, not pinned to one
        # specific version. Hardcoding the version made every Dependabot bump
        # fail this test, which is what blocked #51.
        self.assertRegex(workflow, r"pypa/gh-action-pypi-publish@[0-9a-f]{40} # v[0-9.]+")
        self.assertNotRegex(workflow, r"(?m)^\s*pass" r"word:")
        self.assertNotIn("api-token", workflow)

    def test_sicario_core_uses_upstream_preset_schema(self) -> None:
        preset_dir = ROOT / "presets" / "sicario-core"
        manifest = (preset_dir / "preset.yml").read_text(encoding="utf-8")
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

        expected_fragments = [
            'schema_version: "1.0"',
            "preset:",
            '  id: "sicario-core"',
            '  name: "SicarioSpec Core"',
            f'  version: "{version}"',
            '  repository: "https://github.com/dfirs1car1o/sicario-spec"',
            '  license: "MIT"',
            '  description: "Baseline secure-by-default Spec Kit governance profile."',
            "requires:",
            '  speckit_version: ">=0.9.0"',
            "provides:",
            "  templates:",
            "  - security-ops",
            "  - evidence",
        ]
        for fragment in expected_fragments:
            self.assertIn(fragment, manifest)

        for filename in [
            "spec-template.md",
            "plan-template.md",
            "tasks-template.md",
            "checklist-template.md",
            "constitution-template.md",
        ]:
            self.assertIn(f'      file: "templates/{filename}"', manifest)
            self.assertTrue((preset_dir / "templates" / filename).exists(), filename)

        for filename in ["README.md", "LICENSE", "CHANGELOG.md"]:
            self.assertTrue((preset_dir / filename).exists(), filename)
            self.assertTrue(
                (ROOT / "sicario_cli" / "assets" / "presets" / "sicario-core" / filename).exists(),
                filename,
            )

        expected_template_terms = {
            "README.md": [
                "Security Evidence Chain",
                "What Makes It Different",
                "operational proof",
            ],
            "templates/spec-template.md": [
                "## Security Evidence Chain",
                "## Operational Signal / Response Path",
            ],
            "templates/plan-template.md": [
                "## Security Evidence Chain",
                "## Operational Readiness",
            ],
            "templates/tasks-template.md": [
                "Populate the Security Evidence Chain",
                "configured project verification gate",
            ],
            "templates/checklist-template.md": [
                "Security Evidence Chain maps risks",
                "Project verification gate passed",
            ],
            "templates/constitution-template.md": ["### 4. Security Evidence Chain"],
        }
        for relative, terms in expected_template_terms.items():
            text = (preset_dir / relative).read_text(encoding="utf-8")
            for term in terms:
                self.assertIn(term, text, f"{relative}: {term}")

    def test_machine_user_policy_documents_audited_fallback(self) -> None:
        policy = (ROOT / "docs" / "machine-user-pr-flow.md").read_text(encoding="utf-8")
        self.assertIn("by default", policy)
        self.assertIn("Fallback Path", policy)
        self.assertIn("machine-user flow was unavailable", policy)
        self.assertIn("branch protection is restored", policy)

    def test_scorecard_workflow_can_publish_badge_results(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "scorecard.yml").read_text(encoding="utf-8")
        self.assertRegex(workflow, r"ossf/scorecard-action@[0-9a-f]{40} # v2\.4\.4")
        self.assertIn("publish_results: true", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("security-events: write", workflow)

    def test_shipped_ci_template_installs_pinned_sicario_and_sha_pins_actions(self) -> None:
        # Regression test for #68: the CI template shipped to adopters must
        # install SicarioSpec itself, pinned, and must hold this repo's own
        # SHA-pinning discipline (see test_pypi_publish_workflow_uses_trusted_publishing
        # for why the regex is version-agnostic rather than hardcoding a SHA that
        # a legitimate Dependabot bump would then break).
        for relative in (
            "workflow_templates/sicario-verify.yml",
            # Packaged mirror used by `sicario init` for installed (non-source-checkout)
            # adopters — see sicario_cli.cli._resolve_asset_root. Both copies must ship
            # the fix, or only in-repo dogfooding gets it.
            "sicario_cli/assets/workflow_templates/sicario-verify.yml",
        ):
            workflow = (ROOT / relative).read_text(encoding="utf-8")

            # Actions are SHA-pinned (40-hex) with a trailing version comment, not a
            # bare tag pin like `@v4`.
            self.assertRegex(workflow, r"actions/checkout@[0-9a-f]{40} # v[0-9.]+", relative)
            self.assertRegex(workflow, r"actions/setup-python@[0-9a-f]{40} # v[0-9.]+", relative)
            self.assertNotRegex(workflow, r"actions/checkout@v\d", relative)
            self.assertNotRegex(workflow, r"actions/setup-python@v\d", relative)

            # The install step installs SicarioSpec itself from a pinned ref, not
            # the adopting repository via `-e .`.
            self.assertRegex(
                workflow,
                r"pip install \"git\+https://github\.com/dfirs1car1o/sicario-spec\.git@v[0-9.]+\"",
                relative,
            )
            self.assertNotIn("pip install -e .", workflow, relative)

        # Both copies must agree, or only the source-checkout path gets the fix.
        self.assertEqual(
            (ROOT / "workflow_templates" / "sicario-verify.yml").read_text(encoding="utf-8"),
            (
                ROOT / "sicario_cli" / "assets" / "workflow_templates" / "sicario-verify.yml"
            ).read_text(encoding="utf-8"),
        )

    def test_workflow_template_copies_are_byte_identical(self) -> None:
        # Regression guard: `sicario init` reads from
        # sicario_cli/assets/workflow_templates/ when installed (non-source-checkout)
        # and workflow_templates/ when dogfooding this repo (see
        # sicario_cli.cli._resolve_asset_root). A fix landed in only one copy is a
        # fix adopters never receive. Covers every file in workflow_templates/, not
        # just sicario-verify.yml (that narrower check predates this one and is kept
        # above for its docstring/history).
        source_dir = ROOT / "workflow_templates"
        packaged_dir = ROOT / "sicario_cli" / "assets" / "workflow_templates"

        source_files = sorted(p.name for p in source_dir.glob("*.yml"))
        packaged_files = sorted(p.name for p in packaged_dir.glob("*.yml"))
        self.assertEqual(
            source_files, packaged_files, "workflow_templates/ directory listings diverged"
        )
        self.assertTrue(source_files, "expected at least one workflow template")

        for name in source_files:
            self.assertEqual(
                (source_dir / name).read_text(encoding="utf-8"),
                (packaged_dir / name).read_text(encoding="utf-8"),
                name,
            )

    def test_docs_site_workflow_succeeds_on_a_fresh_init_with_no_lockfile(self) -> None:
        # Regression test for #72: `sicario init` generates docs-site/package.json
        # without a package-lock.json (init cannot assume npm is available on the
        # adopter's machine to produce one). `actions/setup-node`'s `cache: npm`
        # input errors out before any step runs if the lockfile it would key on
        # doesn't exist, and `npm ci` separately refuses to run without one — so
        # every fresh adopter's first push previously shipped a red workflow next
        # to their gate. The generated workflow must not depend on a lockfile that
        # was never generated.
        for relative in (
            "workflow_templates/docs-site.yml",
            "sicario_cli/assets/workflow_templates/docs-site.yml",
        ):
            workflow = (ROOT / relative).read_text(encoding="utf-8")

            self.assertRegex(workflow, r"actions/checkout@[0-9a-f]{40} # v[0-9.]+", relative)
            self.assertRegex(workflow, r"actions/setup-node@[0-9a-f]{40} # v[0-9.]+", relative)
            self.assertNotRegex(workflow, r"actions/checkout@v\d", relative)
            self.assertNotRegex(workflow, r"actions/setup-node@v\d", relative)

            # No cache keyed on a lockfile that init never generates. Matched as
            # an actual YAML key (start-of-line, no `#`) rather than a plain
            # substring, since the workflow's own explanatory comment mentions
            # `cache:` in prose.
            self.assertNotRegex(workflow, r"(?m)^\s*cache:\s", relative)
            self.assertNotRegex(workflow, r"(?m)^\s*cache-dependency-path:", relative)

            # `npm ci` requires an existing lockfile and errors (EUSAGE) without
            # one; `npm install` does not. Matched as an actual `run:` step
            # rather than a plain substring, since the workflow's own
            # explanatory comment mentions `npm ci` in prose.
            self.assertRegex(workflow, r"(?m)^\s*-\s*run:\s*npm install\s*$", relative)
            self.assertNotRegex(workflow, r"(?m)^\s*-\s*run:\s*npm ci\b", relative)


if __name__ == "__main__":
    unittest.main()
