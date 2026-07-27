# Feature Specification: Issue Email Alerts

**Feature Branch**: `003-issue-email-alerts`
**Created**: 2026-07-22
**Status**: Draft
**Input**: User description: "create the email automation to myself when changes or response occurs"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Track Issue Changes (Priority: P1)

As the issue owner, I want an email when a tracked GitHub issue changes so I
can follow progress without checking GitHub manually.

**Why this priority**: The main value is timely awareness of status changes,
new comments, and closure events on the submission issue.

**Independent Test**: Change a tracked issue’s state, labels, or comment count
and confirm a single email is sent with the issue number, title, URL, and a
summary of what changed.

**Acceptance Scenarios**:

1. **Given** a tracked issue is open, **When** a new comment is added, **Then**
   an email is sent to the configured owner address summarizing the response.
2. **Given** a tracked issue changes state, labels, or other monitored metadata,
   **When** the watcher runs, **Then** an email is sent that identifies the
   change and links to the issue.

---

### User Story 2 - Avoid Duplicate Alerts (Priority: P1)

As the issue owner, I want the automation to remember what it already saw so I
do not receive repeated emails for the same unchanged issue snapshot.

**Why this priority**: Duplicate alerts reduce trust in the automation and make
the notifications easy to ignore.

**Independent Test**: Run the watcher twice without any issue changes and
confirm no second email is emitted.

**Acceptance Scenarios**:

1. **Given** a tracked issue has not changed since the last successful check,
   **When** the watcher runs again, **Then** no email is sent.
2. **Given** a previous notification was sent for a specific snapshot,
   **When** the same snapshot is seen again, **Then** the watcher does not
   resend the same alert.

---

### User Story 3 - Reconfigure the Tracked Item (Priority: P2)

As the issue owner, I want to switch the automation between tracked issues
without rewriting the alerting logic so I can follow the current submission
thread.

**Why this priority**: The tracked issue may change over time, but the alerting
behavior should remain consistent.

**Independent Test**: Update the tracked issue configuration to a different
repository issue and confirm the next watcher run follows that issue instead.

**Acceptance Scenarios**:

1. **Given** the watcher is configured for one issue, **When** the tracked
   issue number is changed, **Then** alerts follow the new issue on the next
   run.

### Edge Cases

- What happens when the issue is closed without any new comment?
- What happens when several monitored fields change between runs?
- How does the automation behave if email delivery fails after detecting a
  change?
- What happens when the tracked issue already has the latest snapshot stored?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST monitor at least one configured GitHub issue for
  changes relevant to the owner.
- **FR-002**: The system MUST send an email notification to the configured
  owner address when a tracked issue receives a new response or other monitored
  state change.
- **FR-003**: The system MUST include the issue number, issue title, issue URL,
  and a concise description of the detected change in each alert.
- **FR-004**: The system MUST preserve the last-seen snapshot for each tracked
  issue so it can detect new changes and suppress duplicates.
- **FR-005**: The system MUST avoid sending duplicate notifications when a
  tracked issue has not changed since the last successful run.
- **FR-006**: The system MUST allow the tracked issue to be changed through
  configuration without requiring changes to the alerting logic.
- **FR-007**: The system MUST record notification attempts and detection events
  for troubleshooting.
- **FR-008**: The system MUST fail safely if email delivery is unavailable,
  preserving the detected state for the next run.
- **FR-009**: The system MUST read the GitHub API credential and the email
  delivery credential from the CI secret store at run time, and MUST NOT
  persist either one to the repository, the snapshot file, or any log.
- **FR-010**: The system MUST authenticate to GitHub with a credential scoped
  to read-only access on public issue data, with no write, no admin, and no
  private-repository scope.
- **FR-011**: The system MUST use TLS with certificate validation for every
  GitHub API call and every handoff to the email provider, and MUST fail the
  run rather than fall back to an unencrypted transport.
- **FR-012**: The system MUST treat issue titles, labels, author names, and
  comment text as untrusted third-party input, and MUST render them in the
  alert email so that they cannot execute, cannot supply their own link
  targets, and are visually separated from watcher-generated text.
- **FR-013**: The system MUST confirm that the configured issue belongs to a
  public repository before fetching it, and MUST refuse to run and send no
  email when the target is private.
- **FR-014**: The system MUST emit at most one email per watcher run,
  collapsing every change detected in that run into a single message, and MUST
  state in the message how many changes were collapsed.
- **FR-015**: The system MUST treat a missing, unreadable, or malformed
  snapshot as "state unknown" and alert on the current issue state, rather
  than treating it as "no change detected".
- **FR-016**: The system MUST NOT send issue titles, labels, or comment text
  to any language model, summarization service, or agent tool while composing
  an alert.
