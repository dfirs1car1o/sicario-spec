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
    keywords = params.get("keywords", [])
    match_all = params.get("match_all", False)

    findings: List[Dict[str, str]] = []
    for target in targets:
        try:
            text = target.read_text(encoding="utf-8").lower()
        except (OSError, UnicodeDecodeError):
            continue

        found = [kw for kw in keywords if kw.lower() in text]

        if match_all:
            if len(found) < len(keywords):
                findings.append(
                    {
                        "severity": rule["severity"],
                        "code": rule["id"],
                        "message": rule["message"],
                        "path": str(target.relative_to(root)),
                    }
                )
        else:
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
