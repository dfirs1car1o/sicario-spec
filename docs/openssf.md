# OpenSSF Posture

SicarioSpec uses OpenSSF Scorecard for public security-health signal and tracks
OpenSSF Best Practices as a release-readiness target.

## Current Automation

- OpenSSF Scorecard workflow: `.github/workflows/scorecard.yml`
- Scorecard badge: `README.md`
- Dependabot: `.github/dependabot.yml`
- CodeQL: `.github/workflows/codeql.yml`
- Security policy: `SECURITY.md`
- Code of conduct: `CODE_OF_CONDUCT.md`
- Structured issue and PR workflow: `.github/`

## Current Scorecard Posture

The public Scorecard result on 2026-06-22 was `5.4/10`. The lowest checks were
mostly maturity and supply-chain hardening signals:

- `Maintained`: the repository was created on 2026-06-19 and is younger than
  Scorecard's 90-day maturity window.
- `Code-Review`: early changes included direct pushes; future changes should go
  through reviewed pull requests.
- `Pinned-Dependencies`: GitHub Actions, container images, and release build
  tools must stay pinned.
- `Signed-Releases`: releases must include provenance or signatures that
  Scorecard can detect.
- `Packaging`: package publication should use a detectable GitHub workflow and
  avoid long-lived registry credentials.
- `Fuzzing`: no fuzzing integration is configured yet.
- `CII-Best-Practices`: OpenSSF Best Practices self-certification has not been
  completed.

## Hardening Targets

- Pin GitHub Actions by full commit SHA and keep Dependabot enabled for updates.
- Keep release build dependencies hash-pinned under
  `.github/requirements/release-build.txt`.
- Pin starter container images by digest in both source presets and packaged
  preset assets.
- Scope workflow token permissions at the job level and grant write permissions
  only to jobs that publish releases, Pages, SARIF, or provenance.
- Use reviewed pull requests for normal changes to improve the `Code-Review`
  signal over time.
- Prefer GitHub repository rulesets for branch protection so Scorecard can read
  protection state using the default token.
- Publish future releases with artifact attestations or signatures and confirm
  Scorecard detects provenance.
- Publish PyPI packages through the manual `publish-pypi` workflow after the
  `sicario-spec` PyPI project and GitHub `pypi` environment are configured for
  trusted publishing.
- Decide whether fuzzing is appropriate for the CLI and template parsers. If it
  is, add a real fuzzing workflow rather than a badge-only placeholder.

## Best Practices Badge

The OpenSSF Best Practices badge is not claimed yet. It requires external
self-certification through the OpenSSF Best Practices app. Track this as a
future governance issue after the first public release.

Do not add a passing/silver/gold badge until the project has actually earned
that status.
