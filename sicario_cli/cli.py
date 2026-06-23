"""Command line entrypoint for SicarioSpec.

The CLI intentionally uses only the Python standard library. SicarioSpec should
be installable and testable in constrained environments without pulling a
dependency graph before the governance gates are active.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sysconfig
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.resources import files as package_files
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from sicario_cli._render import (
    FileReport,
    _copy_tree,
    _print_report,
    _write_text,
)
from sicario_cli.version import __version__

PRESET_CLASSES: "dict[str, type]" = {}
try:
    from presets.sicario_core import SicarioCorePreset  # type: ignore[import-untyped]  # noqa: E501

    PRESET_CLASSES["sicario-core"] = SicarioCorePreset
except ImportError:
    pass
try:
    from presets.sicario_docs import SicarioDocsPreset  # type: ignore[import-untyped]  # noqa: E501

    PRESET_CLASSES["sicario-docs"] = SicarioDocsPreset
except ImportError:
    pass


REPO_ROOT = Path(__file__).resolve().parents[1]


def _asset_root() -> Path:
    env_root = os.environ.get("SICARIO_ASSET_ROOT")
    candidates = []
    if env_root:
        candidates.append(Path(env_root).expanduser())
    candidates.extend(
        [
            REPO_ROOT,
            Path(str(package_files("sicario_cli").joinpath("assets"))),
            Path(sysconfig.get_path("data")) / "share" / "sicario-spec",
        ]
    )
    for candidate in candidates:
        if (candidate / "presets").exists() and (candidate / "extensions").exists():
            return candidate
    return REPO_ROOT


ASSET_ROOT = _asset_root()
PRESETS_ROOT = ASSET_ROOT / "presets"
EXTENSIONS_ROOT = ASSET_ROOT / "extensions"
WORKFLOW_ROOT = ASSET_ROOT / "workflow_templates"
CONTROL_MAPS_ROOT = ASSET_ROOT / "control_maps"

REQUIRED_TEMPLATES = [
    "spec-template.md",
    "plan-template.md",
    "tasks-template.md",
    "checklist-template.md",
    "constitution-template.md",
]

PROFILE_PRESETS = {
    "public-core": ["sicario-core", "sicario-docs"],
    "core": ["sicario-core", "sicario-docs"],
    "docs": ["sicario-core", "sicario-docs"],
    "appsec": ["sicario-core", "sicario-docs", "sicario-appsec"],
    "ai-system": ["sicario-core", "sicario-docs", "sicario-ai-system"],
    "agent-fleet": ["sicario-core", "sicario-docs", "sicario-ai-system", "sicario-agent-fleet"],
    "cloud-iac": ["sicario-core", "sicario-docs", "sicario-cloud-iac"],
    "supply-chain": ["sicario-core", "sicario-docs", "sicario-supply-chain"],
    "compliance": ["sicario-core", "sicario-docs", "sicario-compliance"],
    "saas": ["sicario-core", "sicario-docs", "sicario-ai-system", "sicario-saas"],
    "security-toolchain": ["sicario-core", "sicario-docs", "sicario-security-toolchain"],
    "enterprise-strict": [
        "sicario-core",
        "sicario-docs",
        "sicario-appsec",
        "sicario-ai-system",
        "sicario-agent-fleet",
        "sicario-security-toolchain",
        "sicario-supply-chain",
        "sicario-compliance",
        "sicario-enterprise-strict",
    ],
}

# --- Framework selector (#18) -------------------------------------------------
#
# SicarioSpec ships 10 control-map frameworks. By default a project does not
# have to enforce all of them — that would punish a team that only owes evidence
# for, say, ISO 27001 and HIPAA. The framework selector lets a project declare
# which subset applies. The declaration lives in a plain-text project config file
# (`.sicario/frameworks.txt`, one framework key per line). `sicario verify` reads
# it and, when present, fails if any SELECTED framework's control map is absent
# (SICARIO-MISSING-FRAMEWORK-MAP) — so a team enforces exactly the frameworks it
# chose, not all 10 and not none.
#
# Backward-compatible by construction: with NO config file, verify behaves
# exactly as before (the single coarse SICARIO-MISSING-CONTROL-MAPS check).

# Short, stable selector key -> shipped control-map filename.
FRAMEWORK_IDS = {
    "ccm": "ccm-v4.1-sicario.json",
    "sox": "sox-404-itgc-sicario.json",
    "ssdf": "ssdf-800-218-sicario.json",
    "ai-rmf": "ai-rmf-sicario.json",
    "iso27001": "iso-27001-2022-sicario.json",
    "nist-800-53": "nist-800-53-r5-sicario.json",
    "eu-ai-act": "eu-ai-act-sicario.json",
    "gdpr": "gdpr-cpra-sicario.json",
    "pci-dss": "pci-dss-v4.0-sicario.json",
    "hipaa": "hipaa-security-rule-sicario.json",
    "owasp-asvs": "owasp-asvs-sicario.json",
}

# The project config file that records the selected subset (one key per line).
FRAMEWORKS_CONFIG = Path(".sicario") / "frameworks.txt"

# Default framework subset per profile. The default = the profile's natural set
# (`public-core` carries no compliance obligation; compliance-shaped profiles
# carry the maps they imply). `enterprise-strict` enforces all 10.
PROFILE_FRAMEWORKS = {
    "compliance": ["ccm", "sox", "iso27001", "nist-800-53"],
    "saas": ["ccm", "iso27001", "ai-rmf"],
    "ai-system": ["ai-rmf", "eu-ai-act"],
    "agent-fleet": ["ai-rmf", "eu-ai-act"],
    "cloud-iac": ["ccm", "nist-800-53"],
    "supply-chain": ["ssdf"],
    "appsec": ["ssdf", "iso27001", "owasp-asvs"],
    "enterprise-strict": list(FRAMEWORK_IDS),
}


def _parse_frameworks(value: str) -> List[str]:
    """Parse a comma-separated --frameworks value into validated selector keys.

    ``all`` expands to every shipped framework. Unknown keys are a hard error so
    a typo can never silently disable a framework the user meant to enforce.
    """
    names = [part.strip().lower() for part in value.split(",") if part.strip()]
    selected: List[str] = []
    for name in names:
        if name == "all":
            for key in FRAMEWORK_IDS:
                if key not in selected:
                    selected.append(key)
            continue
        if name not in FRAMEWORK_IDS:
            known = ", ".join(sorted(FRAMEWORK_IDS))
            raise SystemExit(f"Unknown framework(s): {name}. Known frameworks: {known}")
        if name not in selected:
            selected.append(name)
    return selected


def _default_frameworks_for_profiles(profile_names: Sequence[str]) -> List[str]:
    """Compute the default framework subset from the selected profile name(s)."""
    selected: List[str] = []
    for name in profile_names:
        for key in PROFILE_FRAMEWORKS.get(name, []):
            if key not in selected:
                selected.append(key)
    return selected


def _frameworks_config_content(frameworks: Sequence[str]) -> str:
    header = (
        "# SicarioSpec framework selector (#18).\n"
        "# One framework key per line. `sicario verify` requires a control map\n"
        "# for each key listed here (SICARIO-MISSING-FRAMEWORK-MAP if absent).\n"
        "# Remove this file to fall back to the default coarse control-map check.\n"
        f"# Known keys: {', '.join(sorted(FRAMEWORK_IDS))}\n"
    )
    body = "\n".join(frameworks)
    return header + (body + "\n" if body else "")


def _read_selected_frameworks(root: Path) -> Optional[List[str]]:
    """Read the project's selected frameworks, or None when no config exists.

    None (no config file) means "no explicit selection" — verify keeps its
    legacy coarse control-map behavior. An empty/comment-only file returns an
    empty list, meaning "explicitly no per-framework enforcement".
    """
    config = root / FRAMEWORKS_CONFIG
    if not config.exists():
        return None
    selected: List[str] = []
    for raw in config.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key = line.lower()
        if key in FRAMEWORK_IDS and key not in selected:
            selected.append(key)
    return selected


TEXT_SUFFIXES = {
    ".env",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".tf",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}

DATA_CLASSIFICATION_VALUES = {"public", "internal", "confidential", "restricted", "regulated"}

SECRET_PATTERNS = [
    re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----"),
]

AI_KEYWORDS = re.compile(r"\b(ai|llm|rag|agent|mcp|model|prompt|tool use|tool-call)\b", re.I)
FLEET_KEYWORDS = re.compile(
    r"\b(langgraph|temporal|ray|celery|queue|worker|orchestrator|orchestration|"
    r"durable workflow|sub-agent|subagent|agent fleet|multi-agent|soar|playbook)\b",
    re.I,
)

SEMGREQ_SEVERITIES = {"error", "high", "critical"}
SARIF_ERROR_LEVELS = {"error"}


def _parse_semgrep_json(path: Path) -> List[Finding]:
    """Parse a Semgrep JSON output file and return findings for high/critical/error results."""
    findings: List[Finding] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return findings
    results = data if isinstance(data, list) else data.get("results", [])
    for i, result in enumerate(results):
        extra = result.get("extra", {})
        severity = (extra.get("severity") or "").lower()
        if severity not in SEMGREQ_SEVERITIES:
            continue
        check_id = result.get("check_id", "unknown-rule")
        message = extra.get("message", "No message")
        location = result.get("path", "unknown")
        line = result.get("start", {}).get("line", "?")
        findings.append(
            Finding(
                severity="critical",
                code="SICARIO-CRITICAL-VULNS",
                message=f"Semgrep [{check_id}] {message}",
                path=f"{location}:{line}",
            )
        )
    return findings


def _parse_sarif(path: Path) -> List[Finding]:
    """Parse a SARIF format file and return findings for error-level results."""
    findings: List[Finding] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return findings
    for run in data.get("runs", []):
        for result in run.get("results", []):
            level = (result.get("level") or "").lower()
            if level not in SARIF_ERROR_LEVELS:
                continue
            rule_id = result.get("ruleId", "unknown-rule")
            message = result.get("message", {}).get("text", "No message")
            locations = result.get("locations", [])
            if locations:
                loc = locations[0]
                uri = (
                    loc.get("physicalLocation", {})
                    .get("artifactLocation", {})
                    .get("uri", "unknown")
                )
                line = loc.get("physicalLocation", {}).get("region", {}).get("startLine", "?")
                path_str = f"{uri}:{line}"
            else:
                path_str = "unknown"
            findings.append(
                Finding(
                    severity="critical",
                    code="SICARIO-CRITICAL-VULNS",
                    message=f"SARIF [{rule_id}] {message}",
                    path=path_str,
                )
            )
    return findings


def _scan_evidence_files(root: Path) -> List[Finding]:
    """Scan for Semgrep JSON and SARIF scanner output files in the project.

    Recognised file names:
      - ``semgrep.json`` — Semgrep JSON output
      - ``*.sarif`` — SARIF format (GitHub Advanced Security, Trivy, Snyk)
    """
    findings: List[Finding] = []
    for path in sorted(root.rglob("semgrep.json")):
        findings.extend(_parse_semgrep_json(path))
    for path in sorted(root.rglob("*.sarif")):
        findings.extend(_parse_sarif(path))
    return findings


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    path: str = ""

    def as_dict(self) -> dict:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "path": self.path,
        }


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _parse_profile_names(value: str) -> List[str]:
    """Validate and return the requested profile NAMES (not expanded presets)."""
    names = [part.strip() for part in value.split(",") if part.strip()]
    if not names:
        return ["public-core"]
    unknown = [name for name in names if name not in PROFILE_PRESETS]
    if unknown:
        known = ", ".join(sorted(PROFILE_PRESETS))
        raise SystemExit(f"Unknown profile(s): {', '.join(unknown)}. Known profiles: {known}")
    return names


def _parse_profiles(value: str) -> List[str]:
    names = _parse_profile_names(value)
    presets: List[str] = []
    for name in names:
        for preset in PROFILE_PRESETS[name]:
            if preset not in presets:
                presets.append(preset)
    return presets


# --- Brownfield-safe adoption -------------------------------------------------
#
# Adopting SicarioSpec into a repository that already has a constitution,
# Spec Kit templates, or agent-instruction files (CLAUDE.md / AGENTS.md /
# mission.md) is the trust gate for a community tool. The default behavior MUST
# NOT silently clobber a user's existing governance.
#
# Defaults (no flag):
#   - new file                -> created
#   - existing file we can    -> merged/overlaid (additive, idempotent, backed up)
#     additively extend
#   - existing file we cannot -> preserved (left untouched, reported)
#     safely merge
#
# `--force` restores the legacy full-overwrite behavior (still backs up first).
# `--dry-run` previews every decision and writes nothing.


SPECKIT_TEMPLATE_FILES = ["spec-template.md", "plan-template.md", "tasks-template.md"]

# Project-supremacy / agent-instruction files we look for when deciding whether
# the constitution overlay must defer to an existing higher authority.
PROJECT_INSTRUCTION_FILES = [
    "mission.md",
    "MISSION.md",
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    ".cursorrules",
]


def detect_existing_governance(target: Path) -> "dict[str, List[str]]":
    """Detect a pre-existing governance/instruction setup before writing.

    Returns a dict of category -> list of relative paths found, so adoption can
    choose merge/overlay over clobber and so the report can explain decisions.
    """
    found: "dict[str, List[str]]" = {
        "constitution": [],
        "templates": [],
        "instructions": [],
        "mission": [],
    }
    constitution = target / ".specify" / "memory" / "constitution.md"
    if constitution.exists():
        found["constitution"].append(str(constitution.relative_to(target)))
    templates_dir = target / ".specify" / "templates"
    if templates_dir.exists():
        for template in SPECKIT_TEMPLATE_FILES + [
            "checklist-template.md",
            "constitution-template.md",
        ]:
            candidate = templates_dir / template
            if candidate.exists():
                found["templates"].append(str(candidate.relative_to(target)))
    for name in PROJECT_INSTRUCTION_FILES:
        candidate = target / name
        if candidate.exists():
            key = "mission" if name.lower() == "mission.md" else "instructions"
            found[key].append(str(candidate.relative_to(target)))
    return found


def _validate_specify_available() -> str:
    specify = shutil.which("specify")
    if not specify:
        return "not found"
    try:
        result = subprocess.run(
            [specify, "--version"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return "found but not executable"
    return result.stdout.strip() or result.stderr.strip() or "found"


def init_project(args: argparse.Namespace) -> int:
    target = Path(args.project).expanduser().resolve()
    actions: List[str] = []
    reports: List[FileReport] = []
    selected_presets = _parse_profiles(args.profile)

    # Brownfield-safe adoption is the DEFAULT: a non-empty target is fine. We
    # detect any existing governance and merge/overlay/preserve instead of
    # clobbering. `--force` is the explicit full-overwrite opt-in.
    existing = (
        detect_existing_governance(target)
        if target.exists()
        else {
            "constitution": [],
            "templates": [],
            "instructions": [],
            "mission": [],
        }
    )
    # The constitution overlay must defer to any mission.md / project-supremacy
    # instruction file we found.
    deferrals = existing["mission"] + existing["instructions"]

    interactive_config: Optional[dict] = None
    if getattr(args, "interactive", False):
        interactive_config = _interactive_init(target)
        actions.append("mode: interactive setup wizard")
        if interactive_config["frameworks"]:
            args.frameworks = ",".join(interactive_config["frameworks"])
            actions.append(f"interactive frameworks: {', '.join(interactive_config['frameworks'])}")
        else:
            args.frameworks = None
        # Auto-include cloud-iac profile when cloud providers are selected.
        if interactive_config["cloud_providers"] and "sicario-cloud-iac" not in selected_presets:
            if "cloud-iac" not in args.profile:
                args.profile = args.profile + ",cloud-iac"
                selected_presets = _parse_profiles(args.profile)
            actions.append(f"cloud providers: {', '.join(interactive_config['cloud_providers'])}")
        actions.append(f"data classification: {interactive_config['data_classification']}")

    actions.append(f"target {target}")
    actions.append(f"specify {_validate_specify_available()}")
    actions.append(f"integration {args.integration}")
    actions.append(f"presets {', '.join(selected_presets)}")
    detected = [f"{k}={v}" for k, v in existing.items() if v]
    if detected:
        actions.append("detected existing governance: " + "; ".join(detected))
        actions.append(
            "mode: brownfield-safe (merge/overlay/preserve)"
            if not args.force
            else "mode: FORCE full-overwrite (backups taken)"
        )
    else:
        actions.append("mode: greenfield (no existing governance detected)")

    if not args.dry_run:
        target.mkdir(parents=True, exist_ok=True)

    for preset in selected_presets:
        _copy_tree(
            PRESETS_ROOT / preset,
            target / ".specify" / "presets" / preset,
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
            reports=reports,
        )

    if CONTROL_MAPS_ROOT.exists():
        _copy_tree(
            CONTROL_MAPS_ROOT,
            target / "docs" / "compliance" / "control-maps",
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
            reports=reports,
        )

    shipped_rules = PRESETS_ROOT / "sicario-core" / "rules"
    if shipped_rules.is_dir():
        _copy_tree(
            shipped_rules,
            target / ".sicario" / "rules",
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
            reports=reports,
        )

    # Framework selector (#18): record which frameworks this project enforces.
    # Explicit --frameworks wins; otherwise default to the profile's set. When
    # neither yields a selection (e.g. bare public-core), we write no config so
    # verify keeps its legacy coarse control-map behavior.
    if getattr(args, "frameworks", None):
        selected_frameworks = _parse_frameworks(args.frameworks)
    else:
        selected_frameworks = _default_frameworks_for_profiles(_parse_profile_names(args.profile))
    if selected_frameworks:
        actions.append(f"frameworks {', '.join(selected_frameworks)}")
        _write_text(
            target / FRAMEWORKS_CONFIG,
            _frameworks_config_content(selected_frameworks),
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
            reports=reports,
        )
    else:
        actions.append("frameworks (none selected; default coarse control-map check)")

    if interactive_config is not None:
        sicario_dir = target / ".sicario"
        if not args.dry_run:
            sicario_dir.mkdir(parents=True, exist_ok=True)
        _write_text(
            sicario_dir / "config.json",
            json.dumps(interactive_config, indent=2) + "\n",
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
            reports=reports,
        )

    _copy_tree(
        EXTENSIONS_ROOT / "sicario-guard",
        target / ".specify" / "extensions" / "sicario-guard",
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
        reports=reports,
    )

    _write_text(
        target / ".specify" / "extensions.yml",
        _extensions_yml(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
        reports=reports,
    )

    # Delegate generated content (docs, integrations, workflows) to presets.
    for preset_id in selected_presets:
        cls = PRESET_CLASSES.get(preset_id)
        if cls is not None:
            cls().write(
                target,
                presets_root=PRESETS_ROOT,
                workflows_root=WORKFLOW_ROOT,
                selected_presets=selected_presets,
                integration=args.integration,
                apply_to_speckit=getattr(args, "apply_to_speckit", True),
                deferrals=deferrals,
                speckit_template_files=SPECKIT_TEMPLATE_FILES,
                force=args.force,
                dry_run=args.dry_run,
                actions=actions,
                reports=reports,
            )

    print("\n".join(actions))
    _print_report(reports, dry_run=args.dry_run, force=args.force)
    if args.dry_run:
        print("dry-run complete; no files written")
    else:
        print(f"SicarioSpec initialized at {target}")
        print("Next: cd into the project and run `sicario verify`.")
    return 0


def _extensions_yml() -> str:
    return """installed:
  - sicario-guard
