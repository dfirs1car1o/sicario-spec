#!/usr/bin/env bash
set -euo pipefail

catalog_base_url="${1:-http://127.0.0.1:8766/catalogs}"
specify_bin="${SPECIFY_BIN:-specify}"
python_bin="${PYTHON_BIN:-python3}"
tmp_parent="${RUNNER_TEMP:-/tmp}"
project_dir="$(mktemp -d "${tmp_parent%/}/sicario-bundle-smoke.XXXXXX")"

export NO_COLOR=1

echo "Smoke project: ${project_dir}"
cd "${project_dir}"

"${specify_bin}" init --here --integration codex --ignore-agent-tools --force >/tmp/sicario-bundle-smoke-init.log
"${specify_bin}" preset catalog add "${catalog_base_url}/presets.json" --name sicario --priority 1 --install-allowed
"${specify_bin}" extension catalog add "${catalog_base_url}/extensions.json" --name sicario --priority 1 --install-allowed
"${specify_bin}" bundle catalog add "${catalog_base_url}/bundles.json" --id sicario --priority 1 --policy install-allowed
"${specify_bin}" bundle info sicario-spec >/tmp/sicario-bundle-smoke-info.log
"${specify_bin}" bundle install sicario-spec >/tmp/sicario-bundle-smoke-install.log
"${specify_bin}" preset resolve spec-template >/tmp/sicario-bundle-smoke-resolve.log

"${python_bin}" - <<'PY'
import json
from pathlib import Path

expected_presets = {
    "sicario-agent-fleet",
    "sicario-ai-system",
    "sicario-appsec",
    "sicario-cloud-iac",
    "sicario-compliance",
    "sicario-core",
    "sicario-docs",
    "sicario-enterprise-strict",
    "sicario-saas",
    "sicario-security-toolchain",
    "sicario-supply-chain",
}
expected_priorities = {
    "sicario-core": 50,
    "sicario-docs": 10,
    "sicario-appsec": 9,
    "sicario-ai-system": 8,
    "sicario-agent-fleet": 7,
    "sicario-cloud-iac": 6,
    "sicario-supply-chain": 5,
    "sicario-compliance": 4,
    "sicario-saas": 3,
    "sicario-security-toolchain": 2,
    "sicario-enterprise-strict": 1,
}

records = json.loads(Path(".specify/bundle-records.json").read_text(encoding="utf-8"))
bundles = records.get("bundles", [])
if len(bundles) != 1 or bundles[0].get("bundle_id") != "sicario-spec":
    raise SystemExit("sicario-spec bundle record was not created")

components = bundles[0].get("contributed_components", [])
preset_ids = {item["id"] for item in components if item.get("kind") == "presets"}
extension_ids = {item["id"] for item in components if item.get("kind") == "extensions"}
if preset_ids != expected_presets:
    raise SystemExit(f"unexpected preset components: {sorted(preset_ids)}")
if extension_ids != {"sicario-guard"}:
    raise SystemExit(f"unexpected extension components: {sorted(extension_ids)}")
if len(components) != 12:
    raise SystemExit(f"expected 12 contributed components, got {len(components)}")

preset_registry = json.loads(Path(".specify/presets/.registry").read_text(encoding="utf-8"))
installed_presets = preset_registry.get("presets", {})
for preset_id, priority in expected_priorities.items():
    actual = installed_presets.get(preset_id, {}).get("priority")
    if actual != priority:
        raise SystemExit(f"{preset_id} priority {actual!r} != {priority}")

extension_registry = json.loads(Path(".specify/extensions/.registry").read_text(encoding="utf-8"))
if "sicario-guard" not in extension_registry.get("extensions", {}):
    raise SystemExit("sicario-guard extension was not installed")

resolve_output = Path("/tmp/sicario-bundle-smoke-resolve.log").read_text(encoding="utf-8")
for preset_id in ("sicario-core", "sicario-docs", "sicario-enterprise-strict"):
    if preset_id not in resolve_output:
        raise SystemExit(f"{preset_id} missing from spec-template composition")
PY

echo "sicario-spec bundle smoke passed"
