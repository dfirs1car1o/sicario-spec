from pathlib import Path
from typing import Any, Dict, List


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
    condition_keywords = params.get("condition_keywords")
    keywords = params.get("keywords", [])

    findings: List[Dict[str, str]] = []
    for target in targets:
        try:
            text = target.read_text(encoding="utf-8").lower()
        except (OSError, UnicodeDecodeError):
            continue

        if condition_keywords is not None:
            has_condition = any(kw.lower() in text for kw in condition_keywords)
            if not has_condition:
                continue

        found = [kw for kw in keywords if kw.lower() in text]

        if not found:
            findings.append(
                {
                    "severity": rule["severity"],
                    "code": rule["id"],
                    "message": rule["message"],
                    "path": str(target.relative_to(root)),
                }
            )

    return findings
