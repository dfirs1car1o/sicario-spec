# `/sicario.assess`

Assess the repository against SicarioSpec guardrails.

Output:

- `generated/sicario/assessment.md`
- `generated/sicario/gate-summary.json`

Required checks:

- required spec/plan/task sections
- threat model presence
- docs impact presence
- diagram source presence
- hardcoded secret patterns
- AI-sensitive specs with prompt-injection/tool-boundary guardrails

