"""Command line entrypoint for SicarioSpec.

The CLI intentionally uses only the Python standard library. SicarioSpec should
be installable and testable in constrained environments without pulling a
dependency graph before the governance gates are active.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import sysconfig
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.resources import files as package_files
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from sicario_cli._render import (
    FileReport,
    _copy_tree,
    _ensure_gitignore_rule,
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


@dataclass(frozen=True)
class AssetRootResolution:
    """How the asset root was chosen, captured for gate evidence.

    ``SICARIO_ASSET_ROOT`` is a legitimate feature (relocated installs, test
    fixtures), but it also lets a decoy directory carrying ``presets/`` and
    ``extensions/`` — with a partial or empty rules tree — silently replace the
    shipped rule set while the gate still looks populated. An env var that
    silently swaps the rule set is indistinguishable from an attack, so a
    redirected gate must not present as a normal one: the resolution is
    recorded in ``scan_coverage`` and a redirect raises a finding.
    """

    #: The asset root actually used for this process (rules load from here).
    root: Path
    #: ``root`` resolved at construction time — symlinks and cwd-relative
    #: spellings pinned to one absolute path while the resolution-time cwd is
    #: still in effect. This is what evidence records: a raw relative env value
    #: like ``decoyA`` is not reproducible evidence on its own.
    resolved_root: Path
    #: Raw ``SICARIO_ASSET_ROOT`` value observed at resolution time, or None.
    env_value: Optional[str]
    #: True when the env var was set AND its directory won the candidate race.
    env_honored: bool
    #: The root that would have won with the env var unset.
    default_root: Path

    @property
    def redirected(self) -> bool:
        """True when the env var actually changed which root was used.

        Path identity, not content, is the criterion: pointing the env var at
        a byte-identical copy of the real assets still counts as a redirect,
        because the SOURCE of the gate's rules moved and a reviewer must see
        that. Pointing it at the root that would win anyway is a no-op and is
        not a redirect.

        DIRECTORY identity is inode identity where the filesystem can say so:
        on a case-insensitive filesystem (macOS APFS default) a case-variant
        spelling of the default root names the SAME directory, and resolve()
        does not fold case, so a pure resolved-path comparison fired a false
        redirect. ``os.path.samefile`` compares the actual directories; the
        resolved-path comparison remains only as the fallback when either side
        does not exist (samefile raises there), where it still keeps symlinked
        spellings of one directory from reading as a move.
        """
        if not self.env_honored:
            return False
        try:
            return not os.path.samefile(self.resolved_root, self.default_root)
        except OSError:
            return self.resolved_root != self.default_root.resolve()


def _has_asset_layout(candidate: Path) -> bool:
    return (candidate / "presets").exists() and (candidate / "extensions").exists()


def _resolve_asset_root() -> AssetRootResolution:
    """Resolve the asset root, keeping provenance for evidence.

    Selection behavior is unchanged from the original ``_asset_root``: the env
    var candidate races first, then the repo checkout, packaged assets, and the
    sysconfig share directory; ``REPO_ROOT`` is the fallback. What is new is
    that the losing default is computed alongside, so callers can tell whether
    the env var merely named the winner or actually replaced it.
    """
    env_value = os.environ.get("SICARIO_ASSET_ROOT")
    default_candidates = [
        REPO_ROOT,
        Path(str(package_files("sicario_cli").joinpath("assets"))),
        Path(sysconfig.get_path("data")) / "share" / "sicario-spec",
    ]
    default_root = next((c for c in default_candidates if _has_asset_layout(c)), REPO_ROOT)
    root = default_root
    env_honored = False
    if env_value:
        env_candidate = Path(env_value).expanduser()
        if _has_asset_layout(env_candidate):
            root = env_candidate
            env_honored = True
    return AssetRootResolution(
        root=root,
        resolved_root=root.resolve(),
        env_value=env_value,
        env_honored=env_honored,
        default_root=default_root,
    )


# Resolved once at import time; every module global below derives from it, and
# rules are loaded from PRESETS_ROOT, so the evidence written by
# ``verify_project`` records THIS snapshot — the root the run actually used —
# rather than re-reading the environment later and possibly describing a root
# the rules never came from.
ASSET_ROOT_RESOLUTION = _resolve_asset_root()
ASSET_ROOT = ASSET_ROOT_RESOLUTION.root
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
# SicarioSpec ships 14 control-map frameworks. By default a project does not
# have to enforce all of them — that would punish a team that only owes evidence
# for, say, ISO 27001 and HIPAA. The framework selector lets a project declare
# which subset applies. The declaration lives in a plain-text project config file
# (`.sicario/frameworks.txt`, one framework key per line). `sicario verify` reads
# it and, when present, fails if any SELECTED framework's control map is absent
# (SICARIO-MISSING-FRAMEWORK-MAP) — so a team enforces exactly the frameworks it
# chose, not all 14 and not none.
#
# Backward-compatible by construction: with NO config file, no framework is
# selected and SICARIO-MISSING-FRAMEWORK-MAP cannot fire.
#
# SICARIO-MISSING-CONTROL-MAPS is a DIFFERENT check and is not conditional on
# any of this — it is shipped rule 020, a file-glob over
# docs/compliance/control-maps/*, and it runs on every project regardless of the
# selector. An earlier version of this comment implied the selector governed it,
# and that error propagated into USAGE.md and README, where it told readers the
# gate would accept a `control_maps/` layout it in fact rejects.

# Short, stable selector key -> shipped control-map filename.
FRAMEWORK_IDS = {
    "ccm": "ccm-v4.1-sicario.json",
    "sox": "sox-404-itgc-sicario.json",
    "soc2": "soc2-trust-services-sicario.json",
    "fedramp": "fedramp-rev5-sicario.json",
    "bsi-c5": "bsi-c5-2026-sicario.json",
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

# Framework maturity tiers.
#
# All 14 maps are coarse traceability aids, not certification artifacts. But they
# are not equally substantial, and presenting them as peers means the weakest map
# sets the credibility of the whole set. These three fall measurably short of the
# rest — PCI DSS resolves ~29% of its evidence to bare directory names and covers
# 12 requirements against ~300 sub-requirements; NIST AI RMF's "GOVERN 1" labels
# are function names rather than real subcategory IDs; OWASP ASVS ships 3 entries
# and 7 evidence references covering roughly a fifth of the standard.
#
# EXPERIMENTAL maps remain fully installable and are still enforced by
# `sicario verify` when explicitly selected via `--frameworks`. The only
# behavioral difference is that they are never selected implicitly: they are
# excluded from per-profile defaults, so a team opts into them deliberately.
EXPERIMENTAL_FRAMEWORKS = {"pci-dss", "ai-rmf", "owasp-asvs"}
SUPPORTED_FRAMEWORKS = [k for k in FRAMEWORK_IDS if k not in EXPERIMENTAL_FRAMEWORKS]


def _framework_label(key: str) -> str:
    """Render a framework key with its tier, so experimental never passes silently."""
    return f"{key} (experimental)" if key in EXPERIMENTAL_FRAMEWORKS else key


# The project config file that records the selected subset (one key per line).
FRAMEWORKS_CONFIG = Path(".sicario") / "frameworks.txt"

# Default framework subset per profile. The default = the profile's natural set
# (`public-core` carries no compliance obligation; compliance-shaped profiles
# carry the maps they imply). This table states what a profile is ABOUT;
# _default_frameworks_for_profiles filters experimental keys at its single choke
# point, so the EFFECTIVE default for `enterprise-strict` is the 11 supported
# maps, never all 14 — experimental maps require explicit --frameworks.
PROFILE_FRAMEWORKS = {
    "compliance": ["ccm", "sox", "soc2", "iso27001", "nist-800-53"],
    "saas": ["ccm", "soc2", "iso27001", "ai-rmf"],
    "ai-system": ["ai-rmf", "eu-ai-act"],
    "agent-fleet": ["ai-rmf", "eu-ai-act"],
    "cloud-iac": ["ccm", "fedramp", "bsi-c5", "nist-800-53"],
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
            supported = ", ".join(sorted(SUPPORTED_FRAMEWORKS))
            experimental = ", ".join(sorted(EXPERIMENTAL_FRAMEWORKS))
            raise SystemExit(
                f"Unknown framework(s): {name}. "
                f"Supported: {supported}. Experimental: {experimental}."
            )
        if name not in selected:
            selected.append(name)
    return selected


def _default_frameworks_for_profiles(profile_names: Sequence[str]) -> List[str]:
    """Compute the default framework subset from the selected profile name(s).

    EXPERIMENTAL maps are filtered out here rather than being removed from
    ``PROFILE_FRAMEWORKS``: the table keeps stating which frameworks a profile is
    *about*, and this single choke point guarantees none of them can be enforced
    without someone naming it explicitly on ``--frameworks``.
    """
    selected: List[str] = []
    for name in profile_names:
        for key in PROFILE_FRAMEWORKS.get(name, []):
            if key in EXPERIMENTAL_FRAMEWORKS:
                continue
            if key not in selected:
                selected.append(key)
    return selected


def _frameworks_config_content(frameworks: Sequence[str]) -> str:
    header = (
        "# SicarioSpec framework selector (#18).\n"
        "# One framework key per line. `sicario verify` requires a control map\n"
        "# for each key listed here (SICARIO-MISSING-FRAMEWORK-MAP if absent).\n"
        "# Remove this file to fall back to the default coarse control-map check.\n"
        f"# Supported keys: {', '.join(sorted(SUPPORTED_FRAMEWORKS))}\n"
        f"# Experimental keys: {', '.join(sorted(EXPERIMENTAL_FRAMEWORKS))}\n"
        "#   Experimental maps are thinner than the supported set. They are\n"
        "#   enforced exactly like any other key when listed here, but are never\n"
        "#   selected by a profile default -- only by explicit --frameworks.\n"
    )
    # Key lines stay bare so the reader stays a plain one-key-per-line parse; the
    # experimental call-out belongs in the header, not appended to a key.
    experimental = [k for k in frameworks if k in EXPERIMENTAL_FRAMEWORKS]
    if experimental:
        header += f"# This project explicitly enforces experimental: {', '.join(experimental)}\n"
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

# NOTE: DATA_CLASSIFICATION_VALUES used to live here; it served only the
# deleted `_validate_spec_classification_and_tags` (see the note above
# `_write_evidence`). The live copy is `_DATA_CLASSIFICATION_VALUES` in
# sicario_cli/rules/kinds/classification_complete.py, next to the rule kind
# that actually enforces it.

# NOTE: SECRET_PATTERNS, AI_KEYWORDS and FLEET_KEYWORDS used to live here. The
# 0.5.0 rule-engine migration moved every check into declarative `.rule.json`
# files, but left these constants behind with no remaining reference. Three of
# the four secret patterns (AWS access key ids, `sk-` provider tokens, and
# private key blocks) were therefore enforced by nothing while the docs still
# claimed coverage. They now ship as rules 041-043 in
# presets/sicario-core/rules/, which is the only place a check should live.

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
    """Ingest third-party scanner output. NOT WIRED IN — see the warning below.

    Nothing calls this. Before wiring it into ``verify_project``, note that
    ``_parse_semgrep_json`` and ``_parse_sarif`` build findings from the
    third-party tool's ``message.text``, and scanners routinely put matched
    source snippets there. Those findings flow into
    ``generated/sicario/gate-summary.json``, so enabling this as written would
    import scanned source text — potentially a live credential — straight into
    the evidence artifact, breaching the no-secret-echo property that
    specs/006 SEC-002 establishes for the native evaluators.

    Wiring it in therefore requires discarding or sanitising the third-party
    message rather than copying it through.
    """
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
    #: One-based line of the occurrence, when the producing rule kind has a
    #: line concept. Kinds with no line concept leave it unset and the finding
    #: is a file-scoped location (FR-006). The line is a distinct value and is
    #: never packed into ``path``, so ``path`` stays a resolvable file
    #: reference for SARIF consumers (FR-005).
    line: Optional[int] = None

    @property
    def location(self) -> str:
        """Human-readable location in the repository's ``path:line`` convention.

        For human output only (FR-007). Machine formats carry the path and the
        line as separate values.
        """
        if self.line is None or not self.path:
            return self.path
        return f"{self.path}:{self.line}"

    def as_dict(self) -> dict:
        data: dict = {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "path": self.path,
        }
        if self.line is not None:
            data["line"] = self.line
        return data


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


def _init_existing_governance(target: Path) -> "dict[str, List[str]]":
    """Detect existing governance, or the greenfield empty shape for a fresh target."""
    if target.exists():
        return detect_existing_governance(target)
    return {"constitution": [], "templates": [], "instructions": [], "mission": []}


def _init_apply_interactive(
    args: argparse.Namespace, actions: List[str], selected_presets: List[str]
) -> "tuple[Optional[dict], List[str]]":
    """Run the interactive wizard (if requested) and fold its choices into args/presets."""
    if not getattr(args, "interactive", False):
        return None, selected_presets
    interactive_config = _interactive_init()
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
    return interactive_config, selected_presets


def _init_report_header(
    target: Path,
    args: argparse.Namespace,
    selected_presets: List[str],
    existing: "dict[str, List[str]]",
    actions: List[str],
) -> None:
    """Append the target/specify/integration/preset/mode summary lines."""
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


def _init_write_framework_selection(
    target: Path, args: argparse.Namespace, actions: List[str], reports: List[FileReport]
) -> None:
    """Resolve and persist the project's framework selector (#18).

    Explicit ``--frameworks`` wins; otherwise default to the profile's set. When
    neither yields a selection (e.g. bare public-core), no config is written so
    verify keeps its legacy coarse control-map behavior.
    """
    if getattr(args, "frameworks", None):
        selected_frameworks = _parse_frameworks(args.frameworks)
    else:
        selected_frameworks = _default_frameworks_for_profiles(_parse_profile_names(args.profile))
    if not selected_frameworks:
        actions.append("frameworks (none selected; default coarse control-map check)")
        return
    # An existing selector is preserved rather than clobbered (brownfield-safe),
    # so on a re-run the set we just computed may NOT be the set that is
    # enforced. Report what will actually be enforced — a project that selected
    # an experimental framework before it was tiered keeps enforcing it, and
    # printing the computed defaults instead would state the opposite.
    existing_selection = _read_selected_frameworks(target) if not args.force else None
    effective = existing_selection if existing_selection is not None else selected_frameworks
    actions.append(f"frameworks {', '.join(_framework_label(k) for k in effective)}")
    if existing_selection is not None and set(existing_selection) != set(selected_frameworks):
        actions.append(
            "frameworks: existing .sicario/frameworks.txt preserved; it differs from this "
            "profile's defaults. Re-run with --force or edit the file to adopt them."
        )
    _write_text(
        target / FRAMEWORKS_CONFIG,
        _frameworks_config_content(selected_frameworks),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
        reports=reports,
    )


def _init_write_interactive_config(
    target: Path,
    args: argparse.Namespace,
    interactive_config: Optional[dict],
    actions: List[str],
    reports: List[FileReport],
) -> None:
    """Persist the interactive wizard's answers to .sicario/config.json, if run."""
    if interactive_config is None:
        return
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


