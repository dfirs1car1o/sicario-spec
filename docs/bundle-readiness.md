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

The operational install path for 0.5.1 is the Python package plus the
`sicario-core` Spec Kit preset ZIP:

```bash
pip install sicario-spec
sicario init ./project --profile appsec,cloud-iac,security-toolchain,compliance
sicario verify ./project
```

The release must also publish `sicario-core-0.5.1.zip` so Spec Kit users can
install the core preset directly from the GitHub release asset:

```bash
specify preset add --from https://github.com/dfirs1car1o/sicario-spec/releases/download/v0.5.1/sicario-core-0.5.1.zip
specify preset info sicario-core
```

The root `bundle.yml` is the intended full SicarioSpec bundle manifest, but it
is not a one-step fresh-project install until every referenced Sicario preset
and extension is available through an install-allowed Spec Kit catalog. Spec
Kit's current bundle resolver does not install arbitrary local preset folders
embedded next to `bundle.yml`; it resolves bundle components from bundled Spec
Kit assets, already-installed project components, or active catalogs.

## Maintainer Operating State

Before calling the repo clean, confirm this state:

| Area | Ready state |
|---|---|
| Issues | Open work is assigned and scoped; stale `needs-triage` labels are removed. |
| Pull requests | No open PR has failing checks or unresolved maintainer-owned cleanup. |
| Branches | Active branches have an open PR or an explicit reason to remain. |
| CI | Test, docs build, CodeQL, and static analysis checks are green. |
| Docs | Public docs reflect the latest release version, control-map count, and rule-engine behavior. |
| Release assets | The latest tag has wheel, source distribution, and `sicario-core` preset ZIP assets. |
| Bundle manifest | `bundle.yml` pins the intended component set and documents any catalog dependencies honestly. |

## Release Verification Stack

Run these before merging release-shaping changes:

```bash
python3 -m unittest discover -s tests
python3 -m sicario_cli.cli verify .
python3 -m sicario_cli.cli verify . --validate-rules
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

For the core Spec Kit preset release asset, validate the ZIP over an HTTP(S)
URL rather than only from a local file path:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory dist
tmpdir="$(mktemp -d)"
cd "$tmpdir"
specify init --here --integration codex --ignore-agent-tools --force
specify preset add --from http://127.0.0.1:8765/sicario-core-0.5.1.zip
specify preset info sicario-core
```

Expected result: `specify preset info sicario-core` reports version `0.5.1`.

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
