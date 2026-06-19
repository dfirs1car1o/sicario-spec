# `/sicario.verify`

Run deterministic verification.

Expected local command:

```bash
sicario verify
```

Fail closed for:

- missing threat model
- missing docs impact record
- missing diagram source directory
- missing control maps
- missing risk and exception registers
- missing required spec sections
- missing required plan sections
- missing security tasks
- hardcoded secret patterns
- AI-sensitive specs with no prompt-injection/tool-boundary controls
- orchestration specs with no retry/idempotency/dead-letter/approval controls
- active risk or exception rows without owner, expiration, approval/rationale,
  compensating control, and evidence
