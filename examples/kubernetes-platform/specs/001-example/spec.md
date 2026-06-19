# Feature Specification: Kubernetes Platform Example

## Data Classification
Workload metadata.
## Trust Boundaries
CI runner to Kubernetes API server.
## Security Requirements
Restricted pod security, namespace isolation, network policy, non-root containers.
## Abuse Cases
Privileged pod or hostPath mount is introduced.
## Evidence
Manifest scan, admission policy result, and review record.

