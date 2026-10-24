from pathlib import Path
from typing import Any

_REQUIRED_PHRASES = [
    "classification owner",
    "retention",
    "residency",
    "sharing",
    "redaction",
]

_DATA_CLASSIFICATION_VALUES = {"public", "internal", "confidential", "restricted", "regulated"}


def _resolve_paths(pattern: str, root: Path) -> list[Path]:
    if any(c in pattern for c in "*?["):
        return sorted(root.glob(pattern))
    target = root / pattern
    return [target] if target.exists() else []


def evaluate(rule: dict[str, Any], root: Path) -> list[dict[str, str]]:
    targets = _resolve_paths(rule["path"], root)
    if not targets:
        return []

    params = rule.get("params", {})
    required = params.get("required_columns", list(_REQUIRED_PHRASES))
    findings: list[dict[str, str]] = []

    for target in targets:
        try:
            text = target.read_text(encoding="utf-8").lower()
        except (OSError, UnicodeDecodeError):
            continue

        if "data classification" not in text:
            continue

        missing = [p for p in required if p not in text]
        has_level = any(level in text for level in _DATA_CLASSIFICATION_VALUES)
        if missing or not has_level:
            findings.append(
                {
                    "severity": rule["severity"],
                    "code": rule["id"],
                    "message": rule["message"],
                    "path": str(target.relative_to(root)),
                }
            )

    return findings
