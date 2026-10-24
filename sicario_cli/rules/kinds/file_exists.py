from pathlib import Path
from typing import Any


def evaluate(rule: dict[str, Any], root: Path) -> list[dict[str, str]]:
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
