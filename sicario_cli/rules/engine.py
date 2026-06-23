from __future__ import annotations

import json
import re
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

    for field in ("id", "severity", "kind", "path", "message"):
        if field not in rule:
            errors.append(f"missing required field: {field}")

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

    return errors


def _load_rule_file(path: Path) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    return data


class RuleEngine:
    def __init__(self) -> None:
        self._schema = json.loads(_RULE_SCHEMA_PATH.read_text(encoding="utf-8"))

    def load_rules(self, rule_dirs: List[Path]) -> List[Dict[str, Any]]:
        rules: List[Dict[str, Any]] = []
        seen_ids: Dict[str, int] = {}

        for directory in rule_dirs:
            if not directory.is_dir():
                continue
            for rule_file in sorted(directory.glob("*.rule.json")):
                data = _load_rule_file(rule_file)
                if data is None:
                    continue
                errors = _validate_rule(data)
                if errors:
                    import sys

                    print(
                        f"warning: skipping invalid rule {rule_file.name}: {'; '.join(errors)}",
                        file=sys.stderr,
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

    def evaluate(self, rule: Dict[str, Any], root: Path) -> List[Dict[str, str]]:
        from sicario_cli.rules.kinds import evaluate as kind_evaluate

        if not rule.get("enabled", True):
            return []
        return kind_evaluate(rule["kind"], rule, root)

    def run(self, root: Path, rule_dirs: Optional[List[Path]] = None) -> List[Dict[str, str]]:
        if rule_dirs is None:
            rule_dirs = [
                root / ".sicario" / "rules",
            ]
        rules = self.load_rules(rule_dirs)
        findings: List[Dict[str, str]] = []
        for rule in rules:
            findings.extend(self.evaluate(rule, root))
        return findings
