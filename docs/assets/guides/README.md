# Guide Visual Assets

Visual assets for the onboarding guides and playbooks (feature
007-onboarding-guides-and-playbooks). One subdirectory per guide slug:

```
docs/assets/guides/<guide-slug>/<step-slug>--v<captured-version>.<ext>
```

The captured version is embedded in every file name, so staleness is
computable from the name alone. A superseded asset is replaced under the
new captured-version name and the old file deleted in the same change.

## Capture classes

Every asset belongs to exactly one labeled class, recorded in its asset
record:

- `terminal-text` — terminal interactions are captured as text blocks in
  the guide source, never as images of text; they produce no file here.
- `tool-captured` — automated screenshots of real rendered surfaces taken
  with browser tooling during a real reference run, reproducible by
  re-running the documented capture.
- `manual` — reserved for surfaces that genuinely require a human desktop,
  and for all screencasts. Tasks for these carry the `MANUAL CAPTURE:`
  prefix and are never performed or checked off by automation.

Fabricated, synthesized, or edited-to-depict-the-unobserved imagery is
prohibited for every class.

## Asset records

Each guide directory that contains assets carries an `asset-records.md`
listing, per asset: file name, capture class, the step it belongs to, and
the reference-run identifiers it was captured from (reference-run
repository name, run date, captured version). An asset with no reference
run to point at is illegitimate. Asset-bearing changes include the
sanitation review as an explicit review step for tool-captured and manual
assets alike.

## Current contents

The three onboarding-core guides (`getting-started`,
`initial-setup-selection`, `first-spec`) direct the reader only at
terminal surfaces, captured as text blocks in the guide sources; their
directories are present as the destination for any future tool-captured
or manual assets and hold none today, with the stated reason recorded in
each guide's Visual Assets Note.
