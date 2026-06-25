# Bundle Readiness

This page is the maintainer checklist for keeping SicarioSpec bundle-ready:
installable, reviewable, demonstrable, and safe for public contributors.

## Current Bundle Surface

SicarioSpec 0.5.1 ships:

- 11 Spec Kit preset manifests under `presets/sicario-*/preset.yml`.
- 8 guard commands in `extensions/sicario-guard/`.
- A Python CLI entry point, `sicario`, backed by `sicario_cli.cli`.
- A declarative `sicario verify` rule engine with 10 evaluator kinds.
- Shipped default rules in `presets/sicario-core/rules/*.rule.json`.
- 11 starter control maps under `control_maps/` and
  `docs/compliance/control-maps/`.
- Docusaurus documentation under `docs-site/`, sourcing content from `docs/`.
- GitHub Actions for tests, CodeQL, Pages build, release packaging, Scorecard,
  Dependabot, and safe issue triage.

## Operational Install State

The native Spec Kit install path for 0.5.1 is the full `sicario-spec` bundle
served through Sicario-owned install-allowed catalogs. Spec Kit keeps separate
catalogs for presets, extensions, and bundles, so a fresh project needs all
three catalog registrations before the bundle can resolve its components:

```bash
specify init --here --integration codex --ignore-agent-tools --force
specify preset catalog add https://raw.githubusercontent.com/dfirs1car1o/sicario-spec/main/catalogs/presets.json --name sicario --priority 1 --install-allowed
specify extension catalog add https://raw.githubusercontent.com/dfirs1car1o/sicario-spec/main/catalogs/extensions.json --name sicario --priority 1 --install-allowed
specify bundle catalog add https://raw.githubusercontent.com/dfirs1car1o/sicario-spec/main/catalogs/bundles.json --id sicario --priority 1 --policy install-allowed
specify bundle install sicario-spec
specify preset resolve spec-template
```

Expected result: `specify bundle install sicario-spec` installs 12 components:
the `sicario-guard` extension plus all 11 SicarioSpec presets. The resolved
`spec-template` composition chain should start with `sicario-core`, then append
the profile overlays, ending with `sicario-enterprise-strict`.

The Python package remains the fastest full bootstrap path when the target
repository should receive docs, risk registers, control maps, workflow
templates, and deterministic verification immediately:

```bash
pip install sicario-spec
sicario init ./project --profile appsec,cloud-iac,security-toolchain,compliance
sicario verify ./project
```

The release also publishes `sicario-core-0.5.1.zip` so users can install the
minimal baseline preset directly:

```bash
specify preset add --from https://github.com/dfirs1car1o/sicario-spec/releases/download/v0.5.1/sicario-core-0.5.1.zip
specify preset info sicario-core
```

The upstream Spec Kit community catalog is optional discovery. It should not be
treated as the release authority for every SicarioSpec version bump; the
Sicario-owned catalogs in this repository are what make current release assets
installable without an upstream catalog PR for every patch.

## Maintainer Operating State

Before calling the repo clean, confirm this state:

| Area | Ready state |
|---|---|
| Issues | Open work is assigned and scoped; stale `needs-triage` labels are removed. |
| Pull requests | No open PR has failing checks or unresolved maintainer-owned cleanup. |
| Branches | Active branches have an open PR or an explicit reason to remain. |
| CI | Test, docs build, CodeQL, and static analysis checks are green. |
| Docs | Public docs reflect the latest release version, control-map count, and rule-engine behavior. |
| Release assets | The latest tag has wheel, source distribution, 11 preset ZIPs, the guard extension ZIP, the bundle ZIP, and catalog JSON assets. |
| Bundle manifest | `bundle.yml` pins the intended component set and composes `sicario-core` as the base layer under appended profile overlays. |

## Release Verification Stack

Run these before merging release-shaping changes:

```bash
python3 -m unittest discover -s tests
python3 -m sicario_cli.cli verify .
python3 -m sicario_cli.cli verify . --validate-rules
python3 scripts/build_release_assets.py
(cd docs-site && npm run build)
```

For packaging-sensitive changes, add an installed-wheel smoke test:

```bash
python3 -m build
python3 -m venv /tmp/sicario-wheel-smoke
/tmp/sicario-wheel-smoke/bin/pip install dist/sicario_spec-0.5.1-py3-none-any.whl
/tmp/sicario-wheel-smoke/bin/sicario init /tmp/sicario-smoke --profile appsec --force
/tmp/sicario-wheel-smoke/bin/sicario verify /tmp/sicario-smoke
```

For the native Spec Kit bundle release path, validate the catalogs and ZIPs over
an HTTP(S) URL rather than only from local file paths:

```bash
smoke_assets="$(mktemp -d)"
python3 scripts/build_release_assets.py \
  --output-dir "$smoke_assets" \
  --catalog-dir "$smoke_assets/catalogs" \
  --catalog-base-url "http://127.0.0.1:8766"
python3 -m http.server 8766 --bind 127.0.0.1 --directory "$smoke_assets" &
server_pid="$!"
trap 'kill "$server_pid"' EXIT
SPECIFY_BIN=specify scripts/smoke_bundle_install.sh http://127.0.0.1:8766/catalogs
```

Expected result: `scripts/smoke_bundle_install.sh` reports
`sicario-spec bundle smoke passed`.

## Contributor Review Queue

The current public issue queue is intentionally small. The maintainer should be
waiting for contributor PRs that:

- add a custom rule example and README for `.sicario/rules/`;
- add one new high-quality control map from the requested framework set.

Review those PRs for:

- no invalid JSON comments;
- valid `*.rule.json` or control-map JSON;
- clear README or docs updates;
- no generated artifacts committed accidentally;
- passing `sicario verify`, tests, and docs build.

## Branch Cleanup Rules

Use these rules before deleting branches:

- Delete merged feature branches after their PR is merged and the branch is not
  needed for a release tag.
- Do not delete unmerged branches that contain useful submission/demo artifacts
  unless the content has been folded into active docs or explicitly abandoned.
- Keep `main` aligned with `origin/main` after merges; do not leave local-only
  commits on `main` that duplicate an open PR branch.

## Public Story Check

The public story should remain narrow and defensible:

- SicarioSpec is evidence-first Spec Kit governance.
- The differentiator is a halting, code-owned gate with no LLM in the pass/fail
  path.
- Control maps are starter evidence maps, not certification claims.
- AI agents can draft, explain, and remediate, but code decides the verdict and
  humans approve high-impact changes.
