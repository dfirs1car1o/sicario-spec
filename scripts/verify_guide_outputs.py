#!/usr/bin/env python3
"""FR-051 docs verification runner.

Re-executes the *paired* commands of every ``verified`` output block quoted
in ``docs/guides/*.md`` and ``docs/playbooks/*.md``, in one fresh scratch
repository per guide, and diffs the observed output (after applying only the
block's own declared normalizations) against the quoted text. Blocks marked
``illustrative`` are skipped (never diffed) but counted. A ``verified`` block
with no command paired to it is a failure: "verified but not verifiable" —
see FR-050/FR-051 in specs/007-onboarding-guides-and-playbooks/spec.md.

SEC-C-007: this script is a SEPARATE check with its own exit code. It never
imports, calls, or otherwise touches ``sicario_cli``'s verdict path.

This runner enforces exactly two containment properties around the
disposable scratch repo it builds per guide, and claims no more than that:

1. After every ``sicario-cmd`` fence executes, the fence's resulting working
   directory (read back from a ``pwd`` marker, to track ``cd``) must still
   resolve under that guide's scratch root. If it does not, the guide fails
   with a structural error and no further fence in that guide is executed.
2. Every ``sicario-write`` destination is resolved (parent traversal and
   all) before anything is written, and rejected as a structural error —
   again halting the guide — if the resolved path does not fall under the
   scratch root.

Neither check inspects the body of a ``bash`` fence: arbitrary shell inside
the scratch repo remains executable by design (that is the whole point of
``sicario-cmd``). A fence that writes outside the scratch root via an
absolute path or a symlink baked into its own script — rather than via a
``cd`` this runner tracks or a declared ``sicario-write`` — is not caught by
either property. ``sicario verify`` itself is completely unaffected by
anything in this file.

Stdlib only, on purpose: this runs in CI next to the gate, and the gate's
own dependency discipline (``dependencies = []`` in pyproject.toml) applies
here too even though this script never feeds the verdict path.

## The pairing grammar (additive to the existing marker grammar)

The existing grammar (FR-050) marks *output* fences:

    ```text title="..." sicario-output=verified|illustrative sicario-block=<slug>/<id> [sicario-normalize=paths,line-numbers] [sicario-stream=stdout|stderr]
    ...quoted output...
    ```

This script adds three attributes, all additive and all optional, used only
by this runner (a human reader can ignore every one of them):

- ``sicario-cmd=<slug>/<id>[,<slug>/<id>...]`` on a ```bash fence: execute
  this fence's literal content as one shell script, in document order, in
  the guide's scratch repo. Diff its stdout/stderr against each named
  output block (illustrative targets are executed for state but never
  diffed). ``sicario-stream`` on the *output* fence selects which stream of
  this one execution it is compared against (default ``stdout``); this is
  how one command that writes to both streams (``--format json``, whose
  document goes to stdout and whose summary line goes to stderr) pairs to
  two separate quoted blocks.
- ``sicario-cmd=setup`` on a ```bash fence: execute for state only (e.g. a
  ``mkdir``, an ``sicario init`` whose own output block is illustrative but
  whose *effect* later verified blocks depend on). Never diffed, never
  counted against the verified/illustrative totals.
- ``sicario-write=<repo-relative-path>`` on any fenced block: write that
  fence's literal content verbatim to the given path in the scratch repo
  (parent directories created as needed), in document order. Used for the
  guide's shown-in-full input files (a rule JSON, a markdown fixture) that
  the reader is told to create by hand.

A ```bash fence with none of these attributes (a `pip install` line, a
`specify` bundle command, an illustrative dry-run) is simply not executed —
it is outside the self-contained, re-executable sequence this runner scopes
itself to.
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GUIDE_GLOBS = ("docs/guides/*.md", "docs/playbooks/*.md")

FENCE_OPEN_RE = re.compile(r"^(?P<indent>[ \t]*)```(?P<lang>[A-Za-z0-9_-]*)(?P<rest>.*)$")
FENCE_CLOSE_RE = re.compile(r"^[ \t]*```[ \t]*$")
ATTR_RE = re.compile(r'([A-Za-z][\w-]*)=("(?:[^"\\]|\\.)*"|\S+)')
FRONTMATTER_LINE_RE = re.compile(r"^([A-Za-z][\w-]*):\s*(.*)$")

# The only ``sicario-normalize`` keys apply_normalizations() knows how to
# apply. Anything else is a structural error (F4): a typo'd normalize key
# must not silently pass a block whose diff was never actually normalized.
KNOWN_NORMALIZE_KEYS = {"line-numbers", "paths"}

# The only legal ``sicario-stream`` values (F11). Anything else must not
# silently fall through to stderr.
KNOWN_STREAMS = {"stdout", "stderr"}


# --------------------------------------------------------------------------
# Markdown parsing (no third-party dependency: a small, purpose-built parser)
# --------------------------------------------------------------------------


@dataclass
class Fence:
    lang: str
    attrs: Dict[str, str]
    content: str
    line_no: int


def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    """Split leading ``---``-delimited YAML-ish frontmatter from the body.

    Only flat ``key: value`` scalars are needed by this script (guide-slug,
    captured-version); a hand-rolled parser keeps this stdlib-only.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    meta: Dict[str, str] = {}
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
        m = FRONTMATTER_LINE_RE.match(lines[i])
        if m:
            key, value = m.group(1), m.group(2).strip()
            if len(value) >= 2 and value[0] == value[-1] == '"':
                value = value[1:-1]
            meta[key] = value
    if end is None:
        return {}, text
    body = "\n".join(lines[end + 1 :])
    return meta, body