def _init_write_preset_content(
    target: Path,
    args: argparse.Namespace,
    selected_presets: List[str],
    deferrals: List[str],
    actions: List[str],
    reports: List[FileReport],
) -> None:
    """Delegate generated content (docs, integrations, workflows) to presets."""
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


def init_project(args: argparse.Namespace) -> int:
    target = Path(args.project).expanduser().resolve()
    actions: List[str] = []
    reports: List[FileReport] = []
    selected_presets = _parse_profiles(args.profile)

    # Brownfield-safe adoption is the DEFAULT: a non-empty target is fine. We
    # detect any existing governance and merge/overlay/preserve instead of
    # clobbering. `--force` is the explicit full-overwrite opt-in.
    existing = _init_existing_governance(target)
    # The constitution overlay must defer to any mission.md / project-supremacy
    # instruction file we found.
    deferrals = existing["mission"] + existing["instructions"]

    interactive_config, selected_presets = _init_apply_interactive(args, actions, selected_presets)

    _init_report_header(target, args, selected_presets, existing, actions)

    if not args.dry_run:
        target.mkdir(parents=True, exist_ok=True)

    # Ensure backups are unstageable BEFORE the first one is written. Brownfield
    # adoption backs up the target's own constitution/instructions/templates, which
    # may contain secrets; the ignore rule must land ahead of that, not after.
    _ensure_gitignore_rule(
        target,
        dry_run=args.dry_run,
        actions=actions,
        reports=reports,
    )

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
    _init_write_framework_selection(target, args, actions, reports)

    _init_write_interactive_config(target, args, interactive_config, actions, reports)

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
    _init_write_preset_content(target, args, selected_presets, deferrals, actions, reports)

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
| compliance-scope | scoped artifacts | none, sox, ccm, soc2, fedramp, bsi-c5, pci, hipaa, gdpr, ai-rmf, other | control mapping |
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
| AppSec | Applicable | spec/plan/tasks |
| AI Security | Applicable | threat model, evals, AIBOM |
| Agent Fleet / Orchestration | Applicable | state graph, workflow evidence, approval records |
| Cloud/IaC | Applicable | IaC scan, architecture notes |
| CSA CCM v4.1 | Applicable | cloud control map, shared responsibility, cloud/IaC evidence |
| SOX 404 / ICFR | Applicable | ITGC evidence, access/change/operations evidence |
| Supply Chain | Applicable | SBOM, dependency scan, provenance |
| Compliance | Applicable | evidence index, risk acceptance |
| Data Classification | Applicable | data classification register, tagging taxonomy |
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
| $(date +%Y-%m-%d) | Initial setup | Docs scaffold created | Update as project evolves |
"""


def _default_risk_register() -> str:
    return """# Risk Register

