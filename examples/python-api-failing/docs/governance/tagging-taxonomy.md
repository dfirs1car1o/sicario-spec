# Tagging Taxonomy — Customer Invoice Export API

Stable tags so handling, ownership, retention, and traceability are
enforceable.

## Required Tags

| Tag | Required For | Accepted Values / Format | Purpose |
|---|---|---|---|
| owner | all artifacts/evidence | team or person handle | accountability |
| system | all artifacts/evidence | system slug | grouping |
| environment | runtime/evidence | dev, test, staging, prod | blast-radius context |
| data-classification | data/evidence | public, internal, confidential, restricted | handling requirements |
| retention | data/evidence/logs | duration or policy name | deletion expectations |
| feature-id | feature evidence | specs/NNN-name | feature traceability |

## This Feature's Tags

| Tag | Value |
|---|---|
| owner | @finance-platform |
| system | invoice-export-api |
| environment | prod |
| data-classification | confidential |
| retention | 90d |
| feature-id | specs/001-example |
