# Abuse Cases

| Abuse Case | Outcome | Mitigation |
|---|---|---|
| A developer runs `sicario init --force` in the wrong directory, destroying unrelated governance files | Irreversible data loss | `--dry-run` is the default; `--force` requires an explicit flag and still takes a timestamped backup first |
| A developer initializes SicarioSpec and then removes or ignores all governance artifacts to pass verification without meaningful evidence | False sense of security | `sicario verify` checks that required sections contain substantive content (not empty or placeholder), and control maps must be present for selected frameworks |
| A repo contributor adds an AI feature without prompt-injection guardrails | AI agent behavior bypass | Verify rejects AI-domain specs that omit the mandatory `## Prompt Injection` guardrails section; the finding code is non-zero exit |
| A developer commits a hardcoded token and attempts to verify | Credential leak | Pattern-based secret scan runs as a verify gate; finding produces a non-zero exit and a specific finding code |
| A feature changes behavior without updating docs, diagrams, or the risk register | Documentation drift + blind risk acceptance | Verify gates for `docs-impact`, `docs/diagrams/`, and valid risk-register rows; any of these missing produces a finding |
| A maintainer temporarily disables a verify gate to unblock a deploy, then forgets to re-enable it | Regression in governance coverage | Gate rules are in `.sicario/rules/*.rule.json` under version control; a PR that removes or disables a rule is visible in diff review |
| An external contributor forks the repo and removes all governance before submitting changes | Fork bypasses governance | Governance is enforced via CI on the upstream repo; forks cannot modify the upstream CI workflow or branch protection rules |
| A developer uses `--frameworks` to select no frameworks, bypassing all control-map checks | Control-map requirements circumvented | Selecting zero frameworks is rejected by the CLI; at least one framework must be specified |