Track material security, privacy, compliance, operational, and AI/fleet risks.

| Risk ID | Status | Risk | Owner | Severity | Treatment | Evidence |
|---|---|---|---|---|---|---|
| RISK-001 | open | Bootstrap overwrites uncommitted user changes | Maintainers | Medium | Mitigated: dry-run, backups, --force guard | generated/sicario/gate-summary.json |
| RISK-002 | open | AI spec omits prompt-injection guardrails | Maintainers | High | Mitigated: verify rejects AI specs without guardrails | generated/sicario/gate-summary.json |
| RISK-003 | open | Hardcoded credentials shipped in governed repo | Maintainers | Critical | Mitigated: secret scan in verify gate | generated/sicario/gate-summary.json |
"""


def _default_security_exceptions() -> str:
    return """# Security Exceptions

Exceptions must be explicit, owned, time-bound, approved, and backed by a
compensating control. Permanent exceptions are not allowed.

| Exception ID | Status | Control / Gate | Owner | Expires | Approval | Compensating Control | Evidence |
|---|---|---|---|---|---|---|---|
| EXC-001 | open | SICARIO-MISSING-THREAT-MODEL — threat-model section required | Maintainers | 2027-01-01 | TBD | External threat-modeling process documented | generated/sicario/gate-summary.json |
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


