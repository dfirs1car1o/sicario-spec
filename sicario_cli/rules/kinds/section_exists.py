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

    findings: List[Dict[str, str]] = []
    for target in targets:
        try:
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        text_lower = text.lower()
        missing: List[str] = []
        for heading in rule.get("params", {}).get("headings", []):
            if heading.lower() not in text_lower:
                missing.append(heading)

        if missing:
            findings.append(
                {
                    "severity": rule["severity"],
                    "code": rule["id"],
                    "message": rule["message"].format(missing=", ".join(missing)),
                    "path": str(target.relative_to(root)),
                }
            )

    return findings
