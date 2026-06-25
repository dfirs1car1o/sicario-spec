#!/usr/bin/env python3
"""Build SicarioSpec release assets and install-allowed Spec Kit catalogs."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from datetime import date
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


REPO_URL = "https://github.com/dfirs1car1o/sicario-spec"
DOCS_URL = "https://dfirs1car1o.github.io/sicario-spec/"
CATALOG_BASE_URL = "https://raw.githubusercontent.com/dfirs1car1o/sicario-spec/main/catalogs"
AUTHOR = "SicarioSpec Contributors"
BUNDLE_MANIFEST_NAME = "bundle.yml"
DEFAULT_SPECKIT_VERSION = ">=0.9.0"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="dist", type=Path)
    parser.add_argument("--catalog-dir", default="catalogs", type=Path)
    parser.add_argument(
        "--catalog-base-url",
        help=(
            "Base URL where built ZIP assets will be reachable. Defaults to the "
            "GitHub release URL for VERSION."
        ),
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    release_tag = f"v{version}"
    base_url = (args.catalog_base_url or f"{REPO_URL}/releases/download/{release_tag}").rstrip("/")

    out_dir = _resolve_under_root(root, args.output_dir)
    catalog_dir = _resolve_under_root(root, args.catalog_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    catalog_dir.mkdir(parents=True, exist_ok=True)

    preset_entries: dict[str, dict] = {}
    for preset_dir in sorted((root / "presets").glob("sicario-*")):
        if not (preset_dir / "preset.yml").is_file():
            continue
        manifest = _read_simple_manifest(preset_dir / "preset.yml")
        preset_id = str(manifest["id"])
        archive_name = f"{preset_id}-{version}.zip"
        _zip_directory(preset_dir, out_dir / archive_name)
        preset_entries[preset_id] = _preset_catalog_entry(
            preset_id, manifest, preset_dir, version, f"{base_url}/{archive_name}"
        )

    extension_dir = root / "extensions" / "sicario-guard"
    extension_manifest = _read_simple_manifest(extension_dir / "extension.yml")
    extension_id = str(extension_manifest["id"])
    extension_archive = f"{extension_id}-{version}.zip"
    _zip_directory(extension_dir, out_dir / extension_archive)

    bundle_manifest = _read_bundle_manifest(root / BUNDLE_MANIFEST_NAME)
    bundle_id = str(bundle_manifest["id"])
    bundle_archive = f"{bundle_id}-{version}.zip"
    _build_bundle_archive(root, out_dir / bundle_archive)

    _write_json(
        catalog_dir / "presets.json",
        {
            "schema_version": "1.0",
            "updated_at": _catalog_date(),
            "catalog_url": f"{CATALOG_BASE_URL}/presets.json",
            "presets": preset_entries,
        },
    )
    _write_json(
        catalog_dir / "extensions.json",
        {
            "schema_version": "1.0",
            "updated_at": _catalog_date(),
            "catalog_url": f"{CATALOG_BASE_URL}/extensions.json",
            "extensions": {
                extension_id: _extension_catalog_entry(
                    extension_id,
                    extension_manifest,
                    version,
                    f"{base_url}/{extension_archive}",
                )
            },
        },
    )
    _write_json(
        catalog_dir / "bundles.json",
        {
            "schema_version": "1.0",
            "updated_at": _catalog_date(),
            "catalog_url": f"{CATALOG_BASE_URL}/bundles.json",
            "bundles": {
                bundle_id: _bundle_catalog_entry(
                    bundle_id,
                    bundle_manifest,
                    version,
                    f"{base_url}/{bundle_archive}",
                )
            },
        },
    )

    print(f"built {len(preset_entries)} preset archives, 1 extension archive, 1 bundle archive")
    print(f"catalogs written to {catalog_dir}")
    return 0


def _catalog_date() -> str:
    return f"{date.today().isoformat()}T00:00:00Z"


def _resolve_under_root(root: Path, path: Path) -> Path:
    resolved = path if path.is_absolute() else root / path
    return resolved.resolve()


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _zip_directory(source_dir: Path, archive_path: Path) -> None:
    if archive_path.exists():
        archive_path.unlink()
    with ZipFile(archive_path, "w", ZIP_DEFLATED) as archive:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(source_dir))


def _build_bundle_archive(root: Path, archive_path: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        bundle_dir = Path(tmp) / "sicario-spec-bundle"
        bundle_dir.mkdir()
        shutil.copy2(root / BUNDLE_MANIFEST_NAME, bundle_dir / BUNDLE_MANIFEST_NAME)
        (bundle_dir / "README.md").write_text(
            "# SicarioSpec Security & Governance Bundle\n\n"
            "Installs the full SicarioSpec Spec Kit component set from the "
            "SicarioSpec install-allowed preset and extension catalogs.\n",
            encoding="utf-8",
        )
        _zip_directory(bundle_dir, archive_path)


def _read_simple_manifest(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    manifest: dict[str, object] = {}
    for key in ("id", "name", "version", "description", "license", "category", "effect"):
        value = _scalar(text, key)
        if value is not None:
            manifest[key] = value
    manifest["tags"] = _yaml_list(text, "tags")
    manifest["commands"] = _block_list(text, "commands")
    manifest["hooks"] = _block_keys(text, "hooks")
    speckit = _nested_scalar(text, ("requires", "speckit_version"))
    if speckit is None:
        speckit = _nested_scalar(text, ("requires", "spec-kit"))
    if speckit is None:
        speckit = _nested_scalar(text, ("requirements", "spec-kit"))
    manifest["speckit_version"] = speckit or DEFAULT_SPECKIT_VERSION

    missing = [key for key in ("id", "name", "version", "description") if key not in manifest]
    if missing:
        raise SystemExit(f"{path} missing required fields: {', '.join(missing)}")
    return manifest


def _read_bundle_manifest(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    bundle_block = _mapping_block(text, "bundle")
    requires_block = _mapping_block(text, "requires")
    result: dict[str, object] = {}
    for key in ("id", "name", "version", "role", "description", "author", "license"):
        value = _scalar(bundle_block, key)
        if value is not None:
            result[key] = value
    result["tags"] = _yaml_list(text, "tags")
    result["speckit_version"] = _scalar(requires_block, "speckit_version") or DEFAULT_SPECKIT_VERSION
    result["provides"] = {
        "extensions": len(re.findall(r"^\s{4}- id:", _mapping_block(text, "extensions"), re.MULTILINE)),
        "presets": len(re.findall(r"^\s{4}- id:", _mapping_block(text, "presets"), re.MULTILINE)),
        "steps": 0,
        "workflows": 0,
    }
    missing = [
        key
        for key in ("id", "name", "version", "role", "description", "author", "license")
        if key not in result
    ]
    if missing:
        raise SystemExit(f"{path} missing required bundle fields: {', '.join(missing)}")
    return result


def _preset_catalog_entry(
    preset_id: str,
    manifest: dict[str, object],
    preset_dir: Path,
    version: str,
    download_url: str,
) -> dict:
    return {
        "name": manifest["name"],
        "id": preset_id,
        "version": version,
        "description": manifest["description"],
        "author": AUTHOR,
        "download_url": download_url,
        "repository": REPO_URL,
        "homepage": DOCS_URL,
        "documentation": f"{REPO_URL}/blob/main/presets/{preset_id}/README.md",
        "license": manifest.get("license", "MIT"),
        "requires": {"speckit_version": manifest.get("speckit_version", DEFAULT_SPECKIT_VERSION)},
        "provides": {
            "templates": len(list((preset_dir / "templates").glob("*.md"))),
            "commands": len(list((preset_dir / "commands").glob("*.md"))) if (preset_dir / "commands").exists() else 0,
        },
        "tags": manifest.get("tags") or ["security", "governance"],
        "created_at": "2026-06-25T00:00:00Z",
        "updated_at": _catalog_date(),
    }


def _extension_catalog_entry(
    extension_id: str,
    manifest: dict[str, object],
    version: str,
    download_url: str,
) -> dict:
    return {
        "name": manifest["name"],
        "id": extension_id,
        "description": manifest["description"],
        "author": AUTHOR,
        "version": version,
        "download_url": download_url,
        "repository": REPO_URL,
        "homepage": DOCS_URL,
        "documentation": f"{REPO_URL}/blob/main/extensions/{extension_id}/README.md",
        "changelog": f"{REPO_URL}/blob/main/CHANGELOG.md",
        "license": manifest.get("license", "MIT"),
        "category": manifest.get("category", "security"),
        "effect": manifest.get("effect", "read-write"),
        "requires": {"speckit_version": manifest.get("speckit_version", DEFAULT_SPECKIT_VERSION)},
        "provides": {
            "commands": len(manifest.get("commands", [])),
            "hooks": len(manifest.get("hooks", [])),
        },
        "tags": manifest.get("tags") or ["security", "governance", "verification"],
        "verified": False,
        "downloads": 0,
        "stars": 0,
        "created_at": "2026-06-25T00:00:00Z",
        "updated_at": _catalog_date(),
    }


def _bundle_catalog_entry(
    bundle_id: str,
    manifest: dict[str, object],
    version: str,
    download_url: str,
) -> dict:
    return {
        "id": bundle_id,
        "name": manifest["name"],
        "version": version,
        "role": manifest["role"],
        "description": manifest["description"],
        "author": manifest.get("author", AUTHOR),
        "license": manifest.get("license", "MIT"),
        "download_url": download_url,
        "requires": {"speckit_version": manifest.get("speckit_version", DEFAULT_SPECKIT_VERSION)},
        "provides": manifest["provides"],
        "repository": REPO_URL,
        "tags": manifest.get("tags") or ["security", "governance", "compliance"],
        "verified": False,
    }


def _scalar(text: str, key: str) -> str | None:
    match = re.search(rf"^\s*{re.escape(key)}:\s*(.+?)\s*$", text, re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    return value.strip("'\"")


def _nested_scalar(text: str, path: tuple[str, str]) -> str | None:
    block = _mapping_block(text, path[0])
    if not block:
        return None
    return _scalar(block, path[1])


def _inline_list(text: str, key: str) -> list[str]:
    match = re.search(rf"^\s*{re.escape(key)}:\s*\[(.*?)\]\s*$", text, re.MULTILINE)
    if not match:
        return []
    return [item.strip().strip("'\"") for item in match.group(1).split(",") if item.strip()]


def _yaml_list(text: str, key: str) -> list[str]:
    inline = _inline_list(text, key)
    if inline:
        return inline
    block = _mapping_block(text, key)
    if not block:
        return []
    return _block_items(block)


def _block_list(text: str, key: str) -> list[str]:
    block = _mapping_block(text, key)
    if not block:
        return []
    return _block_items(block)


def _block_keys(text: str, key: str) -> list[str]:
    block = _mapping_block(text, key)
    if not block:
        return []
    keys: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.endswith(":") and not stripped.startswith("-"):
            keys.append(stripped[:-1].strip().strip("'\""))
    return keys


def _block_items(block: str) -> list[str]:
    values: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        value = stripped[2:].strip().strip("'\"")
        if value:
            values.append(value)
    return values


def _mapping_block(text: str, key: str) -> str:
    match = re.search(rf"^(?P<indent>\s*){re.escape(key)}:\s*$", text, re.MULTILINE)
    if not match:
        return ""
    base_indent = len(match.group("indent"))
    start = match.end()
    lines = []
    for line in text[start:].splitlines():
        if line.strip() and len(line) - len(line.lstrip(" ")) <= base_indent:
            break
        lines.append(line)
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