def _rule_sources(root: Path) -> "tuple[List[Path], List[str]]":
    """The ordered rule directories `sicario verify` loads, with their labels.

    ORDER IS THE POLICY. `RuleEngine.load_rules` has exactly one precedence
    rule — the last file loaded wins for a given `id` — so the target project's
    `.sicario/rules/` is returned LAST, on purpose, and must stay last.

    That is what makes the documented capability real: a project can narrow or
    disable a shipped rule by reusing its id, without editing the package. With
    the two entries swapped, the shipped rule wins instead and a project cannot
    override anything at all — which is exactly the defect this ordering fixes,
    so do not "tidy" the project directory back to the front.

    Overriding a shipped rule is legitimate and never fails the gate on its own.
    It is also how someone could switch off the secret scan, so every override
    is recorded in `scan_coverage.overrides` in the evidence artifact. Visibility
    is the control here, not prohibition.
    """
    rule_dirs: List[Path] = []
    origins: List[str] = []
    shipped = PRESETS_ROOT / "sicario-core" / "rules"
    if shipped.is_dir():
        rule_dirs.append(shipped)
        origins.append("shipped")
    rule_dirs.append(root / ".sicario" / "rules")
    origins.append("project")
    return rule_dirs, origins


def _no_rules_loaded_findings(rule_report, rule_dirs: List[Path]) -> List[Finding]:
    """Fail closed when nothing loaded.

    A run with zero rules cannot fail, so it reports "passed" over any
    repository at all. That is not hypothetical: the packaged build resolved
    its asset root to a tree with no rules/ directory, so every pip-installed
    deployment enforced nothing while printing "sicario verify passed" — and a
    wheel smoke test read that as healthy. A gate that enforces nothing must
    say so rather than agreeing with you.
    """
    if rule_report.loaded_rule_ids:
        return []
    return [
        Finding(
            "critical",
            "SICARIO-NO-RULES-LOADED",
            "No rules were loaded, so this run enforced nothing. A passing verdict "
            f"here means only that no checks ran. Searched: "
            f"{', '.join(str(d) for d in rule_dirs) or '(none)'}",
            ".sicario/rules",
        )
    ]


