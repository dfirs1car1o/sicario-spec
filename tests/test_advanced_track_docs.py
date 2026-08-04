"""Publication tests for the Advanced Track (spec 008 FR-003, SEC-006).

Two properties are asserted here, both about *published documentation*
rather than about the verdict path:

* FR-003 — the three new page ids appear EXACTLY ONCE across the rendered
  sidebar structure, in the Advanced Track category and not also under
  'When You Need It'. That category is a computed complement of the curated
  ones, so an id that is not subtracted from it silently appears twice.
* SEC-006 — both lessons carry the SR-005 non-assurance statement and the
  SR-006 real-graph warning as literal sentences.

Nothing in this file imports or exercises ``sicario_cli``'s verdict path.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIDEBARS = ROOT / "docs-site" / "sidebars.js"
PLAYBOOKS = ROOT / "docs" / "playbooks"
GUIDES = ROOT / "docs" / "guides"

GRAPH_LESSON = PLAYBOOKS / "graph-engineering.md"
LOOP_LESSON = PLAYBOOKS / "loop-engineering.md"
TRACK_INDEX = GUIDES / "advanced-track.md"

ADVANCED_LABEL = "Advanced Track — Graph & Loop Engineering"
ADVANCED_IDS = (
    "guides/advanced-track",
    "playbooks/graph-engineering",
    "playbooks/loop-engineering",
)

# SEC-006: asserted as literal sentences, exactly as spec 008 SR-005 and
# SR-006 state them. Line wrapping in the markdown source is normalized away
# before the comparison (see _normalized_text), so a reflow of the paragraph
# does not silently drop the requirement.
NON_ASSURANCE_SENTENCE = (
    "A graph-derived spec is not thereby complete, verified, or certified: "
    "the graph determines relevance and depth, never the gate's required "
    "form, and an inapplicable concern still receives an explicit rationale."
)
REAL_GRAPH_WARNING_SENTENCE = (
    "A graph of a real system is a map of its attack surface: treat it as "
    "sensitive, keep it out of public repositories, and publish only "
    "synthetic examples."
)


def _normalized_text(path: Path) -> str:
    """Collapse whitespace so a wrapped markdown sentence still matches.

    Leading blockquote markers are stripped first: the required sentences
    are quoted as blockquotes on the pages, and ``>`` prefixes would
    otherwise land in the middle of the joined text.
    """
    lines = [
        line.lstrip().lstrip(">") if line.lstrip().startswith(">") else line
        for line in path.read_text(encoding="utf-8").splitlines()
    ]
    return " ".join(" ".join(lines).split())


def _render_sidebar() -> object:
    """Evaluate sidebars.js with node and return the structure it exports.

    sidebars.js derives its item lists from the files actually present on
    disk, so the only faithful way to assert on the published structure is
    to run it. Skipped rather than failed when node is unavailable.
    """
    node = shutil.which("node")
    if node is None:  # pragma: no cover - environment dependent
        raise unittest.SkipTest("node is not available to evaluate sidebars.js")
    script = f"process.stdout.write(JSON.stringify(require({str(SIDEBARS)!r})));"
    completed = subprocess.run(
        [node, "-e", script],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=True,
    )
    return json.loads(completed.stdout)


def _walk_ids(node: object) -> list[str]:
    """Collect every doc id referenced anywhere in the sidebar structure."""
    found: list[str] = []
    if isinstance(node, str):
        found.append(node)
    elif isinstance(node, list):
        for item in node:
            found.extend(_walk_ids(item))
    elif isinstance(node, dict):
        if node.get("type") == "doc" and isinstance(node.get("id"), str):
            found.append(node["id"])
        # Only structural values are recursed into: a dict's own scalar
        # fields ("type", "label") are metadata, never doc ids.
        for value in node.values():
            if isinstance(value, (list, dict)):
                found.extend(_walk_ids(value))
    return found


def _categories(sidebar: object) -> list[dict]:
    return [
        item
        for item in sidebar["docs"]  # type: ignore[index]
        if isinstance(item, dict) and item.get("type") == "category"
    ]


class AdvancedTrackPagesExistTests(unittest.TestCase):
    def test_the_track_ships_exactly_two_playbooks_and_one_index(self) -> None:
        for path in (GRAPH_LESSON, LOOP_LESSON, TRACK_INDEX):
            self.assertTrue(path.is_file(), f"{path.relative_to(ROOT)} is missing")

    def test_each_page_carries_the_007_frontmatter_convention(self) -> None:
        required = (
            "title:",
            "sidebar_label:",
            "guide-slug:",
            "captured-version:",
            "reference-run-repository:",
            "reference-run-date:",
        )
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        for path in (GRAPH_LESSON, LOOP_LESSON, TRACK_INDEX):
            with self.subTest(page=path.name):
                head = path.read_text(encoding="utf-8").split("---", 2)[1]
                for key in required:
                    self.assertIn(key, head, f"{path.name} frontmatter lacks {key}")
                self.assertIn(f"captured-version: {version}", head)

    def test_each_lesson_states_a_time_budget_in_the_60_to_90_minute_band(self) -> None:
        for path in (GRAPH_LESSON, LOOP_LESSON):
            with self.subTest(page=path.name):
                self.assertIn("60–90 minutes", _normalized_text(path))


class SidebarPublicationTests(unittest.TestCase):
    """FR-003: the computed-complement trap, asserted rather than assumed."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.sidebar = _render_sidebar()

    def test_each_new_id_appears_exactly_once_in_the_whole_sidebar(self) -> None:
        ids = _walk_ids(self.sidebar)
        for doc_id in ADVANCED_IDS:
            with self.subTest(doc_id=doc_id):
                self.assertEqual(
                    ids.count(doc_id),
                    1,
                    f"{doc_id} appears {ids.count(doc_id)} time(s) in the sidebar; "
                    "an id missing from the 'When You Need It' exclusion appears "
                    "in both categories (spec 008 FR-003)",
                )

    def test_the_new_ids_live_in_the_advanced_category(self) -> None:
        categories = {c["label"]: c for c in _categories(self.sidebar)}
        self.assertIn(ADVANCED_LABEL, categories)
        advanced_ids = _walk_ids(categories[ADVANCED_LABEL]["items"])
        self.assertEqual(list(ADVANCED_IDS), advanced_ids)

    def test_the_new_ids_are_absent_from_when_you_need_it(self) -> None:
        categories = {c["label"]: c for c in _categories(self.sidebar)}
        self.assertIn("When You Need It", categories)
        when_needed = _walk_ids(categories["When You Need It"]["items"])
        for doc_id in ADVANCED_IDS:
            self.assertNotIn(doc_id, when_needed)

    def test_the_advanced_category_sits_between_lessons_and_when_you_need_it(self) -> None:
        labels = [c["label"] for c in _categories(self.sidebar)]
        self.assertIn(ADVANCED_LABEL, labels)
        self.assertLess(labels.index("Start Here — Six Lessons"), labels.index(ADVANCED_LABEL))
        self.assertLess(labels.index(ADVANCED_LABEL), labels.index("When You Need It"))

    def test_the_advanced_category_is_collapsed_by_default(self) -> None:
        categories = {c["label"]: c for c in _categories(self.sidebar)}
        self.assertTrue(
            categories[ADVANCED_LABEL]["collapsed"],
            "the Advanced Track must stay collapsed so the six-lesson path "
            "stays visually primary (spec 008 FR-002)",
        )

    def test_the_six_lesson_path_is_unchanged(self) -> None:
        categories = {c["label"]: c for c in _categories(self.sidebar)}
        lessons = _walk_ids(categories["Start Here — Six Lessons"]["items"])
        self.assertEqual(
            lessons,
            [
                "guides/start-here",
                "guides/getting-started",
                "playbooks/initial-setup-selection",
                "playbooks/first-spec",
                "playbooks/wire-ci",
                "playbooks/spec-authoring",
                "playbooks/read-evidence-as-reviewer",
            ],
        )