settings:
  auto_execute_hooks: true
hooks:
  after_specify:
    - extension: sicario-guard
      command: sicario.threatmodel
      enabled: true
      optional: false
      description: Create or update threat model stubs after specification
  after_plan:
    - extension: sicario-guard
      command: sicario.review
      enabled: true
      optional: false
      description: Review plan for required governance gates
  after_tasks:
    - extension: sicario-guard
      command: sicario.verify
      enabled: true
      optional: false
      description: Verify security tasks and evidence requirements
"""


def _default_threat_model() -> str:
    return """# Threat Model

Status: draft

## Scope

Document the feature, system, or repository being assessed.

## Trust Boundaries

- Boundary 1: user input to application logic
- Boundary 2: application logic to external systems
- Boundary 3: generated/model output to tools or file writes

## Threats

| Threat | Impact | Control | Status |
|---|---|---|---|
| Prompt injection or unsafe generated output | High | Validate and sanitize before tool use | Planned |
| Broken access control | High | Explicit authorization checks and tests | Planned |
| Secret exposure | Critical | Secret scanning and runtime secret isolation | Planned |

## Approval Boundaries

High-impact writes, production changes, releases, and security exceptions require
human approval.
"""


def _default_abuse_cases() -> str:
    return """# Abuse Cases

