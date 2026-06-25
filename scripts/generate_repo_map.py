#!/usr/bin/env python3
"""Generate the Docusaurus repo-map data file.

The map is intentionally curated: users need a product-oriented view of the
repo, not a raw recursive file tree. The script scans stable project surfaces
and writes JSON consumed by docs-site/src/pages/repo-map.js.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "docs-site" / "src" / "generated" / "repo-map.json"


ACRONYMS = {
    "ai": "AI",
    "api": "API",
    "asvs": "ASVS",
    "ccm": "CCM",
    "ci": "CI",
    "cli": "CLI",
    "codeql": "CodeQL",
    "cpra": "CPRA",
    "dss": "DSS",
    "eu": "EU",
    "gdpr": "GDPR",
    "hipaa": "HIPAA",
    "iac": "IaC",
    "icfr": "ICFR",
    "id": "ID",
    "iso": "ISO",
    "itgc": "ITGC",
    "nist": "NIST",
    "oidc": "OIDC",
    "openssf": "OpenSSF",
    "owasp": "OWASP",
    "pci": "PCI",
    "pr": "PR",
    "pypi": "PyPI",
    "readme": "README",
    "rmf": "RMF",
    "saas": "SaaS",
    "sdks": "SDKs",
    "soc": "SOC",
    "sox": "SOX",
    "sp": "SP",
    "ssdf": "SSDF",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def titleize(value: str) -> str:
    suffixes = (
        ".md",
        ".json",
        ".yaml",
        ".yml",
        ".py",
        ".toml",
        ".in",
        ".txt",
        ".sh",
    )
    for suffix in suffixes:
        if value.endswith(suffix):
            value = value[: -len(suffix)]
            break
    value = value.replace("sicario-", "").replace("-sicario", "").replace("_", "-")
    parts = [
        part
        for segment in value.split("/")
        for part in segment.split("-")
        if part
    ]
    return " ".join(ACRONYMS.get(part.lower(), part.capitalize()) for part in parts)


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def sorted_files(pattern: str) -> List[Path]:
    return sorted(path for path in REPO_ROOT.glob(pattern) if path.is_file())


def node(
    *,
    node_id: str,
    title: str,
    path: str,
    kind: str,
    summary: str,
    tags: Iterable[str],
) -> Dict[str, object]:
    return {
        "id": node_id,
        "title": title,
        "path": path,
        "kind": kind,
        "summary": summary,
        "tags": sorted(set(tags)),
    }


def docs_nodes() -> List[Dict[str, object]]:
    docs = [
        path
        for path in sorted_files("docs/**/*.md")
        if "/assets/" not in rel(path) and "/diagrams/" not in rel(path)
    ]
    priority = [
        "docs/getting-started.md",
        "docs/security-model.md",
        "docs/rule-engine.md",
        "docs/control-maps.md",
        "docs/bundle-readiness.md",
        "docs/catalog-submission.md",
        "docs/release-process.md",
    ]
    by_rel = {rel(path): path for path in docs}
    ordered = [by_rel[item] for item in priority if item in by_rel]
    ordered.extend(path for path in docs if path not in ordered)
    return [
        node(
            node_id=f"doc-{rel(path).replace('/', '-').replace('.', '-')}",
            title=titleize(path.stem),
            path=rel(path),
            kind="doc",
            summary="User-facing documentation page in the published Docusaurus site.",
            tags=["user", "maintainer", "docs"],
        )
        for path in ordered
    ]


def preset_nodes() -> List[Dict[str, object]]:
    presets = sorted_files("presets/*/preset.yml")
    return [
        node(
            node_id=f"preset-{path.parent.name}",
            title=titleize(path.parent.name),
            path=rel(path),
            kind="preset",
            summary="Composable Spec Kit preset profile shipped with the SicarioSpec bundle.",
            tags=["user", "contributor", "preset"],
        )
        for path in presets
    ]


def control_map_nodes() -> List[Dict[str, object]]:
    maps = sorted_files("control_maps/*.json")
    return [
        node(
            node_id=f"control-map-{path.stem}",
            title=titleize(path.stem),
            path=rel(path),
            kind="control-map",
            summary="Framework evidence map connecting SicarioSpec artifacts to control expectations.",
            tags=["reviewer", "maintainer", "assurance"],
        )
        for path in maps
    ]


def rule_nodes() -> List[Dict[str, object]]:
    rules = [
        path
        for path in sorted_files("sicario_cli/rules/kinds/*.py")
        if path.name != "__init__.py"
    ]
    primary = [
        node(
            node_id="rule-engine",
            title="Rule Engine",
            path="sicario_cli/rules/engine.py",
            kind="engine",
            summary="Loads declarative rule files and dispatches them to fixed evaluator modules.",
            tags=["maintainer", "contributor", "ci"],
        ),
        node(
            node_id="rule-schema",
            title="Rule Schema",
            path="sicario_cli/rules/schema.json",
            kind="schema",
            summary="Defines the supported custom rule contract for project-owned gates.",
            tags=["contributor", "reviewer", "ci"],
        ),
    ]
    evaluators = [
        node(
            node_id=f"rule-kind-{path.stem}",
            title=titleize(path.stem),
            path=rel(path),
            kind="evaluator",
            summary="Rule evaluator used by sicario verify.",
            tags=["contributor", "maintainer", "ci"],
        )
        for path in rules
    ]
    return primary + evaluators


def workflow_nodes() -> List[Dict[str, object]]:
    workflows = sorted_files(".github/workflows/*.yml") + sorted_files(
        "workflow_templates/*.yml"
    )
    return [
        node(
            node_id=f"workflow-{rel(path).replace('/', '-').replace('.', '-')}",
            title=titleize(path.stem),
            path=rel(path),
            kind="workflow",
            summary="Automation surface for verification, publishing, docs, or release operations.",
            tags=["maintainer", "ci", "release"],
        )
        for path in workflows
    ]


def example_nodes() -> List[Dict[str, object]]:
    examples = [path.parent for path in sorted_files("examples/*/README.md")]
    return [
        node(
            node_id=f"example-{path.name}",
            title=titleize(path.name),
            path=rel(path),
            kind="example",
            summary="Reference target used to show how SicarioSpec behaves in a real project shape.",
            tags=["user", "contributor", "demo"],
        )
        for path in examples
    ]


def spec_nodes() -> List[Dict[str, object]]:
    specs = [path.parent for path in sorted_files("specs/*/spec.md")]
    return [
        node(
            node_id=f"spec-{path.name}",
            title=titleize(path.name),
            path=rel(path),
            kind="spec",
            summary="Spec Kit feature package with spec, plan, and task artifacts.",
            tags=["maintainer", "contributor", "planning"],
        )
        for path in specs
    ]


def package_nodes() -> List[Dict[str, object]]:
    files = {
        "sicario_cli/cli.py": "Sicario CLI",
        "pyproject.toml": "Python Project Metadata",
        "setup.py": "Legacy Package Build",
        "MANIFEST.in": "Package Asset Manifest",
        "VERSION": "Bundle Version",
        "bundle.yml": "Bundle Manifest",
        "demo/run.sh": "Demo Runner",
        "SUBMISSION.md": "Catalog Submission",
    }
    return [
        node(
            node_id=f"package-{item.replace('/', '-').replace('.', '-')}",
            title=title,
            path=item,
            kind="package",
            summary="Release, packaging, demo, or command-line surface used by the bundle.",
            tags=["maintainer", "release", "user"],
        )
        for item, title in files.items()
        if (REPO_ROOT / item).exists()
    ]


def group(
    *,
    group_id: str,
    title: str,
    summary: str,
    persona: str,
    tone: str,
    nodes: List[Dict[str, object]],
) -> Dict[str, object]:
    return {
        "id": group_id,
        "title": title,
        "summary": summary,
        "persona": persona,
        "tone": tone,
        "count": len(nodes),
        "nodes": nodes,
    }


def build_map() -> Dict[str, object]:
    version_path = REPO_ROOT / "VERSION"
    version = read_text(version_path) if version_path.exists() else "unversioned"
    groups = [
        group(
            group_id="docs",
            title="Published Docs",
            summary="The Pages site that teaches the operating model and links users into the bundle.",
            persona="user",
            tone="gold",
            nodes=docs_nodes(),
        ),
        group(
            group_id="presets",
            title="Spec Kit Presets",
            summary="Profiles users install or compose to add SicarioSpec governance to target repos.",
            persona="user",
            tone="teal",
            nodes=preset_nodes(),
        ),
        group(
            group_id="rules",
            title="Verify Rule Engine",
            summary="Deterministic code and schema that make governance checks enforceable in CI.",
            persona="contributor",
            tone="red",
            nodes=rule_nodes(),
        ),
        group(
            group_id="controls",
            title="Control Maps",
            summary="Framework mappings that turn project artifacts into standards evidence.",
            persona="reviewer",
            tone="blue",
            nodes=control_map_nodes(),
        ),
        group(
            group_id="automation",
            title="CI, Pages, Release",
            summary="GitHub Actions and workflow templates that publish, verify, and package the project.",
            persona="maintainer",
            tone="violet",
            nodes=workflow_nodes(),
        ),
        group(
            group_id="examples",
            title="Examples And Demo",
            summary="Working and failing target projects used to show the verifier in action.",
            persona="user",
            tone="green",
            nodes=example_nodes(),
        ),
        group(
            group_id="specs",
            title="Planning Artifacts",
            summary="Spec Kit feature histories that explain why the repo is shaped this way.",
            persona="maintainer",
            tone="orange",
            nodes=spec_nodes(),
        ),
        group(
            group_id="package",
            title="Bundle And CLI",
            summary="The package, CLI, demo, and submission files that make the repo bundle-ready.",
            persona="maintainer",
            tone="slate",
            nodes=package_nodes(),
        ),
    ]
    personas = sorted({group["persona"] for group in groups})
    return {
        "version": version,
        "root": {
            "title": "SicarioSpec",
            "subtitle": "Evidence-first Spec Kit governance bundle",
            "path": "README.md",
        },
        "personas": ["all"] + personas,
        "groups": groups,
        "summary": {
            "groups": len(groups),
            "nodes": sum(int(group["count"]) for group in groups),
            "generatedBy": rel(Path(__file__).resolve()),
        },
    }


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(build_map(), handle, indent=2, sort_keys=False)
        handle.write("\n")


if __name__ == "__main__":
    main()
