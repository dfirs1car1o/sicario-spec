# Profiles

Profiles are install selections for the bootstrap CLI.

| Profile | Installed Presets | Default enforced frameworks |
|---|---|---|
| `public-core` | `sicario-core`, `sicario-docs` | none (coarse control-map check only) |
| `appsec` | core, docs, appsec | `ssdf`, `iso27001` |
| `ai-system` | core, docs, AI system | `eu-ai-act` |
| `agent-fleet` | core, docs, AI system, agent fleet orchestration | `eu-ai-act` |
| `cloud-iac` | core, docs, cloud/IaC plus infrastructure starter folders | `ccm`, `fedramp`, `bsi-c5`, `nist-800-53` |
| `security-toolchain` | core, docs, security scanning and evidence toolchain | none |
| `supply-chain` | core, docs, supply chain | `ssdf` |
| `compliance` | core, docs, compliance | `ccm`, `sox`, `soc2`, `iso27001`, `nist-800-53` |
| `saas` | core, docs, AI system, SaaS | `ccm`, `soc2`, `iso27001` |
| `enterprise-strict` | core, docs, appsec, AI system, agent fleet, security toolchain, supply chain, compliance, enterprise strict | all 11 supported |

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

Profile defaults contain only **supported**-tier frameworks. The three
**experimental** maps (`pci-dss`, `ai-rmf`, `owasp-asvs`) are never selected by
a profile default - including `enterprise-strict` - and are enforced only when
named explicitly on `--frameworks`. Once selected, they are enforced exactly
like any other framework, and CLI output labels them, e.g.
`owasp-asvs (experimental)`.

See [Control maps](control-maps.md#selecting-which-frameworks-apply---frameworks)
for the full selector-key table and behavior, and
[Map tiers](control-maps.md#map-tiers) for what the tiers mean.
