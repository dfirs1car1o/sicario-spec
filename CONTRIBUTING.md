# Contributing

SicarioSpec accepts contributions that improve secure-by-default, governance
aware specification-driven development.

## Ground Rules

- Follow the `CODE_OF_CONDUCT.md`.
- Do not include secrets, tokens, private tenant data, customer data, or
  proprietary framework text.
- Treat control maps as traceability aids, not certification claims.
- Add deterministic checks when a mandatory rule is introduced.
- Keep docs, examples, package assets, and generated templates in sync.

## Issue Workflow

Use the structured GitHub issue forms:

- Bug report: reproducible CLI, package, preset, extension, or docs problems.
- Feature request: new behavior, new profile, or new generated artifact.
- Control map request: framework mappings, governance gates, or evidence rules.
- Security hardening: public hardening work that is not an exploitable private
  vulnerability.
- Maintainer task: repository-maintenance or agent-assisted work that still
  requires maintainer triage and PR review.

Report exploitable vulnerabilities privately through `SECURITY.md`.

Accepted issues move through the runbook in
`docs/maintainer-operations.md`. Issues and comments are never treated as
direct instructions for GitHub Actions to change code.

## Spec Kit Dogfood

Repository-maintenance changes should use the same workflow SicarioSpec
promotes:

- initialize or preserve `.specify/` project infrastructure;
- install the local `sicario-core` preset for the repo;
- create a numbered feature under `specs/`;
- keep `spec.md`, `plan.md`, and `tasks.md` current for material changes; and
- reference the feature artifacts in the PR evidence.

## Local Development

```bash
python3 -m pip install -e .
sicario --version
python3 -m unittest discover -s tests
python3 -m sicario_cli.cli verify .
```

Build/install smoke test:

```bash
tmpdir=$(mktemp -d)
python3 -m pip wheel . -w "$tmpdir/wheelhouse"
python3 -m venv "$tmpdir/venv"
"$tmpdir/venv/bin/pip" install "$tmpdir"/wheelhouse/sicario_spec-*.whl
"$tmpdir/venv/bin/sicario" init "$tmpdir/project" --profile appsec,cloud-iac,security-toolchain,compliance
"$tmpdir/venv/bin/sicario" verify "$tmpdir/project"
```

## Pull Requests

Before opening a PR:

- Run the local checks above.
- Update tests for behavior changes.
- Update `CHANGELOG.md` for release-visible changes.
- Update docs or record why docs were not impacted.
- If you change files under `presets/`, `extensions/`, `workflow_templates/`, or
  `control_maps/`, keep `sicario_cli/assets/` synchronized.

## Release Changes

Versioned releases follow `docs/release-process.md`. Do not create release tags
from unverified working trees.