def _rule_load_error_findings(rule_report, root: Path) -> List[Finding]:
    """Turn each rule file that failed to load into a critical finding.

    A rule file that could not be loaded is a gap in enforcement, so it is a
    critical finding rather than a stderr warning: a cap of 0 on the
    secret-scan rule would otherwise drop it silently and turn a repository
    full of live credentials into a clean gate result.

    Two details an earlier version got wrong. The path was hardcoded to
    `.sicario/rules/`, which misattributed a broken SHIPPED rule to the
    project. And the message always said "did not run", which is false when a
    valid definition of the same id loaded from the other directory — the
    common case, since `init` copies every shipped rule into the project.
    """
    enforced_ids = set(rule_report.loaded_rule_ids)
    findings: List[Finding] = []
    for err in rule_report.load_errors:
        rule_id = err.get("rule_id")
        named = rule_id or err["file"]
        origin = err.get("origin", "project")
        still_enforced = bool(rule_id) and rule_id in enforced_ids
        if still_enforced:
            detail = (
                f"Rule file for '{named}' was rejected and is not in effect "
                f"({origin} copy); another definition of this rule is still enforced"
            )
        else:
            detail = f"Rule '{named}' did not run"
        raw_path = err.get("path")
        if raw_path:
            candidate = Path(raw_path)
            try:
                # Repo-relative POSIX, matching every other finding location.
                location = candidate.relative_to(root).as_posix()
            except ValueError:
                # A shipped rule lives outside the scanned tree; name it plainly
                # rather than emitting an absolute path or a bogus relative one.
                location = f"<shipped>/{candidate.name}"
        else:
            location = f".sicario/rules/{err['file']}"
        findings.append(
            Finding("critical", err["code"], f"{detail}: {'; '.join(err['errors'])}", location)
        )
    return findings


