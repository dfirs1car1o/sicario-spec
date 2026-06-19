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
import sys
import sysconfig
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.resources import files as package_files
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from sicario_cli.version import __version__


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


def _parse_profiles(value: str) -> List[str]:
    names = [part.strip() for part in value.split(",") if part.strip()]
    if not names:
        return ["public-core"]
    unknown = [name for name in names if name not in PROFILE_PRESETS]
    if unknown:
        known = ", ".join(sorted(PROFILE_PRESETS))
        raise SystemExit(f"Unknown profile(s): {', '.join(unknown)}. Known profiles: {known}")
    presets: List[str] = []
    for name in names:
        for preset in PROFILE_PRESETS[name]:
            if preset not in presets:
                presets.append(preset)
    return presets


def _copy_tree(src: Path, dst: Path, *, force: bool, dry_run: bool, actions: List[str]) -> None:
    if not src.exists():
        raise SystemExit(f"Source does not exist: {src}")
    if dst.exists() and not force:
        actions.append(f"skip existing {dst}")
        return
    actions.append(f"copy {src} -> {dst}")
    if dry_run:
        return
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _write_text(path: Path, content: str, *, force: bool, dry_run: bool, actions: List[str]) -> None:
    if path.exists() and not force:
        actions.append(f"skip existing {path}")
        return
    actions.append(f"write {path}")
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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
    selected_presets = _parse_profiles(args.profile)

    if target.exists() and any(target.iterdir()) and not args.force:
        raise SystemExit(f"Target exists and is not empty: {target}. Use --force to write into it.")

    actions.append(f"target {target}")
    actions.append(f"specify { _validate_specify_available() }")
    actions.append(f"integration {args.integration}")
    actions.append(f"presets {', '.join(selected_presets)}")

    if not args.dry_run:
        target.mkdir(parents=True, exist_ok=True)

    for preset in selected_presets:
        _copy_tree(
            PRESETS_ROOT / preset,
            target / ".specify" / "presets" / preset,
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
        )

    if "sicario-cloud-iac" in selected_presets:
        _copy_tree(
            PRESETS_ROOT / "sicario-cloud-iac" / "templates" / "terraform",
            target / "infra" / "terraform",
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
        )
        _copy_tree(
            PRESETS_ROOT / "sicario-cloud-iac" / "templates" / "azure-bicep",
            target / "infra" / "azure-bicep",
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
        )
        _copy_tree(
            PRESETS_ROOT / "sicario-cloud-iac" / "templates" / "azure-avm-bicep",
            target / "infra" / "azure-avm-bicep",
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
        )
        _copy_tree(
            PRESETS_ROOT / "sicario-cloud-iac" / "templates" / "azure-avm-terraform",
            target / "infra" / "azure-avm-terraform",
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
        )
        _copy_tree(
            PRESETS_ROOT / "sicario-cloud-iac" / "templates" / "aws-cloudformation",
            target / "infra" / "aws-cloudformation",
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
        )
        _copy_tree(
            PRESETS_ROOT / "sicario-cloud-iac" / "templates" / "gcp",
            target / "infra" / "gcp-terraform",
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
        )
        _copy_tree(
            PRESETS_ROOT / "sicario-cloud-iac" / "templates" / "kubernetes",
            target / "infra" / "kubernetes",
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
        )
        _copy_tree(
            PRESETS_ROOT / "sicario-cloud-iac" / "templates" / "policy-as-code",
            target / "policy" / "policy-as-code",
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
        )

    if "sicario-security-toolchain" in selected_presets:
        _copy_tree(
            PRESETS_ROOT / "sicario-security-toolchain" / "templates" / "toolchain",
            target / "security" / "toolchain",
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
        )

    if CONTROL_MAPS_ROOT.exists():
        _copy_tree(
            CONTROL_MAPS_ROOT,
            target / "docs" / "compliance" / "control-maps",
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
        )

    _copy_tree(
        EXTENSIONS_ROOT / "sicario-guard",
        target / ".specify" / "extensions" / "sicario-guard",
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )

    _write_text(
        target / ".specify" / "extensions.yml",
        _extensions_yml(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )

    _write_text(
        target / "SICARIO.md",
        _sicario_project_readme(selected_presets),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )

    _write_text(
        target / "docs" / "security" / "threat-model.md",
        _default_threat_model(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )
    _write_text(
        target / "docs" / "security" / "abuse-cases.md",
        _default_abuse_cases(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )
    _write_text(
        target / "docs" / "governance" / "data-classification.md",
        _default_data_classification(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )
    _write_text(
        target / "docs" / "governance" / "tagging-taxonomy.md",
        _default_tagging_taxonomy(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )
    _write_text(
        target / "docs" / "compliance" / "control-applicability.md",
        _default_control_applicability(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )
    _write_text(
        target / "docs" / "compliance" / "evidence-index.md",
        _default_evidence_index(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )
    _write_text(
        target / "docs" / "architecture" / "system-context.md",
        _default_system_context(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )
    _write_text(
        target / "docs" / "diagrams" / "system-context.mmd",
        _default_system_context_diagram(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )
    _write_text(
        target / "docs" / "docs-impact.md",
        _default_docs_impact(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )
    _write_text(
        target / "docs" / "risk" / "risk-register.md",
        _default_risk_register(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )
    _write_text(
        target / "docs" / "risk" / "security-exceptions.md",
        _default_security_exceptions(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )
    _write_text(
        target / "docs" / "risk" / "accepted-risk-log.md",
        _default_accepted_risk_log(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )
    _write_text(
        target / "docs-site" / "package.json",
        _docs_site_package_json(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )
    _write_text(
        target / "docs-site" / "docusaurus.config.js",
        _docusaurus_config(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )
    _write_text(
        target / "docs-site" / "sidebars.js",
        _docusaurus_sidebars(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )
    _write_text(
        target / "docs-site" / "docs" / "intro.md",
        _docusaurus_intro(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )
    _write_text(
        target / "docs-site" / "src" / "css" / "custom.css",
        _docusaurus_css(),
        force=args.force,
        dry_run=args.dry_run,
        actions=actions,
    )

    if args.integration == "claude":
        _write_text(
            target / "CLAUDE.md",
            _claude_instructions(),
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
        )

    for workflow_name in ["sicario-verify.yml", "docs-site.yml"]:
        workflow_src = WORKFLOW_ROOT / workflow_name
        if not workflow_src.exists():
            continue
        _write_text(
            target / ".github" / "workflows" / workflow_name,
            workflow_src.read_text(encoding="utf-8"),
            force=args.force,
            dry_run=args.dry_run,
            actions=actions,
        )

    if "sicario-security-toolchain" in selected_presets:
        workflow_src = WORKFLOW_ROOT / "security-toolchain.yml"
        if workflow_src.exists():
            _write_text(
                target / ".github" / "workflows" / "security-toolchain.yml",
                workflow_src.read_text(encoding="utf-8"),
                force=args.force,
                dry_run=args.dry_run,
                actions=actions,
            )

    print("\n".join(actions))
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


def _sicario_project_readme(presets: Sequence[str]) -> str:
    return f"""# SicarioSpec Project Guardrails

SicarioSpec is installed for this project.

Installed presets:

{chr(10).join(f'- `{preset}`' for preset in presets)}

Run:

```bash
sicario verify
sicario assess
```

Principle: AI can draft and review, but deterministic gates decide whether the
work is complete enough to ship.
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


def _claude_instructions() -> str:
    return """# Claude Project Instructions

Use SicarioSpec guardrails for all non-trivial changes.

- Start with the spec.
- Keep AI out of authoritative decisions.
- Add threat model and abuse cases for meaningful features.
- Add well-architected review for meaningful features.
- Add negative/security tests when risk applies.
- Run `sicario verify` before handoff.
- Keep security exceptions owned, approved, time-bound, and evidenced.
- Keep data classification and tags current for specs, evidence, resources, and releases.
- Do not place secrets in files, logs, artifacts, or LLM context.
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
    root = path.resolve()
    findings: List[Finding] = []

    threat_model = root / "docs" / "security" / "threat-model.md"
    if not threat_model.exists():
        findings.append(
            Finding(
                "high",
                "SICARIO-MISSING-THREAT-MODEL",
                "Missing docs/security/threat-model.md",
                str(threat_model.relative_to(root)),
            )
        )

    docs_impact = root / "docs" / "docs-impact.md"
    if not docs_impact.exists():
        findings.append(
            Finding(
                "medium",
                "SICARIO-MISSING-DOCS-IMPACT",
                "Missing docs/docs-impact.md",
                str(docs_impact.relative_to(root)),
            )
        )

    if not (root / "docs" / "diagrams").exists():
        findings.append(
            Finding(
                "medium",
                "SICARIO-MISSING-DIAGRAMS",
                "Missing docs/diagrams directory for architecture diagrams",
                "docs/diagrams",
            )
        )

    governance_files = [
        (
            root / "docs" / "governance" / "data-classification.md",
            "SICARIO-MISSING-DATA-CLASSIFICATION",
            "Missing docs/governance/data-classification.md",
        ),
        (
            root / "docs" / "governance" / "tagging-taxonomy.md",
            "SICARIO-MISSING-TAGGING-TAXONOMY",
            "Missing docs/governance/tagging-taxonomy.md",
        ),
    ]
    for governance_file, code, message in governance_files:
        if not governance_file.exists():
            findings.append(
                Finding(
                    "high",
                    code,
                    message,
                    str(governance_file.relative_to(root)),
                )
            )

    control_maps_present = (root / "docs" / "compliance" / "control-maps").exists() or (
        root / "control_maps"
    ).exists()
    if not control_maps_present:
        findings.append(
            Finding(
                "medium",
                "SICARIO-MISSING-CONTROL-MAPS",
                "Missing control mapping pack",
                "docs/compliance/control-maps",
            )
        )

    risk_files = [
        root / "docs" / "risk" / "risk-register.md",
        root / "docs" / "risk" / "security-exceptions.md",
        root / "docs" / "risk" / "accepted-risk-log.md",
    ]
    for risk_file in risk_files:
        if not risk_file.exists():
            findings.append(
                Finding(
                    "medium",
                    "SICARIO-MISSING-RISK-REGISTER",
                    f"Missing {risk_file.relative_to(root)}",
                    str(risk_file.relative_to(root)),
                )
            )
            continue
        findings.extend(_validate_active_risk_rows(root, risk_file))

    for text_file in iter_text_files(root):
        rel = str(text_file.relative_to(root))
        try:
            text = text_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(
                    Finding("critical", "SICARIO-HARDCODED-SECRET", "Potential hardcoded secret", rel)
                )
                break

    for spec in sorted(root.glob("specs/**/spec.md")):
        text = spec.read_text(encoding="utf-8")
        rel = str(spec.relative_to(root))
        required = [
            "Data Classification",
            "Tagging Discipline",
            "Trust Boundaries",
            "Security Requirements",
            "Abuse Cases",
            "Evidence",
        ]
        for heading in required:
            if heading.lower() not in text.lower():
                findings.append(
                    Finding("high", "SICARIO-SPEC-SECTION", f"spec.md missing {heading}", rel)
                )
        findings.extend(_validate_spec_classification_and_tags(root, spec, text))
        if AI_KEYWORDS.search(text) and not _contains_any(text, ["prompt injection", "tool boundary"]):
            findings.append(
                Finding(
                    "high",
                    "SICARIO-AI-GUARDRAIL-MISSING",
                    "AI-sensitive spec missing prompt injection or tool boundary guardrails",
                    rel,
                )
            )
        if FLEET_KEYWORDS.search(text) and not _contains_any(
            text,
            [
                "idempotency",
                "retry",
                "dead-letter",
                "dead letter",
                "workflow state",
                "human approval",
            ],
        ):
            findings.append(
                Finding(
                    "high",
                    "SICARIO-FLEET-GUARDRAIL-MISSING",
                    "Agent/workflow orchestration spec missing retry, idempotency, state, dead-letter, or approval guardrails",
                    rel,
                )
            )

    for plan in sorted(root.glob("specs/**/plan.md")):
        text = plan.read_text(encoding="utf-8")
        rel = str(plan.relative_to(root))
        for heading in [
            "Threat Model",
            "Data Classification",
            "Tagging",
            "Well-Architected",
            "Supply Chain",
            "Rollback",
            "Human Approval",
            "Evidence",
        ]:
            if heading.lower() not in text.lower():
                findings.append(
                    Finding("high", "SICARIO-PLAN-SECTION", f"plan.md missing {heading}", rel)
                )

    for tasks in sorted(root.glob("specs/**/tasks.md")):
        text = tasks.read_text(encoding="utf-8")
        rel = str(tasks.relative_to(root))
        task_checks = [
            ("security test", "tasks.md missing security test task"),
            ("negative", "tasks.md missing negative test task"),
            ("classification", "tasks.md missing data classification task"),
            ("tagging", "tasks.md missing tagging task"),
            ("docs impact", "tasks.md missing docs impact task"),
            ("evidence", "tasks.md missing evidence generation task"),
            ("threat model", "tasks.md missing threat model update task"),
        ]
        for phrase, message in task_checks:
            if phrase not in text.lower():
                findings.append(Finding("high", "SICARIO-TASKS-SECTION", message, rel))

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
    (out_dir / "gate-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
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
    (out_dir / "spec-run-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


def verify_command(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()
    findings = verify_project(root, write=True)
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
            lines.append(f"- **{finding.severity.upper()} {finding.code}** `{finding.path}` - {finding.message}")
    else:
        lines.append("Status: PASS")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report)
    return 0 if not findings else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sicario", description="Kill risk before it ships.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Initialize SicarioSpec in a project")
    init.add_argument("project", help="Target project directory")
    init.add_argument("--integration", default="claude", choices=["claude", "generic"])
    init.add_argument("--profile", default="public-core", help="Comma-separated profile list")
    init.add_argument("--dry-run", action="store_true")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=init_project)

    verify = sub.add_parser("verify", help="Run deterministic SicarioSpec gates")
    verify.add_argument("path", nargs="?", default=".")
    verify.set_defaults(func=verify_command)

    assess = sub.add_parser("assess", help="Write a repo posture assessment")
    assess.add_argument("path", nargs="?", default=".")
    assess.set_defaults(func=assess_command)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
