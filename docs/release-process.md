# Release Process

SicarioSpec releases are GitHub releases backed by signed-off local validation,
tag-driven packaging, and GitHub artifact attestations for built distributions.

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
- `README.md` install and badge links are accurate.
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
`VERSION`, `pyproject.toml`, and `sicario_cli/version.py`, builds the sdist and
wheel, smoke-tests the wheel, emits artifact attestations, and creates the
GitHub release with assets when the release does not already exist.

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
- Install command.
- Validation performed.
- Known limitations.

## Post-Release

- Confirm the GitHub release is public.
- Confirm the release badge resolves.
- Confirm OpenSSF Scorecard has a recent result after the workflow runs.
- Keep the OpenSSF Best Practices badge status honest; do not display an
  achievement badge until the project has completed the external self-assessment.
