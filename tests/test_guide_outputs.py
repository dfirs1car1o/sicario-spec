"""Tests for scripts/verify_guide_outputs.py (FR-051 docs verification runner).

SEC-C-007: this test file exercises a SEPARATE check with its own exit code.
It never imports anything that would make the docs runner participate in
`sicario verify`'s verdict path, and it never edits tests/test_sicario.py.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.verify_guide_outputs import (
    apply_normalizations,
    check_guide,
    discover_guides,
    iter_fences,
    normalize_line_numbers,
    normalize_paths,
    parse_frontmatter,
)

ROOT = Path(__file__).resolve().parents[1]


class FrontmatterParsingTests(unittest.TestCase):
    def test_parses_flat_scalars_and_strips_quotes(self) -> None:
        text = (
            "---\n"
            'title: "A Guide"\n'
            "guide-slug: my-guide\n"
            "captured-version: 0.6.0\n"
            "reference-run-repository: refrun-x\n"
            "---\n"
            "\n# Body\n"
        )
        meta, body = parse_frontmatter(text)
        self.assertEqual(meta["title"], "A Guide")
        self.assertEqual(meta["guide-slug"], "my-guide")
        self.assertEqual(meta["captured-version"], "0.6.0")
        self.assertEqual(body.strip(), "# Body")

    def test_missing_frontmatter_returns_empty_meta(self) -> None:
        meta, body = parse_frontmatter("# No frontmatter here\n")
        self.assertEqual(meta, {})
        self.assertIn("No frontmatter", body)


class FenceParsingTests(unittest.TestCase):
    def test_parses_attributes_on_bash_fence(self) -> None:
        body = "```bash sicario-cmd=setup\nmkdir foo\n```\n"
        fences = iter_fences(body)
        self.assertEqual(len(fences), 1)
        self.assertEqual(fences[0].lang, "bash")
        self.assertEqual(fences[0].attrs["sicario-cmd"], "setup")
        self.assertEqual(fences[0].content, "mkdir foo\n")

    def test_parses_quoted_title_and_multiple_attrs(self) -> None:
        body = (
            '```text title="Verified output" sicario-output=verified '
            "sicario-block=guide/step-1 sicario-normalize=paths,line-numbers\n"
            "hello\n"
            "```\n"
        )
        fences = iter_fences(body)
        attrs = fences[0].attrs
        self.assertEqual(attrs["title"], "Verified output")
        self.assertEqual(attrs["sicario-output"], "verified")
        self.assertEqual(attrs["sicario-block"], "guide/step-1")
        self.assertEqual(attrs["sicario-normalize"], "paths,line-numbers")

    def test_strips_indentation_from_nested_fences(self) -> None:
        body = "- a bullet\n\n  ```bash sicario-cmd=setup\n  echo hi\n  ```\n"
        fences = iter_fences(body)
        self.assertEqual(len(fences), 1)
        self.assertEqual(fences[0].content, "echo hi\n")

    def test_multiple_fences_in_document_order(self) -> None:
        body = (
            "```bash sicario-cmd=g/a\n"
            "cmd-a\n"
            "```\n"
            "```text sicario-output=verified sicario-block=g/a\n"
            "out-a\n"
            "```\n"
            "```bash sicario-cmd=g/b\n"
            "cmd-b\n"
            "```\n"
            "```text sicario-output=verified sicario-block=g/b\n"
            "out-b\n"
            "```\n"
        )
        fences = iter_fences(body)
        self.assertEqual(
            [f.attrs.get("sicario-cmd") or f.attrs.get("sicario-block") for f in fences],
            [
                "g/a",
                "g/a",
                "g/b",
                "g/b",
            ],
        )


class NormalizationTests(unittest.TestCase):
    def test_normalize_line_numbers_replaces_digits_between_colons(self) -> None:
        text = 'generated/sicario/gate-summary.json:130:        "impact": "x",'
        self.assertEqual(
            normalize_line_numbers(text),
            'generated/sicario/gate-summary.json:<LINE>:        "impact": "x",',
        )

    def test_normalize_paths_replaces_real_root_with_placeholder(self) -> None:
        observed = "/tmp/scratch-xyz/.sicario/rules/foo.json: ignored\n"
        result = normalize_paths(observed, "/tmp/scratch-xyz", "~/refrun-rules/app")
        self.assertEqual(result, "~/refrun-rules/app/.sicario/rules/foo.json: ignored\n")

    def test_apply_normalizations_line_numbers_is_symmetric(self) -> None:
        observed = 'file.json:42:      "impact": "x",\n'
        quoted = 'file.json:130:      "impact": "x",\n'
        observed_n, quoted_n = apply_normalizations(
            observed, quoted, ["line-numbers"], real_root="", placeholder=""
        )
        self.assertEqual(observed_n, quoted_n)

    def test_apply_normalizations_paths_only_rewrites_observed(self) -> None:
        observed = "/scratch/root/x.json: ignored\n"
        quoted = "~/refrun/app/x.json: ignored\n"
        observed_n, quoted_n = apply_normalizations(
            observed, quoted, ["paths"], real_root="/scratch/root", placeholder="~/refrun/app"
        )
        self.assertEqual(observed_n, quoted_n)


class CheckGuideEndToEndTests(unittest.TestCase):
    """Exercises check_guide() against small synthetic fixture guides so the
    execution engine (shim, cwd tracking, sicario-write, sicario-cmd=setup,
    multi-block stream grouping, and every failure mode) is verified without
    depending on the shipped docs content."""

    def _write_guide(self, tmp_path: Path, body: str, **frontmatter: str) -> Path:
        fm = {
            "guide-slug": "smoke",
            "captured-version": "0.6.0",
            "reference-run-repository": "smoke-repo",
        }
        fm.update(frontmatter)
        lines = ["---"]
        for key, value in fm.items():
            lines.append(f'{key}: "{value}"')
        lines.append("---")
        lines.append("")
        lines.append(body)
        path = tmp_path / "smoke.md"
        path.write_text("\n".join(lines))
        return path

    def test_verified_block_reexecutes_and_passes(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```bash sicario-cmd=smoke/only\n"
                "echo hello\n"
                "```\n"
                "\n"
                '```text title="Verified output" sicario-output=verified sicario-block=smoke/only\n'
                "hello\n"
                "```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertTrue(report.ok, report.structural_errors)
            self.assertEqual(report.verified_reexecuted, 1)
            self.assertEqual(report.illustrative_skipped, 0)
            self.assertEqual(report.verified_failed, [])

    def test_mismatch_is_reported_with_diff(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```bash sicario-cmd=smoke/only\n"
                "echo hello\n"
                "```\n"
                "\n"
                '```text title="Verified output" sicario-output=verified sicario-block=smoke/only\n'
                "goodbye\n"
                "```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertFalse(report.ok)
            self.assertEqual(len(report.verified_failed), 1)
            self.assertIn("goodbye", report.verified_failed[0].diff)
            self.assertIn("hello", report.verified_failed[0].diff)

    def test_illustrative_block_is_skipped_not_diffed(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```bash sicario-cmd=smoke/only\n"
                "echo hello\n"
                "```\n"
                "\n"
                '```text title="Illustrative" sicario-output=illustrative sicario-block=smoke/only\n'
                "this text is never checked\n"
                "```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertTrue(report.ok)
            self.assertEqual(report.verified_reexecuted, 0)
            self.assertEqual(report.illustrative_skipped, 1)

    def test_unpaired_verified_block_is_a_failure(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                '```text title="Verified output" sicario-output=verified sicario-block=smoke/orphan\n'
                "never re-executed\n"
                "```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertFalse(report.ok)
            self.assertEqual(len(report.unpaired_verified), 1)
            self.assertIn("smoke/orphan", report.unpaired_verified[0])

    def test_missing_output_marker_is_a_structural_error(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```text sicario-block=smoke/bad\nno marker at all\n```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertFalse(report.ok)
            self.assertEqual(len(report.structural_errors), 1)
            self.assertIn("FR-050", report.structural_errors[0])

    def test_captured_version_mismatch_is_a_structural_error(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(Path(tmp), "no blocks\n", **{"captured-version": "9.9.9"})
            report = check_guide(path, "0.6.0")
            self.assertFalse(report.ok)
            self.assertEqual(len(report.structural_errors), 1)
            self.assertIn("FR-052", report.structural_errors[0])
            self.assertIn("9.9.9", report.structural_errors[0])

    def test_setup_command_executes_but_is_never_counted(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```bash sicario-cmd=setup\n"
                "mkdir -p sub\n"
                "printf 'x' > sub/marker.txt\n"
                "```\n"
                "\n"
                "```bash sicario-cmd=smoke/read\n"
                "cat sub/marker.txt\n"
                "```\n"
                "\n"
                '```text title="Verified output" sicario-output=verified sicario-block=smoke/read\n'
                "x\n"
                "```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertTrue(report.ok, report.structural_errors)
            self.assertEqual(report.verified_reexecuted, 1)

    def test_sicario_write_creates_file_before_later_commands(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```json sicario-write=nested/config.json\n"
                '{"a": 1}\n'
                "```\n"
                "\n"
                "```bash sicario-cmd=smoke/cat\n"
                "cat nested/config.json\n"
                "```\n"
                "\n"
                '```text title="Verified output" sicario-output=verified sicario-block=smoke/cat\n'
                '{"a": 1}\n'
                "```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertTrue(report.ok, report.structural_errors)
            self.assertEqual(report.verified_reexecuted, 1)

    def test_cwd_persists_across_fences_after_cd(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```bash sicario-cmd=setup\n"
                "mkdir project\n"
                "cd project\n"
                "```\n"
                "\n"
                "```bash sicario-cmd=setup\n"
                "printf 'inside' > here.txt\n"
                "```\n"
                "\n"
                "```bash sicario-cmd=smoke/pwd-check\n"
                "cat here.txt\n"
                "```\n"
                "\n"
                '```text title="Verified output" sicario-output=verified sicario-block=smoke/pwd-check\n'
                "inside\n"
                "```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertTrue(report.ok, report.structural_errors)
            self.assertEqual(report.verified_reexecuted, 1)

    def test_multi_block_stream_grouping_stdout_and_stderr(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```bash sicario-cmd=smoke/out,smoke/err\n"
                "echo to-stdout\n"
                "echo to-stderr 1>&2\n"
                "```\n"
                "\n"
                '```text title="Verified output" sicario-output=verified sicario-block=smoke/out\n'
                "to-stdout\n"
                "```\n"
                "\n"
                '```text title="Verified output" sicario-output=verified sicario-block=smoke/err sicario-stream=stderr\n'
                "to-stderr\n"
                "```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertTrue(report.ok, report.structural_errors)
            self.assertEqual(report.verified_reexecuted, 2)

    def test_multi_id_same_stream_concatenated_comparison(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```bash sicario-cmd=smoke/a,smoke/b\n"
                "echo line-one\n"
                "echo line-two\n"
                "```\n"
                "\n"
                '```text title="Verified output" sicario-output=verified sicario-block=smoke/a\n'
                "line-one\n"
                "```\n"
                "\n"
                '```text title="Verified output" sicario-output=verified sicario-block=smoke/b\n'
                "line-two\n"
                "```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertTrue(report.ok, report.structural_errors)
            self.assertEqual(report.verified_reexecuted, 2)

    def test_sicario_cmd_uses_this_checkouts_cli_not_a_stray_install(self) -> None:
        """A literal `sicario ...` command in a guide must run THIS checkout's
        code (FR-051's CI job requirement), not any other installed copy."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```bash sicario-cmd=smoke/version\n"
                "sicario --version\n"
                "```\n"
                "\n"
                '```text title="Verified output" sicario-output=verified sicario-block=smoke/version\n'
                "sicario 0.6.0\n"
                "```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertTrue(report.ok, report.structural_errors)
            self.assertEqual(report.verified_reexecuted, 1)

    def test_unknown_block_named_by_sicario_cmd_is_structural_error(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```bash sicario-cmd=smoke/does-not-exist\necho hi\n```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertFalse(report.ok)
            self.assertTrue(
                any("unknown block" in e for e in report.structural_errors),
                report.structural_errors,
            )

    def test_duplicate_sicario_block_id_is_a_structural_error(self) -> None:
        """F1: a second output fence reusing an id used to silently win,
        leaving the first fence's quoted text never diffed and never
        reported. Both locations must now be named in a structural error."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                '```text title="First" sicario-output=verified sicario-block=smoke/dup\n'
                "first\n"
                "```\n"
                "\n"
                '```text title="Second" sicario-output=verified sicario-block=smoke/dup\n'
                "second\n"
                "```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertFalse(report.ok)
            dup_errors = [e for e in report.structural_errors if "duplicate sicario-block id" in e]
            self.assertEqual(len(dup_errors), 1, report.structural_errors)
            # The error must name both the earlier and the later location.
            self.assertIn("already defined at", dup_errors[0])

    def test_duplicate_sicario_cmd_claim_is_a_structural_error(self) -> None:
        """F1 (part two): two different sicario-cmd fences both claiming the
        same output block id is exactly as ambiguous as a duplicate output
        block id — both claiming fences must be named."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```bash sicario-cmd=smoke/claimed\necho one\n```\n"
                "\n"
                "```bash sicario-cmd=smoke/claimed\necho two\n```\n"
                "\n"
                '```text title="Verified output" sicario-output=verified sicario-block=smoke/claimed\n'
                "one\n"
                "```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertFalse(report.ok)
            self.assertTrue(
                any("already claimed by the fence at" in e for e in report.structural_errors),
                report.structural_errors,
            )

    def test_verified_without_block_id_is_a_structural_error(self) -> None:
        """F2: a fence marked sicario-output=verified but with no
        sicario-block used to be skipped before its marker was even read —
        its quoted text was never checked and never reported anywhere."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                '```text title="No block id" sicario-output=verified\n'
                "this text was never checked before the fix\n"
                "```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertFalse(report.ok)
            self.assertTrue(
                any("verified but unidentifiable" in e for e in report.structural_errors),
                report.structural_errors,
            )

    def test_setup_fence_cd_escaping_scratch_root_is_a_structural_error(self) -> None:
        """F3(a): a setup fence that `cd`s outside the scratch root (e.g.
        into the actual repository checkout) must abort the guide rather
        than let later fences keep running there."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```bash sicario-cmd=setup\ncd /\n```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertFalse(report.ok)
            self.assertTrue(
                any("left the scratch root" in e for e in report.structural_errors),
                report.structural_errors,
            )

    def test_sicario_write_escaping_scratch_root_is_a_structural_error(self) -> None:
        """F3(b): a sicario-write destination that resolves outside the
        scratch root (parent traversal here, an absolute path elsewhere)
        must be refused rather than written."""
        import tempfile

        # Every per-guide scratch root is created directly under the system
        # tempdir via tempfile.mkdtemp(), so "../escaped.txt" from inside it
        # resolves to a sibling of every scratch root: the tempdir itself.
        escape_target = Path(tempfile.gettempdir()).resolve() / "escaped.txt"
        escape_target.unlink(missing_ok=True)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                path = self._write_guide(
                    Path(tmp),
                    "```text sicario-write=../escaped.txt\nshould never land here\n```\n",
                )
                report = check_guide(path, "0.6.0")
                self.assertFalse(report.ok)
                self.assertTrue(
                    any("outside the scratch root" in e for e in report.structural_errors),
                    report.structural_errors,
                )
                # And the escape must actually have been refused, not merely
                # reported after the fact.
                self.assertFalse(escape_target.exists())
        finally:
            escape_target.unlink(missing_ok=True)

    def test_unknown_sicario_normalize_key_is_a_structural_error(self) -> None:
        """F4: an unknown sicario-normalize key was silently ignored rather
        than applied — the module's own comment claimed this was already a
        structural error via a validate_guide() that did not exist."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```bash sicario-cmd=smoke/only\necho hello\n```\n"
                "\n"
                '```text title="Verified output" sicario-output=verified '
                "sicario-block=smoke/only sicario-normalize=totally-made-up\n"
                "hello\n"
                "```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertFalse(report.ok)
            self.assertTrue(
                any("unknown sicario-normalize key" in e for e in report.structural_errors),
                report.structural_errors,
            )

    def test_failing_setup_fence_is_a_structural_error(self) -> None:
        """F10: a failing sicario-cmd=setup fence used to be completely
        silent — later verified fences would run against whatever partial
        state setup left behind and fail with a confusing diff instead of
        surfacing the real cause."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```bash sicario-cmd=setup\necho 'boom' 1>&2\nexit 3\n```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertFalse(report.ok)
            errs = [e for e in report.structural_errors if "state-prep failure" in e]
            self.assertEqual(len(errs), 1, report.structural_errors)
            self.assertIn("3", errs[0])
            self.assertIn("boom", errs[0])

    def test_paired_nonzero_exit_is_not_flagged_by_itself(self) -> None:
        """A paired (non-setup) fence that exits non-zero by design (a
        staged gate failure being demonstrated) must NOT be treated as a
        structural error — only the quoted output is the contract."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```bash sicario-cmd=smoke/fails\n"
                "echo gate-failed\n"
                "exit 1\n"
                "```\n"
                "\n"
                '```text title="Verified output" sicario-output=verified sicario-block=smoke/fails\n'
                "gate-failed\n"
                "```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertTrue(report.ok, report.structural_errors)
            self.assertEqual(report.verified_reexecuted, 1)

    def test_invalid_sicario_stream_value_is_a_structural_error(self) -> None:
        """F11: any sicario-stream value other than exactly "stdout" used to
        silently select stderr, including typos like "stdOut" or "std-err"."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_guide(
                Path(tmp),
                "```bash sicario-cmd=smoke/only\necho hello\n```\n"
                "\n"
                '```text title="Verified output" sicario-output=verified '
                "sicario-block=smoke/only sicario-stream=stdOut\n"
                "hello\n"
                "```\n",
            )
            report = check_guide(path, "0.6.0")
            self.assertFalse(report.ok)
            self.assertTrue(
                any("invalid sicario-stream" in e for e in report.structural_errors),
                report.structural_errors,
            )


class RealShippedGuidesTests(unittest.TestCase):
    """Runs the actual runner against every shipped guide/playbook. This is
    the same check the `guide-outputs` CI job performs; running it here too
    means a guide regression fails the fast unit-test suite as well."""

    def test_all_shipped_guides_pass(self) -> None:
        guides = discover_guides()
        self.assertGreater(
            len(guides), 0, "no guides discovered under docs/guides or docs/playbooks"
        )
        installed_version = (ROOT / "VERSION").read_text().strip()
        failures = []
        for guide in guides:
            report = check_guide(guide, installed_version)
            if not report.ok:
                failures.append(
                    (
                        guide,
                        report.structural_errors,
                        report.unpaired_verified,
                        [(m.block_id, m.diff) for m in report.verified_failed],
                    )
                )
        self.assertEqual(failures, [], failures)


if __name__ == "__main__":
    unittest.main()