def _parse_attrs(rest: str) -> Dict[str, str]:
    attrs = {}
    for key, value in ATTR_RE.findall(rest):
        if len(value) >= 2 and value[0] == value[-1] == '"':
            value = value[1:-1]
        attrs[key] = value
    return attrs


def iter_fences(body: str) -> List[Fence]:
    lines = body.splitlines()
    fences: List[Fence] = []
    i = 0
    while i < len(lines):
        m = FENCE_OPEN_RE.match(lines[i])
        if not m:
            i += 1
            continue
        indent = m.group("indent")
        lang = m.group("lang")
        attrs = _parse_attrs(m.group("rest"))
        start_line = i + 1
        content_lines = []
        i += 1
        while i < len(lines) and not FENCE_CLOSE_RE.match(lines[i]):
            line = lines[i]
            if indent and line.startswith(indent):
                line = line[len(indent) :]
            content_lines.append(line)
            i += 1
        # advance past the closing fence line, if one was found
        if i < len(lines):
            i += 1
        fences.append(
            Fence(
                lang=lang, attrs=attrs, content="\n".join(content_lines) + "\n", line_no=start_line
            )
        )
    return fences


# --------------------------------------------------------------------------
# Normalizations (FR-051): applied ONLY as declared on the output block
# --------------------------------------------------------------------------


def normalize_line_numbers(text: str) -> str:
    """Replace ``:<digits>:`` (a grepped line number) with a stable token.

    Applied symmetrically to both the observed and the quoted text before
    comparison, since the reference run's line number is itself just a
    capture of something that "shifts with repository state" per the
    guides' own stated caveat — not a value this runner should have to
    reproduce exactly.
    """
    return re.sub(r":\d+:", ":<LINE>:", text)


def normalize_paths(text: str, real_root: str, placeholder: str) -> str:
    """Replace the scratch repo's real absolute path with the guide's
    documented placeholder (``~/<reference-run-repository>``). Applied only
    to the observed text: the quoted text already contains the placeholder.
    """
    if not real_root:
        return text
    resolved = str(Path(real_root).resolve())
    text = text.replace(resolved, placeholder)
    return text.replace(real_root, placeholder)


def apply_normalizations(
    observed: str, quoted: str, normalize_keys: List[str], real_root: str, placeholder: str
) -> Tuple[str, str]:
    for key in normalize_keys:
        key = key.strip()
        if not key:
            continue
        if key == "line-numbers":
            observed = normalize_line_numbers(observed)
            quoted = normalize_line_numbers(quoted)
        elif key == "paths":
            observed = normalize_paths(observed, real_root, placeholder)
        # Any other key is unreachable here: check_guide() validates every
        # output block's sicario-normalize keys against KNOWN_NORMALIZE_KEYS
        # up front and reports an unknown one as a structural error before
        # execution — and thus before apply_normalizations is ever called.
    return observed, quoted


