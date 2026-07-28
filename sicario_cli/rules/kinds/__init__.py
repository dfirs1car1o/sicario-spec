from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

KIND_REGISTRY: Dict[str, str] = {
    "file-exists": "sicario_cli.rules.kinds.file_exists",
    "file-glob": "sicario_cli.rules.kinds.file_glob",
    "section-exists": "sicario_cli.rules.kinds.section_exists",
    "keyword-exists": "sicario_cli.rules.kinds.keyword_exists",
    "keyword-absent": "sicario_cli.rules.kinds.keyword_absent",
    "regex-forbidden": "sicario_cli.rules.kinds.regex_forbidden",
    "regex-required": "sicario_cli.rules.kinds.regex_required",
    "risk-rows-valid": "sicario_cli.rules.kinds.risk_rows_valid",
    "classification-complete": "sicario_cli.rules.kinds.classification_complete",
    "tagging-complete": "sicario_cli.rules.kinds.tagging_complete",
}


def _load_kind_module(kind: str):
    import importlib

    module_path = KIND_REGISTRY.get(kind)
    if module_path is None:
        raise ValueError(f"Unknown rule kind: {kind}")
    return importlib.import_module(module_path)


def evaluate(kind: str, rule: Dict[str, Any], root: Path) -> List[Dict[str, Any]]:
    return _load_kind_module(kind).evaluate(rule, root)


def evaluate_detailed(
    kind: str, rule: Dict[str, Any], root: Path
) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Evaluate a rule, returning findings plus a coverage record when the kind
    produces one. Kinds with no coverage concept return ``None`` for it."""
    module = _load_kind_module(kind)
    detailed = getattr(module, "evaluate_detailed", None)
    if detailed is None:
        return module.evaluate(rule, root), None
    return detailed(rule, root)