- **FR-017**: The system MUST redact credential material, authorization
  headers, and the full owner email address from all log output and error
  messages, including stack traces surfaced by the CI runner.
- **FR-018**: The system MUST advance the stored snapshot only after the email
  provider has accepted the message, never before.
- **FR-019**: The system MUST send alerts only to the single configured owner
  address, and MUST NOT derive the recipient from issue content.

### Key Entities *(include if feature involves data)*

- **Tracked Issue**: A GitHub issue selected for monitoring; includes issue
  number, repository, title, URL, state, labels, and comment activity.
- **Snapshot**: The last known view of a tracked issue used to detect changes
  between runs.
- **Notification**: An email alert describing a detected change for the owner.
- **Delivery Target**: The owner mailbox that receives alerts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A tracked issue comment or state change produces exactly one email
  alert on the next successful watcher run.
- **SC-002**: Re-running the watcher without issue changes produces zero new
  emails.
- **SC-003**: The alert body identifies the issue and the detected change well
  enough that the owner can understand the event without opening GitHub.
- **SC-004**: The tracked issue can be switched by configuration and the new
  issue is observed on the next run without changing the alerting logic.

## Assumptions

- The owner wants notifications sent to a single email address controlled by
  the existing repo automation setup.
- Only tracked public GitHub issue metadata is monitored; private repository
  data and issue content are out of scope.
- Polling cadence is handled by the existing scheduled watcher and is not part
  of this feature.
- Notification delivery may use the existing email delivery path already
  configured for this repository.

## Data Classification

| Data | Level | Classification owner | Retention | Residency | Sharing | Redaction |
|---|---|---|---|---|---|---|
| Tracked issue metadata (number, title, URL, state, labels, comment count) | Public | Issue owner | Life of the tracked issue | GitHub | Already public; may be quoted in full in the alert | None required |
| Third-party issue and comment text | Public but untrusted | Issue owner | Not stored between runs | GitHub; transits the email provider | Quoted into the alert body only | Rendered inert per FR-012; no third-party markup or link targets survive |
| Owner email address | Confidential | Issue owner | Life of the watcher configuration | CI secret store and email provider | Never written to the repository, the snapshot, or a log | Masked in logs as `j***@example.com` |
| Snapshot file | Internal | Issue owner | Overwritten each successful run; no history kept | Repository workspace or CI cache | Not published | Holds metadata and digests only, never credentials or comment bodies |
| Notification and detection logs | Internal | Issue owner | CI log retention (30 days) | CI provider log store | World-readable, see note below | Credential material and full recipient address redacted per FR-017 |
| GitHub API credential and mail credential | Restricted | Repository maintainer | Rotated on maintainer change or suspected exposure | CI secret store only | Never shared, never printed | Never rendered; relies on CI secret masking plus FR-017 |

Note on the log row: this repository is public, so its scheduled-workflow logs
are readable by anyone on the internet. "Internal" describes the intent, not the
enforcement. That gap is the reason FR-017 exists and the reason AC-006 is
treated as a real abuse case rather than a theoretical one.

The owner email address is deliberately not classified Public. Everything else
this feature touches on the GitHub side already is, which makes it easy to
assume the whole feature handles only public data; the recipient address and the
two credentials are the exceptions that set the security posture.

## Tagging Discipline

| Tag | Value | Applied to |
|---|---|---|
| owner | issue-owner (repository maintainer) | watcher workflow, snapshot file, alert emails |
| system | issue-email-alerts | workflow run, snapshot file, log lines |
| environment | ci | the scheduled watcher run |
| data-classification | confidential | the workflow run and its artifacts, set by the highest level it handles (the owner email address) |
| retention | snapshot: current run only; logs: 30 days | snapshot file, CI logs |

Every alert email carries the same `system` and `owner` tags plus the tracked
issue number in a footer, so an owner receiving an unexpected alert can tell
which watcher instance and which tracked issue produced it without opening
GitHub. This is what makes AC-004 (redirected or duplicated alerts) detectable
by the recipient.

## Trust Boundaries

**Boundary 1 - GitHub API to watcher.** Issue metadata and third-party text
cross into the watcher process over TLS. The watcher authenticates to GitHub;
GitHub does not authenticate to the watcher beyond certificate validation.
Everything returned is untrusted data, including label names, author names, and
field lengths. Controls: TLS with certificate validation (FR-011), a read-only
credential (FR-010), a public-repository precondition (FR-013), and bounds on
field sizes before any value is placed in an email.

**Boundary 2 - watcher to email provider.** The composed alert and the owner
address cross out of the watcher, and the mail credential is presented at this
boundary. Controls: TLS (FR-011), credential from the secret store (FR-009), a
fixed recipient that issue content cannot influence (FR-019), and a delivery
failure path that never destroys detection state (FR-008, FR-018).