def _asset_root_override_findings() -> List[Finding]:
    """Flag a SICARIO_ASSET_ROOT redirect as a finding, never silently.

    An env var that silently swaps the rule set is indistinguishable from an
    attack — a decoy asset root with a PARTIAL rule set weakens enforcement
    while looking populated, and the zero-rules fail-closed check cannot see
    it. The env var stays a legitimate feature; the control is visibility, so
    a redirected gate must not present as a normal one. This fires only when
    SICARIO_ASSET_ROOT actually changed which root won the race — naming the
    root that would win anyway stays silent. No path is attached: the
    redirected root lives outside the scanned tree, and the message carries
    both paths.
    """
    if not ASSET_ROOT_RESOLUTION.redirected:
        return []
    return [
        Finding(
            "medium",
            "SICARIO-ASSET-ROOT-OVERRIDE",
            "SICARIO_ASSET_ROOT redirected this gate's rule source: rules were "
            f"loaded from '{ASSET_ROOT_RESOLUTION.resolved_root}' instead of the default "
            f"'{ASSET_ROOT_RESOLUTION.default_root}'. This finding fails the run "
            "by design — a redirected rule source is indistinguishable from a "
            "tampered one until a reviewer confirms it. See "
            "scan_coverage.asset_root in the evidence for the resolution record.",
        )
    ]


def _missing_framework_map_findings(root: Path, selected_frameworks: Optional[List[str]]) -> List[Finding]:
    """One finding per selected framework whose control map is absent."""
    if selected_frameworks is None:
        return []
    findings: List[Finding] = []
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
    return findings


def verify_project(path: Path, *, write: bool = True) -> List[Finding]:
    from sicario_cli.rules import RuleEngine

    root = path.resolve()
    findings: List[Finding] = []

    rule_dirs, rule_origins = _rule_sources(root)

    engine = RuleEngine()
    rule_report = engine.run_detailed(root, rule_dirs=rule_dirs, origins=rule_origins)

    findings.extend(_no_rules_loaded_findings(rule_report, rule_dirs))
    findings.extend(_rule_load_error_findings(rule_report, root))
    findings.extend(_asset_root_override_findings())

    for r in rule_report.findings:
        findings.append(Finding(r["severity"], r["code"], r["message"], r["path"], r.get("line")))

    selected_frameworks = _read_selected_frameworks(root)
    findings.extend(_missing_framework_map_findings(root, selected_frameworks))

    if write:
        _write_evidence(root, findings, scan_coverage=_scan_coverage(rule_report))

    return findings


def _scan_coverage(rule_report) -> dict:
    """Build the coverage record written into gate evidence.

    Records per-rule scan coverage and truncation counts (FR-020), the
    effective skipped-path set (FR-021, SEC-010), rules loaded but disabled
    (FR-022), and every shipped rule a project rule replaced by reusing its id.
    Evidence only: nothing here feeds the verdict.

    `overrides` sits next to `disabled_rules` because the two answer different
    questions. `disabled_rules` says which rules did not run. `overrides` says
    who changed them, from which file, and what changed — including the case a
    reviewer most needs to catch, a project rule turning off a shipped
    `critical` rule, which carries `impact: "disables-critical-severity-rule"`.

    `asset_root` records WHERE the shipped rules came from: the resolved asset
    root, the raw `SICARIO_ASSET_ROOT` value as given (`env_value`, possibly
    relative), whether the env var was set and honored, whether it actually
    redirected resolution, and the shipped-rules directory with its top-level
    rule-file count (the same non-recursive glob the loader uses). Without
    this, a decoy asset root that drops the shipped rules leaves no trace in
    evidence at all. Existing keys keep their names, types, and meanings;
    `asset_root` is additive.
    """
    from sicario_cli.rules.kinds.regex_forbidden import SKIPPED_DIR_NAMES

    shipped_rules_dir = PRESETS_ROOT / "sicario-core" / "rules"
    return {
        "skipped_path_set": sorted(SKIPPED_DIR_NAMES),
        "rules": rule_report.coverage,
        "disabled_rules": rule_report.disabled_rules,
        "overrides": rule_report.overrides,
        "asset_root": {
            # The RESOLVED absolute path — a relative env value like `decoyA`
            # recorded verbatim is not reproducible evidence. `env_value` below
            # keeps the raw value as given, so the evidence shows both what was
            # asked and what it meant.
            "path": str(ASSET_ROOT_RESOLUTION.resolved_root),
            "env_value": ASSET_ROOT_RESOLUTION.env_value,
            "env_override_set": ASSET_ROOT_RESOLUTION.env_value is not None,
            "env_override_honored": ASSET_ROOT_RESOLUTION.env_honored,
            "redirected_by_env": ASSET_ROOT_RESOLUTION.redirected,
            "shipped_rules_dir": str(shipped_rules_dir),
            "shipped_rule_file_count": (
                len(list(shipped_rules_dir.glob("*.rule.json")))
                if shipped_rules_dir.is_dir()
                else 0
            ),
        },
    }


# NOTE: `_validate_spec_classification_and_tags` used to live here. It was
# never called after the 0.5.0 rule-engine migration — its two codes
# (SICARIO-DATA-CLASSIFICATION-INCOMPLETE, SICARIO-TAGGING-DISCIPLINE-INCOMPLETE)
# are enforced by shipped rules 080/081 in presets/sicario-core/rules/. Keeping
# an uncalled Python twin alongside the declarative rules was two sources of
# truth for one check — a drift trap — so it was deleted rather than kept.


