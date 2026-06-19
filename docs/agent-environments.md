# Agent Environments

SicarioSpec can bootstrap agent-native instructions for Claude Code, Codex, and
GitHub Copilot coding agent.

Use the combined integration for teams that use multiple agents:

```bash
sicario init . --integration all --profile ai-system,agent-fleet,supply-chain
```

## Claude Code

`--integration claude` and `--integration all` create:

- `CLAUDE.md`
- `.claude/skills/sicario-verify/SKILL.md`
- `.claude/skills/sicario-governance-review/SKILL.md`
- `.claude/skills/sicario-release-readiness/SKILL.md`
- `.claude/agents/sicario-security-reviewer.md`
- `.claude/agents/sicario-release-manager.md`

The skills provide reusable SicarioSpec workflows. The subagents are read-first
reviewers for security/governance and release readiness.

## Codex

`--integration codex` and `--integration all` create:

- `AGENTS.md`
- `.agents/skills/sicario-verify/SKILL.md`
- `.agents/skills/sicario-governance-review/SKILL.md`
- `.agents/skills/sicario-release-readiness/SKILL.md`

`AGENTS.md` is the durable repository instruction file. The skills are
repo-scoped workflows that Codex can invoke explicitly or implicitly.

## GitHub Copilot

`--integration copilot` and `--integration all` create:

- `AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/sicario-governance.instructions.md`
- `.github/workflows/copilot-setup-steps.yml`

The Copilot setup workflow installs the local project when Python package
metadata exists, then runs the SicarioSpec verifier when available. The workflow
is intentionally minimal so Copilot can run in a clean cloud environment without
requiring private secrets.

## Operating Rules

- Do not put secrets, private evidence, tenant identifiers, customer data, or
  unpublished vulnerability details into agent instructions or prompts.
- Keep data classification and tagging current when prompts, specs, logs,
  evidence, workflows, or release artifacts change.
- Use machine-user pull requests when available; document the maintainer
  fallback when a machine user is unavailable.
- Treat verification as a gate, not approval. High-impact changes still need
  human review.
