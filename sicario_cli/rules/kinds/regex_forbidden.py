"""Evaluator for the ``regex-forbidden`` rule kind.

This module is part of the ``sicario verify`` gate. It is stdlib-only and
offline by contract: no network call, no subprocess, no model call, and no AI
library import, directly or transitively (FR-026, SEC-012). It is also
read-only with respect to the repository (SEC-013).

Reporting contract:

* every resolved target file is examined; the scan never stops at the first
  match (FR-001, SEC-001);
* one finding is emitted per distinct matching *line*, deduplicated within the
  line (FR-002, FR-003);
* the line is carried as its own value so the path stays a resolvable file
  reference for SARIF consumers (FR-005);
* a finding never carries the matched text, any substring, transformation, or
  digest of it (FR-027, SEC-002);
* output is bounded by a per-file and a per-rule cap, applied in that order and
  only after deterministic ordering (FR-010, FR-011, FR-016);
* any suppression emits a mandatory, unsuppressible overflow finding carrying
  exact reported / suppressed / total counts (FR-013, FR-014, SEC-003, SEC-004);
* counting continues after emission stops, so those counts are exact rather
  than lower bounds (FR-015, SEC-005);
* a file the scanner did not inspect is never indistinguishable from a file the
  scanner cleared, whether it was unreadable or excluded by the skipped-path
  policy (SEC-011, FR-020). The two are counted separately, because "could not
  be read" and "excluded by policy" are different facts a reviewer acts on
  differently.
"""

from __future__ import annotations

import bisect
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

#: Directory names excluded from every ``regex-forbidden`` scan. This is the
#: effective skipped-path set recorded in gate evidence (FR-021, SEC-010).
#: It is fixed in code, not configurable, because this feature introduces no
#: new exclusion mechanism (FR-030, SEC-009).
SKIPPED_DIR_NAMES = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        "build",
        "dist",
        "generated",
        "sicario_spec.egg-info",
    }
)

_SKIP_DIRS = SKIPPED_DIR_NAMES

#: Cap on how many distinct excluded directories the coverage record itemises.
#: The *count* of excluded files is exact and never capped; only the per-
#: directory attribution list is bounded, so a vendored tree cannot inflate the
#: evidence file. Whenever the list is shortened the record says so explicitly
#: (``excluded_dirs_truncated``, ``excluded_dirs_total``): a truncated list that
#: looked complete would be the same defect this record exists to close.
MAX_EXCLUDED_DIRS_RECORDED = 50

#: Documented cap defaults. High enough that a normal repository never reaches
#: them, low enough that a pathological one stays usable (FR-010).
DEFAULT_MAX_FINDINGS_PER_FILE = 20
DEFAULT_MAX_FINDINGS_PER_RULE = 200

#: Rule parameters that carry caps. Both must be positive integers (FR-012).
CAP_PARAMS: Tuple[str, str] = ("max_findings_per_file", "max_findings_per_rule")

#: Code of the mandatory overflow finding emitted whenever a cap suppresses
#: anything. It is not itself capped and cannot be configured away (FR-014).
TRUNCATION_FINDING_CODE = "SICARIO-FINDINGS-TRUNCATED"


