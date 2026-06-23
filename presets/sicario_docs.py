"""SicarioDocsPreset — Docusaurus documentation site preset."""

from __future__ import annotations

from pathlib import Path
from typing import List, Sequence


def _docs_site_package_json() -> str:
    return """{
  "name": "sicario-docs-site",
  "private": true,
  "scripts": {
    "build": "docusaurus build",
    "start": "docusaurus start"
  },
  "dependencies": {
    "@docusaurus/core": "^3.8.0",
    "@docusaurus/preset-classic": "^3.8.0",
    "mermaid": "^11.0.0"
  },
  "devDependencies": {}
}
"""


def _docusaurus_config() -> str:
    return """const config = {
  title: 'Project Docs',
  tagline: 'Secure-by-default delivery evidence',
  url: 'https://example.com',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  presets: [
    ['classic', {
      docs: {
        sidebarPath: require.resolve('./sidebars.js')
      },
      blog: false,
      theme: {
        customCss: require.resolve('./src/css/custom.css')
      }
    }]
  ]
};

module.exports = config;
"""


def _docusaurus_sidebars() -> str:
    return """module.exports = {
  tutorialSidebar: [
    'intro'
  ]
};
"""


def _docusaurus_intro() -> str:
    return """# Project Documentation

This site is generated from repository documentation. Keep docs and diagrams
current as part of every change.

## Required Evidence

- Threat model
- Abuse cases
- Data classification
- Tagging taxonomy
- Control applicability
- Evidence index
- Control maps
- Risk register
- Security exceptions
- Accepted risk log
- System context diagram
- SicarioSpec gate summary
"""


def _docusaurus_css() -> str:
    return """:root {
  --ifm-color-primary: #0f766e;
  --ifm-code-font-size: 95%;
}
"""


class SicarioDocsPreset:
    """Generates Docusaurus docs-site boilerplate."""

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
        **kwargs: object,
    ) -> None:
        from sicario_cli._render import _write_text

        _write_text(
            target / "docs-site" / "package.json",
            _docs_site_package_json(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / "docs-site" / "docusaurus.config.js",
            _docusaurus_config(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / "docs-site" / "sidebars.js",
            _docusaurus_sidebars(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / "docs-site" / "docs" / "intro.md",
            _docusaurus_intro(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
        _write_text(
            target / "docs-site" / "src" / "css" / "custom.css",
            _docusaurus_css(),
            force=force,
            dry_run=dry_run,
            actions=actions,
            reports=reports,
        )
