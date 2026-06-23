"""SicarioDocsPreset — Docusaurus documentation site preset."""

from __future__ import annotations

from pathlib import Path
from typing import List, Sequence


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
    ) -> None:
        from sicario_cli._render import _write_text
        from sicario_cli.cli import (
            _docs_site_package_json,
            _docusaurus_config,
            _docusaurus_css,
            _docusaurus_intro,
            _docusaurus_sidebars,
        )

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
