# Docs And Diagrams

SicarioSpec treats documentation as a delivery gate.

Default structure:

```text
docs/
├── architecture/
├── compliance/
├── diagrams/
├── security/
└── docs-impact.md

docs-site/
├── docs/
├── docusaurus.config.js
├── sidebars.js
└── package.json
```

Rules:

- Every implementation change updates docs, diagrams, or `docs/docs-impact.md`.
- Architecture diagrams are source-controlled, preferably Mermaid.
- CI builds docs on PR and `main`.
- Publishing docs after merge is allowed, but committing generated docs back to
  `main` is opt-in and should use a machine user plus branch protection.

