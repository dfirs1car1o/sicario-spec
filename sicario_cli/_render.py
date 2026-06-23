"""Centralized file-render helpers for SicarioSpec.

Extracted from ``cli.py`` so presets and the init orchestrator share a single
set of brownfield-safe write/overlay/copy utilities.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Sequence


# Per-file outcome codes used in the final report.
OUTCOME_CREATED = "created"
OUTCOME_MERGED = "merged-overlaid"
OUTCOME_PRESERVED = "preserved"
OUTCOME_OVERWRITTEN = "overwritten"
OUTCOME_SKIPPED = "skipped"

# A clearly-marked, idempotent overlay marker. If this marker is already present
# in a file, the overlay has been applied and we must not append it again.
SICARIO_OVERLAY_BEGIN = "<!-- BEGIN SICARIO-SPEC OVERLAY (additive; do not edit by hand) -->"
SICARIO_OVERLAY_END = "<!-- END SICARIO-SPEC OVERLAY -->"


@dataclass
class FileReport:
    """One per-file outcome line for the end-of-run report."""

    path: str
    outcome: str
    detail: str = ""


def _record(reports: List[FileReport], path: Path, outcome: str, detail: str = "") -> None:
    reports.append(FileReport(path=str(path), outcome=outcome, detail=detail))


def _backup_path(path: Path) -> Path:
    """Return a timestamped, non-clobbering backup path next to ``path``."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    candidate = path.with_name(f"{path.name}.sicario-bak.{stamp}")
    counter = 1
    while candidate.exists():
        candidate = path.with_name(f"{path.name}.sicario-bak.{stamp}.{counter}")
        counter += 1
    return candidate


def _backup_file(path: Path, *, dry_run: bool) -> Optional[Path]:
    """Back up an existing file before modifying or overwriting it."""
    if not path.exists() or dry_run:
        return None
    backup = _backup_path(path)
    shutil.copy2(path, backup)
    return backup


def _copy_tree(
    src: Path,
    dst: Path,
    *,
    force: bool,
    dry_run: bool,
    actions: List[str],
    reports: Optional[List[FileReport]] = None,
) -> None:
    if not src.exists():
        raise SystemExit(f"Source does not exist: {src}")
    if dst.exists() and not force:
        actions.append(f"skip existing {dst}")
        if reports is not None:
            _record(
                reports,
                dst,
                OUTCOME_PRESERVED,
                "directory exists; left untouched (use --force to replace)",
            )
        return
    backup = None
    if dst.exists():
        backup = _backup_path(dst)
        if not dry_run:
            shutil.move(str(dst), str(backup))
    actions.append(f"copy {src} -> {dst}" + (f" (backup {backup.name})" if backup else ""))
    if reports is not None:
        _record(
            reports,
            dst,
            OUTCOME_OVERWRITTEN if backup else OUTCOME_CREATED,
            f"backup {backup.name}" if backup else "",
        )
    if dry_run:
        return
    shutil.copytree(src, dst)


def _write_text(
    path: Path,
    content: str,
    *,
    force: bool,
    dry_run: bool,
    actions: List[str],
    reports: Optional[List[FileReport]] = None,
) -> None:
    """Write a generated file.

    Brownfield-safe default: a pre-existing file is PRESERVED (never silently
    clobbered) unless ``--force`` is set. ``--force`` overwrites, but first takes
    a timestamped backup. New files are always created.
    """
    if not path.exists():
        actions.append(f"write {path}")
        if reports is not None:
            _record(reports, path, OUTCOME_CREATED)
        if dry_run:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return

    if not force:
        actions.append(f"preserve existing {path}")
        if reports is not None:
            _record(
                reports,
                path,
                OUTCOME_PRESERVED,
                "exists; left untouched (use --force to overwrite)",
            )
        return

    # --force: full overwrite, but never without a backup.
    backup = _backup_file(path, dry_run=dry_run)
    detail = f"backup {backup.name}" if backup else ""
    actions.append(f"overwrite {path}" + (f" (backup {backup.name})" if backup else ""))
    if reports is not None:
        _record(reports, path, OUTCOME_OVERWRITTEN, detail)
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _overlay_text(
    path: Path,
    overlay: str,
    *,
    force: bool,
    dry_run: bool,
    actions: List[str],
    reports: List[FileReport],
    full_content: Optional[str] = None,
) -> None:
    """Non-destructively overlay SicarioSpec content onto an existing file.

    - If the file does not exist: create it with ``full_content`` (a complete
      standalone document) when provided, else with the overlay block.
    - If the file exists and already contains the overlay marker: idempotent —
      do nothing (re-run safe).
    - If the file exists without the marker: back it up and APPEND the overlay
      block, delimited by clear begin/end markers. The user's content is kept
      verbatim above the overlay.
    - With ``--force``: overwrite with ``full_content`` (after backup), matching
      legacy clobber behavior for callers that explicitly ask for it.
    """
    if not path.exists():
        body = full_content if full_content is not None else overlay
        actions.append(f"write {path}")
        _record(reports, path, OUTCOME_CREATED)
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        return

    if force and full_content is not None:
        backup = _backup_file(path, dry_run=dry_run)
        actions.append(f"overwrite {path}" + (f" (backup {backup.name})" if backup else ""))
        _record(reports, path, OUTCOME_OVERWRITTEN, f"backup {backup.name}" if backup else "")
        if not dry_run:
            path.write_text(full_content, encoding="utf-8")
        return

    existing = path.read_text(encoding="utf-8")
    if SICARIO_OVERLAY_BEGIN in existing:
        actions.append(f"overlay already present in {path}")
        _record(reports, path, OUTCOME_PRESERVED, "overlay already present (idempotent)")
        return

    backup = _backup_file(path, dry_run=dry_run)
    actions.append(f"overlay {path}" + (f" (backup {backup.name})" if backup else ""))
    _record(
        reports,
        path,
        OUTCOME_MERGED,
        f"appended overlay; backup {backup.name}" if backup else "appended overlay",
    )
    if dry_run:
        return
    separator = "" if existing.endswith("\n") else "\n"
    path.write_text(existing + separator + "\n" + overlay, encoding="utf-8")


def _print_report(reports: Sequence[FileReport], *, dry_run: bool, force: bool) -> None:
    """Print a clear per-file REPORT: created / merged-overlaid / preserved / overwritten."""
    if not reports:
        return
    header = "SicarioSpec adoption report"
    if dry_run:
        header += " (dry-run preview — nothing written)"
    elif force:
        header += " (--force full-overwrite; backups taken)"
    else:
        header += " (brownfield-safe: merge/overlay/preserve)"
    print("")
    print(header)
    print("-" * len(header))
    counts: "dict[str, int]" = {}
    for report in reports:
        counts[report.outcome] = counts.get(report.outcome, 0) + 1
        suffix = f" — {report.detail}" if report.detail else ""
        print(f"  [{report.outcome}] {report.path}{suffix}")
    summary = ", ".join(f"{value} {key}" for key, value in sorted(counts.items()))
    print(f"  summary: {summary}")
