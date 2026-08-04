#!/usr/bin/env python3
"""Spec-graph checklist helper — an authoring aid, never an authority.

This script belongs to the SicarioSpec Advanced Track (spec 008). It reads a
typed graph document, computes the crossing set, walks traversal rules R1-R13,
and prints an obligation checklist plus a gap list. Everything it prints is
raw material for a human author to turn into spec and plan content.

It renders no verdict. `sicario verify` is the sole authority on whether a
repository meets the governance contract, and nothing here participates in
that decision. Concretely, and by contract (spec 008 SR-002 / SR-003):

  * standard library only; it never imports sicario_cli
  * no network call, no subprocess, no model call
  * it never writes, creates, or modifies any file; stdout only
  * it always exits 0, including on a malformed graph document
  * it never emits finding codes, severities, or verdict vocabulary

Usage:

    python3 spec_graph_checklist.py saas-integration.graph.json
    python3 spec_graph_checklist.py cloud-architecture.graph.json --to-mermaid

See specs/008-graph-loop-engineering-track/spec.md (FR-010, FR-013, FR-043,
FR-044) and the README beside this file.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

GRANT_KINDS: frozenset[str] = frozenset(
    {
        "system",
        "identity",
        "credential",
        "scope",
        "data_class",
        "endpoint",
        "store",
        "human",
    }
)
ARCH_KINDS: frozenset[str] = frozenset(
    {
        "resource",
        "data_store",
        "identity",
        "policy",
        "key",
        "network_edge",
        "control_plane",
        "actor",
    }
)
ARCH_ONLY_KINDS: frozenset[str] = ARCH_KINDS - GRANT_KINDS
# `actor` appears in both vocabularies (a forged sender is as real in a grant
# graph as an internet client is in an architecture graph), so it never on its
# own makes a document an architecture graph.
ARCH_MARKER_KINDS: frozenset[str] = ARCH_ONLY_KINDS - {"actor"}
NODE_KINDS: frozenset[str] = GRANT_KINDS | ARCH_KINDS

EDGE_TYPES: frozenset[str] = frozenset(
    {
        "grants",
        "holds",
        "authorizes",
        "permits",
        "calls",
        "flows",
        "logs",
        "trusts",
        "can_assume",
        "applies_to",
        "reads",
        "writes",
        "reaches",
        "exposes",
        "encrypts",
        "deploys",
        "logs_to",
    }
)

UNCONTROLLED_ZONES: frozenset[str] = frozenset({"public-internet", "vendor-saas", "subprocessor"})
REQUIRED_TAG_KEYS: tuple[str, ...] = (
    "owner",
    "system",
    "environment",
    "data-classification",
    "retention",
)
CREDENTIAL_KINDS: frozenset[str] = frozenset({"credential", "key"})
DATA_BEARING_EDGE_TYPES: frozenset[str] = frozenset({"flows", "reads", "writes"})
LOG_EDGE_TYPES: frozenset[str] = frozenset({"logs", "logs_to"})
AUTHORIZING_EDGE_TYPES: frozenset[str] = frozenset(
    {"grants", "authorizes", "permits", "applies_to"}
)
HOLDING_EDGE_TYPES: frozenset[str] = frozenset({"holds", "can_assume"})
REACHING_DATA_EDGE_TYPES: frozenset[str] = frozenset({"permits", "flows", "reads", "writes"})
MODEL_MARKERS: tuple[str, ...] = ("llm", "model", "inference", "ai-agent", "prompt")

CYCLE_FAMILIES: tuple[tuple[str, tuple[str, ...], str, str], ...] = (
    (
        "calls+flows",
        ("calls", "flows"),
        "replay or echo of a message already handled",
        "an idempotency key and replay rejection, with a dead-letter path and its owner",
    ),
    (
        "can_assume",
        ("can_assume",),
        "privilege-escalation: a compromise at one hop returns with more authority",
        "a break in the assumption chain, or a documented rationale for the loop",
    ),
    (
        "trusts",
        ("trusts",),
        "circular trust: each side treats the other as already verified",
        "an independent verification step that does not depend on the other side",
    ),
)

MAX_CYCLE_DEPTH = 32


class SpecGraph:
    """An in-memory view of a graph document. Only well-formed parts load."""

    def __init__(self, document: dict[str, Any]) -> None:
        self.feature: str = str(document.get("feature", "<feature not recorded>"))
        raw_version = document.get("graph_version")
        self.graph_version: str = str(raw_version) if raw_version is not None else "<not recorded>"
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []

        for node in _as_list(document.get("nodes")):
            if not isinstance(node, dict):
                continue
            node_id = node.get("id")
            if isinstance(node_id, str) and node_id and node_id not in self.nodes:
                self.nodes[node_id] = node

        for edge in _as_list(document.get("edges")):
            if not isinstance(edge, dict):
                continue
            src, dst = edge.get("src"), edge.get("dst")
            if src in self.nodes and dst in self.nodes and isinstance(edge.get("id"), str):
                self.edges.append(edge)

        self.edges.sort(key=lambda item: str(item.get("id")))

    # -- element accessors -------------------------------------------------

    def kind(self, node_id: str) -> str:
        return str(self.nodes.get(node_id, {}).get("kind", "<kind not recorded>"))

    def zone(self, node_id: str) -> str:
        return str(self.nodes.get(node_id, {}).get("zone", "<zone not recorded>"))

    def attrs(self, node_id: str) -> dict[str, Any]:
        value = self.nodes.get(node_id, {}).get("attrs")
        return value if isinstance(value, dict) else {}

    def node_ids(self) -> list[str]:
        return sorted(self.nodes)

    def nodes_of_kind(self, *kinds: str) -> list[str]:
        wanted = set(kinds)
        return [node_id for node_id in self.node_ids() if self.kind(node_id) in wanted]

    def zones(self) -> list[str]:
        return sorted({self.zone(node_id) for node_id in self.nodes})

    # -- derived cuts ------------------------------------------------------

    def crossing_edges(self) -> list[dict[str, Any]]:
        return [
            edge
            for edge in self.edges
            if self.zone(str(edge["src"])) != self.zone(str(edge["dst"]))
        ]

    def is_architecture_graph(self) -> bool:
        return any(self.kind(node_id) in ARCH_MARKER_KINDS for node_id in self.nodes)

    def adjacency(
        self, edge_types: frozenset[str] | tuple[str, ...] | None = None
    ) -> dict[str, list[str]]:
        wanted = set(edge_types) if edge_types is not None else None
        table: dict[str, set[str]] = defaultdict(set)
        for edge in self.edges:
            if wanted is not None and str(edge.get("type")) not in wanted:
                continue
            table[str(edge["src"])].add(str(edge["dst"]))
        return {source: sorted(targets) for source, targets in sorted(table.items())}

    def reachable_from(self, sources: list[str]) -> set[str]:
        table = self.adjacency()
        seen: set[str] = set()
        frontier = sorted(sources)
        while frontier:
            current = frontier.pop()
            if current in seen:
                continue
            seen.add(current)
            frontier.extend(table.get(current, []))
        return seen

    def blast_radius(self, node_id: str) -> list[str]:
        table = self.adjacency(("deploys",))
        seen: set[str] = set()
        frontier = list(table.get(node_id, []))
        while frontier:
            current = frontier.pop()
            if current in seen:
                continue
            seen.add(current)
            frontier.extend(table.get(current, []))
        return sorted(seen)


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _canonical_cycle(cycle: list[str]) -> tuple[str, ...]:
    pivot = cycle.index(min(cycle))
    return tuple(cycle[pivot:] + cycle[:pivot])


def find_cycles(adjacency: dict[str, list[str]]) -> list[list[str]]:
    """Return canonical simple cycles by depth-first walk, deterministically."""
    seen: set[tuple[str, ...]] = set()
    path: list[str] = []
    on_path: set[str] = set()

    def walk(node: str) -> None:
        if len(path) >= MAX_CYCLE_DEPTH:
            return
        path.append(node)
        on_path.add(node)
        for target in adjacency.get(node, []):
            if target in on_path:
                seen.add(_canonical_cycle(path[path.index(target) :]))
            else:
                walk(target)
        path.pop()
        on_path.discard(node)

    for start in sorted(adjacency):
        walk(start)
    return [list(cycle) for cycle in sorted(seen)]


# -- structural checks -----------------------------------------------------


def structural_problems(document: dict[str, Any]) -> list[str]:
    """Report shape departures from graph.schema.json. Never a verdict."""
    problems: list[str] = []

    if not isinstance(document.get("graph_version"), int):
        problems.append("graph_version is absent or is not an integer")
    if not isinstance(document.get("feature"), str) or not document.get("feature"):
        problems.append("feature is absent or is not a non-empty string")
    if not isinstance(document.get("nodes"), list):
        problems.append("nodes is absent or is not an array")
    if not isinstance(document.get("edges"), list):
        problems.append("edges is absent or is not an array")

    known_ids: set[str] = set()
    for index, node in enumerate(_as_list(document.get("nodes"))):
        label = f"nodes[{index}]"
        if not isinstance(node, dict):
            problems.append(f"{label} is not an object")
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            problems.append(f"{label} has no usable id")
            continue
        label = f"node {node_id}"
        if node_id in known_ids:
            problems.append(f"{label} repeats an id already used")
        known_ids.add(node_id)
        if node.get("kind") not in NODE_KINDS:
            problems.append(f"{label} has kind {node.get('kind')!r}, outside the schema vocabulary")
        if not isinstance(node.get("zone"), str) or not node.get("zone"):
            problems.append(f"{label} has no zone, so it takes part in no crossing computation")
        if not isinstance(node.get("attrs"), dict):
            problems.append(f"{label} has no attrs object")

    edge_ids: set[str] = set()
    for index, edge in enumerate(_as_list(document.get("edges"))):
        label = f"edges[{index}]"
        if not isinstance(edge, dict):
            problems.append(f"{label} is not an object")
            continue
        edge_id = edge.get("id")
        if not isinstance(edge_id, str) or not edge_id:
            problems.append(f"{label} has no usable id")
        else:
            label = f"edge {edge_id}"
            if edge_id in edge_ids:
                problems.append(f"{label} repeats an id already used")
            edge_ids.add(edge_id)
        if edge.get("type") not in EDGE_TYPES:
            problems.append(f"{label} has type {edge.get('type')!r}, outside the schema vocabulary")
        for slot in ("src", "dst"):
            endpoint = edge.get(slot)
            if not isinstance(endpoint, str) or endpoint not in known_ids:
                problems.append(f"{label} {slot} {endpoint!r} names no node in this document")

    return problems


# -- traversal rules -------------------------------------------------------


def _line(rule: str, element: str, target: str, text: str) -> str:
    return f"  [{rule}] {element} | {target} | {text}"


def rule_r1(graph: SpecGraph) -> list[str]:
    lines: list[str] = []
    for node_id in graph.nodes_of_kind("data_class"):
        attrs = graph.attrs(node_id)
        regulated = attrs.get("regulated_kind")
        extra = f", regulated kind {regulated}" if regulated else ""
        lines.append(
            _line(
                "R1",
                node_id,
                "spec § Data Classification",
                f"one row for level {attrs.get('level', '<level not recorded>')}{extra}: "
                "owner, retention, residency, sharing, redaction",
            )
        )
    for node_id in graph.nodes_of_kind("data_store"):
        attrs = graph.attrs(node_id)
        lines.append(
            _line(
                "R1",
                node_id,
                "spec § Data Classification",
                f"one row for level {attrs.get('data_class', '<data_class not recorded>')}: "
                f"residency {attrs.get('residency', '<not recorded>')}, "
                f"retention {attrs.get('retention', '<not recorded>')}, owner, sharing, redaction",
            )
        )
    return lines


def rule_r2(graph: SpecGraph) -> list[str]:
    lines: list[str] = []
    counts: dict[str, int] = defaultdict(int)
    for node_id in graph.nodes:
        counts[graph.zone(node_id)] += 1
    for zone in graph.zones():
        lines.append(
            _line(
                "R2",
                f"zone:{zone}",
                "spec § Trust Boundaries",
                "describe this zone, its administrator, and what it holds "
                f"({counts[zone]} node(s))",
            )
        )
    pairs: dict[tuple[str, str], int] = defaultdict(int)
    for edge in graph.crossing_edges():
        pairs[(graph.zone(str(edge["src"])), graph.zone(str(edge["dst"])))] += 1
    for (source_zone, target_zone), count in sorted(pairs.items()):
        lines.append(
            _line(
                "R2",
                f"zone-pair:{source_zone}->{target_zone}",
                "spec § Trust Boundaries",
                f"describe what is checked at this boundary ({count} crossing edge(s))",
            )
        )
    return lines


def rule_r3(graph: SpecGraph) -> list[str]:
    lines: list[str] = []
    for edge in graph.crossing_edges():
        edge_id = str(edge["id"])
        src, dst = str(edge["src"]), str(edge["dst"])
        crossing = f"{graph.zone(src)} -> {graph.zone(dst)}"
        shape = f"{edge.get('type')} {src} -> {dst}"
        lines.append(
            _line(
                "R3",
                edge_id,
                "spec § Misuse / Abuse Cases",
                f"abuse case for the crossing {crossing} ({shape})",
            )
        )
        lines.append(
            _line(
                "R3",
                edge_id,
                "spec § Security Requirements",
                "control requirement: who authenticates this edge, what authorizes it, "
                "what validates its payload",
            )
        )
        lines.append(
            _line(
                "R3",
                edge_id,
                "spec § Security Evidence Chain",
                "evidence row: requirement, control, negative test, evidence path, owner",
            )
        )
    return lines


def rule_r4(graph: SpecGraph) -> list[str]:
    lines: list[str] = []
    for node_id in graph.nodes_of_kind(*sorted(CREDENTIAL_KINDS)):
        attrs = graph.attrs(node_id)
        owner = attrs.get("rotation_owner")
        detail = (
            f"lifetime {attrs.get('lifetime', '<not recorded>')}, "
            f"storage {attrs.get('storage', '<not recorded>')}"
            if graph.kind(node_id) == "credential"
            else f"key scope {attrs.get('scope', '<not recorded>')}"
        )
        suffix = (
            f", rotation owner {owner}"
            if owner
            else ", rotation owner is unrecorded — name one before this row advances"
        )
        lines.append(_line("R4", node_id, "spec § Secrets / Credential Handling", detail + suffix))
    return lines


def rule_r5(graph: SpecGraph) -> list[str]:
    lines: list[str] = []
    triggered: list[tuple[str, str]] = []
    for node_id in graph.nodes_of_kind("scope"):
        attrs = graph.attrs(node_id)
        verb, breadth = str(attrs.get("verb", "")), str(attrs.get("breadth", ""))
        reasons: list[str] = []
        if verb in {"write", "admin"}:
            reasons.append(f"verb {verb}")
        if breadth == "tenant-wide":
            reasons.append("breadth tenant-wide")
        if reasons:
            triggered.append((node_id, ", ".join(reasons)))
    for node_id in graph.nodes_of_kind("policy"):
        if str(graph.attrs(node_id).get("breadth", "")) == "wildcard":
            triggered.append((node_id, "wildcard policy breadth"))
    for node_id, reason in sorted(triggered):
        lines.append(
            _line(
                "R5",
                node_id,
                "spec § Security Requirements",
                f"high-impact action ({reason}): state the authorization requirement for it",
            )
        )
        lines.append(
            _line(
                "R5",
                node_id,
                "plan § Human Approval Points",
                f"human approval point for the high-impact action ({reason})",
            )
        )
    return lines


def rule_r6(graph: SpecGraph) -> list[str]:
    lines: list[str] = []
    uncontrolled = [
        node_id for node_id in graph.node_ids() if graph.zone(node_id) in UNCONTROLLED_ZONES
    ]
    exposed = graph.reachable_from(uncontrolled)
    for node_id in graph.nodes_of_kind("identity", "human", "actor"):
        attrs = graph.attrs(node_id)
        descriptor = attrs.get("principal_type") or attrs.get("role") or graph.kind(node_id)
        owner = attrs.get("owner")
        suffix = f", owner {owner}" if owner else f", in zone {graph.zone(node_id)}"
        lines.append(
            _line(
                "R6",
                node_id,
                "spec § Roles, Assets, And Abuse Actors",
                f"role entry for {descriptor}{suffix}",
            )
        )
        if node_id in exposed:
            lines.append(
                _line(
                    "R6",
                    node_id,
                    "spec § Roles, Assets, And Abuse Actors",
                    "abuse-actor entry: this principal is reachable from an uncontrolled zone",
                )
            )
    return lines


def rule_r7(graph: SpecGraph) -> list[str]:
    lines: list[str] = []
    for node_id in graph.node_ids():
        zone = graph.zone(node_id)
        if zone in UNCONTROLLED_ZONES:
            lines.append(
                _line(
                    "R7",
                    node_id,
                    "spec § External System Access",
                    f"externally zoned ({zone}): state what is read or written, by whom, "
                    "with what approval, and the production impact",
                )
            )
    return lines


def rule_r8(graph: SpecGraph) -> list[str]:
    lines: list[str] = []
    receivers: dict[str, list[str]] = defaultdict(list)
    for edge in graph.edges:
        if str(edge.get("type")) in LOG_EDGE_TYPES:
            receivers[str(edge["dst"])].append(str(edge["src"]))
    for node_id, sources in sorted(receivers.items()):
        attrs = graph.attrs(node_id)
        retention = attrs.get("retention", "<retention not recorded>")
        residency = attrs.get("residency", "<residency not recorded>")
        lines.append(
            _line(
                "R8",
                node_id,
                "spec § Audit / Logging Requirements",
                f"log receiver for {', '.join(sorted(sources))}: what is recorded, "
                f"retention {retention}, residency {residency}, who may read it",
            )
        )
    return lines


def rule_r9(graph: SpecGraph) -> list[str]:
    lines: list[str] = []
    if not graph.is_architecture_graph():
        lines.append(
            _line(
                "R9",
                "graph",
                "spec § Tagging Discipline",
                "no architecture node in this graph; state the tagging rows the feature "
                "still owns rather than deleting the section",
            )
        )
        return lines
    for node_id in graph.node_ids():
        tags = graph.attrs(node_id).get("tags")
        present = tags if isinstance(tags, dict) else {}
        missing = [key for key in REQUIRED_TAG_KEYS if not present.get(key)]
        if missing:
            lines.append(
                _line(
                    "R9",
                    node_id,
                    "spec § Tagging Discipline",
                    f"traversal finding: tag key(s) absent — {', '.join(missing)}",
                )
            )
    return lines


def rule_r10(graph: SpecGraph) -> list[str]:
    lines: list[str] = []
    for family, edge_types, abuse_text, requirement_text in CYCLE_FAMILIES:
        cycles = find_cycles(graph.adjacency(edge_types))
        if not cycles:
            lines.append(
                _line(
                    "R10",
                    f"cycle-family:{family}",
                    "spec § Misuse / Abuse Cases",
                    "no cycle detected in this family; if the return edges were simply not "
                    "modelled, model them before relying on this line",
                )
            )
            continue
        for cycle in cycles:
            label = " -> ".join(cycle + [cycle[0]])
            lines.append(
                _line(
                    "R10",
                    f"cycle:{family}:{cycle[0]}",
                    "spec § Misuse / Abuse Cases",
                    f"abuse case for {abuse_text} ({label})",
                )
            )
            lines.append(
                _line(
                    "R10",
                    f"cycle:{family}:{cycle[0]}",
                    "spec § Security Requirements",
                    f"requirement: {requirement_text}",
                )
            )
    return lines


def _model_markers(node_id: str, graph: SpecGraph) -> list[str]:
    haystack: list[str] = [graph.kind(node_id)]

    def collect(value: Any) -> None:
        if isinstance(value, str):
            haystack.append(value)
        elif isinstance(value, dict):
            for key, item in value.items():
                haystack.append(str(key))
                collect(item)
        elif isinstance(value, list):
            for item in value:
                collect(item)

    collect(graph.attrs(node_id))
    lowered = " ".join(haystack).lower()
    return [marker for marker in MODEL_MARKERS if marker in lowered]


def rule_r11(graph: SpecGraph) -> list[str]:
    lines: list[str] = []
    for node_id in graph.node_ids():
        markers = _model_markers(node_id, graph)
        if markers:
            lines.append(
                _line(
                    "R11",
                    node_id,
                    "spec § AI / LLM Risk",
                    f"model or agent marker(s) {', '.join(markers)}: state the tool boundary, "
                    "the untrusted-input posture, and what a human confirms",
                )
            )
    if not lines:
        lines.append(
            _line(
                "R11",
                "graph",
                "spec § AI / LLM Risk",
                "no model or agent node in this graph; record the explicit rationale for "
                "non-applicability rather than deleting the section",
            )
        )
    return lines


def rule_r12(graph: SpecGraph) -> list[str]:
    lines: list[str] = []
    kinds = {graph.kind(node_id) for node_id in graph.nodes}

    lines.append(
        _line(
            "R12",
            "graph",
            "spec § Compliance / Control Applicability",
            "Secure development / SSDF PW row: this traversal is itself the design analysis",
        )
    )

    vendors = sorted(
        node_id
        for node_id in graph.nodes_of_kind("system")
        if str(graph.attrs(node_id).get("party", "")) in {"vendor", "subprocessor"}
    )
    if vendors:
        lines.append(
            _line(
                "R12",
                ", ".join(vendors),
                "spec § Compliance / Control Applicability",
                "Supply chain row: third-party system node(s) present",
            )
        )
    else:
        lines.append(
            _line(
                "R12",
                "graph",
                "spec § Compliance / Control Applicability",
                "Supply chain row: no third-party system node; record the rationale",
            )
        )

    if kinds & ARCH_MARKER_KINDS:
        lines.append(
            _line(
                "R12",
                "graph",
                "spec § Compliance / Control Applicability",
                "Cloud / IaC row: architecture node kind(s) present — "
                f"{', '.join(sorted(kinds & ARCH_MARKER_KINDS))}",
            )
        )
    else:
        lines.append(
            _line(
                "R12",
                "graph",
                "spec § Compliance / Control Applicability",
                "Cloud / IaC row: no architecture node kind; record the rationale",
            )
        )

    regulated = sorted(
        node_id
        for node_id in graph.node_ids()
        if graph.attrs(node_id).get("regulated_kind")
        or str(graph.attrs(node_id).get("data_class", "")).lower().startswith("regulated")
    )
    if regulated:
        lines.append(
            _line(
                "R12",
                ", ".join(regulated),
                "spec § Compliance / Control Applicability",
                "Privacy or regulated-data row: regulated node(s) present",
            )
        )
    else:
        lines.append(
            _line(
                "R12",
                "graph",
                "spec § Compliance / Control Applicability",
                "Privacy or regulated-data row: no regulated node; record the rationale",
            )
        )
    return lines


def rule_r13(graph: SpecGraph) -> list[str]:
    lines: list[str] = []
    lines.append(
        _line(
            "R13",
            "graph",
            "plan § Data Flow And Trust Boundaries",
            f"mirror the mermaid fence for {graph.feature} here and keep "
            "docs/diagrams/ as the artifact of record",
        )
    )
    control_planes = graph.nodes_of_kind("control_plane")
    if control_planes:
        for node_id in control_planes:
            radius = graph.blast_radius(node_id)
            listed = ", ".join(radius) if radius else "nothing it deploys was modelled"
            lines.append(
                _line(
                    "R13",
                    node_id,
                    "plan § Rollback",
                    f"blast radius via the deploys closure: {listed}",
                )
            )
    else:
        lines.append(
            _line(
                "R13",
                "graph",
                "plan § Rollback",
                "no control_plane node was modelled; state who can revert this feature "
                "and how the revert is confirmed",
            )
        )
    lines.append(
        _line(
            "R13",
            "graph",
            "plan § Threat Model",
            f"one entry per crossing zone-pair, keyed to the abuse cases R3 emitted "
            f"({len(graph.crossing_edges())} crossing edge(s))",
        )
    )
    return lines


RULES = (
    rule_r1,
    rule_r2,
    rule_r3,
    rule_r4,
    rule_r5,
    rule_r6,
    rule_r7,
    rule_r8,
    rule_r9,
    rule_r10,
    rule_r11,
    rule_r12,
    rule_r13,
)


# -- gap list --------------------------------------------------------------


def gap_lines(graph: SpecGraph) -> list[str]:
    lines: list[str] = []

    for edge in graph.edges:
        if str(edge.get("type")) not in DATA_BEARING_EDGE_TYPES:
            continue
        attrs = edge.get("attrs")
        carried = attrs.get("data_class") if isinstance(attrs, dict) else None
        if not carried:
            lines.append(
                f"  [gap] edge {edge['id']} ({edge.get('type')} {edge['src']} -> {edge['dst']}) "
                "carries data with no data_class recorded"
            )

    for node_id in graph.nodes_of_kind(*sorted(CREDENTIAL_KINDS)):
        if not graph.attrs(node_id).get("rotation_owner"):
            lines.append(f"  [gap] {node_id} has no rotation owner, so no one owns its renewal")

    crossings = graph.crossing_edges()
    if crossings:
        lines.append(
            f"  [gap] {len(crossings)} crossing edge(s) each still need a control and an "
            f"evidence row: {', '.join(str(edge['id']) for edge in crossings)}"
        )

    if graph.is_architecture_graph():
        for node_id in graph.node_ids():
            tags = graph.attrs(node_id).get("tags")
            present = tags if isinstance(tags, dict) else {}
            missing = [key for key in REQUIRED_TAG_KEYS if not present.get(key)]
            if missing:
                consequence = (
                    "no owner is derivable from the graph"
                    if "owner" in missing
                    else "the tagging row cannot be completed from the graph"
                )
                lines.append(
                    f"  [gap] {node_id} is untagged for {', '.join(missing)} — {consequence}"
                )

    for family, edge_types, _abuse, _requirement in CYCLE_FAMILIES:
        for cycle in find_cycles(graph.adjacency(edge_types)):
            label = " -> ".join(cycle + [cycle[0]])
            lines.append(
                f"  [gap] cycle in {family} is untreated until a ledger row names its "
                f"control and negative test: {label}"
            )

    reached_data = {
        str(edge["dst"])
        for edge in graph.edges
        if str(edge.get("type")) in REACHING_DATA_EDGE_TYPES
    }
    for node_id in graph.nodes_of_kind("data_class"):
        if node_id not in reached_data:
            lines.append(
                f"  [gap] data class {node_id} has no modelled path reaching it, so no "
                "crossing was computed for it"
            )

    for node_id in graph.nodes_of_kind("identity"):
        holds = any(
            str(edge["src"]) == node_id and str(edge.get("type")) in HOLDING_EDGE_TYPES
            for edge in graph.edges
        )
        authorized = any(
            str(edge["dst"]) == node_id and str(edge.get("type")) in AUTHORIZING_EDGE_TYPES
            for edge in graph.edges
        )
        if not holds and not authorized:
            lines.append(
                f"  [gap] identity {node_id} holds no modelled credential and is granted "
                "no modelled authorization"
            )

    if not lines:
        lines.append(
            "  [gap] nothing unanswered was computable from this graph — which bounds the "
            "graph, not the feature; look for off-graph concerns next"
        )
    return lines


# -- rendering -------------------------------------------------------------


def render_checklist(graph: SpecGraph, problems: list[str]) -> list[str]:
    lines: list[str] = []
    lines.append("== Spec graph checklist ==")
    lines.append(f"feature: {graph.feature}")
    lines.append(f"graph_version: {graph.graph_version}")
    lines.append(f"nodes: {len(graph.nodes)}")
    lines.append(f"edges: {len(graph.edges)}")
    zones = graph.zones()
    lines.append(f"zones: {len(zones)} ({', '.join(zones) if zones else 'none'})")
    lines.append("this output is authoring material for a human; it is not a verdict")

    if problems:
        lines.append("")
        lines.append("== Problem report (shape departures from graph.schema.json) ==")
        for problem in problems:
            lines.append(f"  [problem] {problem}")
        lines.append("  the traversal below covers only the well-formed part of the document")

    lines.append("")
    crossings = graph.crossing_edges()
    lines.append("== Crossing set: zone(src) != zone(dst) ==")
    lines.append(f"crossing edges: {len(crossings)} of {len(graph.edges)}")
    for edge in crossings:
        src, dst = str(edge["src"]), str(edge["dst"])
        lines.append(
            f"  {edge['id']}  {edge.get('type')}  {src} -> {dst}  "
            f"[{graph.zone(src)} -> {graph.zone(dst)}]"
        )

    lines.append("")
    lines.append("== Obligation checklist: traversal rules R1-R13 ==")
    for rule in RULES:
        lines.extend(rule(graph))

    lines.append("")
    lines.append("== Gap list (what the deterministic gate cannot see) ==")
    lines.extend(gap_lines(graph))
    lines.append("  every line above is an unanswered question for a human, never a finding code")
    return lines


def _mermaid_id(node_id: str) -> str:
    return "n_" + "".join(char if char.isalnum() else "_" for char in node_id)


def render_mermaid(graph: SpecGraph, problems: list[str]) -> list[str]:
    lines: list[str] = []
    lines.append("%% derived from the graph JSON by spec_graph_checklist.py --to-mermaid")
    lines.append(f"%% feature: {graph.feature} (graph_version {graph.graph_version})")
    for problem in problems:
        lines.append(f"%% problem: {problem}")
    lines.append("flowchart LR")

    by_zone: dict[str, list[str]] = defaultdict(list)
    for node_id in graph.node_ids():
        by_zone[graph.zone(node_id)].append(node_id)

    for index, zone in enumerate(sorted(by_zone)):
        lines.append(f"  subgraph z{index}[{zone}]")
        for node_id in sorted(by_zone[zone]):
            lines.append(f'    {_mermaid_id(node_id)}["{graph.kind(node_id)}:{node_id}"]')
        lines.append("  end")

    for edge in graph.edges:
        src, dst = str(edge["src"]), str(edge["dst"])
        label = str(edge.get("type"))
        if graph.zone(src) != graph.zone(dst):
            label = f"{label} ⟨CROSSING⟩"
        lines.append(f'  {_mermaid_id(src)} -->|"{label}"| {_mermaid_id(dst)}')
    return lines


# -- entry point -----------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spec_graph_checklist.py",
        description=(
            "Walk a spec graph and print an obligation checklist and a gap list. "
            "An authoring aid only: it renders no verdict and always exits 0."
        ),
    )
    parser.add_argument("graph", help="path to a graph JSON document")
    parser.add_argument(
        "--to-mermaid",
        action="store_true",
        help="emit a mermaid flowchart derived from the JSON instead of the checklist",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.graph)

    problems: list[str] = []
    document: dict[str, Any] = {}
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        problems.append(f"the graph document could not be read: {exc}")
        raw = ""
    if raw:
        try:
            loaded = json.loads(raw)
        except json.JSONDecodeError as exc:
            problems.append(
                f"the graph document is not valid JSON at line {exc.lineno} "
                f"column {exc.colno}: {exc.msg}"
            )
            loaded = None
        if isinstance(loaded, dict):
            document = loaded
            problems.extend(structural_problems(document))
        elif loaded is not None:
            problems.append("the top level of a graph document must be a JSON object")

    graph = SpecGraph(document)
    render = render_mermaid if args.to_mermaid else render_checklist
    sys.stdout.write("\n".join(render(graph, problems)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