class HonestLimitsStatementsTests(unittest.TestCase):
    """SEC-006: both required sentences, literally, in both lessons."""

    def test_both_lessons_carry_the_non_assurance_statement(self) -> None:
        for path in (GRAPH_LESSON, LOOP_LESSON):
            with self.subTest(page=path.name):
                self.assertIn(NON_ASSURANCE_SENTENCE, _normalized_text(path))

    def test_both_lessons_carry_the_real_graph_warning(self) -> None:
        for path in (GRAPH_LESSON, LOOP_LESSON):
            with self.subTest(page=path.name):
                self.assertIn(REAL_GRAPH_WARNING_SENTENCE, _normalized_text(path))

    def test_the_track_index_repeats_both_statements(self) -> None:
        text = _normalized_text(TRACK_INDEX)
        self.assertIn(NON_ASSURANCE_SENTENCE, text)
        self.assertIn(REAL_GRAPH_WARNING_SENTENCE, text)

    def test_neither_lesson_claims_the_helper_renders_a_verdict(self) -> None:
        """SR-002's vocabulary prohibition, applied to what the lessons say
        the helper does: no lesson may describe its output as a verdict."""
        for path in (GRAPH_LESSON, LOOP_LESSON):
            with self.subTest(page=path.name):
                text = _normalized_text(path)
                self.assertIn("renders no verdict", text)
                self.assertIn("always exits `0`", text)


class StartHereLinksTheTrackTests(unittest.TestCase):
    """FR-004: one closing paragraph, optional, prerequisite-gated."""

    def test_start_here_links_the_track_after_its_close(self) -> None:
        text = (GUIDES / "start-here.md").read_text(encoding="utf-8")
        self.assertIn("advanced-track.md", text)
        close = text.index("**That's it.**")
        self.assertGreater(text.index("advanced-track.md"), close)

    def test_start_here_labels_the_track_optional_and_gated(self) -> None:
        text = _normalized_text(GUIDES / "start-here.md")
        self.assertIn("strictly optional", text)
        self.assertIn("**Lesson 5 as a hard prerequisite**", text)

    def test_start_here_still_promises_six_lessons_in_about_three_hours(self) -> None:
        """FR-002/SC-003: the track must not dilute the onboarding promise."""
        text = _normalized_text(GUIDES / "start-here.md")
        self.assertIn("Six lessons, about three hours", text)

    def test_the_track_index_links_back_to_start_here(self) -> None:
        self.assertIn("start-here.md", TRACK_INDEX.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