- An unauthenticated or low-privilege actor attempts privileged behavior.
- A user submits malformed input to bypass validation.
- A prompt or document attempts to override developer/system instructions.
- A dependency or workflow attempts to execute unexpected code.
- An operator attempts a production-impacting action without approval.
"""


def _default_data_classification() -> str:
    return """# Data Classification

Use the highest applicable classification for each feature, dataset, evidence
artifact, log stream, model prompt, model output, queue message, and generated
document.

## Levels

| Level | Description | Examples | Minimum Handling |
|---|---|---|---|
| Public | Approved for public release | docs, public examples | Source review before publication |
| Internal | Internal project or operational data | backlog notes, internal diagrams | Repository access controls |
| Confidential | Business, customer, or security-sensitive data | customer config, private architecture | Need-to-know access and redaction |
| Restricted | Highly sensitive security, credential, or regulated data | secrets, tokens, vuln details | Do not commit; approved secure storage only |
| Regulated | Data under legal, contractual, or audit scope | PII, PHI, PCI, SOX evidence | Control mapping, retention, and reviewer approval |

## Register

| Asset / Flow | Owner | Classification | Regulated Data | Retention | Residency | Sharing / Egress | Redaction | Evidence |
|---|---|---|---|---|---|---|---|---|
| Initial project artifacts | Maintainers | Internal | none | Per release | N/A | Repository collaborators | Secrets redacted | generated/sicario/gate-summary.json |