def validate_caps(params: Any) -> List[str]:
    """Return validation errors for cap parameters, if any.

    Caps must be positive integers. Zero, negative, and non-integer values are
    rejected at rule load rather than clamped, ignored, or defaulted
    (FR-012, SEC-008). ``bool`` is rejected explicitly: it is an ``int``
    subclass in Python but is not a cap value anybody meant to write.
    """
    errors: List[str] = []
    if not isinstance(params, dict):
        return errors
    for key in CAP_PARAMS:
        if key not in params:
            continue
        value = params[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            errors.append(f"params.{key} must be a positive integer (got {value!r})")
    return errors


def _cap(params: Dict[str, Any], key: str, default: int) -> int:
    if key not in params:
        return default
    value = params[key]
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        # Never clamp to a permissive default: a bad cap is a load-time error.
        raise ValueError(f"params.{key} must be a positive integer (got {value!r})")
    return value


def _excluded_root(parts: Sequence[str]) -> Optional[str]:
    """Return the shallowest prefix of ``parts`` whose own name is skipped.

    The skip policy matches any path component at any depth, so the component
    that triggered the exclusion is what a reader needs to see: it is the fact
    that explains why the files beneath it were not scanned. Attribution is to
    that prefix rather than to each file, so an excluded vendored tree collapses
    to one record instead of tens of thousands.
    """
    for index, part in enumerate(parts):
        if part in _SKIP_DIRS:
            # POSIX form, built from components, so it does not depend on the
            # platform path separator (FR-018, SEC-014).
            return "/".join(parts[: index + 1])
    return None


def _resolve_paths(pattern: str, root: Path) -> Tuple[List[Path], Dict[str, int]]:
    """Resolve a rule target to a deterministically ordered list of paths, plus
    a per-directory tally of the files the skipped-path policy excluded.

    Ordering is by repository-relative POSIX path, so it does not depend on
    filesystem enumeration order or on the platform path separator (FR-018).

    The tally is the effect of the policy, where ``SKIPPED_DIR_NAMES`` is only
    its statement. Recording the statement alone let an excluded file be
    reported exactly like a cleared one, which SEC-011 forbids.
    """
    if not any(c in pattern for c in "*?["):
        # A literal target is not filtered by the skip policy today, so there is
        # nothing for it to exclude. Left as-is deliberately: widening the
        # policy to literal targets would change what is scanned, which this
        # coverage fix must not do (FR-025, SEC-006).
        target = root / pattern
        return ([target] if target.exists() else []), {}

    matches: List[Path] = []
    excluded: Dict[str, int] = {}
    for path in root.glob(pattern):
        skip_root = _excluded_root(path.relative_to(root).parts)
        if skip_root is None:
            matches.append(path)
        elif not path.is_dir():
            # Count exactly what ``files_scanned`` and ``files_skipped`` count:
            # directories are neither scanned nor skipped, so they are not
            # excluded either, and the three counters stay commensurable.
            excluded[skip_root] = excluded.get(skip_root, 0) + 1
    matches.sort(key=lambda p: p.relative_to(root).as_posix())
    return matches, excluded


def _record_exclusions(coverage: Dict[str, Any], excluded: Dict[str, int]) -> None:
    """Write the skip-policy tally into the coverage record.

    ``files_excluded`` is always the exact total. Only ``excluded_dirs`` is
    bounded, and the record carries the true directory count alongside it so a
    shortened list can never be mistaken for a complete one.
    """
    ordered = sorted(excluded.items())
    listed = ordered[:MAX_EXCLUDED_DIRS_RECORDED]
    coverage["files_excluded"] = sum(excluded.values())
    coverage["excluded_dirs"] = [{"path": path, "files": count} for path, count in listed]
    coverage["excluded_dirs_total"] = len(ordered)
    coverage["excluded_dirs_truncated"] = len(listed) < len(ordered)


def _line_starts(text: str) -> List[int]:
    """Byte-agnostic offsets of the first character of each line."""
    starts = [0]
    index = text.find("\n")
    while index != -1:
        starts.append(index + 1)
        index = text.find("\n", index + 1)
    return starts


def _position(line_starts: Sequence[int], offset: int) -> Tuple[int, int]:
    """Return the one-based (line, column) of ``offset``."""
    line_index = bisect.bisect_right(line_starts, offset) - 1
    return line_index + 1, offset - line_starts[line_index] + 1


def _new_coverage(rule: Dict[str, Any], per_file_cap: int, per_rule_cap: int) -> Dict[str, Any]:
    return {
        "rule_id": rule["id"],
        "kind": "regex-forbidden",
        "target": rule["path"],
        "files_scanned": 0,
        # Could not be read or decoded (SEC-011).
        "files_skipped": 0,
        "skipped_files": [],
        # Excluded by the skipped-path policy before any read was attempted.
        # Kept distinct from `files_skipped`: an unreadable file is a scanner
        # limitation to investigate, an excluded file is a policy decision to
        # review, and collapsing them would hide both (SEC-011, FR-021).
        # Always present, including as zero, so "no exclusions" is stated
        # rather than inferred from an absent key.
        "files_excluded": 0,
        "excluded_dirs": [],
        "excluded_dirs_total": 0,
        "excluded_dirs_truncated": False,
        "max_excluded_dirs_recorded": MAX_EXCLUDED_DIRS_RECORDED,
        "files_matched": 0,
        "total_occurrences": 0,
        "total_matches": 0,
        "findings_reported": 0,
        "occurrences_suppressed": 0,
        "truncated": False,
        "truncation_scopes": [],
        "max_findings_per_file": per_file_cap,
        "max_findings_per_rule": per_rule_cap,
    }


def evaluate_detailed(
    rule: Dict[str, Any], root: Path
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Evaluate the rule and return ``(findings, coverage_record)``.

    The coverage record makes scan gaps and truncation legible from evidence
    alone (FR-020, SEC-011).
    """
    params = rule.get("params") or {}
    per_file_cap = _cap(params, "max_findings_per_file", DEFAULT_MAX_FINDINGS_PER_FILE)
    per_rule_cap = _cap(params, "max_findings_per_rule", DEFAULT_MAX_FINDINGS_PER_RULE)
    coverage = _new_coverage(rule, per_file_cap, per_rule_cap)

    pattern_str = params.get("pattern", "")
    try:
        pattern = re.compile(pattern_str, re.IGNORECASE)
    except re.error:
        coverage["invalid_pattern"] = True
        coverage["findings_reported"] = 1
        return (
            [
                {
                    "severity": "high",
                    "code": rule["id"],
                    "message": f"Invalid regex pattern: {pattern_str}",
                    "path": rule["path"],
                }
            ],
            coverage,
        )

    candidates: List[Tuple[str, int, int]] = []
    per_file_suppressed = 0

    targets, excluded = _resolve_paths(rule["path"], root)
    _record_exclusions(coverage, excluded)

    for target in targets:
        if target.is_dir():
            continue
        try:
            # Lexically repository-relative: never escapes the project root,
            # including via a symlink, because the path is not resolved
            # (SEC-014).
            rel = target.relative_to(root).as_posix()
        except ValueError:
            continue
        try:
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError, ValueError):
            # A file the scanner could not inspect is never indistinguishable
            # from a file the scanner cleared (SEC-011).
            coverage["files_skipped"] += 1
            coverage["skipped_files"].append(rel)
            continue
        coverage["files_scanned"] += 1

        # One pass over the file's text; line offsets are computed only for
        # files that actually match (FR-009).
        first_column_by_line: Dict[int, int] = {}
        line_starts: Optional[List[int]] = None
        match_count = 0
        for match in pattern.finditer(text):
            match_count += 1
            if line_starts is None:
                line_starts = _line_starts(text)
            line, column = _position(line_starts, match.start())
            # Two matches on one line are one remediation action (FR-003).
            if line not in first_column_by_line:
                first_column_by_line[line] = column
        if not first_column_by_line:
            continue

        coverage["files_matched"] += 1
        coverage["total_matches"] += match_count
        occurrences = sorted(first_column_by_line.items())
        coverage["total_occurrences"] += len(occurrences)
        # Per-file cap first, so no single file can consume the whole per-rule
        # budget (FR-011, AC-004).
        kept = occurrences[:per_file_cap]
        per_file_suppressed += len(occurrences) - len(kept)
        candidates.extend((rel, line, column) for line, column in kept)

    # Total order on POSIX path, then line, then column, before any per-rule
    # cap is applied, so a truncated run diffs cleanly (FR-016, FR-017, AC-008).
    candidates.sort()
    reported = candidates[:per_rule_cap]
    per_rule_suppressed = len(candidates) - len(reported)
    suppressed = per_file_suppressed + per_rule_suppressed

    findings: List[Dict[str, Any]] = [
        {
            "severity": rule["severity"],
            "code": rule["id"],
            # Always the static rule message: never composed from scanned
            # content, so no code path can carry matched text outward (SEC-002).
            "message": rule["message"],
            "path": rel,
            "line": line,
        }
        for rel, line, _column in reported
    ]

    coverage["findings_reported"] = len(reported)
    coverage["occurrences_suppressed"] = suppressed

    if suppressed:
        scopes: List[str] = []
        if per_file_suppressed:
            scopes.append("per-file")
        if per_rule_suppressed:
            scopes.append("per-rule")
        coverage["truncated"] = True
        coverage["truncation_scopes"] = scopes
        # Mandatory and unsuppressible: appended after every cap has been
        # applied, so no cap, parameter, or repository content can remove it
        # (FR-013, FR-014, SEC-003, AC-006). Severity is inherited from the
        # truncated rule (SEC-004).
        findings.append(
            {
                "severity": rule["severity"],
                "code": TRUNCATION_FINDING_CODE,
                "message": (
                    f"Findings truncated for {rule['id']}: reported {len(reported)} of "
                    f"{coverage['total_occurrences']} occurrence(s) across "
                    f"{coverage['files_matched']} file(s); {suppressed} suppressed "
                    f"(truncation-scope: {', '.join(scopes)}; "
                    f"caps: per-file={per_file_cap}, per-rule={per_rule_cap})"
                ),
                "path": "",
            }
        )

    return findings, coverage


def evaluate(rule: Dict[str, Any], root: Path) -> List[Dict[str, Any]]:
    return evaluate_detailed(rule, root)[0]
