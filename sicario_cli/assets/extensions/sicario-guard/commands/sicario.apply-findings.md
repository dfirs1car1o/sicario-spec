# `/sicario.apply-findings`

Convert approved SicarioSpec review findings into tasks.

Rules:

- Do not auto-apply high-risk changes.
- Do not overwrite human edits.
- Add tasks under the active `specs/*/tasks.md`.
- Preserve finding ID, rationale, and evidence path.