**Boundary 3 - untrusted issue text to the owner's mail client.** This is the
boundary that matters most and the one easiest to miss, because no system
component sits on the far side of it. The rendering engine is the owner's mail
client, running in the owner's own authenticated session, and the message
arrives from a sender the owner has been trained to trust. By design this
feature carries text written by arbitrary internet strangers across that
boundary. Controls: FR-012 - quoted issue text is inert, is visually fenced from
watcher-generated text, is attributed to its author login, and contributes no
clickable link targets; the only link in an alert is the issue URL the watcher
constructed itself.

**Boundary 4 - CI secret store to watcher process.** Two credentials cross into
a process whose stdout is world-readable. Controls: FR-009, FR-017, and no
verbose HTTP tracing in the scheduled workflow.

## Security Requirements

- Credentials are injected from the CI secret store at run time and are never
  committed, never written to the snapshot, and never echoed (FR-009).
- The GitHub credential is read-only on public issue data. It needs no write
  scope, because the watcher never comments, labels, or closes (FR-010).
- The mail credential is used only for the single configured recipient. A
  compromise of this watcher should not yield a general-purpose mail relay
  (FR-019).
- All network calls use TLS with certificate validation, and an unencrypted
  fallback is a failure, not a degradation (FR-011).
- No secrets in logs: credential material, authorization headers, and the full
  owner address are redacted from normal output, error output, and stack
  traces. The CI logs for this repository are public (FR-017).
- The snapshot file stores issue metadata and digests only. It never stores
  comment bodies, the owner address, or credentials, because it may be cached
  by CI or committed to the repository (FR-004, FR-009).
- The snapshot is single-writer. Concurrent watcher runs must not be permitted,
  since two runs racing on the same snapshot can each conclude the other
  already alerted.
- Third-party issue text is data, never markup and never instructions
  (FR-012, FR-016).
- The public-repository-only assumption is enforced at run time, not merely
  documented in this spec (FR-013).

### Security Acceptance Scenarios

1. **Given** an issue comment containing HTML markup and an off-site link,
   **When** the watcher composes the alert, **Then** the markup appears as
   inert quoted text and the only clickable link in the message is the
   watcher-constructed issue URL.
2. **Given** the mail credential is unavailable, **When** the watcher detects a
   change, **Then** the run fails, the failure message contains no credential
   material, and the snapshot is left at its previous value so the next run
   re-alerts.
3. **Given** the tracked issue is configured to a private repository, **When**
   the watcher runs, **Then** it refuses to fetch the issue, sends no email,
   and reports a configuration error.
4. **Given** a completed watcher run, **When** its world-readable CI log is
   inspected, **Then** no credential material and no full owner email address
   appears in it.

## AI / Tool Boundary

**Current position: there is no model in the loop, and there must not be one
without re-opening this section.** The "concise description of the detected
change" required by FR-003 is produced by field-level comparison of two
snapshots over a small fixed set of metadata. It is a diff, not generated prose.
FR-016 states that boundary as a requirement rather than leaving it as an
implementation accident.

This section is written anyway because the shape of the feature is a textbook
**prompt injection** setup waiting for a model to be added: attacker-controlled
text from arbitrary internet users flows, by design, into a message delivered to
a trusted mailbox, in a process that holds a GitHub credential and a mail
sender. The moment anyone routes issue text through an agent to "summarize the
thread," a stranger's comment becomes instruction text for a system with
credentials.

**Tool boundary if a model is ever introduced:**

- Issue text is data, never instruction. It is delimited and labeled as
  untrusted input in any prompt.
- The summarizing model gets no tools, no network access, no credential, and no
  repository write path.
- Model output is treated as untrusted: it is quoted into the alert body under
  the same inert-rendering rules as issue text (FR-012), never executed, and
  never used for routing.
- The recipient address and the tracked issue selection are never derived from
  model output (FR-019).
- Adding a model or agent dependency to this watcher is a security-relevant
  change and requires human review of this section, not just a passing gate.

## Fleet Guardrails

- **Idempotency**: the last-seen snapshot (FR-004, FR-005) is the idempotency
  key for this feature. Each run is compare, notify, then commit the snapshot,
  and it is the commit step that makes a repeated run a no-op. The ordering is
  load-bearing: FR-018 requires the snapshot to advance only after the provider
  accepts the message, because advancing first turns a delivery failure into a
  permanently lost alert.
- **Retry**: transient GitHub API and mail-delivery errors get bounded retry
  with backoff inside the run. Retry is safe precisely because the snapshot has
  not advanced yet, so a retried send cannot double-count as a new change.
- **Failure after detection**: when retries are exhausted (FR-008), the watcher
  leaves the snapshot unchanged, marks the run failed, and lets the next
  scheduled run re-detect and re-alert. A detected change that was never
  delivered must never be silently dropped.
