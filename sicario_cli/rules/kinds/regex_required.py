import re
from pathlib import Path
from typing import Any, Dict, List


def _resolve_paths(pattern: str, root: Path) -> List[Path]:
    if any(c in pattern for c in "*?["):
        return sorted(root.glob(pattern))
    target = root / pattern
    return [target] if target.exists() else []


def evaluate(rule: Dict[str, Any], root: Path) -> List[Dict[str, str]]:
    pattern_str = rule.get("params", {}).get("pattern", "")
    try:
        pattern = re.compile(
            pattern_str,
            re.IGNORECASE if rule.get("params", {}).get("case_insensitive", True) else 0,
        )
    except re.error:
        return [
            {
                "severity": "high",
                "code": rule["id"],
                "message": f"Invalid regex pattern: {pattern_str}",
                "path": rule["path"],
            }
        ]

    targets = _resolve_paths(rule["path"], root)
    findings: List[Dict[str, str]] = []

    for target in targets:
        try:
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        if not pattern.search(text):
            findings.append(
                {
                    "severity": rule["severity"],
                    "code": rule["id"],
                    "message": rule["message"],
                    "path": str(target.relative_to(root)),
                }
            )

    return findings