# --------------------------------------------------------------------------
# Execution
# --------------------------------------------------------------------------


def make_shim(bin_dir: Path) -> None:
    """A ``sicario`` on PATH that always runs *this checkout's* CLI, so a
    literal ``sicario ...`` command in a guide exercises the code under
    test — never a pip-installed copy, never a stray PATH entry."""
    script = bin_dir / "sicario"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        f"sys.path.insert(0, {str(REPO_ROOT)!r})\n"
        "from sicario_cli.cli import main\n"
        "sys.exit(main(sys.argv[1:]))\n"
    )
    script.chmod(0o755)


@dataclass
class ExecResult:
    stdout: str
    stderr: str
    returncode: int


def run_fence_script(
    content: str, cwd: Path, env: Dict[str, str], cwd_marker: Path
) -> Tuple[ExecResult, str]:
    script = content + f"\npwd > {shlex.quote(str(cwd_marker))}\n"
    proc = subprocess.run(
        ["bash", "-c", script],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    new_cwd = cwd.as_posix()
    if cwd_marker.exists():
        recorded = cwd_marker.read_text().strip()
        if recorded:
            new_cwd = recorded
        cwd_marker.unlink()
    return ExecResult(stdout=proc.stdout, stderr=proc.stderr, returncode=proc.returncode), new_cwd


def _is_contained(path: Path, root: Path) -> bool:
    """True if ``path`` resolves to ``root`` itself or somewhere under it.

    Both arguments must already be resolved (symlinks followed) — the
    caller is responsible, since ``root`` is typically resolved once per
    guide and reused across many calls.
    """
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


# --------------------------------------------------------------------------
# Guide model
# --------------------------------------------------------------------------


@dataclass
class Mismatch:
    block_id: str
    line_no: int
    diff: str


@dataclass
class GuideReport:
    path: Path
    slug: str
    verified_reexecuted: int = 0
    verified_failed: List[Mismatch] = field(default_factory=list)
    illustrative_skipped: int = 0
    unpaired_verified: List[str] = field(default_factory=list)
    structural_errors: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (self.verified_failed or self.unpaired_verified or self.structural_errors)


def _installed_version() -> str:
    version_file = REPO_ROOT / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    sys.path.insert(0, str(REPO_ROOT))
    from sicario_cli.version import __version__  # type: ignore

    return __version__


def _check_captured_version(
    path: Path, meta: Dict[str, str], installed_version: str, report: GuideReport
) -> None:
    """FR-052's enforcement hook: a release that bumps VERSION without
    updating the guides must fail loudly here, not slide through."""
    captured_version = meta.get("captured-version")
    if not captured_version:
        report.structural_errors.append(f"{path}: missing 'captured-version' in frontmatter")
    elif captured_version != installed_version:
        report.structural_errors.append(
            f"{path}: captured-version {captured_version!r} does not match "
            f"installed VERSION {installed_version!r} — this guide's captures "
            f"are stale for the current release (FR-052)"
        )


def _validate_output_block(path: Path, fence: Fence, output_blocks: Dict[str, Fence], report: GuideReport) -> None:
    """Validate one fence's sicario-block/sicario-output/sicario-normalize/
    sicario-stream attributes (FR-050) and, if valid, add it to
    ``output_blocks``."""
    block_id = fence.attrs.get("sicario-block")
    marker = fence.attrs.get("sicario-output")
    if block_id is None:
        # F2: a fence declaring sicario-output=verified with no
        # sicario-block would otherwise be skipped here entirely — its
        # quoted text is then never paired, never diffed, and never
        # reported as unpaired either, because unpaired-verified detection
        # below only walks output_blocks. That is a silent hole, not a
        # pass: flag it as its own structural error.
        if marker == "verified":
            report.structural_errors.append(
                f"{path}:{fence.line_no}: sicario-output=verified but no "
                f"sicario-block — verified but unidentifiable"
            )
        return
    if marker not in ("verified", "illustrative"):
        report.structural_errors.append(
            f"{path}:{fence.line_no}: block {block_id!r} carries "
            f"sicario-block but no valid sicario-output marker (FR-050)"
        )
        return
    # F1: a duplicate sicario-block id means an earlier verified/
    # illustrative fence is silently dropped and never diffed even though
    # it counts as paired — last-wins with no detection. Both locations
    # must be named so a guide author can tell which one to rename.
    if block_id in output_blocks:
        report.structural_errors.append(
            f"{path}:{fence.line_no}: duplicate sicario-block id "
            f"{block_id!r} (already defined at "
            f"{path}:{output_blocks[block_id].line_no})"
        )
        return
    normalize_attr = fence.attrs.get("sicario-normalize", "")
    for key in normalize_attr.split(","):
        key = key.strip()
        if key and key not in KNOWN_NORMALIZE_KEYS:
            # F4: an unknown sicario-normalize key was silently ignored
            # (neither applied nor reported) — make the module's own claim
            # about that true.
            report.structural_errors.append(
                f"{path}:{fence.line_no}: block {block_id!r} declares "
                f"unknown sicario-normalize key {key!r} (known: "
                f"{sorted(KNOWN_NORMALIZE_KEYS)})"
            )
    stream_attr = fence.attrs.get("sicario-stream")
    if stream_attr is not None and stream_attr not in KNOWN_STREAMS:
        # F11: anything other than exactly "stdout" fell through to stderr
        # silently.
        report.structural_errors.append(
            f"{path}:{fence.line_no}: block {block_id!r} declares invalid "
            f"sicario-stream={stream_attr!r} (must be exactly 'stdout' or "
            f"'stderr')"
        )
    output_blocks[block_id] = fence


def _build_output_blocks(path: Path, fences: List[Fence], report: GuideReport) -> Dict[str, Fence]:
    """Build the block-id -> output fence map, validating FR-050 along the way."""
    output_blocks: Dict[str, Fence] = {}
    for fence in fences:
        _validate_output_block(path, fence, output_blocks, report)
    return output_blocks


def _pair_cmd_fences(
    path: Path, fences: List[Fence], output_blocks: Dict[str, Fence], report: GuideReport
) -> "set[str]":
    """Match every sicario-cmd fence to the output blocks it claims.

    Returns the set of block ids claimed by some sicario-cmd fence.
    """
    paired_block_ids: "set[str]" = set()
    claimed_by: Dict[str, int] = {}
    for fence in fences:
        cmd_attr = fence.attrs.get("sicario-cmd")
        if not cmd_attr or cmd_attr == "setup":
            continue
        for block_id in cmd_attr.split(","):
            block_id = block_id.strip()
            if block_id not in output_blocks:
                report.structural_errors.append(
                    f"{path}:{fence.line_no}: sicario-cmd names unknown block {block_id!r}"
                )
                continue
            # F1 (part two): two different sicario-cmd fences both claiming
            # the same output block is exactly as ambiguous as two output
            # fences sharing an id — name both claiming locations.
            if block_id in claimed_by and claimed_by[block_id] != fence.line_no:
                report.structural_errors.append(
                    f"{path}:{fence.line_no}: sicario-cmd claims block "
                    f"{block_id!r} already claimed by the fence at "
                    f"{path}:{claimed_by[block_id]}"
                )
                continue
            claimed_by[block_id] = fence.line_no
            paired_block_ids.add(block_id)
    return paired_block_ids


def _mark_unpaired_verified(
    path: Path, output_blocks: Dict[str, Fence], paired_block_ids: "set[str]", report: GuideReport
) -> None:
    for block_id, fence in output_blocks.items():
        if fence.attrs.get("sicario-output") == "verified" and block_id not in paired_block_ids:
            report.unpaired_verified.append(f"{path}:{fence.line_no}: {block_id}")


def _handle_write_fence(
    fence: Fence, write_path: str, cwd: Path, scratch_root_resolved: Path, path: Path, report: GuideReport
) -> bool:
    """Write a sicario-write fence's content verbatim under the scratch root.

    Returns True if the guide must abort (a structural error was recorded).
    """
    target = (cwd / write_path).resolve()
    if not _is_contained(target, scratch_root_resolved):
        # F3(b): a sicario-write destination that resolves outside scratch
        # (``../x``, or an absolute path) is refused rather than written —
        # the guide fails instead of leaving a file somewhere it should
        # never reach.
        report.structural_errors.append(
            f"{path}:{fence.line_no}: sicario-write={write_path!r} resolves "
            f"to {target} which is outside the scratch root "
            f"({scratch_root_resolved}) — refusing to write"
        )
        return True
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(fence.content)
    return False


def _advance_cwd_or_abort(
    new_cwd: str, scratch_root_resolved: Path, fence: Fence, path: Path, report: GuideReport
) -> "Tuple[Path, bool]":
    """Resolve a fence's post-execution cwd and confirm it stayed contained.

    Returns (resolved cwd, aborted). The caller only adopts the resolved cwd
    when ``aborted`` is False.
    """
    # Constructing this path from fence-derived data is the point: it exists
    # solely to be validated by the containment check on the next line,
    # which refuses anything outside the scratch root before any later
    # fence can use it. (Sonar S6549 flags the construction; the sink IS the
    # validator.)
    new_cwd_resolved = Path(new_cwd).resolve()  # NOSONAR
    if not _is_contained(new_cwd_resolved, scratch_root_resolved):
        # F3(a): a fence that `cd`s (directly, or via a script it runs)
        # somewhere outside the scratch root — e.g. into the actual
        # repository checkout — must not be allowed to keep running there;
        # every later sicario-write in this guide would inherit that
        # escaped cwd as its base.
        report.structural_errors.append(
            f"{path}:{fence.line_no}: fence's working directory left the "
            f"scratch root (now {new_cwd_resolved}, root is "
            f"{scratch_root_resolved}) — refusing to continue"
        )
        return new_cwd_resolved, True
    return new_cwd_resolved, False


def _group_blocks_by_stream(
    cmd_attr: str, output_blocks: Dict[str, Fence], report: GuideReport
) -> Dict[str, List[str]]:
    """Group a sicario-cmd fence's paired output blocks by which stream they
    check against.

    Several output blocks can come from ONE execution (a `verify` block on
    stdout plus a separate `echo $?` block also on stdout; or a `--format
    json` document on stdout paired with its stderr summary line as a second
    block). Illustrative targets are counted here and never diffed.
    """
    by_stream: Dict[str, List[str]] = {}
    for block_id in cmd_attr.split(","):
        block_id = block_id.strip()
        out_fence = output_blocks.get(block_id)
        if out_fence is None:
            continue  # already reported as a structural error above
        if out_fence.attrs.get("sicario-output") == "illustrative":
            report.illustrative_skipped += 1
            continue
        stream = out_fence.attrs.get("sicario-stream", "stdout")
        by_stream.setdefault(stream, []).append(block_id)
    return by_stream


def _compare_stream(
    stream: str,
    block_ids: List[str],
    result: ExecResult,
    output_blocks: Dict[str, Fence],
    scratch_root: Path,
    placeholder: str,
    report: GuideReport,
) -> None:
    """Diff one stream's concatenated quoted blocks against the observed output."""
    observed = result.stdout if stream == "stdout" else result.stderr
    quoted = "".join(output_blocks[b].content for b in block_ids)
    normalize_keys: List[str] = []
    for b in block_ids:
        normalize_keys.extend(output_blocks[b].attrs.get("sicario-normalize", "").split(","))
    observed_n, quoted_n = apply_normalizations(
        observed, quoted, normalize_keys, str(scratch_root), placeholder
    )
    if observed_n.rstrip("\n") == quoted_n.rstrip("\n"):
        report.verified_reexecuted += len(block_ids)
        return
    diff = "\n".join(
        difflib.unified_diff(
            quoted_n.splitlines(),
            observed_n.splitlines(),
            fromfile="quoted",
            tofile="observed",
            lineterm="",
        )
    )
    first_fence = output_blocks[block_ids[0]]
    report.verified_failed.append(
        Mismatch(block_id=",".join(block_ids), line_no=first_fence.line_no, diff=diff)
    )


def _handle_cmd_fence(
    fence: Fence,
    idx: int,
    cwd: Path,
    scratch_root_resolved: Path,
    env: Dict[str, str],
    marker_dir: Path,
    output_blocks: Dict[str, Fence],
    scratch_root: Path,
    placeholder: str,
    path: Path,
    report: GuideReport,
) -> "Tuple[Path, bool]":
    """Execute one sicario-cmd fence: advance cwd, handle setup-vs-paired,
    diff paired output blocks. Returns (new cwd, aborted)."""
    cmd_attr = fence.attrs["sicario-cmd"]
    marker = marker_dir / f"cwd-{idx}.txt"
    result, new_cwd = run_fence_script(fence.content, cwd, env, marker)
    new_cwd_resolved, aborted = _advance_cwd_or_abort(
        new_cwd, scratch_root_resolved, fence, path, report
    )
    if aborted:
        return cwd, True

    if cmd_attr == "setup":
        if result.returncode != 0:
            # F10: a failing setup fence used to be silent — later verified
            # fences would then run against whatever partial state setup
            # left behind and fail with a confusing diff instead of the
            # real, upstream cause.
            report.structural_errors.append(
                f"{path}:{fence.line_no}: sicario-cmd=setup fence exited "
                f"{result.returncode} (state-prep failure) — stderr:\n"
                f"{result.stderr}"
            )
            return new_cwd_resolved, True
        return new_cwd_resolved, False

    # Non-setup (paired) sicario-cmd fences deliberately do NOT check
    # returncode: many guides pair a fence that exits non-zero by design —
    # a staged gate failure is itself the pedagogy being demonstrated. The
    # quoted output block — including any quoted `echo $?` line — is the
    # contract those fences are verified against, not the process exit code.
    by_stream = _group_blocks_by_stream(cmd_attr, output_blocks, report)
    for stream, block_ids in by_stream.items():
        _compare_stream(stream, block_ids, result, output_blocks, scratch_root, placeholder, report)
    return new_cwd_resolved, False


def _run_fences(
    fences: List[Fence],
    scratch_root: Path,
    marker_dir: Path,
    env: Dict[str, str],
    output_blocks: Dict[str, Fence],
    placeholder: str,
    path: Path,
    report: GuideReport,
) -> bool:
    """Execute every fence in document order. Returns whether execution
    aborted partway through (F3/F10)."""
    # F3: the scratch root is the only place any fence may leave a trace.
    # Resolved once so every containment check below compares against the
    # same, symlink-free root (macOS's /tmp -> /private/tmp would otherwise
    # make a same-directory path look "outside").
    scratch_root_resolved = scratch_root.resolve()

    cwd = scratch_root
    for idx, fence in enumerate(fences):
        write_path = fence.attrs.get("sicario-write")
        if write_path:
            if _handle_write_fence(fence, write_path, cwd, scratch_root_resolved, path, report):
                return True
            continue

        cmd_attr = fence.attrs.get("sicario-cmd")
        if not cmd_attr:
            continue

        cwd, aborted = _handle_cmd_fence(
            fence,
            idx,
            cwd,
            scratch_root_resolved,
            env,
            marker_dir,
            output_blocks,
            scratch_root,
            placeholder,
            path,
            report,
        )
        if aborted:
            return True

    return False


def _count_unreached_illustrative(
    output_blocks: Dict[str, Fence], paired_block_ids: "set[str]", report: GuideReport
) -> None:
    """Count illustrative blocks never reached via a sicario-cmd execution."""
    for block_id, fence in output_blocks.items():
        if fence.attrs.get("sicario-output") == "illustrative" and block_id not in paired_block_ids:
            report.illustrative_skipped += 1


def check_guide(path: Path, installed_version: str, keep_scratch: bool = False) -> GuideReport:
    text = path.read_text()
    meta, body = parse_frontmatter(text)
    slug = meta.get("guide-slug", path.stem)
    report = GuideReport(path=path, slug=slug)

    _check_captured_version(path, meta, installed_version, report)

    reference_run_repository = meta.get("reference-run-repository", "")
    placeholder = f"~/{reference_run_repository}" if reference_run_repository else ""

    fences = iter_fences(body)
    output_blocks = _build_output_blocks(path, fences, report)
    paired_block_ids = _pair_cmd_fences(path, fences, output_blocks, report)
    _mark_unpaired_verified(path, output_blocks, paired_block_ids, report)

    if report.structural_errors:
        # A structurally broken guide cannot be safely executed (unknown
        # block references, bad markers) — report and stop before running
        # anything.
        return report

    scratch_root = Path(tempfile.mkdtemp(prefix=f"guide-{slug}-"))
    marker_dir = Path(tempfile.mkdtemp(prefix=f"guide-{slug}-markers-"))
    bin_dir = Path(tempfile.mkdtemp(prefix=f"guide-{slug}-bin-"))
    try:
        make_shim(bin_dir)
        env = dict(os.environ)
        env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env.pop("SICARIO_ASSET_ROOT", None)

        aborted = _run_fences(
            fences, scratch_root, marker_dir, env, output_blocks, placeholder, path, report
        )

        # Any output block never reached via a sicario-cmd execution (e.g.
        # illustrative blocks with no pairing at all) is still counted —
        # unless execution was aborted partway through (F3/F10), in which
        # case counts past the abort point are meaningless.
        if not aborted:
            _count_unreached_illustrative(output_blocks, paired_block_ids, report)
    finally:
        if not keep_scratch:
            shutil.rmtree(scratch_root, ignore_errors=True)
        shutil.rmtree(marker_dir, ignore_errors=True)
        shutil.rmtree(bin_dir, ignore_errors=True)

    return report


def _display_path(path: Path) -> Path:
    try:
        return path.relative_to(REPO_ROOT)
    except ValueError:
        return path


def format_report(report: GuideReport) -> str:
    lines = [f"== {_display_path(report.path)} (slug: {report.slug}) =="]
    for err in report.structural_errors:
        lines.append(f"  STRUCTURAL ERROR: {err}")
    for missing in report.unpaired_verified:
        lines.append(f"  FAIL (verified but not verifiable — no sicario-cmd pairing): {missing}")
    for mismatch in report.verified_failed:
        lines.append(f"  FAIL {mismatch.block_id} (line {mismatch.line_no}):")
        for diff_line in mismatch.diff.splitlines():
            lines.append(f"    {diff_line}")
    lines.append(
        f"  summary: {report.verified_reexecuted} verified re-executed, "
        f"{report.illustrative_skipped} illustrative skipped, "
        f"{len(report.verified_failed)} mismatch(es), "
        f"{len(report.unpaired_verified)} unpaired verified block(s), "
        f"{len(report.structural_errors)} structural error(s)"
    )
    return "\n".join(lines)


def discover_guides() -> List[Path]:
    paths: List[Path] = []
    for pattern in DEFAULT_GUIDE_GLOBS:
        paths.extend(sorted(REPO_ROOT.glob(pattern)))
    return paths


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "paths",
        nargs="*",
        help="Guide markdown files to check (default: all shipped guides/playbooks)",
    )
    parser.add_argument(
        "--keep-scratch",
        action="store_true",
        help="Do not delete the per-guide scratch repos (debugging)",
    )
    args = parser.parse_args(argv)

    guides = [Path(p).resolve() for p in args.paths] if args.paths else discover_guides()
    if not guides:
        print("no guides found", file=sys.stderr)
        return 1

    installed_version = _installed_version()
    reports = [check_guide(g, installed_version, keep_scratch=args.keep_scratch) for g in guides]

    ok = True
    total_verified = 0
    total_illustrative = 0
    total_failed = 0
    total_unpaired = 0
    total_struct = 0
    for report in reports:
        print(format_report(report))
        total_verified += report.verified_reexecuted
        total_illustrative += report.illustrative_skipped
        total_failed += len(report.verified_failed)
        total_unpaired += len(report.unpaired_verified)
        total_struct += len(report.structural_errors)
        if not report.ok:
            ok = False

    print(
        f"\nTOTAL across {len(reports)} guide(s): {total_verified} verified re-executed, "
        f"{total_illustrative} illustrative skipped, {total_failed} mismatch(es), "
        f"{total_unpaired} unpaired verified block(s), {total_struct} structural error(s)"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
