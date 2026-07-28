from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


class RuleValidationError(Exception):
    """Raised when a rule file fails schema validation."""


_RULE_SCHEMA_PATH = Path(__file__).resolve().parent / "schema.json"

ALLOWED_SEVERITIES = {"critical", "high", "medium", "low"}
ALLOWED_KINDS = {
    "file-exists",
    "file-glob",
    "section-exists",
    "keyword-exists",
    "keyword-absent",
    "regex-forbidden",
    "regex-required",
    "risk-rows-valid",
    "classification-complete",
    "tagging-complete",
}

KIND_REQUIRES_PARAMS = {
    "section-exists": ["headings"],
    "keyword-exists": ["keywords"],
    "keyword-absent": ["keywords"],
    "regex-forbidden": ["pattern"],
    "regex-required": ["pattern"],
    "risk-rows-valid": ["forbidden_values"],
    "classification-complete": [],
    "tagging-complete": [],
}


def _validate_rule(rule: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    for required_field in ("id", "severity", "kind", "path", "message"):
        if required_field not in rule:
            errors.append(f"missing required field: {required_field}")

    if errors:
        return errors

    rid = rule["id"]
    if not isinstance(rid, str) or not re.match(r"^[A-Z][A-Z0-9-]+$", rid):
        errors.append(f"rule id '{rid}' must match ^[A-Z][A-Z0-9-]+$")

    sev = rule["severity"]
    if sev not in ALLOWED_SEVERITIES:
        errors.append(f"severity '{sev}' must be one of {sorted(ALLOWED_SEVERITIES)}")

    kind = rule["kind"]
    if kind not in ALLOWED_KINDS:
        errors.append(f"kind '{kind}' must be one of {sorted(ALLOWED_KINDS)}")

    if not isinstance(rule.get("path"), str):
        errors.append("path must be a string")

    if not isinstance(rule.get("message"), str):
        errors.append("message must be a string")

    enabled = rule.get("enabled", True)
    if not isinstance(enabled, bool):
        errors.append("enabled must be a boolean")

    params = rule.get("params")
    if params is not None and not isinstance(params, dict):
        errors.append("params must be an object")

    if kind in KIND_REQUIRES_PARAMS:
        required = KIND_REQUIRES_PARAMS[kind]
        if params is None:
            errors.append(f"kind '{kind}' requires params with: {required}")
        else:
            for key in required:
                if key not in params:
                    errors.append(f"kind '{kind}' requires params.{key}")

    if kind == "regex-forbidden":
        from sicario_cli.rules.kinds.regex_forbidden import validate_caps

        # Caps must be positive integers. A zero, negative, or non-integer cap
        # is rejected here, at rule load, rather than clamped to a permissive
        # default at evaluation time (FR-012, SEC-008, SA-005).
        errors.extend(validate_caps(params))

    return errors


def _load_rule_file(path: Path) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    return data


@dataclass
class RuleRunReport:
    """Result of a rule-engine run.

    ``findings`` is what the verdict is computed from. ``coverage`` and
    ``disabled_rules`` are evidence only and never participate in pass/fail
    (SEC-006).
    """

    findings: List[Dict[str, Any]] = field(default_factory=list)
    coverage: List[Dict[str, Any]] = field(default_factory=list)
    disabled_rules: List[Dict[str, Any]] = field(default_factory=list)
    #: Rule files that could not be loaded or failed validation. These DO reach
    #: the verdict: a rule that does not run is a gap in enforcement, and a gap
    #: that reports "pass" is worse than a failure. See load_rules.
    load_errors: List[Dict[str, Any]] = field(default_factory=list)


class RuleEngine:
    def __init__(self) -> None:
        self._schema = json.loads(_RULE_SCHEMA_PATH.read_text(encoding="utf-8"))

    def load_rules(self, rule_dirs: List[Path]) -> List[Dict[str, Any]]:
        """Load and validate every rule file, recording any that cannot be used.

        A rule file that fails to parse or fails validation is NOT silently
        dropped. Dropping it removes a check from the run while the gate still
        reports its verdict, so a one-token edit — say a cap of ``0`` on the
        secret-scan rule — can turn a failing repository into a passing one with
        no trace in the evidence. That is the exact failure this project exists
        to prevent, so load failures are recorded here and surfaced as findings
        by the caller (SICARIO-RULE-INVALID / SICARIO-RULE-UNREADABLE).
        """
        rules: List[Dict[str, Any]] = []
        seen_ids: Dict[str, int] = {}
        self.load_errors = []

        for directory in rule_dirs:
            if not directory.is_dir():
                continue
            for rule_file in sorted(directory.glob("*.rule.json")):
                data = _load_rule_file(rule_file)
                if data is None:
                    self.load_errors.append(
                        {
                            "file": rule_file.name,
                            "code": "SICARIO-RULE-UNREADABLE",
                            "errors": ["file is not readable, decodable, or a JSON object"],
                        }
                    )
                    continue
                errors = _validate_rule(data)
                if errors:
                    self.load_errors.append(
                        {
                            "file": rule_file.name,
                            "rule_id": data.get("id"),
                            "code": "SICARIO-RULE-INVALID",
                            "errors": errors,
                        }
                    )
                    continue
                rid = data["id"]
                if rid in seen_ids:
                    idx = seen_ids[rid]
                    rules[idx] = data
                else:
                    seen_ids[rid] = len(rules)
                    rules.append(data)

        return rules

    def evaluate(self, rule: Dict[str, Any], root: Path) -> List[Dict[str, Any]]:
        from sicario_cli.rules.kinds import evaluate as kind_evaluate

        if not rule.get("enabled", True):
            return []
        return kind_evaluate(rule["kind"], rule, root)

    def run_detailed(self, root: Path, rule_dirs: Optional[List[Path]] = None) -> RuleRunReport:
        from sicario_cli.rules.kinds import evaluate_detailed as kind_evaluate_detailed

        if rule_dirs is None:
            rule_dirs = [
                root / ".sicario" / "rules",
            ]
        rules = self.load_rules(rule_dirs)
        report = RuleRunReport()
        report.load_errors = list(self.load_errors)
        for rule in rules:
            if not rule.get("enabled", True):
                # Recorded so a rule disabled by identifier override — a
                # disabled `critical` rule especially — is visible in evidence
                # rather than only in an overriding file (FR-022, AC-003).
                report.disabled_rules.append(
                    {
                        "id": rule["id"],
                        "severity": rule["severity"],
                        "kind": rule["kind"],
                    }
                )
                continue
            rule_findings, rule_coverage = kind_evaluate_detailed(rule["kind"], rule, root)
            report.findings.extend(rule_findings)
            if rule_coverage is not None:
                report.coverage.append(rule_coverage)
        return report

    def run(self, root: Path, rule_dirs: Optional[List[Path]] = None) -> List[Dict[str, Any]]:
        return self.run_detailed(root, rule_dirs=rule_dirs).findings
