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
            self.assertIn(f"version: {version}", text, preset)

        extension = ROOT / "extensions" / "sicario-guard" / "extension.yml"
        self.assertIn(f"version: {version}", extension.read_text(encoding="utf-8"))

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
            ".github/dependabot.yml",
            ".github/release.yml",
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
        self.assertIn("api.scorecard.dev/projects/github.com/dfirs1car1o/sicario-spec/badge", readme)
        self.assertIn("img.shields.io/github/v/release/dfirs1car1o/sicario-spec", readme)
        self.assertIn("OpenSSF Best Practices status is not claimed yet", readme)

    def test_release_workflow_builds_and_attests_distributions(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
        self.assertIn("actions/upload-artifact@v7", workflow)
        self.assertIn("actions/attest-build-provenance@v4", workflow)
        self.assertIn("attestations: write", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("Release $RELEASE_TAG already exists; immutable release assets will not be modified.", workflow)
        self.assertNotIn("--clobber", workflow)
        self.assertNotIn("gh release upload", workflow)

    def test_machine_user_policy_documents_audited_fallback(self) -> None:
        policy = (ROOT / "docs" / "machine-user-pr-flow.md").read_text(encoding="utf-8")
        self.assertIn("by default", policy)
        self.assertIn("Fallback Path", policy)
        self.assertIn("machine-user flow was unavailable", policy)
        self.assertIn("branch protection is restored", policy)

    def test_scorecard_workflow_can_publish_badge_results(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "scorecard.yml").read_text(encoding="utf-8")
        self.assertIn("ossf/scorecard-action@v2.4.3", workflow)
        self.assertIn("publish_results: true", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("security-events: write", workflow)


if __name__ == "__main__":
    unittest.main()