## Rules

- Classification must be explicit before data storage, logging, telemetry,
  training/evaluation, external sharing, or release packaging.
- Restricted data and secrets must not enter git, logs, generated artifacts, or
  LLM context.
- Evidence that contains customer, tenant, vulnerability, credential, or audit
  details must carry the same or higher classification as the source data.
"""


def _default_tagging_taxonomy() -> str:
    return """# Tagging Taxonomy

Use stable tags so data handling, ownership, cost, evidence, risk, and exception
decisions can be found and enforced.

## Required Tags

| Tag | Required For | Accepted Values / Format | Purpose |
|---|---|---|---|
| owner | all artifacts/resources | team or person handle | accountability |
| system | all artifacts/resources | system or repo slug | grouping |
| environment | runtime resources/evidence | dev, test, staging, prod, shared, local | blast-radius context |
| data-classification | data, resources, evidence | public, internal, confidential, restricted, regulated | handling requirements |
| retention | data/evidence/logs | duration or policy name | deletion expectations |
| compliance-scope | scoped artifacts | none, sox, ccm, pci, hipaa, gdpr, ai-rmf, other | control mapping |
| cost-center | cloud/resources | org-approved value | cost accountability |
| source-repo | generated/runtime artifacts | owner/repo | traceability |
| managed-by | runtime resources | terraform, bicep, cloudformation, kubernetes, manual | drift ownership |
| expires-on | temporary resources/exceptions | YYYY-MM-DD or N/A | cleanup discipline |
| feature-id | feature evidence | specs/NNN-name | feature traceability |
| control-id | control evidence | framework control ID or N/A | audit traceability |
| risk-id | risk evidence | risk register ID or N/A | risk traceability |
| exception-id | exceptions | exception register ID or N/A | exception traceability |

