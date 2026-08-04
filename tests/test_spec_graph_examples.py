"""Invariant tests for examples/spec-graph/ (spec 008 SEC-002, SEC-003, SEC-005).

The examples package is an authoring aid on the human side of the Two-Tier
Authority. These tests hold the boundary: the helper never speaks like the
gate, `sicario_cli` has no path to it, no shipped example value looks like a
credential, and its output is stable enough to quote in a lesson.

Running the helper via subprocess is fine *here* — the prohibition in spec 008
SR-002 is on the helper itself, which uses no subprocess.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "spec-graph"
HELPER = EXAMPLES / "spec_graph_checklist.py"
SAAS_GRAPH = EXAMPLES / "saas-integration.graph.json"
CLOUD_GRAPH = EXAMPLES / "cloud-architecture.graph.json"

VERDICT_WORDS = ("pass", "passed", "fail", "failed", "blocking", "violation")
VERDICT_WORD_PATTERN = re.compile(
    r"\b(" + "|".join(VERDICT_WORDS) + r")\b", flags=re.IGNORECASE
)

SECRET_SCAN_RULE_IDS = ("040", "041", "042", "043")


def run_helper(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HELPER), *args],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )


def shipped_secret_patterns() -> list[tuple[str, str]]:
    """Return (rule file name, pattern) for the shipped regex-forbidden rules."""
    patterns: list[tuple[str, str]] = []
    rules_dir = ROOT / "presets" / "sicario-core" / "rules"
    for rule_path in sorted(rules_dir.glob("*.rule.json")):
        if not rule_path.name.startswith(SECRET_SCAN_RULE_IDS):
            continue
        rule = json.loads(rule_path.read_text(encoding="utf-8"))
        if rule.get("kind") != "regex-forbidden":
            continue
        pattern = rule.get("params", {}).get("pattern")
        if isinstance(pattern, str) and pattern:
            patterns.append((rule_path.name, pattern))
    return patterns


class ExamplesPackageLayoutTests(unittest.TestCase):
    def test_examples_package_ships_the_declared_files(self) -> None:
        for name in (
            "README.md",
            "graph.schema.json",
            "spec_graph_checklist.py",
            "saas-integration.graph.json",
            "cloud-architecture.graph.json",
        ):
            self.assertTrue((EXAMPLES / name).is_file(), name)

    def test_example_graphs_conform_to_the_shipped_kind_vocabularies(self) -> None:
        schema = json.loads((EXAMPLES / "graph.schema.json").read_text(encoding="utf-8"))
        node_kinds = set(schema["$defs"]["node"]["properties"]["kind"]["enum"])
        edge_types = set(schema["$defs"]["edge"]["properties"]["type"]["enum"])
        for graph_path in (SAAS_GRAPH, CLOUD_GRAPH):
            graph = json.loads(graph_path.read_text(encoding="utf-8"))
            self.assertIsInstance(graph["graph_version"], int, graph_path.name)
            node_ids = {node["id"] for node in graph["nodes"]}
            self.assertEqual(len(node_ids), len(graph["nodes"]), graph_path.name)
            for node in graph["nodes"]:
                self.assertIn(node["kind"], node_kinds, f"{graph_path.name}:{node['id']}")
                self.assertTrue(node["zone"], f"{graph_path.name}:{node['id']}")
            edge_ids = {edge["id"] for edge in graph["edges"]}
            self.assertEqual(len(edge_ids), len(graph["edges"]), graph_path.name)
            for edge in graph["edges"]:
                self.assertIn(edge["type"], edge_types, f"{graph_path.name}:{edge['id']}")
                self.assertIn(edge["src"], node_ids, f"{graph_path.name}:{edge['id']}")
                self.assertIn(edge["dst"], node_ids, f"{graph_path.name}:{edge['id']}")


class HelperIsNotAnAuthorityTests(unittest.TestCase):
    """SEC-002: no verdict vocabulary, and exit 0 on every input."""

    def assert_no_verdict_vocabulary(self, label: str, text: str) -> None:
        self.assertNotIn("SICARIO-", text, f"{label} emitted a finding-code prefix")
        found = VERDICT_WORD_PATTERN.findall(text)
        self.assertEqual(found, [], f"{label} emitted verdict vocabulary: {sorted(set(found))}")

    def test_both_example_graphs_produce_no_verdict_vocabulary_and_exit_zero(self) -> None:
        for graph_path in (SAAS_GRAPH, CLOUD_GRAPH):
            for extra in ([], ["--to-mermaid"]):
                with self.subTest(graph=graph_path.name, mode=extra or ["checklist"]):
                    result = run_helper(str(graph_path), *extra)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertTrue(result.stdout.strip())
                    self.assert_no_verdict_vocabulary(graph_path.name, result.stdout)
                    self.assert_no_verdict_vocabulary(
                        f"{graph_path.name} (stderr)", result.stderr
                    )

    def test_malformed_input_still_exits_zero_with_a_structured_report(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            broken = Path(scratch) / "broken.graph.json"
            broken.write_text('{"graph_version": 1, "nodes": [ {"id": ', encoding="utf-8")
            result = run_helper(str(broken))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Problem report", result.stdout)
        self.assertIn("not valid JSON", result.stdout)
        self.assert_no_verdict_vocabulary("broken JSON", result.stdout)

    def test_schema_invalid_input_still_exits_zero(self) -> None:
        document = {
            "graph_version": "one",
            "nodes": [{"id": "a", "kind": "not-a-kind"}],
            "edges": [{"id": "e1", "type": "not-a-type", "src": "a", "dst": "ghost"}],
        }
        with tempfile.TemporaryDirectory() as scratch:
            invalid = Path(scratch) / "invalid.graph.json"
            invalid.write_text(json.dumps(document), encoding="utf-8")
            result = run_helper(str(invalid))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Problem report", result.stdout)
        self.assertIn("outside the schema vocabulary", result.stdout)
        self.assertIn("names no node in this document", result.stdout)
        self.assert_no_verdict_vocabulary("schema-invalid graph", result.stdout)

    def test_missing_input_still_exits_zero(self) -> None:
        result = run_helper(str(EXAMPLES / "no-such-file.graph.json"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("could not be read", result.stdout)
        self.assert_no_verdict_vocabulary("missing input", result.stdout)


class HelperIsDecoupledFromTheVerdictPathTests(unittest.TestCase):
    """SEC-003: no import path from sicario_cli, and no CI gating."""

    def test_sicario_cli_never_references_the_examples_helper(self) -> None:
        needles = ("spec_graph", "spec-graph", "examples.spec_graph", "spec_graph_checklist")
        for source in sorted((ROOT / "sicario_cli").rglob("*.py")):
            text = source.read_text(encoding="utf-8")
            for needle in needles:
                self.assertNotIn(needle, text, f"{source} references {needle}")

    def test_helper_imports_only_the_standard_library(self) -> None:
        text = HELPER.read_text(encoding="utf-8")
        imported = set(re.findall(r"^(?:from|import)\s+([A-Za-z_][\w.]*)", text, re.MULTILINE))
        allowed = {"__future__", "argparse", "json", "sys", "collections", "pathlib", "typing"}
        self.assertTrue(
            imported <= allowed,
            "helper imports outside the allowed standard-library set: "
            f"{sorted(imported - allowed)}",
        )
        for forbidden in ("subprocess", "socket", "urllib", "requests", "httpx", "sicario_cli"):
            self.assertNotIn(forbidden, imported, f"helper imports {forbidden}")

    def test_helper_never_opens_a_file_for_writing(self) -> None:
        text = HELPER.read_text(encoding="utf-8")
        for forbidden in ("write_text(", "open(", "mkdir(", "os.remove", "shutil"):
            self.assertNotIn(forbidden, text, f"helper contains {forbidden}")

    def test_verify_workflow_template_and_its_mirror_never_mention_the_helper(self) -> None:
        candidates = (
            ROOT / "workflow_templates" / "sicario-verify.yml",
            ROOT / "sicario_cli" / "assets" / "workflow_templates" / "sicario-verify.yml",
        )
        for workflow in candidates:
            self.assertTrue(workflow.is_file(), workflow)
            text = workflow.read_text(encoding="utf-8")
            for needle in ("spec-graph", "spec_graph", "spec_graph_checklist.py"):
                self.assertNotIn(needle, text, f"{workflow} mentions {needle}")


class ExampleValuesAreNotSecretShapedTests(unittest.TestCase):
    """SEC-005: the shipped secret-scan patterns find nothing in the examples."""

    def test_shipped_secret_patterns_are_discoverable(self) -> None:
        patterns = shipped_secret_patterns()
        self.assertGreaterEqual(len(patterns), 4, "expected rules 040-043 to ship patterns")

    def test_no_example_file_matches_a_shipped_secret_pattern(self) -> None:
        patterns = [(name, re.compile(pattern)) for name, pattern in shipped_secret_patterns()]
        files = sorted(path for path in EXAMPLES.rglob("*") if path.is_file())
        self.assertTrue(files)
        for path in files:
            text = path.read_text(encoding="utf-8")
            for rule_name, compiled in patterns:
                match = compiled.search(text)
                excerpt = match.group(0) if match else ""
                self.assertIsNone(
                    match,
                    f"{path.relative_to(ROOT)} matches {rule_name}: {excerpt}",
                )

    def test_every_credential_node_value_is_an_angle_bracket_placeholder(self) -> None:
        graph = json.loads(SAAS_GRAPH.read_text(encoding="utf-8"))
        credentials = [node for node in graph["nodes"] if node["kind"] == "credential"]
        self.assertTrue(credentials)
        for node in credentials:
            storage = node["attrs"]["storage"]
            self.assertTrue(
                storage.startswith("<") and storage.endswith(">"),
                f"{node['id']} storage is not an angle-bracket placeholder: {storage}",
            )


class HelperOutputIsDeterministicTests(unittest.TestCase):
    def test_repeat_runs_are_byte_identical(self) -> None:
        for graph_path in (SAAS_GRAPH, CLOUD_GRAPH):
            for extra in ([], ["--to-mermaid"]):
                with self.subTest(graph=graph_path.name, mode=extra or ["checklist"]):
                    first = run_helper(str(graph_path), *extra)
                    second = run_helper(str(graph_path), *extra)
                    self.assertEqual(first.returncode, 0)
                    self.assertEqual(first.stdout, second.stdout)


class TraversalSubstanceTests(unittest.TestCase):
    def test_saas_graph_emits_the_idempotency_obligation_from_its_cycle(self) -> None:
        output = run_helper(str(SAAS_GRAPH)).stdout
        self.assertIn("[R10]", output)
        self.assertIn("idempotency", output)
        self.assertIn("replay", output)
        self.assertIn("ep-webhook -> sys-crm -> sys-helpdesk -> ep-webhook", output)

    def test_saas_graph_lists_its_crossing_set_and_credential_gap(self) -> None:
        output = run_helper(str(SAAS_GRAPH)).stdout
        self.assertIn("== Crossing set: zone(src) != zone(dst) ==", output)
        self.assertIn("crossing edges: 5 of 18", output)
        self.assertIn("Gap list (what the deterministic gate cannot see)", output)
        self.assertIn("cred-webhook-signing-key has no rotation owner", output)

    def test_cloud_graph_emits_the_privilege_escalation_obligation(self) -> None:
        output = run_helper(str(CLOUD_GRAPH)).stdout
        self.assertIn("privilege-escalation", output)
        self.assertIn("id-ci-deploy -> id-svc-api -> id-fn-export -> id-ci-deploy", output)

    def test_cloud_graph_reports_the_untagged_node_as_a_gap(self) -> None:
        output = run_helper(str(CLOUD_GRAPH)).stdout
        gap_section = output.split("== Gap list", 1)[1]
        self.assertIn("res-legacy-report-job is untagged for", gap_section)
        self.assertIn("res-metrics-agent is untagged for", gap_section)
        self.assertIn("[R9] res-legacy-report-job", output)

    def test_cloud_graph_reports_the_deploys_closure_blast_radius(self) -> None:
        output = run_helper(str(CLOUD_GRAPH)).stdout
        self.assertIn("blast radius via the deploys closure", output)
        self.assertIn("ds-orders-db, res-api-service, res-export-function", output)

    def test_mermaid_mode_labels_crossing_edges_and_groups_zones(self) -> None:
        output = run_helper(str(SAAS_GRAPH), "--to-mermaid").stdout
        self.assertIn("flowchart LR", output)
        self.assertIn("subgraph z0[our-tenant]", output)
        self.assertIn("CROSSING", output)
        self.assertNotIn("[R1]", output)


if __name__ == "__main__":
    unittest.main()
