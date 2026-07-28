from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


class RuleValidationError(Exception):
    """Raised when a rule file fails schema validation."""


ALLOWED_SEVERITIES = {"critical", "high", "medium", "low"}
ALLOWED_KINDS = {
    "file-exists",
    "file-glob",
    "section-exists",
    "keyword-exists",
    "keyword-absent",
    "regex-forbidden",
    "regex-required",
    "risk-rows-valid",
    "classification-complete",
    "tagging-complete",
}

KIND_REQUIRES_PARAMS = {
    "section-exists": ["headings"],
    "keyword-exists": ["keywords"],
    "keyword-absent": ["keywords"],
    "regex-forbidden": ["pattern"],
    "regex-required": ["pattern"],
    "risk-rows-valid": ["forbidden_values"],
    "classification-complete": [],
    "tagging-complete": [],
}


def _validate_rule(rule: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    for required_field in ("id", "severity", "kind", "path", "message"):
        if required_field not in rule:
            errors.append(f"missing required field: {required_field}")

    if errors:
        return errors

    rid = rule["id"]
    # fullmatch, not match: `$` in re.match also matches just BEFORE a trailing
    # newline, so an id like "SICARIO-X\n" validated and then rendered
    # identically to the real id in evidence — a grep-poisoning primitive.
    if not isinstance(rid, str) or not re.fullmatch(r"[A-Z][A-Z0-9-]+", rid):
        errors.append(f"rule id '{rid}' must match ^[A-Z][A-Z0-9-]+$")

    sev = rule["severity"]
    if sev not in ALLOWED_SEVERITIES:
        errors.append(f"severity '{sev}' must be one of {sorted(ALLOWED_SEVERITIES)}")

    kind = rule["kind"]
    if kind not in ALLOWED_KINDS:
        errors.append(f"kind '{kind}' must be one of {sorted(ALLOWED_KINDS)}")

    if not isinstance(rule.get("path"), str):
        errors.append("path must be a string")

    if not isinstance(rule.get("message"), str):
        errors.append("message must be a string")

    enabled = rule.get("enabled", True)
    if not isinstance(enabled, bool):
        errors.append("enabled must be a boolean")

    params = rule.get("params")
    if params is not None and not isinstance(params, dict):
        errors.append("params must be an object")

    if kind in KIND_REQUIRES_PARAMS:
        required = KIND_REQUIRES_PARAMS[kind]
        if params is None:
            errors.append(f"kind '{kind}' requires params with: {required}")
        else:
            for key in required:
                if key not in params:
                    errors.append(f"kind '{kind}' requires params.{key}")

    if kind == "regex-forbidden":
        from sicario_cli.rules.kinds.regex_forbidden import validate_caps

        # Caps must be positive integers. A zero, negative, or non-integer cap
        # is rejected here, at rule load, rather than clamped to a permissive
        # default at evaluation time (FR-012, SEC-008, SA-005).
        errors.extend(validate_caps(params))

    return errors


# --- Rule overrides -----------------------------------------------------------
#
# A project may replace a shipped rule by reusing its `id` (see load_rules for
# the precedence contract). That is a documented, legitimate capability — a
# platform team narrowing a noisy rule to the paths it owns. It is also how an
# adopter could switch off the secret scan, so the security property is not
# "you cannot do this", it is "you cannot do this without it showing up in the
# evidence artifact and therefore in review". Everything below exists to make
# an override impossible to perform silently.

#: Severity ordering, most severe first. Used only to rank an override's impact
#: in evidence. It never participates in the pass/fail verdict.
_SEVERITY_ORDER = ["critical", "high", "medium", "low"]

#: Fields whose difference changes what a rule actually ENFORCES. A record whose
#: `changed` set touches none of these (a reworded `message`, say) is flagged
#: `material: false` so a reviewer can tell a real policy change from a cosmetic
#: one without re-reading both rule files.
MATERIAL_OVERRIDE_FIELDS = ("enabled", "severity", "kind", "path", "params")


def _more_severe(*severities: Any) -> str:
    """Return the most severe of the given severity strings.

    An override is ranked by the HIGHEST of the ORIGINAL, the superseded, and
    the winning severity so that demoting a rule to `low` in the same edit that
    disables it cannot dress a disabled `critical` rule up as a routine `low`
    tweak — and so that splitting the demotion and the disable across two files
    cannot either. A chain of N overriding files must yield the same ultimate
    impact string as doing it all in one file.
    """
    candidates = [s for s in severities if s in _SEVERITY_ORDER]
    if not candidates:
        return "unknown"
    return min(candidates, key=_SEVERITY_ORDER.index)


#: Ceiling on any single from/to value recorded in an override's `details`.
#: Values here are rule-file content (patterns, globs) — never scanned
#: repository content — so there is nothing secret to redact; the cap only
#: stops a pathological rule from bloating the evidence artifact.
_DETAIL_VALUE_MAX_CHARS = 500


def _detail_value(value: Any) -> Any:
    """Return ``value`` for an override detail entry, capping pathological sizes.

    Non-string values (keyword lists, caps) are kept as-is when small so the
    detail is machine-readable; anything whose rendering exceeds the cap is
    replaced by its truncated rendering with an explicit ``(truncated)`` marker
    so the truncation itself is visible, never silent.
    """
    rendered = value if isinstance(value, str) else json.dumps(value, sort_keys=True)
    if len(rendered) > _DETAIL_VALUE_MAX_CHARS:
        return rendered[:_DETAIL_VALUE_MAX_CHARS] + " (truncated)"
    return value


def _override_details(
    superseded: Dict[str, Any], winning: Dict[str, Any], changed: List[str]
) -> Dict[str, Any]:
    """From/to values for the changes a reviewer cannot judge from names alone.

    The gate cannot decide whether a `params.pattern` change is a narrowing or
    a neutering — that is regex containment, not something a deterministic gate
    should pretend to judge. What it can do is put the actual change in front
    of the reviewer: without this, replacing the secret-scan pattern with
    `(?!x)x` produced a record saying only `changed: ["params"]`, and the
    resulting green gate was indistinguishable from a clean repository without
    diffing rule files by hand.

    Covered: `path`, `kind`, and every changed KEY inside `params`, each as
    `{"from": ..., "to": ...}`. `severity` and `enabled` already carry from/to
    at the top of the record; `message` is cosmetic and needs no detail. Keys
    are inserted in sorted order so the record is deterministic.
    """
    details: Dict[str, Any] = {}
    for field_name in sorted(("kind", "path")):
        if field_name in changed:
            details[field_name] = {
                "from": _detail_value(superseded.get(field_name)),
                "to": _detail_value(winning.get(field_name)),
            }
    if "params" in changed:
        previous = superseded.get("params")
        current = winning.get("params")
        previous = previous if isinstance(previous, dict) else {}
        current = current if isinstance(current, dict) else {}
        param_details: Dict[str, Any] = {}
        for key in sorted(set(previous) | set(current)):
            if previous.get(key) != current.get(key):
                param_details[key] = {
                    "from": _detail_value(previous.get(key)),
                    "to": _detail_value(current.get(key)),
                }
        details["params"] = param_details
    return details


def _rule_diff(superseded: Dict[str, Any], winning: Dict[str, Any]) -> List[str]:
    """Names of every field whose value differs between two rules sharing an id.

    `enabled` is normalised to its effective value first, so a shipped rule that
    omits the field and a project rule that spells out `"enabled": true` are not
    reported as a difference that is not there.
    """
    previous = dict(superseded)
    current = dict(winning)
    previous["enabled"] = superseded.get("enabled", True)
    current["enabled"] = winning.get("enabled", True)
    keys = (set(previous) | set(current)) - {"id"}
    return sorted(key for key in keys if previous.get(key) != current.get(key))


def _override_record(
    rule_id: str,
    superseded: Dict[str, Any],
    winning: Dict[str, Any],
    superseded_ref: Dict[str, str],
    winning_ref: Dict[str, str],
    changed: List[str],
    original_severity: Any,
) -> Dict[str, Any]:
    """Build the evidence record for one rule replaced by a later rule file.

    ``original_severity`` is the severity of the FIRST definition ever loaded
    for this id — the shipped severity whenever a shipped rule exists. `impact`
    is anchored to it so that a chain of project files (demote in one file,
    disable in a later one) cannot launder `disables-critical-severity-rule`
    down to `disables-low-severity-rule`: each adjacent comparison alone would
    only ever see the already-demoted severity.
    """
    was_enabled = superseded.get("enabled", True)
    now_enabled = winning.get("enabled", True)
    severity = _more_severe(original_severity, superseded.get("severity"), winning.get("severity"))
    disables = bool(was_enabled and not now_enabled)
    # The impact string carries the severity so that turning a rule OFF never
    # reads like narrowing one. `disables-critical-severity-rule` and
    # `modifies-medium-severity-rule` are distinguishable at a glance and by
    # grep, which is the point: this is what a reviewer scans for.
    impact = f"{'disables' if disables else 'modifies'}-{severity}-severity-rule"
    return {
        "rule_id": rule_id,
        "winning_origin": winning_ref["origin"],
        "winning_file": winning_ref["file"],
        "superseded_origin": superseded_ref["origin"],
        "superseded_file": superseded_ref["file"],
        "changed": changed,
        "material": any(field in MATERIAL_OVERRIDE_FIELDS for field in changed),
        "enabled": {"from": was_enabled, "to": now_enabled},
        "severity": {"from": superseded.get("severity"), "to": winning.get("severity")},
        # The anchor made visible: the severity this id was FIRST defined with,
        # not merely applied to `impact`. A reviewer can check the ranking.
        "original_severity": original_severity,
        "disables_rule": disables,
        "impact": impact,
        # The actual change, not just its field names: see _override_details.
        "details": _override_details(superseded, winning, changed),
    }


def _load_rule_file(path: Path) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    return data


@dataclass
class RuleRunReport:
    """Result of a rule-engine run.

    ``findings`` is what the verdict is computed from. ``coverage`` and
    ``disabled_rules`` are evidence only and never participate in pass/fail
    (SEC-006).
    """

    findings: List[Dict[str, Any]] = field(default_factory=list)
    coverage: List[Dict[str, Any]] = field(default_factory=list)
    disabled_rules: List[Dict[str, Any]] = field(default_factory=list)
    #: Every rule replaced by a later rule file with the same `id`, in the order
    #: the replacements happened. Evidence only — an override is a documented,
    #: legitimate action and never produces a finding or changes the verdict.
    #: Its whole purpose is that the action cannot be taken invisibly.
    overrides: List[Dict[str, Any]] = field(default_factory=list)
    #: Rule files that could not be loaded or failed validation. These DO reach
    #: the verdict: a rule that does not run is a gap in enforcement, and a gap
    #: that reports "pass" is worse than a failure. See load_rules.
    load_errors: List[Dict[str, Any]] = field(default_factory=list)
    #: Ids that actually ended up enforced. Lets the caller tell a rejected
    #: rule file that left no enforcement from one whose id is still covered
    #: by a valid definition in the other directory.
    loaded_rule_ids: List[str] = field(default_factory=list)


class RuleEngine:
    # NOTE: schema.json ships alongside this module as the documented statement
    # of intent for rule files, but it is NOT enforced — validation is
    # `_validate_rule`, which overlaps the schema without matching it. An
    # earlier version loaded the schema into `self._schema` here and never read
    # it, which made rules look schema-validated when they were not.
    def __init__(self) -> None:
        self.load_errors: List[Dict[str, Any]] = []
        self.overrides: List[Dict[str, Any]] = []
        #: id -> severity of the FIRST valid definition loaded for that id (the
        #: shipped severity when a shipped rule exists). This is the anchor for
        #: override `impact` ranking and for the severity shown in
        #: `disabled_rules`, so a chain of overriding files cannot demote the
        #: severity context step by step before disabling the rule.
        self.original_severities: Dict[str, str] = {}

    def load_rules(
        self,
        rule_dirs: List[Path],
        origins: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Load and validate every rule file, recording any that cannot be used.

        A rule file that fails to parse or fails validation is NOT silently
        dropped. Dropping it removes a check from the run while the gate still
        reports its verdict, so a one-token edit — say a cap of ``0`` on the
        secret-scan rule — can turn a failing repository into a passing one with
        no trace in the evidence. That is the exact failure this project exists
        to prevent, so load failures are recorded here and surfaced as findings
        by the caller (SICARIO-RULE-INVALID / SICARIO-RULE-UNREADABLE).

        PRECEDENCE CONTRACT — read before reordering anything.

        There is exactly ONE precedence rule and it is deliberately dumb: for a
        given ``id``, THE LAST RULE FILE LOADED WINS. Directories are consumed in
        the order given; within a directory, files are consumed in sorted name
        order. Nothing here knows or cares which directory is "shipped" and
        which is "the project".

        The caller therefore owns the policy, and the policy is that the target
        project's ``.sicario/rules/`` is passed LAST so a project rule beats the
        shipped rule of the same id (``sicario_cli.cli._rule_sources``). That is
        the documented capability: a platform team narrows or disables a shipped
        rule without editing the package. Passing the project directory first
        inverts it and makes the capability unreachable — that was the defect
        this contract now pins down.

        Every replacement is recorded in ``self.overrides``. Overriding is
        allowed; overriding INVISIBLY is not.

        ``origins`` is an optional list of short labels parallel to
        ``rule_dirs`` ("shipped", "project") used in the override records. It
        defaults to the directory paths, which are fine for debugging but are
        machine-specific — callers that write evidence should pass real labels.
        """
        rules: List[Dict[str, Any]] = []
        seen_ids: Dict[str, int] = {}
        # id -> where the last definition of that id that CHANGED anything came
        # from. A byte-equivalent redefinition (the `sicario init` verbatim
        # copies, above all) must not re-anchor this: it changed nothing, so
        # the definition a later real override supersedes is still the one
        # before it. Otherwise `superseded_origin` would read "project" instead
        # of "shipped" in every normally-initialised project, and a reviewer or
        # CI filter on `superseded_origin == "shipped"` would never match.
        provenance: Dict[str, Dict[str, str]] = {}
        self.load_errors = []
        self.overrides = []
        self.original_severities = {}

        labels = [str(directory) for directory in rule_dirs] if origins is None else list(origins)
        if len(labels) != len(rule_dirs):
            raise ValueError("origins must be parallel to rule_dirs")

        for directory, origin in zip(rule_dirs, labels):
            if not directory.is_dir():
                continue
            for rule_file in sorted(directory.glob("*.rule.json")):
                data = _load_rule_file(rule_file)
                if data is None:
                    self.load_errors.append(
                        {
                            "file": rule_file.name,
                            "path": str(rule_file),
                            "origin": origin,
                            "code": "SICARIO-RULE-UNREADABLE",
                            "errors": ["file is not readable, decodable, or a JSON object"],
                        }
                    )
                    continue
                errors = _validate_rule(data)
                if errors:
                    self.load_errors.append(
                        {
                            "file": rule_file.name,
                            "path": str(rule_file),
                            "origin": origin,
                            "rule_id": data.get("id"),
                            "code": "SICARIO-RULE-INVALID",
                            "errors": errors,
                        }
                    )
                    continue
                rid = data["id"]
                ref = {"origin": origin, "file": rule_file.name}
                if rid in seen_ids:
                    idx = seen_ids[rid]
                    changed = _rule_diff(rules[idx], data)
                    # A byte-for-byte equivalent redefinition is not an override
                    # of anything: the effective rule is unchanged. `sicario
                    # init` copies every shipped rule into `.sicario/rules/`, so
                    # recording those ~21 no-op collisions on every run would
                    # bury the one override a reviewer needs to see. For the
                    # same reason it must not re-anchor `provenance` either: the
                    # definition a later override supersedes is the last one
                    # that MATTERED, not a verbatim copy of it.
                    if changed:
                        self.overrides.append(
                            _override_record(
                                rid,
                                rules[idx],
                                data,
                                provenance[rid],
                                ref,
                                changed,
                                self.original_severities.get(rid),
                            )
                        )
                        provenance[rid] = ref
                    rules[idx] = data
                else:
                    seen_ids[rid] = len(rules)
                    rules.append(data)
                    self.original_severities[rid] = data["severity"]
                    provenance[rid] = ref

        return rules

    def evaluate(self, rule: Dict[str, Any], root: Path) -> List[Dict[str, Any]]:
        from sicario_cli.rules.kinds import evaluate as kind_evaluate

        if not rule.get("enabled", True):
            return []
        return kind_evaluate(rule["kind"], rule, root)

    def run_detailed(
        self,
        root: Path,
        rule_dirs: Optional[List[Path]] = None,
        origins: Optional[List[str]] = None,
    ) -> RuleRunReport:
        from sicario_cli.rules.kinds import evaluate_detailed as kind_evaluate_detailed

        if rule_dirs is None:
            rule_dirs = [
                root / ".sicario" / "rules",
            ]
            origins = ["project"]
        rules = self.load_rules(rule_dirs, origins=origins)
        report = RuleRunReport()
        report.load_errors = list(self.load_errors)
        report.loaded_rule_ids = [r["id"] for r in rules]
        report.overrides = list(self.overrides)
        for rule in rules:
            if not rule.get("enabled", True):
                # Recorded so a rule disabled by identifier override — a
                # disabled `critical` rule especially — is visible in evidence
                # rather than only in an overriding file (FR-022, AC-003).
                # The severity shown is the ORIGINAL one for this id (shipped
                # when a shipped rule exists), so an override chain that
                # demotes a rule before disabling it still reads as a disabled
                # rule of its original severity. For a rule never overridden
                # the two are the same value.
                report.disabled_rules.append(
                    {
                        "id": rule["id"],
                        "severity": self.original_severities.get(rule["id"], rule["severity"]),
                        "kind": rule["kind"],
                    }
                )
                continue
            rule_findings, rule_coverage = kind_evaluate_detailed(rule["kind"], rule, root)
            report.findings.extend(rule_findings)
            if rule_coverage is not None:
                report.coverage.append(rule_coverage)
        return report

    def run(
        self,
        root: Path,
        rule_dirs: Optional[List[Path]] = None,
        origins: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        return self.run_detailed(root, rule_dirs=rule_dirs, origins=origins).findings
