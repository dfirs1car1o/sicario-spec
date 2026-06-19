# SicarioSpec Guard Extension

`sicario-guard` adds review, verification, threat-modeling, control mapping,
and evidence generation commands to Spec Kit.

The extension is intentionally deterministic-first. Commands may ask an AI agent
to draft or review, but authoritative pass/fail state comes from repository
files, validators, tests, and `sicario verify`.

