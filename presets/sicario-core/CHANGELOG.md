## 0.6.0 - 2026-07-28

- Three new critical secret rules (041 AWS access key ids, 042 provider
  tokens, 043 private key material), with left-boundary guards so `risk-*`
  identifiers no longer false-positive.
- Rule files now ship inside the packaged assets, so pip installs enforce the
  full rule set (previously the installed build loaded zero rules).
- Templates are complete standalone documents in every preset; a preset's
  template can win the resolution race without weakening the gate.
- Caps (`max_findings_per_file` / `max_findings_per_rule`) documented in the
  schema; invalid caps fail the gate as `SICARIO-RULE-INVALID`.

# Changelog

All notable changes to the SicarioSpec Core preset are tracked here.

## Unreleased

No unreleased changes yet.

## [0.5.1] - 2026-06-25

### Changed

- Expanded the preset README into a catalog-ready usage guide with exact
  `specify preset add` commands, template impact mapping, workflow guidance,
  fit/non-fit guidance, and verification commands.
- Repositioned the preset as evidence-first security operations governance.
- Added the Security Evidence Chain to the README, specification template, plan
  template, checklist, task list, and constitution.
- Added operational signal, detection, response, rollback, and evidence-retention
  prompts.
- Replaced hard standalone dependency language around `sicario verify` with
  project verification gate wording and optional SicarioSpec CLI references.

## [0.1.2] - 2026-06-19

### Changed

- Converted the preset package to the upstream Spec Kit `preset.yml` schema.
- Added preset-local README, changelog, and license files for catalog review.
- Kept the preset focused on baseline secure-by-default governance templates.

## [0.1.0] - 2026-06-19

### Added

- Initial secure-by-default Spec Kit templates for specifications, plans, tasks,
  checklists, and constitutions.