def _write_evidence(
    root: Path, findings: Sequence[Finding], scan_coverage: Optional[dict] = None
) -> None:
    out_dir = root / "generated" / "sicario"
    out_dir.mkdir(parents=True, exist_ok=True)
    # Additions here are additive only: `status`, `finding_count`, and
    # `findings` keep their names, types, and meanings. `finding_count` still
    # means "number of findings" — it is simply larger now that every
    # occurrence is reported (FR-023, FR-024).
    summary = {
        "generated_at_utc": _now(),
        "status": "pass" if not findings else "fail",
        "finding_count": len(findings),
        "findings": [finding.as_dict() for finding in findings],
    }
    if scan_coverage is not None:
        summary["scan_coverage"] = scan_coverage
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


def _finding_line(finding: Finding) -> str:
    """Render one finding for human output.

    Located findings read in the repository's existing ``path:line``
    convention (FR-007). A finding with no path — the overflow finding is the
    only one — omits the location segment rather than leaving a gap.
    """
    location = finding.location
    where = f" {location}" if location else ""
    return f"{finding.severity.upper()} {finding.code}{where}: {finding.message}"


def _physical_location(finding: Finding) -> dict:
    """SARIF physicalLocation for a finding.

    The artifact location is the clean repository-relative path with no
    positional suffix, so a code-scanning platform can resolve it; the line
    goes in the region's start line (FR-008).
    """
    location: dict = {"artifactLocation": {"uri": finding.path}}
    if finding.line is not None:
        location["region"] = {"startLine": finding.line}
    return location


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
                        "locations": [{"physicalLocation": _physical_location(f)}]
                        if f.path
                        else [],
                    }
                    for f in findings
                ],
            }
        ],
    }
    return json.dumps(sarif_runs, indent=2)


def _validate_rules_command(root: Path) -> int:
    """Implement ``sicario verify --validate-rules``: lint rule files without running them.

    This previously called `engine._load_rule_file(...)`, but
    `_load_rule_file` is a module-level function in rules.engine, not a
    method — so every rule file raised AttributeError and reported as an
    error, valid or not, and `_validate_rule` was never reached. The one
    control that catches a malformed rule before a run was inert.
    """
    from sicario_cli.rules.engine import _load_rule_file, _validate_rule

    # Same sources as a real run, so validation never clears a set of files
    # the gate would not actually load. Order is irrelevant here — every
    # file is validated on its own — but sharing one definition keeps the
    # two paths from drifting apart.
    rule_dirs, _ = _rule_sources(root)

    errors: List[str] = []
    unreachable: List[Path] = []
    checked = 0
    for rule_dir in rule_dirs:
        if not rule_dir.is_dir():
            continue
        # Non-recursive, matching `load_rules`, which globs a single level.
        # Validating recursively would clear rule files the gate never loads,
        # reporting "valid" for a rule that silently does not run.
        for rule_file in sorted(rule_dir.glob("*.rule.json")):
            checked += 1
            data = _load_rule_file(rule_file)
            if data is None:
                errors.append(f"{rule_file}: not readable, decodable, or a JSON object")
                continue
            for message in _validate_rule(data):
                errors.append(f"{rule_file}: {message}")
        # Matching the loader is necessary but not sufficient: a rule file in
        # a subdirectory would now get no signal from either side. Silence is
        # the failure mode this gate exists to avoid, so name them.
        unreachable.extend(
            p for p in sorted(rule_dir.rglob("*.rule.json")) if p.parent != rule_dir
        )

    for path in unreachable:
        print(
            f"{path}: ignored — rule files load only from the top level of a "
            "rules directory, not from subdirectories"
        )
    if errors:
        for e in errors:
            print(e)
        print(f"rule validation failed with {len(errors)} error(s) across {checked} file(s)")
        return 1
    suffix = f"; {len(unreachable)} ignored in subdirectories" if unreachable else ""
    print(f"all rules valid ({checked} file(s){suffix})")
    return 0


def _print_verify_findings(findings: List[Finding], fmt: str) -> bool:
    """Print findings in the requested format; return whether it is machine-readable.

    The summary is a human diagnostic, not part of the payload. Printing it to
    stdout after a JSON or SARIF document made that document unparseable —
    `verify --format sarif | jq` failed outright, on passing runs as well as
    failing ones. stdout carries the artifact; stderr carries the commentary.
    """
    machine_readable = fmt in ("json", "sarif")
    if fmt == "json":
        print(json.dumps([f.as_dict() for f in findings], indent=2))
    elif fmt == "sarif":
        print(_sarif_output(findings))
    else:
        for finding in findings:
            print(_finding_line(finding))
    return machine_readable