## Discipline

- Do not invent one-off tag keys when an approved key exists.
- Temporary resources and exceptions require `expires-on`.
- Findings and evidence should carry `feature-id`, `control-id`, `risk-id`, or
  `exception-id` when applicable.
- Public examples must not contain real customer, tenant, credential, or private
  infrastructure values.
"""


def _default_control_applicability() -> str:
    return """# Control Applicability

| Domain | Applicable | Evidence |
|---|---:|---|
| AppSec | TBD | spec/plan/tasks |
| AI Security | TBD | threat model, evals, AIBOM |
| Agent Fleet / Orchestration | TBD | state graph, workflow evidence, approval records |
| Cloud/IaC | TBD | IaC scan, architecture notes |
| CSA CCM v4.1 | TBD | cloud control map, shared responsibility, cloud/IaC evidence |
| SOX 404 / ICFR | TBD | ITGC evidence, access/change/operations evidence |
| Supply Chain | TBD | SBOM, dependency scan, provenance |
| Compliance | TBD | evidence index, risk acceptance |
| Data Classification | TBD | data classification register, tagging taxonomy |
"""


def _default_evidence_index() -> str:
    return """# Evidence Index

| Evidence | Producer | Freshness | Location |
|---|---|---|---|
| Threat model | SicarioSpec / human reviewer | Per feature | docs/security/threat-model.md |
| Abuse cases | SicarioSpec / human reviewer | Per feature | docs/security/abuse-cases.md |
| Data classification | Maintainers / data owner | Per feature | docs/governance/data-classification.md |
| Tagging taxonomy | Maintainers | Per release | docs/governance/tagging-taxonomy.md |
| Control maps | Maintainers | Per release | docs/compliance/control-maps |
| Risk register | Maintainers | Per release | docs/risk/risk-register.md |
| Security exceptions | Security owner | Per exception | docs/risk/security-exceptions.md |
| Accepted risk log | Risk owner | Per exception | docs/risk/accepted-risk-log.md |
| Gate summary | sicario verify | Per run | generated/sicario/gate-summary.json |
| Spec run evidence | sicario verify | Per run | generated/sicario/spec-run-evidence.json |
"""


def _default_system_context() -> str:
    return """# System Context

Keep this document current when architecture, trust boundaries, external systems,
well-architected tradeoffs, control maps, risk registers, or high-impact
workflows change.

Source diagram: `docs/diagrams/system-context.mmd`
"""


def _default_system_context_diagram() -> str:
    return """flowchart LR
    User[User or Operator] --> App[Application / Service]
    App --> Gate[SicarioSpec Gates]
    Gate --> Evidence[(Evidence Artifacts)]
    App --> External[External Systems]
    Gate --> Docs[Docs Site]
"""


def _default_docs_impact() -> str:
    return """# Documentation Impact

Every implementation change must update internal docs, public docs, diagrams, or
record a no-docs-impact decision here.

| Date | Change | Docs Impact | Decision |
|---|---|---|---|
| TBD | Initial setup | Docs scaffold created | Update as project evolves |
"""


def _default_risk_register() -> str:
    return """# Risk Register

Track material security, privacy, compliance, operational, and AI/fleet risks.

| Risk ID | Status | Risk | Owner | Severity | Treatment | Evidence |
|---|---|---|---|---|---|---|
| No active risk | closed | Initial placeholder | Maintainers | low | Monitor | generated/sicario/gate-summary.json |
"""


def _default_security_exceptions() -> str:
    return """# Security Exceptions

Exceptions must be explicit, owned, time-bound, approved, and backed by a
compensating control. Permanent exceptions are not allowed.

| Exception ID | Status | Control / Gate | Owner | Expires | Approval | Compensating Control | Evidence |
|---|---|---|---|---|---|---|---|
| No active exception | closed | None | Maintainers | N/A | N/A | N/A | generated/sicario/gate-summary.json |
"""


def _default_accepted_risk_log() -> str:
    return """# Accepted Risk Log

Accepted risk requires a business owner, security reviewer, expiration date, and
revalidation evidence.

