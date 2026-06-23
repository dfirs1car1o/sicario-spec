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

    forbidden = set(v.lower() for v in rule.get("params", {}).get("forbidden_values", []))
    findings: List[Dict[str, str]] = []

    for target in targets:
        try:
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            lower = stripped.lower()
            if "| active |" not in lower:
                continue
            cells = [cell.strip().lower() for cell in stripped.strip("|").split("|")]
            if any(cell in forbidden for cell in cells):
                findings.append(
                    {
                        "severity": rule["severity"],
                        "code": rule["id"],
                        "message": rule["message"],
                        "path": str(target.relative_to(root)),
                    }
                )
                break

    return findings