def verify_command(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()

    if getattr(args, "validate_rules", False):
        return _validate_rules_command(root)

    findings = verify_project(root, write=True)

    fmt = getattr(args, "format", "text")
    machine_readable = _print_verify_findings(findings, fmt)

    # The exit code is unchanged and remains the authoritative verdict.
    summary_stream = sys.stderr if machine_readable else sys.stdout
    if findings:
        print(f"sicario verify failed with {len(findings)} finding(s)", file=summary_stream)
        return 1
    print("sicario verify passed", file=summary_stream)
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
                f"- **{finding.severity.upper()} {finding.code}** `{finding.location}` - {finding.message}"
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


def _collect_hook_tokens(stripped: str, into: List[str]) -> None:
    """Append any recognized hook-command tokens on this line to `into`, in order.

    Recognizes both the flat list form (``- sicario.verify``) and the
    structured ``command: sicario.verify`` form.
    """
    for token in stripped.replace("- ", " ").replace("command:", " ").split():
        if token in HOOK_COMMAND_KIND and token not in into:
            into.append(token)


def _parse_hook_commands(extensions_yml: Path) -> "dict[str, List[str]]":
    """Extract ordered hook commands per event from .specify/extensions.yml.

    Uses a tiny, dependency-free line scanner (stdlib-only runtime constraint).
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
        if current is not None:
            _collect_hook_tokens(stripped, events[current])
    return events


def _run_deterministic_hook(command: str, root: Path) -> int:
    if command == "sicario.verify":
        findings = verify_project(root, write=True)
        for finding in findings:
            print(f"  {_finding_line(finding)}")
        return 1 if findings else 0
    if command in {"sicario.assess", "sicario.evidence"}:
        ns = argparse.Namespace(path=str(root))
        return assess_command(ns)
    return 0


def _run_hook_event_commands(commands: List[str], root: Path) -> "tuple[bool, bool]":
    """Run/report every command for one hook event. Returns (ran_any, failed)."""
    ran_any = False
    failed = False
    for command in commands:
        kind = HOOK_COMMAND_KIND.get(command, "agent")
        if kind == "deterministic":
            ran_any = True
            print(f"- run {command} (deterministic)")
            result = _run_deterministic_hook(command, root)
            if result != 0:
                failed = True
        else:
            print(
                f"- {command} (agent guidance): see "
                f".specify/extensions/sicario-guard/commands/{command}.md "
                "— a coding agent performs this; the runner does not execute it"
            )
    return ran_any, failed


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
        event_ran, event_failed = _run_hook_event_commands(commands, root)
        ran_any = ran_any or event_ran
        if event_failed:
            exit_code = 1
    if not ran_any and exit_code == 0:
        print("No deterministic hooks ran. Agent-guidance hooks are reported above.")
    return exit_code


def _interactive_init_frameworks() -> List[str]:
    """Step 1 of the interactive wizard: framework selection."""
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
    return selected_frameworks


def _interactive_init_data_classification() -> str:
    """Step 2 of the interactive wizard: data classification boundary."""
    print("Step 2: Data Classification Boundary")
    print("-" * 30)
    print("What is the maximum data classification level for this project?")
    class_levels = ["public", "internal", "confidential", "restricted", "regulated"]
    for i, level in enumerate(class_levels, start=1):
        print(f"  {i}. {level}")
    classification_input = input("Choice (1-5, default 3): ").strip()
    data_classification = "confidential"
    if classification_input.isdigit():
        idx = int(classification_input)
        if 1 <= idx <= len(class_levels):
            data_classification = class_levels[idx - 1]
    print(f"  Selected: {data_classification}")
    print("")
    return data_classification


def _interactive_init_cloud_providers() -> List[str]:
    """Step 3 of the interactive wizard: cloud/infrastructure provider targets."""
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
    return selected_cloud


def _interactive_init() -> dict:
    """Run an interactive wizard to collect user choices for SicarioSpec init.

    Returns a dict with keys:
      - ``frameworks``: list of selected framework keys
      - ``data_classification``: chosen max classification level
      - ``cloud_providers``: list of selected cloud provider targets
    """
    print("SicarioSpec Interactive Setup")
    print("=" * 40)
    print("")

    selected_frameworks = _interactive_init_frameworks()
    data_classification = _interactive_init_data_classification()
    selected_cloud = _interactive_init_cloud_providers()

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
        f"(supported: {', '.join(sorted(SUPPORTED_FRAMEWORKS))}; "
        f"experimental: {', '.join(sorted(EXPERIMENTAL_FRAMEWORKS))}; or 'all'). "
        "Experimental maps are thinner and are never chosen by a profile default, "
        "but are enforced normally when named here. Writes .sicario/frameworks.txt, "
        "which `sicario verify` honors so you enforce only the frameworks you "
        "chose. Default: the profile's supported framework set.",
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
