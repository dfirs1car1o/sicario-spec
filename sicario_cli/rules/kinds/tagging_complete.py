from pathlib import Path
from typing import Any, Dict, List


_REQUIRED_TAGS = {"owner", "system", "environment", "data-classification", "retention"}


def _resolve_paths(pattern: str, root: Path) -> List[Path]:
    if any(c in pattern for c in "*?["):
        return sorted(root.glob(pattern))
    target = root / pattern
    return [target] if target.exists() else []


def evaluate(rule: Dict[str, Any], root: Path) -> List[Dict[str, str]]:
    targets = _resolve_paths(rule["path"], root)
    if not targets:
        return []

    params = rule.get("params", {})
    required = set(params.get("required_columns", list(_REQUIRED_TAGS)))
    findings: List[Dict[str, str]] = []

    for target in targets:
        try:
            text = target.read_text(encoding="utf-8").lower()
        except (OSError, UnicodeDecodeError):
            continue

        if "tagging discipline" not in text:
            continue

        missing = [t for t in required if t not in text]
        if missing:
            findings.append(
                {
                    "severity": rule["severity"],
                    "code": rule["id"],
                    "message": rule["message"],
                    "path": str(target.relative_to(root)),
                }
            )

    return findings