- **Dead-letter**: delivery failure on three consecutive runs is recorded as a
  dead-letter entry in the run log and surfaced as a failed CI run. This exists
  because the failure mode this feature is most exposed to is silence - a
  watcher that is broken and a watcher with nothing to report look identical
  from the owner's inbox.
- **Workflow state**: the snapshot is the only durable state, and it is
  single-writer. Overlapping scheduled runs are not permitted.
- **Human approval**: changing the recipient address, the tracked repository or
  issue, or the credential scope is a configuration change made through the
  normal reviewed pull-request path. The watcher cannot reconfigure itself.

## Misuse / Abuse Cases

- **AC-001 - Phishing or spoofing through the alert body.** An attacker comments
  on the tracked public issue with text and markup crafted to read as if it came
  from the watcher or from GitHub ("your credential expired, re-authenticate
  here"), and the alert delivers it into a mailbox where the sender is already
  trusted. *Mitigation*: FR-012. Quoted issue text is inert, visually fenced
  from watcher-generated text, and attributed to its author login; third-party
  link targets are stripped, and the only clickable link in an alert is the
  issue URL the watcher constructed.
- **AC-002 - Alert flooding to bury a real alert.** Rapid comment spam generates
  enough alerts that the owner mutes the thread or filters the sender, so the
  alert that mattered (the issue being closed, or a security label added) is
  never read. *Mitigation*: FR-014. One email per run, all changes collapsed
  into it, with the collapsed-change count stated in the message so suppression
  is visible to the owner rather than silent.
- **AC-003 - Snapshot tampering or deletion to suppress an alert.** Someone able
  to write to the workspace or CI cache edits the snapshot to match the current
  issue state, so the next run sees no change and stays quiet. *Mitigation*:
  FR-015. A missing, unreadable, or malformed snapshot is "unknown", not
  "unchanged", and forces an alert; the snapshot is written only by the watcher
  job; changes to the snapshot path go through pull-request review. *Residual
  risk, stated plainly*: a snapshot forged to exactly match the current state is
  indistinguishable from a legitimate one, so this case is detected only through
  the run log showing an unexplained state jump.
- **AC-004 - Redirected or silenced delivery.** The recipient address or the
  delivery configuration is changed so alerts go to an attacker's mailbox, or
  nowhere. *Mitigation*: recipient and delivery configuration live in reviewed
  configuration and CI secrets, changed only through the human-approved
  pull-request path; every alert carries the `system`, `owner`, and tracked
  issue tags described under Tagging Discipline, and every run records the
  redacted recipient, so both a swap and a sudden silence are observable.
- **AC-005 - Private repository leakage.** The watcher is pointed at an issue in
  a private repository, and private titles, labels, and comment text are
  forwarded through a third-party email provider and into world-readable CI
  logs. The Assumptions above scope this feature to public issue metadata;
  *mitigation*: FR-013 makes that scope an enforced runtime precondition rather
  than a documented intention, refusing to fetch and sending nothing when the
  target is private.
- **AC-006 - Credential exposure through CI logs.** Debug logging, a verbose
  HTTP client, or an unhandled exception prints an authorization header or the
  mail credential into this public repository's world-readable Actions log.
  *Mitigation*: FR-009 and FR-017 - secret-store injection with CI masking, no
  verbose HTTP tracing in the scheduled workflow, redacted error paths, and
  rotation of both credentials on suspected exposure.
- **AC-007 - Using the watcher as a mail relay.** An attacker attempts to make
  the watcher deliver attacker-chosen content to an attacker-chosen address by
  planting it in issue text. *Mitigation*: FR-019 - the recipient is a single
  fixed configured address that no issue content can influence, and the mail
  credential's usefulness to an attacker is bounded by that.

## Evidence

- **Tests**: unit tests covering SC-001 through SC-004, plus negative and abuse
  tests tied to specific cases above - hostile markup and link stripping
  (AC-001), collapse-and-count behavior under a burst of changes (AC-002),
  missing and malformed snapshot forcing an alert (AC-003), a private target
  being refused (AC-005), and redaction assertions over captured log output
  (AC-006).
- **Fixtures**: a stored sample alert rendered from an issue comment containing
  hostile markup, retained as the regression fixture for AC-001.
- **Run log**: the per-run record required by FR-007, carrying detection result,
  collapsed-change count, redacted recipient, delivery outcome, retry attempts,
  and dead-letter state. This is the artifact that proves a silent period was
  intentional rather than a broken watcher.
- **Gate output**: `sicario verify .` passing on this specification, with
  `generated/sicario/gate-summary.json` recording the result for the run.
- **Configuration history**: the pull-request review record for any change to
  the recipient address, tracked issue, or credential scope, which is the
  evidence behind the human-approval guardrail and AC-004.
