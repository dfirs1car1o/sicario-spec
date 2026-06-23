from pathlib import Path
from typing import Any, Dict, List


def evaluate(rule: Dict[str, Any], root: Path) -> List[Dict[str, str]]:
    pattern = rule["path"]
    params = rule.get("params", {})
    min_count = params.get("min_count", 1)
    matches = list(root.glob(pattern))
    if len(matches) >= min_count:
        return []
    return [
        {
            "severity": rule["severity"],
            "code": rule["id"],
            "message": rule["message"],
            "path": pattern,
        }
    ]
