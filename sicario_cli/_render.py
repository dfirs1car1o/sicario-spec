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

# Stamped onto files ``_overlay_text`` creates from ``full_content`` (see below).
# Unlike the appended overlay block, a freshly-created file's governed content IS
# the whole file -- there is no separate section to add, so this explanation is
# wrapped entirely in HTML comments (one marker per line) so it renders as
# nothing in Markdown and stays inert if the file is later copied verbatim (e.g.
# a Spec Kit template copied into a real spec/plan/tasks document).
SICARIO_OVERLAY_STAMP_NOTE = (
    "<!-- SicarioSpec wrote this file's full governed content directly; there "
    "is no separate section to overlay. This marker exists only so a later "
    "`sicario init`/`apply` run recognizes this file as its own output instead "
    "of treating it as pre-existing content to merge (see issue #70). -->"
)

# Timestamped backups are verbatim copies of the adopting repo's own files, so
# they can carry secrets or internal content. They must never become committable.
BACKUP_IGNORE_PATTERN = "*.sicario-bak.*"
BACKUP_IGNORE_COMMENT = "# SicarioSpec timestamped backups (may contain pre-existing secrets)"


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


def _backup_rule_is_effective(text: str, pattern: str) -> bool:
    """Is ``pattern`` the rule that actually decides backup files in this .gitignore?

    Presence is not protection. Git applies the LAST matching pattern, so a file
    that lists ``*.sicario-bak.*`` and then a negation such as
    ``!keep.sicario-bak.20260101T000000Z`` re-includes backups despite the rule
    being present. Scanning for mere presence would report that file as safe.

    Any negation mentioning the backup marker is treated as re-including, which is
    deliberately conservative: reimplementing gitignore matching would be worse than
    occasionally appending a rule that was already sufficient.
    """
    marker = pattern.strip("*.")
    decisive = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == pattern:
            decisive = True
        elif line.startswith("!") and marker in line:
            decisive = False
    return decisive


def _ensure_gitignore_rule(
    target: Path,
    *,
    pattern: str = BACKUP_IGNORE_PATTERN,
    comment: str = BACKUP_IGNORE_COMMENT,
    dry_run: bool,
    actions: List[str],
    reports: Optional[List[FileReport]] = None,
) -> None:
    """Idempotently ensure ``pattern`` actually ignores backups in the target repo.

    Backups taken by ``sicario init`` are verbatim copies of the adopting repo's
    pre-existing constitution, instruction files, and Spec Kit templates. They can
    therefore contain secrets or internal content that was never meant to be
    committed. This rule is written BEFORE the first backup is taken so the
    protection exists before the risk does.

    Never clobbers. An existing .gitignore is only appended to, and only when the
    rule is not already the effective one, so re-running ``init`` is a no-op. The
    original bytes are preserved verbatim, including line endings.

    Known limitation: a nested ``.gitignore`` in a subdirectory can negate this rule
    for that subtree, and this function only manages the target's root .gitignore.
    Detecting that would mean walking the whole tree on every init for an
    adversarial case; it is documented rather than defended against.
    """
    gitignore = target / ".gitignore"
    block = f"{comment}\n{pattern}\n"

    # Writing through a symlink would modify a file outside the project being
    # initialized. Refuse and say so rather than silently editing someone else's file.
    if gitignore.is_symlink():
        actions.append(f"skip {gitignore}: is a symlink; refusing to write through it")
        if reports is not None:
            _record(
                reports,
                gitignore,
                OUTCOME_SKIPPED,
                f"symlink; add '{pattern}' manually to protect backups",
            )
        return

    if gitignore.exists():
        # Read bytes, not text: text mode normalizes CRLF, which would silently
        # rewrite every line of a CRLF file just to append one rule.
        raw = gitignore.read_bytes()
        existing = raw.decode("utf-8")
        newline = "\r\n" if b"\r\n" in raw else "\n"

        if _backup_rule_is_effective(existing, pattern):
            actions.append(f"gitignore already ignores {pattern}")
            if reports is not None:
                _record(reports, gitignore, OUTCOME_PRESERVED, f"already ignores {pattern}")
            return

        marker = pattern.strip("*.")
        negated = any(
            line.strip().startswith("!") and marker in line for line in existing.splitlines()
        )
        detail = (
            f"appended ignore rule {pattern} after a negation that re-included backups"
            if negated
            else f"appended ignore rule {pattern}"
        )
        actions.append(f"append ignore rule {pattern} to {gitignore}")
        if reports is not None:
            _record(reports, gitignore, OUTCOME_MERGED, detail)
        if dry_run:
            return
        # Build with "\n" then convert once, so a CRLF file stays CRLF and an LF file
        # stays LF without rewriting any pre-existing line.
        separator = "" if existing.endswith("\n") else "\n"
        addition = (separator + "\n" + block).replace("\n", newline)
        gitignore.write_bytes(raw + addition.encode("utf-8"))
        return

    actions.append(f"write {gitignore}")
    if reports is not None:
        _record(reports, gitignore, OUTCOME_CREATED, f"ignore rule {pattern}")
    if dry_run:
        return
    gitignore.parent.mkdir(parents=True, exist_ok=True)
    gitignore.write_text(block, encoding="utf-8")


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


def _stamp_full_content(full_content: str) -> str:
    """Stamp the overlay marker onto content written via the full-content path.

    ``_overlay_text``'s idempotency check keys on ``SICARIO_OVERLAY_BEGIN``
    being present in the file (see below). Previously, a file created straight
    from ``full_content`` -- a SicarioSpec-authored template or instruction
    document -- carried no such marker, so the very next run treated it as
    pre-existing user content and appended the overlay block on top of it,
    taking a needless backup (issue #70: run 2 after a fresh brownfield OR
    greenfield init reported spurious ``merged-overlaid`` files).

    Stamping the marker here makes a file the tool writes recognizable to the
    tool on the next run, matching the marker's stated meaning: the overlay
    has been applied (here, by inclusion in the full content rather than by
    appending a separate section).
    """
    separator = "" if full_content.endswith("\n") else "\n"
    return (
        f"{full_content}{separator}\n"
        f"{SICARIO_OVERLAY_BEGIN}\n"
        f"{SICARIO_OVERLAY_STAMP_NOTE}\n"
        f"{SICARIO_OVERLAY_END}\n"
    )


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
      standalone document), stamped with the overlay marker so a later run
      recognizes it as SicarioSpec's own output (see ``_stamp_full_content``),
      when provided, else with the overlay block.
    - If the file exists and already contains the overlay marker: idempotent —
      do nothing (re-run safe).
    - If the file exists without the marker: back it up and APPEND the overlay
      block, delimited by clear begin/end markers. The user's content is kept
      verbatim above the overlay.
    - With ``--force``: overwrite with ``full_content`` (after backup), stamped
      the same way, matching legacy clobber behavior for callers that
      explicitly ask for it while keeping the result idempotent on the next
      plain re-run.
    """
    if not path.exists():
        body = _stamp_full_content(full_content) if full_content is not None else overlay
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
            path.write_text(_stamp_full_content(full_content), encoding="utf-8")
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
