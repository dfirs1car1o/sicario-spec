from pathlib import Path
from typing import Any, Dict, List


def evaluate(rule: Dict[str, Any], root: Path) -> List[Dict[str, str]]:
    target = root / rule["path"]
    if target.exists():
        return []
    return [
        {
            "severity": rule["severity"],
            "code": rule["id"],
            "message": rule["message"],
            "path": rule["path"],
        }
    ]
