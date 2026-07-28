"""Evaluator for the ``risk-rows-valid`` rule kind.

This module is part of the ``sicario verify`` gate. It is stdlib-only and
offline by contract: no network call, no subprocess, no model call, and no AI
library import, directly or transitively (FR-026). It is read-only with respect
to the repository.

Reporting contract — the same one spec 006 established for the sibling
``regex-forbidden`` evaluator, applied here because this kind had the identical
defect (it stopped at the first invalid row in each file):

* every resolved target file is examined and every invalid active row within it
  is reported; the scan never stops at the first bad row (FR-001);
* one finding is emitted per invalid row, i.e. per matching **line**, rather
  than one per file (FR-002);
* the line is carried as its own value and is never packed into the path, so
  the path stays a resolvable file reference for SARIF consumers (FR-004,
  FR-005);
* findings are emitted in a total, deterministic order — repository-relative
  POSIX path, then line — so the set diffs cleanly across runs and platforms
  (FR-017, FR-018, FR-019);
* the message is always the static rule message. A finding names **where**, not
  **what**: row content is repository text that may name a risk, a system, or a
  person, and none of it crosses into evidence (FR-027).

**No caps here, deliberately.** ``regex-forbidden`` scans the whole tree and
needs per-file and per-rule caps because a vendored directory can produce
thousands of matches. This kind is pointed at a risk register — a small,
hand-maintained, human-reviewed document set whose row count is bounded by what
a team is willing to read. Adding caps would add a truncation path, and a
truncation path that never fires is an untested code path in gate code; it would
also introduce parameters whose only real use is reducing what the gate reports
(AC-001). Output is bounded here by the input, not by a cap. If a register ever
grows large enough to need one, the caps in ``regex_forbidden`` are the pattern
to copy, overflow finding included — silent truncation is not an option.

This evaluator has no coverage record and therefore no ``evaluate_detailed``.
``sicario_cli.rules.kinds.evaluate_detailed`` returns ``(findings, None)`` for
kinds that do not define one, which is the documented contract for a kind with
no coverage concept.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple


def _resolve_paths(pattern: str, root: Path) -> List[Path]:
    """Resolve a rule target to a deterministically ordered list of paths.

    Ordering is by repository-relative POSIX path, so it does not depend on
    filesystem enumeration order or on the platform path separator (FR-018).
    """
    if any(c in pattern for c in "*?["):
        return sorted(root.glob(pattern), key=lambda p: p.relative_to(root).as_posix())
    target = root / pattern
    return [target] if target.exists() else []


def evaluate(rule: Dict[str, Any], root: Path) -> List[Dict[str, Any]]:
    targets = _resolve_paths(rule["path"], root)
    if not targets:
        return []

    forbidden = set(v.lower() for v in rule.get("params", {}).get("forbidden_values", []))
    candidates: List[Tuple[str, int]] = []

    for target in targets:
        if target.is_dir():
            continue
        try:
            # Lexically repository-relative in POSIX form: never escapes the
            # project root, including via a symlink, because the path is not
            # resolved.
            rel = target.relative_to(root).as_posix()
        except ValueError:
            continue
        try:
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError, ValueError):
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
                # Every invalid row, not just the first: a register with three
                # incomplete rows needs three remediation actions, and a
                # reviewer must see all of them in one run (FR-001, FR-002).
                candidates.append((rel, line_number))

    # Total order on POSIX path, then line, so repeated runs over an unchanged
    # tree produce byte-identical output (FR-017, FR-019).
    candidates.sort()

    return [
        {
            "severity": rule["severity"],
            "code": rule["id"],
            # Always the static rule message: never composed from row content,
            # so no code path can carry register text outward (FR-027).
            "message": rule["message"],
            "path": rel,
            "line": line_number,
        }
        for rel, line_number in candidates
    ]
