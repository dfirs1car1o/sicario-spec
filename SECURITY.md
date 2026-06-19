# Security Policy

SicarioSpec is security tooling, so vulnerability reports need to be handled
privately and with enough evidence to reproduce the issue safely.

## Supported Versions

| Version | Supported |
|---|---|
| `0.1.x` | Yes |
| `< 0.1.0` | No |

## Reporting A Vulnerability

Do not open a public issue for exploitable vulnerabilities, leaked secrets,
private tenant data, bypass techniques, or sensitive scanner output.

Preferred reporting path:

1. Open a private GitHub security advisory:
   `https://github.com/dfirs1car1o/sicario-spec/security/advisories/new`
2. Include affected version or commit, impact, reproduction steps, and any safe
   proof-of-concept.
3. Redact secrets, customer data, private repo URLs, and tenant identifiers.

If GitHub private reporting is unavailable, contact the repository owner through
GitHub and request a private reporting channel.

## Response Targets

| Event | Target |
|---|---|
| Initial acknowledgement | 5 business days |
| Triage decision | 10 business days |
| Fix or mitigation plan | Based on severity and exploitability |

## Scope

In scope:

- CLI behavior that can bypass security/governance gates.
- Package or generated-template behavior that introduces unsafe defaults.
- Workflow or release behavior that undermines integrity.
- Secret exposure in generated artifacts.

Out of scope:

- Claims that SicarioSpec guarantees compliance certification.
- Vulnerabilities in third-party tools unless SicarioSpec invokes them
  unsafely.
- Reports requiring access to private tenant data, customer systems, or
  credentials.

## Security Posture

The repository uses CI, CodeQL, Dependabot, and OpenSSF Scorecard. These checks
improve release confidence, but they do not replace human security review.
