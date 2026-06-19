# Profiles

Profiles are install selections for the bootstrap CLI.

| Profile | Installed Presets |
|---|---|
| `public-core` | `sicario-core`, `sicario-docs` |
| `appsec` | core, docs, appsec |
| `ai-system` | core, docs, AI system |
| `agent-fleet` | core, docs, AI system, agent fleet orchestration |
| `cloud-iac` | core, docs, cloud/IaC plus infrastructure starter folders |
| `security-toolchain` | core, docs, security scanning and evidence toolchain |
| `supply-chain` | core, docs, supply chain |
| `compliance` | core, docs, compliance |
| `enterprise-strict` | core, docs, appsec, AI system, agent fleet, security toolchain, supply chain, compliance, enterprise strict |

Profiles are composable:

```bash
sicario init my-service --profile appsec,ai-system,agent-fleet,security-toolchain,supply-chain
```
