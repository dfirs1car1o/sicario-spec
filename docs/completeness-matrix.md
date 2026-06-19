# Completeness Matrix

Completeness means every risk domain maps to a preset requirement, generated
artifact, validator, CI gate, and evidence output.

| Risk Domain | Preset Section | Generated Artifact | Validator | CI Gate | Evidence Output |
|---|---|---|---|---|---|
| Prompt injection | AI / LLM Risk | threat model, abuse cases | `sicario verify` | Sicario verify | gate summary |
| Broken access control | Security Requirements | tests, threat model | test suite | CI test | test report |
| Hardcoded secret | Secrets / Credential Handling | gate summary | secret pattern scan | secret scan | gate summary |
| Unsafe external write | External System Access | human approval record | plan review | Sicario review | evidence index |
| Unpinned dependency | Supply Chain | SBOM/provenance note | dependency scan | SCA | SBOM/evidence |
| Missing threat model | Threat Model | threat-model.md | `sicario verify` | Sicario verify | gate summary |
| Missing security tests | Tasks | tasks.md | `sicario verify` | Sicario verify | gate summary |
| Cloud public exposure | Cloud / IaC Risk | IaC scan report | IaC scanner | IaC scan | evidence index |
| Excessive IAM privilege | Cloud / IaC Risk | cloud risk template | IaC/policy scan | policy-as-code | evidence index |
| Missing cloud logging | Cloud / IaC Risk | cloud risk template | IaC/policy scan | policy-as-code | evidence index |
| No data residency decision | Cloud / IaC Risk | cloud risk template | plan review | Sicario review | evidence index |
| Cost runaway risk | Cloud / IaC Risk | cloud risk template | plan review | Sicario review | evidence index |
| Missing audit evidence | Evidence Outputs | evidence-index.md | `sicario verify` | Sicario verify | evidence index |
| Missing CCM/SOX traceability | Compliance / Control Applicability | control maps | `sicario verify` | Sicario verify | evidence index |
| Unbounded security exception | Risk register | exception register | `sicario verify` | Sicario verify | risk evidence |
| Model/tool overreach | AI / Tool Boundary | AI risk evidence | AI-system profile | Sicario verify | spec-run evidence |
| Unbounded orchestration | Fleet / Orchestration Risk | workflow/state graph | `sicario verify` | Sicario verify | spec-run evidence |
| Unsafe retries or duplicate work | Fleet / Orchestration Risk | retry/idempotency tests | test suite | CI test | test report |
| Poison messages or stuck workflows | Orchestration Design | dead-letter evidence | `sicario verify` / tests | Sicario verify | evidence index |
| Autonomous remediation overreach | Human Approval Points | approval record | plan review | Sicario review | approval evidence |
| Documentation drift | Docs impact | docs-impact.md, docs-site | docs build | docs CI | docs build log |
| Diagram drift | Diagram impact | Mermaid source | diagram source check | docs CI | evidence index |
| Missing well-architected review | Architecture / Security Decision Record | plan.md | `sicario verify` | Sicario verify | gate summary |
