# Profiles

Profiles are install selections for the bootstrap CLI.

| Profile | Installed Presets | Default enforced frameworks |
|---|---|---|
| `public-core` | `sicario-core`, `sicario-docs` | none (coarse control-map check only) |
| `appsec` | core, docs, appsec | `ssdf`, `iso27001`, `owasp-asvs` |
| `ai-system` | core, docs, AI system | `ai-rmf`, `eu-ai-act` |
| `agent-fleet` | core, docs, AI system, agent fleet orchestration | `ai-rmf`, `eu-ai-act` |
| `cloud-iac` | core, docs, cloud/IaC plus infrastructure starter folders | `ccm`, `fedramp`, `bsi-c5`, `nist-800-53` |
| `security-toolchain` | core, docs, security scanning and evidence toolchain | none |
| `supply-chain` | core, docs, supply chain | `ssdf` |
| `compliance` | core, docs, compliance | `ccm`, `sox`, `soc2`, `iso27001`, `nist-800-53` |
| `saas` | core, docs, AI system, SaaS | `ccm`, `soc2`, `iso27001`, `ai-rmf` |
| `enterprise-strict` | core, docs, appsec, AI system, agent fleet, security toolchain, supply chain, compliance, enterprise strict | all 14 |

Profiles are composable:

```bash
sicario init my-service --profile appsec,ai-system,agent-fleet,security-toolchain,supply-chain
```

## Choosing enforced frameworks

The **Default enforced frameworks** column is what `sicario verify` requires when
you omit `--frameworks`. Override it to enforce exactly the subset that applies:

```bash
# Enforce only ISO 27001 + HIPAA regardless of profile default:
sicario init my-service --profile compliance --frameworks iso27001,hipaa
```

See [Control maps](control-maps.md#selecting-which-frameworks-apply---frameworks)
for the full selector-key table and behavior.