| Risk ID | Status | Risk | Business Owner | Security Reviewer | Expires | Rationale | Evidence |
|---|---|---|---|---|---|---|---|
| No active accepted risk | closed | None | Maintainers | Maintainers | N/A | N/A | generated/sicario/gate-summary.json |
"""


def iter_text_files(root: Path) -> Iterable[Path]:
    skip_dirs = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        "build",
        "dist",
        "generated",
        "sicario_spec.egg-info",
    }
    for dirpath, dirnames, filenames in os.walk(str(root)):
        dirnames[:] = [name for name in dirnames if name not in skip_dirs]
        current = Path(dirpath)
        for filename in filenames:
            path = current / filename
            if path.suffix in TEXT_SUFFIXES or path.name in TEXT_SUFFIXES:
                yield path


def _contains_any(text: str, phrases: Sequence[str]) -> bool:
    lower = text.lower()
    return any(phrase.lower() in lower for phrase in phrases)


def verify_project(path: Path, *, write: bool = True) -> List[Finding]:
    from sicario_cli.rules import RuleEngine

    root = path.resolve()
    findings: List[Finding] = []

    rule_dirs: List[Path] = [root / ".sicario" / "rules"]
    shipped = PRESETS_ROOT / "sicario-core" / "rules"
    if shipped.is_dir():
        rule_dirs.append(shipped)

    engine = RuleEngine()
    rule_results = engine.run(root, rule_dirs=rule_dirs)
    for r in rule_results:
        findings.append(Finding(r["severity"], r["code"], r["message"], r["path"]))

    selected_frameworks = _read_selected_frameworks(root)
    if selected_frameworks is not None:
        for key in selected_frameworks:
            filename = FRAMEWORK_IDS[key]
            present = (root / "docs" / "compliance" / "control-maps" / filename).exists() or (
                root / "control_maps" / filename
            ).exists()
            if not present:
                findings.append(
                    Finding(
                        "medium",
                        "SICARIO-MISSING-FRAMEWORK-MAP",
                        f"Selected framework '{key}' has no control map ({filename})",
                        f"docs/compliance/control-maps/{filename}",
                    )
                )

    if write:
        _write_evidence(root, findings)

    return findings


def _validate_active_risk_rows(root: Path, path: Path) -> List[Finding]:
    findings: List[Finding] = []
    text = path.read_text(encoding="utf-8")
    rel = str(path.relative_to(root))
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        lower = stripped.lower()
        if "| active |" not in lower:
            continue
        cells = [cell.strip().lower() for cell in stripped.strip("|").split("|")]
        bad_values = {"", "tbd", "n/a", "na", "none", "never", "permanent"}
        if any(cell in bad_values for cell in cells):
            findings.append(
                Finding(
                    "high",
                    "SICARIO-INCOMPLETE-ACTIVE-RISK",
                    "Active risk or exception row must have owner, expiration, approval/rationale, compensating control, and evidence",
                    f"{rel}:{line_number}",
                )
            )
    return findings


def _validate_spec_classification_and_tags(root: Path, path: Path, text: str) -> List[Finding]:
    findings: List[Finding] = []
    rel = str(path.relative_to(root))
    lower = text.lower()

    if "data classification" in lower:
        required_phrases = [
            "classification owner",
            "retention",
            "residency",
            "sharing",
            "redaction",
        ]
        missing = [phrase for phrase in required_phrases if phrase not in lower]
        has_level = any(level in lower for level in DATA_CLASSIFICATION_VALUES)
        if missing or not has_level:
            details = ", ".join(missing + ([] if has_level else ["classification level"]))
            findings.append(
                Finding(
                    "high",
                    "SICARIO-DATA-CLASSIFICATION-INCOMPLETE",
                    "Data classification must include owner, level, retention, residency, sharing, and redaction fields"
                    + (f": {details}" if details else ""),
                    rel,
                )
            )

    if "tagging discipline" in lower:
        required_tag_terms = ["owner", "system", "environment", "data-classification", "retention"]
        missing_tags = [tag for tag in required_tag_terms if tag not in lower]
        if missing_tags:
            findings.append(
                Finding(
                    "high",
                    "SICARIO-TAGGING-DISCIPLINE-INCOMPLETE",
                    "Tagging discipline must include owner, system, environment, data-classification, and retention tags",
                    rel,
                )
            )

    return findings


def _write_evidence(root: Path, findings: Sequence[Finding]) -> None:
    out_dir = root / "generated" / "sicario"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "generated_at_utc": _now(),
        "status": "pass" if not findings else "fail",
        "finding_count": len(findings),
        "findings": [finding.as_dict() for finding in findings],
    }
    (out_dir / "gate-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    evidence = {
        "generated_at_utc": _now(),
        "tool": "sicario verify",
        "evidence": [
            "docs/security/threat-model.md",
            "docs/security/abuse-cases.md",
            "docs/governance/data-classification.md",
            "docs/governance/tagging-taxonomy.md",
            "docs/compliance/control-applicability.md",
            "docs/compliance/evidence-index.md",
            "docs/compliance/control-maps",
            "docs/risk/risk-register.md",
            "docs/risk/security-exceptions.md",
            "docs/risk/accepted-risk-log.md",
            "generated/sicario/gate-summary.json",
        ],
    }
    (out_dir / "spec-run-evidence.json").write_text(
        json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
    )


def _sarif_output(findings: List[Finding]) -> str:
    """Convert findings to SARIF 2.1.0 format."""
    sarif_runs = {
        "version": "2.1.0",
        "$schema": "https://schemastore.astype.com/schemas/json/sarif-2.1.0-json-schema.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "SicarioSpec",
                        "informationUri": "https://github.com/anomalyco/sicario-spec",
                        "version": __version__,
                    }
                },
                "results": [
                    {
                        "ruleId": f.code,
                        "level": "error" if f.severity == "critical" else "warning",
                        "message": {"text": f.message},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": f.path},
                                }
                            }
                        ]
                        if f.path
                        else [],
                    }
                    for f in findings
                ],
            }
        ],
    }
    return json.dumps(sarif_runs, indent=2)


def verify_command(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()

    from sicario_cli.rules import RuleEngine, RuleValidationError

    rule_dirs = [root / ".sicario" / "rules"]

    if getattr(args, "validate_rules", False):
        engine = RuleEngine()
        errors: List[str] = []
        for rule_dir in rule_dirs:
            if not rule_dir.is_dir():
                continue
            for rule_file in sorted(rule_dir.rglob("*.rule.json")):
                try:
                    engine._load_rule_file(rule_file)
                except RuleValidationError as e:
                    errors.append(f"{rule_file}: {e}")
                except Exception as e:
                    errors.append(f"{rule_file}: unexpected error: {e}")
        if errors:
            for e in errors:
                print(e)
            print(f"rule validation failed with {len(errors)} error(s)")
            return 1
        print("all rules valid")
        return 0

    findings = verify_project(root, write=True)

    fmt = getattr(args, "format", "text")
    if fmt == "json":
        print(json.dumps([f.as_dict() for f in findings], indent=2))
    elif fmt == "sarif":
        print(_sarif_output(findings))
    else:
        for finding in findings:
            print(f"{finding.severity.upper()} {finding.code} {finding.path}: {finding.message}")
    if findings:
        print(f"sicario verify failed with {len(findings)} finding(s)")
        return 1
    print("sicario verify passed")
    return 0


def assess_command(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()
    findings = verify_project(root, write=True)
    report = root / "generated" / "sicario" / "assessment.md"
    lines = ["# SicarioSpec Assessment", "", f"Generated: {_now()}", ""]
    if findings:
        lines.append(f"Status: FAIL ({len(findings)} finding(s))")
        lines.append("")
        for finding in findings:
            lines.append(
                f"- **{finding.severity.upper()} {finding.code}** `{finding.path}` - {finding.message}"
            )
    else:
        lines.append("Status: PASS")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report)
    return 0 if not findings else 1


# Hook command -> how SicarioSpec can act on it.
# "deterministic" commands are backed by the CLI and run automatically.
# "agent" commands are prompt guidance for a coding agent; the runner reports
# them honestly instead of pretending to execute them.
HOOK_COMMAND_KIND = {
    "sicario.verify": "deterministic",
    "sicario.assess": "deterministic",
    "sicario.evidence": "deterministic",
    "sicario.threatmodel": "agent",
    "sicario.review": "agent",
    "sicario.controls": "agent",
    "sicario.apply-findings": "agent",
    "sicario.init": "agent",
}

HOOK_EVENTS = ["after_specify", "after_plan", "after_tasks"]


def _parse_hook_commands(extensions_yml: Path) -> "dict[str, List[str]]":
    """Extract ordered hook commands per event from .specify/extensions.yml.

    Uses a tiny, dependency-free line scanner (stdlib-only runtime constraint).
    Recognizes both the flat list form and the structured `command:` form.
    """
    events: "dict[str, List[str]]" = {event: [] for event in HOOK_EVENTS}
    if not extensions_yml.exists():
        return events
    current: Optional[str] = None
    in_hooks = False
    for raw in extensions_yml.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "hooks:":
            in_hooks = True
            continue
        if in_hooks and not line.startswith(" ") and stripped.endswith(":"):
            # A new top-level key ends the hooks block.
            in_hooks = False
        if not in_hooks:
            continue
        bare = stripped.rstrip(":")
        if bare in HOOK_EVENTS:
            current = bare
            continue
        if current is None:
            continue
        for token in stripped.replace("- ", " ").replace("command:", " ").split():
            if token in HOOK_COMMAND_KIND and token not in events[current]:
                events[current].append(token)
    return events


def _run_deterministic_hook(command: str, root: Path) -> int:
    if command == "sicario.verify":
        findings = verify_project(root, write=True)
        for finding in findings:
            print(f"  {finding.severity.upper()} {finding.code} {finding.path}: {finding.message}")
        return 1 if findings else 0
    if command in {"sicario.assess", "sicario.evidence"}:
        ns = argparse.Namespace(path=str(root))
        return assess_command(ns)
    return 0


def hooks_command(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()
    extensions_yml = root / ".specify" / "extensions.yml"
    events = _parse_hook_commands(extensions_yml)
    requested = [args.event] if args.event else HOOK_EVENTS
    exit_code = 0
    ran_any = False
    for event in requested:
        commands = events.get(event, [])
        if not commands:
            continue
        print(f"[{event}]")
        for command in commands:
            kind = HOOK_COMMAND_KIND.get(command, "agent")
            if kind == "deterministic":
                ran_any = True
                print(f"- run {command} (deterministic)")
                result = _run_deterministic_hook(command, root)
                if result != 0:
                    exit_code = 1
            else:
                print(
                    f"- {command} (agent guidance): see "
                    f".specify/extensions/sicario-guard/commands/{command}.md "
                    "— a coding agent performs this; the runner does not execute it"
                )
    if not ran_any and exit_code == 0:
        print("No deterministic hooks ran. Agent-guidance hooks are reported above.")
    return exit_code


def _interactive_init(target: Path) -> dict:
    """Run an interactive wizard to collect user choices for SicarioSpec init.

    Returns a dict with keys:
      - ``frameworks``: list of selected framework keys
      - ``data_classification``: chosen max classification level
      - ``cloud_providers``: list of selected cloud provider targets
    """
    print("SicarioSpec Interactive Setup")
    print("=" * 40)
    print("")

    # 1. Framework selection
    print("Step 1: Framework Selection")
    print("-" * 30)
    print("Choose which compliance frameworks apply to this project.")
    print("Enter the numbers separated by commas (e.g. 1,3,5) or 'all'.")
    print("Press Enter for none.")
    print("")
    sorted_keys = sorted(FRAMEWORK_IDS)
    for i, key in enumerate(sorted_keys, start=1):
        filename = FRAMEWORK_IDS[key]
        print(f"  {i:2d}. {key:20s} ({filename})")
    print("")
    frameworks_input = input("Frameworks (numbers, 'all', or empty): ").strip().lower()
    selected_frameworks: List[str] = []
    if frameworks_input == "all":
        selected_frameworks = list(FRAMEWORK_IDS)
    elif frameworks_input:
        for part in frameworks_input.split(","):
            part = part.strip()
            if part.isdigit():
                idx = int(part)
                if 1 <= idx <= len(sorted_keys):
                    key = sorted_keys[idx - 1]
                    if key not in selected_frameworks:
                        selected_frameworks.append(key)
            elif part in FRAMEWORK_IDS and part not in selected_frameworks:
                selected_frameworks.append(part)
    print(f"  Selected: {', '.join(selected_frameworks) if selected_frameworks else 'none'}")
    print("")

    # 2. Data classification boundary
    print("Step 2: Data Classification Boundary")
    print("-" * 30)
    print("What is the maximum data classification level for this project?")
    class_levels = ["public", "internal", "confidential", "restricted", "regulated"]
    for i, level in enumerate(class_levels, start=1):
        print(f"  {i}. {level}")
    classification_input = input("Choice (1-5, default 3): ").strip()
    if classification_input.isdigit():
        idx = int(classification_input)
        if 1 <= idx <= len(class_levels):
            data_classification = class_levels[idx - 1]
        else:
            data_classification = "confidential"
    else:
        data_classification = "confidential"
    print(f"  Selected: {data_classification}")
    print("")

    # 3. Cloud provider targets
    print("Step 3: Infrastructure / Cloud Provider Targets")
    print("-" * 30)
    print("Which cloud or infrastructure platforms does this project target?")
    print("Enter numbers separated by commas (e.g. 1,3) or empty for none.")
    cloud_options = [
        ("aws", "AWS CloudFormation / Terraform"),
        ("azure", "Azure Bicep / AVM / Terraform"),
        ("gcp", "Google Cloud Terraform"),
        ("kubernetes", "Kubernetes manifests / Helm"),
    ]
    for i, (key, label) in enumerate(cloud_options, start=1):
        print(f"  {i}. {label}")
    cloud_input = input("Choices (numbers or empty): ").strip()
    selected_cloud: List[str] = []
    if cloud_input:
        for part in cloud_input.split(","):
            part = part.strip()
            if part.isdigit():
                idx = int(part)
                if 1 <= idx <= len(cloud_options):
                    key = cloud_options[idx - 1][0]
                    if key not in selected_cloud:
                        selected_cloud.append(key)
    print(f"  Selected: {', '.join(selected_cloud) if selected_cloud else 'none'}")
    print("")

    config: dict = {
        "frameworks": selected_frameworks,
        "data_classification": data_classification,
        "cloud_providers": selected_cloud,
    }
    return config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sicario", description="Kill risk before it ships.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Initialize SicarioSpec in a project")
    init.add_argument("project", help="Target project directory")
    init.add_argument(
        "--integration", default="claude", choices=["claude", "codex", "copilot", "all", "generic"]
    )
    init.add_argument("--profile", default="public-core", help="Comma-separated profile list")
    init.add_argument(
        "--frameworks",
        default=None,
        help="Comma-separated control-map frameworks this project enforces "
        f"(known: {', '.join(sorted(FRAMEWORK_IDS))}; or 'all'). Writes "
        ".sicario/frameworks.txt, which `sicario verify` honors so you enforce "
        "only the frameworks you chose. Default: the profile's framework set.",
    )
    speckit_group = init.add_mutually_exclusive_group()
    speckit_group.add_argument(
        "--apply-to-speckit",
        dest="apply_to_speckit",
        action="store_true",
        default=True,
        help="Write the selected governance into the live Spec Kit paths "
        "(.specify/templates/ and .specify/memory/constitution.md) so /speckit-* commands use it (default).",
    )
    speckit_group.add_argument(
        "--no-apply-to-speckit",
        dest="apply_to_speckit",
        action="store_false",
        help="Only stage presets under .specify/presets/ without overwriting live Spec Kit templates/constitution.",
    )
    init.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the per-file adoption report (created/merged-overlaid/preserved) and write nothing.",
    )
    init.add_argument(
        "--force",
        action="store_true",
        help="Full-overwrite opt-in: replace existing files with SicarioSpec templates "
        "(a timestamped *.sicario-bak backup is taken first). Default is brownfield-safe "
        "merge/overlay/preserve.",
    )
    init.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Interactive wizard: prompts for framework selection, data classification boundary, "
        "and cloud provider targets, then writes .sicario/config.json.",
    )
    init.set_defaults(func=init_project)

    verify = sub.add_parser("verify", help="Run deterministic SicarioSpec gates")
    verify.add_argument("path", nargs="?", default=".")
    verify.add_argument(
        "--format",
        default="text",
        choices=["text", "json", "sarif"],
        help="Output format (default: text)",
    )
    verify.add_argument(
        "--validate-rules",
        action="store_true",
        help="Validate all rule files instead of running checks",
    )
    verify.set_defaults(func=verify_command)

    assess = sub.add_parser("assess", help="Write a repo posture assessment")
    assess.add_argument("path", nargs="?", default=".")
    assess.set_defaults(func=assess_command)

    hooks = sub.add_parser(
        "hooks",
        help="Run deterministic Spec Kit hooks from .specify/extensions.yml; report agent-guidance hooks honestly",
    )
    hooks.add_argument("path", nargs="?", default=".")
    hooks.add_argument(
        "--event",
        choices=HOOK_EVENTS,
        help="Run a single hook event (default: all). One of after_specify, after_plan, after_tasks.",
    )
    hooks.set_defaults(func=hooks_command)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
