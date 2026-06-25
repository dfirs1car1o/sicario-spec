# Release Process

SicarioSpec releases are GitHub releases backed by signed-off local validation,
tag-driven packaging, full Spec Kit bundle assets, install-allowed catalogs, and
GitHub artifact attestations for built distributions.

## Versioning

- Package version is stored in `VERSION`, `pyproject.toml`, and
  `sicario_cli/version.py`.
- Preset, extension, and starter control-map versions should match the release
  unless they intentionally carry their own schema version.
- Release tags use `vMAJOR.MINOR.PATCH`, for example `v0.1.0`.
- Release tags are immutable once published. Do not move or delete a published
  tag; ship a new patch release instead.
- Release assets are classified as `public` only after validation confirms they
  contain no secrets, private evidence, customer data, tenant identifiers, or
  unpublished vulnerability details.

During the `0.x` line, breaking changes may ship in minor versions. Patch
versions should be bug fixes, documentation fixes, or non-breaking hardening.

## Pre-Release Checklist

Run from the repository root:

```bash
python3 -m unittest discover -s tests
python3 -m sicario_cli.cli verify .
python3 -m sicario_cli.cli verify . --validate-rules
python3 scripts/build_release_assets.py
tmpdir=$(mktemp -d)
python3 -m pip wheel . -w "$tmpdir/wheelhouse"
python3 -m venv "$tmpdir/venv"
"$tmpdir/venv/bin/pip" install "$tmpdir"/wheelhouse/sicario_spec-*.whl
"$tmpdir/venv/bin/sicario" --version
"$tmpdir/venv/bin/sicario" init "$tmpdir/project" --profile appsec,cloud-iac,security-toolchain,compliance
"$tmpdir/venv/bin/sicario" verify "$tmpdir/project"
```

Confirm:

- `CHANGELOG.md` has an entry for the release.
- `presets/sicario-core/CHANGELOG.md` has an entry for the release when the
  catalog preset changes.
- `README.md` install and badge links are accurate.
- `presets/sicario-core/README.md` catalog install instructions point to the
  release preset ZIP asset.
- `catalogs/presets.json`, `catalogs/extensions.json`, and
  `catalogs/bundles.json` point to the intended release ZIP assets.
- `bundle.yml` pins `sicario-spec` components to the release version and keeps
  `sicario-core` as the lower-priority base layer under appended profile
  overlays.
- `docs/governance/data-classification.md` and
  `docs/governance/tagging-taxonomy.md` are current.
- Release notes and assets follow classification and tagging discipline.
- Git working tree is clean.
- GitHub Actions are green for the release commit.
- No generated output, local build output, secrets, or private evidence files
  are staged.

## GitHub Release

```bash
version="$(cat VERSION)"
git tag -a "v$version" -m "SicarioSpec v$version"
git push origin main "v$version"
```

The release workflow runs on the pushed tag. It verifies the tag against
`VERSION`, `pyproject.toml`, and `sicario_cli/version.py`, builds the sdist,
wheel, all 11 preset ZIPs, `sicario-guard-$version.zip`,
`sicario-spec-$version.zip`, and the three catalog JSON files. It then validates
the release asset set, smoke-tests native `specify bundle install sicario-spec`
against localhost catalogs, smoke-tests the wheel, emits artifact attestations,
and creates the GitHub release with assets when the release does not already
exist.

Existing GitHub releases are treated as immutable. A rerun for an existing tag
will rebuild, smoke-test, upload the workflow artifact, and emit attestations,
but it will not add, delete, replace, or rename release assets. Ship a new patch
release if published assets need to change.

If the GitHub release does not already exist, the workflow creates it with
generated release notes. To curate release notes before packaging, create a
draft or published release for the tag first, then push the tag or run the
workflow manually for that tag.

Curated release notes should include:

- What's included.
- Bundle install commands and CLI install command.
- Validation performed.
- Known limitations.

## Bundle Asset Smoke Test

Use this local smoke when bundle manifests, catalogs, release packaging, or
Spec Kit compatibility changes:

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

The smoke checks that a fresh Spec Kit project can add the Sicario preset,
extension, and bundle catalogs; install `sicario-spec`; record all 12 bundle
components; preserve expected preset priorities; install `sicario-guard`; and
resolve a composed `spec-template` chain.

## Post-Release

- Confirm the GitHub release is public.
- Confirm the release badge resolves.
- Confirm OpenSSF Scorecard has a recent result after the workflow runs.
- Keep the OpenSSF Best Practices badge status honest; do not display an
  achievement badge until the project has completed the external self-assessment.

## PyPI Publishing

PyPI publication is intentionally separated from the GitHub release workflow.
The `publish-pypi` workflow is manual, uses PyPI Trusted Publishing through
GitHub's OIDC token, and requires the `pypi` GitHub environment.

Before the first publish:

- Reserve or create the `sicario-spec` PyPI project.
- Configure a PyPI Trusted Publisher for owner `dfirs1car1o`, repository
  `sicario-spec`, workflow `.github/workflows/publish-pypi.yml`, environment
  `pypi`.
- Configure the `pypi` GitHub environment with required reviewers.
- Confirm the GitHub release assets and attestations for the same tag already
  exist.

To publish:

1. Open **Actions** -> **publish-pypi** -> **Run workflow**.
2. Enter the release tag, for example `v0.5.1`.
3. Enter `publish` in the confirmation field.
4. Approve the `pypi` environment gate.
5. Confirm the PyPI release page, package hashes, and install command.

Do not use long-lived PyPI API tokens for this repository. If trusted publishing
is unavailable, defer PyPI publication until it can be configured.
