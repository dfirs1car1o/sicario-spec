# Feature Specification: Advanced Track — Graph Engineering and Loop Engineering for Spec Authoring

**Feature Branch**: `008-graph-loop-engineering-track`
**Created**: 2026-08-03
**Status**: Draft
**Input**: Advanced lessons, with concrete examples and real-world use cases,
teaching an experienced SicarioSpec user to use explicit graph structures
(graph engineering) and disciplined iteration (loop engineering) to determine
the workflow of authoring a security spec — anchored on two scenarios: a
SaaS-to-SaaS integration feature and a cloud security-architecture feature.

## Overview

Lessons 1–6 teach a reader to adopt SicarioSpec and reach a green gate. This
feature specifies the level after that: a **repeatable, mechanical method for
deriving spec substance from a model of the system itself**, taught as an
optional Advanced Track of two playbooks plus a track index.

The method inverts the beginner workflow. A beginner walks the template
section by section and asks "what belongs here?" An advanced author builds a
**typed graph** of the feature — nodes with kinds and attributes, directed
labeled edges, and a `zone` attribute per node — and then applies a fixed set
of **traversal rules** that mechanically emit obligations: abuse cases,
control requirements, classification rows, evidence-chain entries, owners.
The central artifact is not the diagram; it is the **obligation ledger** that
links each graph element to the spec content it forced into existence, and —
more valuable still — the **gap list**: graph elements with no corresponding
spec content, which is exactly the class of omission `sicario verify`
structurally cannot detect.

**The load-bearing design decision**: a trust boundary is not a node. It is a
node attribute (`zone`), and a boundary crossing is a computed predicate —
`crosses(edge) ⟺ zone(src) ≠ zone(dst)`. This turns "which edges cross a
trust boundary" from a judgment call into a set operation, which is what
makes the traversal teachable as a procedure rather than as taste.

**Loop engineering** is the discipline wrapped around the traversal: three
nested loops (per-element interrogation, adversarial one-hop propagation that
mutates the graph, and an outer convergence loop) with a mechanical dry-pass
termination criterion, guards against both premature stop and
non-termination, and a traversal log as a reviewer-facing artifact.

Everything in this feature lives strictly on the **human/authoring side** of
the Two-Tier Authority established by spec 004. `sicario verify` remains the
sole authority on pass/fail and is not modified in any way. The lessons state
plainly, in the shipped four-part lesson contract's "What the gate checks
here" slot, that for most of this method the honest answer is **"nothing"** —
that sentence is the thesis of Lessons 5–6 applied one level up, and it is a
feature, not an apology.

The graph does not need a new spec section. It has two shipped homes already:
`docs/diagrams/*.mmd` (whose presence the gate already counts via
`SICARIO-MISSING-DIAGRAMS`, content-uncoupled) and
`plan.md § Data Flow And Trust Boundaries` (which already ships an edge-list
placeholder and is not a gate-required heading). This feature adds nothing to
any template.

## User Scenarios & Testing

**Primary scenario — SaaS-to-SaaS integration (the grant graph).** An
engineer who completed Lessons 1–6 must spec a connector between a
first-party CRM and a vendor helpdesk SaaS: admin-consented OAuth grant,
access/refresh tokens, tenant-wide read/write scopes, an inbound HMAC webhook,
vendor-side logs with EU residency. The graph lesson walks them through
building the typed grant graph (systems, identities, credentials, scopes,
data classes, endpoints, stores, humans; `grants`/`holds`/`authorizes`/
`permits`/`calls`/`flows`/`logs`/`trusts` edges; zones `our-tenant`,
`vendor-saas`, `subprocessor`, `public-internet`), computing the crossing
set, and running the traversal rules to emit the obligation ledger. The
drill: five crossing edges yield five abuse cases, five control requirements,
and five evidence rows; the `CRM → helpdesk → webhook → CRM` cycle yields a
replay/echo abuse case and an idempotency requirement; the tenant-wide write
scope yields a high-impact action and a human approval point. The
adversarial drill is **substitution**: present tenant A's valid artifact on
tenant B's edge and require a negative test showing rejection.

**Secondary scenario — cloud security architecture (the architecture
graph).** The same engineer specs a cloud feature: public load balancer,
private API service, regulated (PCI) orders database, export function and
bucket, KMS key, audit sink, CI deploy runner with terraform state. The loop
lesson uses this graph in full: reverse-walk every path from protected data
to a root outside its administrative domain; the `can_assume` cycle
(`svc-api → fn-export → ci-deploy → svc-api`) is the privilege-escalation
drill — a service compromise reaches the control plane; the deploy-closure
(`blast_radius(CI) = {service, database}`) drives the plan's Rollback and
Cloud/IaC Risk sections; the wildcard bucket policy yields an authorization
requirement and human approval point.

**Testing the lessons themselves** (inherited from spec 007's contract):
every quoted output block is marked verified or illustrative; verified blocks
are re-executed by the existing docs verification runner with no runner
changes (the new pages live under `docs/playbooks/`, already in its glob);
each lesson has a reference run; a first-run evaluator who did not perform
the reference run completes each lesson cold within its stated time budget.
The example graphs and the checklist helper carry their own acceptance
criteria (below), including the negative criterion that no example value may
match the repo's own secret-scan rules.

## Data Classification

The repository and docs-site are public; everything this feature commits is
published. Classification is about what may enter the artifacts.

| Artifact | Level | Classification owner | Retention | Residency | Sharing | Redaction |
|---|---|---|---|---|---|---|
| Advanced Track pages (`docs/playbooks/graph-engineering.md`, `docs/playbooks/loop-engineering.md`, `docs/guides/advanced-track.md`) | Public | Docs owner (maintainer group) | Life of the repository; versioned in git | Repository host and docs-site host | World-readable by design | Placeholder-only values; no real credentials, tenant names, hostnames, or personal data |
| Example graph files (`examples/spec-graph/*.graph.json`, example `.mmd` sources) | Public | Docs owner (maintainer group) | Life of the examples | Repository host | World-readable | Credential-kind nodes carry angle-bracketed placeholders only; no value may imitate a provider token shape (see SEC-005) |
| Checklist helper (`examples/spec-graph/spec_graph_checklist.py`, `graph.schema.json`) | Public | Maintainer group | Life of the examples | Repository host | World-readable | Code and schema only; no embedded example secrets |
| Quoted helper output in lessons | Public | Docs owner (maintainer group) | Life of the lesson | Repository host | World-readable | Paths and timestamps normalized per the existing guide-output normalization rules |
| Worked example repos (`examples/saas-integration/`, `examples/cloud-architecture/`, if shipped) | Public | Docs owner (maintainer group) | Until superseded | Repository host | World-readable | Same placeholder discipline as the graphs they contain |
| Traversal logs shown in lessons | Public | Docs owner (maintainer group) | Life of the lesson | Repository host | World-readable | Synthetic feature content only; pass counts and deltas carry no sensitive material |

Classification rule: an author's **real** graph of a **real** system is at
minimum Internal and frequently Confidential — it is a map of attack surface.
The lessons must say so explicitly and must not instruct readers to publish
real graphs; the shipped examples are synthetic. The redaction burden sits at
authoring time because publication in a public repo is permanent.

## Tagging Discipline

The feature both follows and teaches the shipped tagging taxonomy. Every
node in the cloud architecture graph schema carries the five required tag
keys — `owner`, `system`, `environment`, `data-classification`, `retention` —
and traversal rule R9 makes an untagged node a first-class traversal finding,
which is how the lessons connect graph discipline to the existing
`SICARIO-TAGGING-DISCIPLINE-INCOMPLETE` gate signal. Repository artifacts
introduced by this feature are tagged through the same documentation
conventions as spec 007's artifacts: each lesson page carries its guide-slug,
captured-version, and reference-run frontmatter; example directories carry a
README identifying owner (maintainer group), system (sicario-spec examples),
environment (documentation only, never production), data-classification
(Public), and retention (life of the examples).

## Fleet Guardrails

The lessons discuss webhooks, queues, retries, and multi-agent authoring
workflows, so the guardrail vocabulary applies both to the content and to the
feature's own delivery:

- **Idempotency**: traversal rule R10 makes any `calls`/`flows` cycle emit an
  idempotency requirement (replay/echo protection); the lesson's webhook
  drill requires an idempotency key and a replay negative test.
- **Retry**: the loop lesson's convergence protocol distinguishes a retry of
  a traversal pass (same graph version) from a new pass (mutated graph);
  retries never increment the pass counter.
- **Dead-letter**: the webhook drill requires the spec to state where
  rejected/unverifiable deliveries land (a dead-letter path with an owner),
  not merely that they are rejected.
- **Workflow state**: the traversal log records graph version, pass number,
  and per-pass deltas — the workflow state that makes convergence auditable.
- **Human approval**: traversal rule R5 routes every admin-verb or
  tenant-wide scope and every wildcard policy to a human approval point in
  the plan; the track itself ships through the repository's existing
  reviewed-PR flow with separation of duties.

## Roles, Assets, And Abuse Actors

**Roles.** Track author (maintainer group) writes the lessons and examples.
First-time evaluator (defined by role, per 007 FR-040) validates each lesson
cold. Reader/adopter (finished Lessons 1–6) applies the method to their own
features. Reviewer consumes the obligation ledger and traversal log as
review artifacts.

**Assets.** The two lesson pages and track index; the graph schema and two
example graphs; the stdlib checklist helper; the obligation-ledger and
traversal-log formats; the six-lesson path's credibility (the track must not
dilute the "six lessons, about three hours" onboarding promise); and the
Two-Tier Authority invariant itself.

**Abuse actors.** (1) An author who uses the method's outputs as a
completeness claim — "the graph is covered, therefore the spec is done" —
laundering mechanical coverage into unearned assurance. (2) A tool author who
extends the checklist helper into a verdict engine, creating a second
authority beside the gate. (3) A contributor who embeds a realistic
credential value in an example graph, poisoning every downstream copy.
(4) A reader who publishes their real system graph in a public repo because
the lesson normalized committing graphs. Each has a named mitigation in
Security Requirements.

## Trust Boundaries

The feature's own boundaries (the lessons' subject-matter boundaries are the
content, not this section):

- **Authoring side vs verdict side.** Everything this feature ships —
  lessons, graphs, helper — sits on the authoring side. The boundary is
  crossed only by a human copying derived content into a spec. No code path
  crosses it: `sicario_cli` never imports the helper, and the helper never
  writes into `generated/sicario/` or any spec file.
- **Shipped examples vs adopter repositories.** Examples are copied by
  humans into target repos. The examples must therefore be safe to copy
  verbatim: placeholder credentials, no real hostnames, and no content that
  trips the copier's own gate.
- **Docs build vs shipped package.** The only permitted new dependency
  (`@docusaurus/theme-mermaid`, if option (i) in FR-042 is taken) lives in
  `docs-site/package.json`, entirely on the docs-build side; nothing in
  `docs/` or `docs-site/` ships in the Python package.

## Security Requirements

- **SR-001**: `sicario verify` MUST be byte-for-byte unaffected: no new or
  changed evaluator kinds, rules, finding codes, severities, exit codes, or
  evidence schemas. (Mitigates abuse actor 2; enforced by SEC-002.)
- **SR-002**: The checklist helper MUST be stdlib-only, MUST NOT import
  `sicario_cli`, MUST NOT perform network or model calls, MUST always exit
  `0`, and MUST NOT emit verdict vocabulary: no `SICARIO-` codes, no
  severity levels, none of `pass`/`passed`/`fail`/`failed`/`blocking`/
  `violation`. It emits a checklist and a gap list, never a judgment.
- **SR-003**: The helper MUST NOT modify any file it reads and MUST NOT
  write into spec files, plan files, or `generated/sicario/` (no
  auto-remediation, inheriting spec 004's non-goal).
- **SR-004**: Example graphs MUST use angle-bracketed placeholders for every
  credential-kind value and MUST NOT contain any string matching the shipped
  secret-scan rules' patterns (AWS-key shape, `sk-` token shape, or any
  other rule in `presets/sicario-core/rules/040–043`). (Mitigates abuse
  actor 3.)
- **SR-005**: Both lessons MUST carry an explicit non-assurance statement:
  a graph-derived spec is not thereby complete, verified, or certified; the
  graph determines *relevance and depth*, never the gate's required form,
  and an inapplicable concern still receives an explicit rationale rather
  than deletion. (Mitigates abuse actor 1; inherits 007 SEC-008.)
- **SR-006**: The graph lesson MUST warn that a real system graph is
  sensitive (attack-surface map), MUST NOT instruct readers to publish real
  graphs, and MUST show the private-location alternatives. (Mitigates abuse
  actor 4.)
- **SR-007**: Any discussion of AI-assisted graph drafting MUST state that
  model output is untrusted input to the human curation step, subject to
  prompt injection via the artifacts the model reads, and that the tool
  boundary is absolute: no model call participates in the helper, the gate,
  or CI gating.

## Privacy Requirements

The lessons and examples contain no personal data. Human roles appear only
as roles (tenant admin, platform engineer, evaluator). The first-run
evaluator is recorded by role attestation, with a public handle only by
consent, per 007's existing policy. Example graphs model data classes
(customer PII, regulated payment data) as **labels on nodes** — the labels
are the teaching content; no actual personal data exists anywhere in the
feature. Readers applying the method to real systems are instructed that a
real graph naming real data stores inherits the privacy obligations of what
those stores contain.

## Compliance / Control Applicability

| Control area | Applicable? | How this feature engages it |
|---|---|---|
| Secure development / SSDF PW | Yes | The method is itself a design-analysis practice; lessons map traversal outputs to spec sections that the shipped control maps already reference |
| Supply chain | Yes (examples only) | Vendor `system` nodes in the grant graph trigger traversal rule R12's supply-chain applicability row; the feature adds no runtime dependency to the package |
| Cloud / IaC | Yes (content) | The architecture graph's `resource` nodes drive the Cloud/IaC applicability row and the plan's Rollback obligations; no cloud access occurs in building or testing the feature |
| AI / LLM governance | Yes (bounded) | AI-assisted drafting is discussed as untrusted-input authoring aid only; see AI / LLM Risk |
| Privacy regimes | Content-level only | Residency and retention are node attributes taught as classification inputs; the feature itself processes no regulated data |

## AI / LLM Risk

The track may note that an author can use an AI agent to *draft* a graph or
a first-pass ledger. The risk posture is explicit:

- Model output is a **draft for human curation**, never an authority. The
  deterministic gate and the human reviewer remain the only authorities.
- **Prompt injection** is in scope for any agent that reads repository
  content to draft a graph: a poisoned README could seed a poisoned graph.
  The lesson's mitigation is the traceability guard — only elements
  traceable to a real system artifact (an OAuth app registration, a
  Terraform resource, an IAM policy document) may enter the graph, which is
  the same guard that bounds the loop protocol.
- The **tool boundary** is absolute: no model call, AI import, or network
  call exists in the checklist helper, the gate, or any CI job introduced by
  this feature. Shipped code is deterministic; AI participation is prose
  guidance about the reader's own workflow, not shipped capability.

## External System Access

Building and testing this feature requires no external system access: no
cloud accounts, no SaaS tenants, no model APIs. The scenarios are synthetic.
The docs-site build touches the npm registry only if FR-042 option (i) is
taken, through the existing lockfile-pinned, scripts-disabled install path.
Read/write is limited to the repository itself via the existing
separation-of-duties PR flow; production impact is nil (documentation and
examples only); human approval is the existing required review.

## Secrets / Credential Handling

- Secret source: none. The feature introduces no secrets, no secret storage,
  and no secret consumption.
- Injection method: not applicable; nothing is injected anywhere.
- Redaction: example credential nodes carry `<angle-bracket-placeholder>`
  values only (SR-004); lesson text teaches that credential **attributes**
  (lifetime, storage, rotation owner) are the spec-relevant content — never
  values.
- Rotation owner: not applicable to the feature itself; `rotation_owner` is
  a required attribute on credential-kind graph nodes, and traversal rule R4
  maps it directly to the Secrets/Credential Handling owner cell in the
  reader's spec — the lesson teaches ownership by construction.

## Audit / Logging Requirements

The feature's auditable artifacts are git-native: lesson pages, examples,
and helper are versioned; the reference run and evaluator attestation follow
007's existing evidence conventions; CI re-executes verified blocks on every
change, producing the same runner logs the docs pipeline already emits. The
method itself adds one new auditable artifact **for readers**: the traversal
log (graph version, pass number, per-pass deltas, dry-pass declaration),
taught as a reviewer-facing record committed alongside the spec. The lessons
state its honest status: the gate cannot read it; it is Tier-2 human
evidence under spec 004's vocabulary.

## Operational Signal / Response Path

If a shipped verified block goes stale (helper output drifts, lesson command
changes), the existing docs verification job fails the PR — signal, owner
(docs owner), and response path (re-capture or fix) are inherited from 007
unchanged. If a reader reports that the traversal produced a wrong or
missing obligation (a defect in R1–R13), the response path is a normal issue
against the lesson content, triaged by the maintainer group; traversal rules
are documentation, so the fix is a docs PR with re-verified examples. If the
secret-scan negative criterion ever fires on example content, that is a
release-blocking defect handled through the standard gate-failure path.

## Misuse / Abuse Cases

- **Coverage laundering.** An author presents "all graph elements have
  ledger rows" as "the spec is complete." Mitigation: SR-005's mandatory
  non-assurance statement; the lesson's closing drill has the evaluator find
  a real omission (an off-graph concern: consent revocation, support access)
  in a "fully covered" example, proving the graph bounds analysis, not
  reality.
- **Verdict creep.** The helper grows a `--strict` flag, an exit code, or a
  severity column and becomes a shadow gate. Mitigation: SR-002 as MUST NOT;
  SEC-002/SEC-003 enforce by test; the helper's README states the
  prohibition and its rationale.
- **Secret-shaped examples.** A contributor "improves realism" with a
  believable token value; every adopter who copies the example inherits a
  gate failure or, worse, normalizes real values. Mitigation: SR-004 with
  SEC-005's negative test executed in CI.
- **Real-graph publication.** A reader commits `production.graph.json` to a
  public repo. Mitigation: SR-006's warning plus the lesson's explicit
  private-location pattern.
- **Cycle blindness.** A reader models only the happy path, omitting the
  return edges (webhook back-calls, role-assumption chains) where the
  highest-value findings live. Mitigation: both example graphs contain a
  deliberate cycle, and the traversal drill fails visibly (empty R10 output)
  if return edges are omitted — the lesson names this as the most common
  authoring error.
- **Eternal loop / premature stop.** Covered by the loop protocol's twin
  guards (FR-031, FR-032); each guard is taught against a worked failure.

## Functional Requirements

### Track placement and publication

- **FR-001**: The track MUST consist of exactly two playbooks —
  `docs/playbooks/graph-engineering.md` and
  `docs/playbooks/loop-engineering.md` — plus a track index at
  `docs/guides/advanced-track.md` mirroring the shape of `start-here.md`.
- **FR-002**: The track MUST be published as a separate sidebar category
  ("Advanced Track") inserted between the six-lesson category and "When You
  Need It", collapsed by default, so the six-lesson path stays visually
  primary. The six-lesson path, its count, and its stated time budget MUST
  NOT change.
- **FR-003**: The new page ids MUST be added to the sidebar's lesson-id
  exclusion mechanism so they do not also appear under "When You Need It"
  (the computed-complement trap); an assertion-bearing test MUST cover this.
- **FR-004**: `start-here.md` MUST gain one closing paragraph after its
  "That's it." close, linking the track, labeling it optional, and stating
  its prerequisite (Lessons 1–6, with Lesson 5 as the hard prerequisite);
  the track index MUST link back.
- **FR-005**: Each lesson MUST be self-contained (007 FR-012): the graph
  lesson carries scenario (a) in full and (b) abbreviated; the loop lesson
  carries (b) in full and revisits (a)'s cycle; each ships its own graph
  files.
- **FR-006**: Each lesson MUST state a target time budget (60–90 minutes)
  and MUST reuse the four-part per-step contract from `spec-authoring.md`
  verbatim — *What it is for / What the gate checks here / Good content
  versus gate-passing filler / Filled example* — including honest "What the
  gate checks here: nothing" entries wherever true.

### Graph schema contract

- **FR-010**: The lessons MUST define a typed graph: nodes with `id`,
  `kind`, `zone`, and kind-specific required attributes; directed labeled
  edges with typed attributes. The grant-graph node kinds (system, identity,
  credential, scope, data_class, endpoint, store, human) and
  architecture-graph node kinds (resource, data_store, identity, policy,
  key, network_edge, control_plane, actor), with their edge vocabularies,
  are the shipped schemas; `graph.schema.json` MUST encode them.
- **FR-011**: A trust boundary MUST be defined as a computed predicate over
  the `zone` attribute — `crosses(edge) ⟺ zone(src) ≠ zone(dst)` — never as
  a node type; the lessons MUST teach the crossing set as a set operation.
- **FR-012**: Node and edge ids MUST be stable across graph versions so the
  ledger, the traversal log, and diffs can reference them; the lesson MUST
  show a graph diff between versions N and N+1.
- **FR-013**: The cloud schema MUST require the five tag keys on every node
  and MUST define the two derived cuts: the crossing set and
  `blast_radius(control_plane)` via the `deploys` closure.

### Traversal procedure (graph → obligations)

- **FR-020**: The graph lesson MUST teach the traversal as numbered,
  ordered, repeatable rules (R1–R13), each with a computable trigger and a
  named output artifact, mapping onto the universal core spec template's
  sections and the plan template — including at minimum: every reachable
  data_class node → a Data Classification row (R1); every zone and crossing
  zone-pair → Trust Boundaries content (R2); **every boundary-crossing edge
  → an abuse case + a control requirement + an evidence-chain row (R3)**;
  every credential node → Secrets/Credential Handling content keyed by its
  attributes (R4); every admin/tenant-wide scope or wildcard policy → a
  high-impact action and a human approval point (R5); identities → roles and
  conditionally abuse actors (R6); externally-zoned nodes → External System
  Access (R7); log-receiving stores → Audit/Logging (R8); missing tag keys →
  a traversal finding (R9); cycles → replay/idempotency,
  privilege-escalation, or trust-verification obligations by cycle type
  (R10); model/agent nodes → AI/LLM Risk (R11); node-kind presence →
  Compliance applicability rows (R12); whole-graph → plan-section
  obligations including Data Flow And Trust Boundaries, Rollback, and
  Threat Model (R13).
- **FR-021**: The traversal's primary artifact MUST be the **obligation
  ledger**: one row per emitted obligation linking graph element id → rule →
  abuse case → requirement → negative test → evidence path → owner, with no
  row advanced while any cell is blank.
- **FR-022**: The lesson MUST teach the **gap list** as the complement —
  dangling elements with no ledger row (unclassified data node, ownerless
  credential, uncontrolled crossing edge, untagged node, untreated cycle) —
  and MUST state that this list is precisely what the deterministic gate
  cannot compute.
- **FR-023**: The SaaS drill MUST include the tenant-substitution
  adversarial exercise (tenant A's valid artifact presented on tenant B's
  edge → required rejection with a negative test) and MUST surface the
  commonly-omitted nodes: token storage, OAuth callback handler, webhook
  retry queue and its dead-letter path, provider administrator, revocation
  path, support/operator access.
- **FR-024**: The cloud drill MUST teach the reverse-path rule — for every
  protected data or control-plane node, reverse-walk every reachable path
  to a root outside its administrative domain, emitting an obligation at
  every cut — and the shared-node fan-out rule (multiple
  tenants/environments converging on one node → isolation abuse case plus
  evidence that one input cannot select another's context).
- **FR-025**: One graph-derived risk MUST appear in the ledger once with a
  stable id and be cross-referenced from the spec sections it touches —
  never copy-pasted into six sections (the boilerplate-multiplication
  guard).

### Loop engineering

- **FR-030**: The loop lesson MUST teach three nested loops: **L1** —
  per-element interrogation of the crossing set with four fixed questions
  (who authenticates it, what authorizes it, what validates its payload,
  what evidences it happened), each unanswered question emitting one spec
  line; **L2** — adversarial one-hop propagation (assume this credential
  leaked / this message replayed / this role wrongly assumed) that MAY
  mutate the graph by adding the nodes and edges the attack revealed; **L3**
  — the outer convergence loop, re-running L1+L2 whenever L2 mutated the
  graph.
- **FR-031**: Convergence MUST be mechanical: a full pass adding no new
  node, no new edge, and no new spec line is **dry**; done is declared only
  on a dry pass; the pass number and per-pass delta counts are recorded in
  the traversal log. Feelings are not a termination criterion (the
  premature-stop guard).
- **FR-032**: The non-termination guard MUST be the traceability rule —
  only elements traceable to a real system artifact may enter the graph;
  speculative elements go to Assumptions, not the graph — plus the split
  rule: not dry after three passes means the feature scope is too large;
  split the feature rather than continuing to loop.
- **FR-033**: The traversal log MUST be taught as a committed,
  reviewer-facing artifact, with its Tier-2 status stated plainly: the gate
  is green on pass 0 because the template is complete in form; the gate
  cannot see convergence, count passes, or distinguish a dry traversal from
  an unperformed one.
- **FR-034**: The lesson MUST connect the loop discipline to the shipped
  vocabulary the reader already knows: the gate-as-checkpoint rhythm from
  the first-spec playbook, and the Fleet Guardrails terms (idempotency,
  retry, workflow state) the rule engine already recognizes.

### Representation and tooling

- **FR-040**: The artifact of record for each example MUST be Mermaid
  source at `docs/diagrams/<feature-id>-<graph-kind>.mmd` in the reader's
  repo (extending the `system-context.mmd` every init already ships), with
  the same fence mirrored into that feature's
  `plan.md § Data Flow And Trust Boundaries`, replacing the shipped
  edge-list placeholder.
- **FR-041**: The lessons MUST note that this strengthens an existing gate
  signal without touching the gate: `SICARIO-MISSING-DIAGRAMS` counts
  `docs/diagrams/*` by presence only.
- **FR-042**: Rendering on the docs-site MUST take exactly one of two
  declared paths: **(i)** add `@docusaurus/theme-mermaid` (docs-site
  `package.json` only; build-time; nothing ships in the wheel) as an
  explicit, reviewed dependency decision, or **(ii)** publish the mermaid
  fence as source plus a tool-captured screenshot of the rendered diagram
  under 007 FR-030's capture class. The chosen path MUST be recorded in the
  implementation plan; the `.mmd` source remains the artifact of record
  either way.
- **FR-043**: A stdlib-only helper MUST ship at `examples/spec-graph/`
  (following the `examples/custom-rules/` precedent, deliberately outside
  `scripts/`): `README.md`, `graph.schema.json`,
  `spec_graph_checklist.py`, and the two example graphs
  (`saas-integration.graph.json`, `cloud-architecture.graph.json`). The
  helper walks a graph file and emits the section checklist, the obligation
  stubs, and the gap list.
- **FR-044**: The helper's contract is SR-002/SR-003 in full, plus: an
  optional `--to-mermaid` flag deriving the `.mmd` view from the JSON
  (making JSON the source of truth and eliminating diagram drift), and
  deterministic output ordering so verified blocks are stable.
- **FR-045**: Helper invocations quoted in the lessons MUST be `verified`
  blocks re-executed by the existing docs runner (its glob already covers
  `docs/playbooks/*.md`; no runner changes are permitted for this feature).
- **FR-046**: If worked example repos are shipped
  (`examples/saas-integration/`, `examples/cloud-architecture/` on the
  `examples/python-api/` pattern), each MUST hold a complete spec, plan, and
  graph that pass `sicario verify` in a fresh init, giving the track the
  same completed-reference anchor the spec-authoring playbook has.

### Invariants and exclusions (all MUST NOT)

- **FR-050**: No change to `sicario verify`: no new evaluator kind, no file
  added or changed under `presets/sicario-core/rules/`, no change to
  required headings or keyword lists, no new finding code, no change to exit
  codes, `gate-summary.json`, or `spec-run-evidence.json`.
- **FR-051**: No graph parsing in the verdict path: `sicario_cli` never
  imports the helper; a test asserts this.
- **FR-052**: No new Python dependency: `pyproject.toml` `dependencies`
  stays empty; `networkx`, `graphviz`, `pyvis`, `pydot` are excluded even as
  optional extras. The sole permitted new dependency is FR-042 option (i)'s
  docs-site theme.
- **FR-053**: No template changes: no section added to any
  `presets/*/templates/*.md` (a core-template addition would propagate to
  all presets via the superset invariant and rewrite every adopter's
  templates); no `preset.yml` or `bundle.yml` changes; upstream bundle and
  preset compatibility untouched.
- **FR-054**: No new `presets/*/rules/` directory anywhere (only
  `sicario-core`'s is loaded; any other would be dead code that looks
  live).
- **FR-055**: No CI gating by the helper: it is never added to
  `workflow_templates/sicario-verify.yml` or its assets mirror; if it runs
  in CI at all it is a separate, non-blocking job.
- **FR-056**: No model call, network call, or AI import in any shipped code
  introduced by this feature.

### Spec 007 inheritance

- **FR-060**: Verified/illustrative markers on every quoted output block,
  per 007 FR-050's marker grammar, enforced by the existing runner.
- **FR-061**: A reference run per lesson, recorded per 007 FR-080–FR-084;
  the first-run evaluation is performed by a designated first-time evaluator
  who did not perform the reference run.
- **FR-062**: Placeholder-only example values throughout (007 SEC-001), with
  this feature's sharper negative criterion in SEC-005.

## Security Acceptance Criteria

- **SEC-001**: `python3 -m unittest discover -s tests` passes with zero
  changes to any existing gate test; a diff of `sicario_cli/` against the
  pre-feature baseline shows no behavioral change (documentation-only or
  zero changes).
- **SEC-002**: A test asserts the helper never emits verdict vocabulary:
  running it over both example graphs produces output containing no
  `SICARIO-` prefix, no severity token, and none of
  `pass`/`passed`/`fail`/`failed`/`blocking`/`violation`; its exit code is
  `0` on both valid and gap-ridden input.
- **SEC-003**: A test asserts `sicario_cli` has no import path to
  `examples/spec-graph/` (static scan of imports), and that
  `workflow_templates/sicario-verify.yml` and its assets mirror are
  byte-identical to baseline.
- **SEC-004**: A fresh `sicario init` + `sicario verify` in a scratch
  project remains green and byte-identical in report wording to baseline —
  proving the feature changed nothing adopters receive.
- **SEC-005**: A negative test runs the shipped secret-scan rule patterns
  over every file in `examples/spec-graph/` and the two lesson pages and
  asserts zero matches; example credential values are angle-bracketed
  placeholders exclusively.
- **SEC-006**: Both lessons contain the SR-005 non-assurance statement and
  the SR-006 real-graph warning, asserted by the docs checks as literal
  required sentences (same mechanism 007 uses for its required notes).
- **SEC-007**: The docs verification runner passes over the new pages with
  its stock configuration — zero runner modifications in the diff.

## Security Evidence Chain

Requirement → control → test → evidence, for this feature's own delivery:

| Requirement | Control | Test | Evidence |
|---|---|---|---|
| Gate untouched (SR-001, FR-050) | Review + invariant tests | SEC-001, SEC-003, SEC-004 | CI logs; unchanged `gate-summary.json` wording in scratch run |
| Helper is not an authority (SR-002) | Contract in code + README | SEC-002 | Test output over both example graphs |
| No verdict-path coupling (FR-051) | Import prohibition | SEC-003 static scan | Test source and CI log |
| No secret-shaped examples (SR-004) | Placeholder policy | SEC-005 negative scan | Test output; reviewed diff |
| Honest-limits statements present (SR-005/006) | Required literal sentences | SEC-006 | Docs check output |
| Lessons stay live (FR-045, FR-060) | Verified-block re-execution | SEC-007 / existing runner | Runner summary per CI run |
| Reader-side evidence exists (FR-021, FR-033) | Ledger + traversal log formats | Evaluator first-run per FR-061 | Attested first-run log; reference-run records |

## Evidence To Produce

- The two lesson pages and track index with frontmatter (guide-slug,
  captured-version, reference-run repository and date).
- `examples/spec-graph/` complete: README, schema, helper, two graphs.
- Reference-run records and first-run evaluator attestation per lesson.
- The new tests (SEC-002, SEC-003, SEC-005, sidebar-exclusion FR-003) in the
  repository test suite.
- CI runs showing: full suite green, docs runner green over the new pages,
  docs-site build green with whichever FR-042 path was chosen.
- The implementation plan recording the FR-042 decision and, if option (i),
  the reviewed dependency addition.

## Success Criteria

- **SC-001**: A first-time evaluator (per FR-061) completes each lesson cold
  within its stated budget and produces, for the lesson's scenario, a
  non-empty obligation ledger and a correct gap list for a deliberately
  incomplete input graph.
- **SC-002**: The evaluator, given the "fully covered" example, identifies
  at least one real off-graph omission in the closing drill — demonstrating
  the non-assurance lesson landed.
- **SC-003**: The six-lesson path is unchanged in count, content, and stated
  time; the track appears exactly once in the sidebar, collapsed.
- **SC-004**: All SEC criteria pass in CI on the merge commit.
- **SC-005**: A reader following the graph lesson in a fresh init'd repo
  ends with `docs/diagrams/` containing their feature graph, a plan whose
  Data Flow section carries the mirrored fence, a committed ledger and
  traversal log, and a green gate — with the lesson having told them exactly
  which of those artifacts the gate can and cannot see.

## Assumptions

- The universal core spec template (20 sections, identical across presets)
  remains the shipped shape; if a future feature diverges per-preset
  templates, the traversal's section mapping needs a compatibility pass.
- The docs verification runner's glob (`docs/guides/*.md`,
  `docs/playbooks/*.md`) remains stable; the track deliberately fits inside
  it.
- Spec 004's Two-Tier Authority language remains the governing vocabulary
  for authority claims; this spec cites it rather than restating it.
- The maintainer group can produce the reference runs and recruit a
  first-run evaluator per 007's existing process.
- Six-lesson-path stability is a product commitment this feature treats as
  a constraint, not a preference.
- The landscape-research finding set (industry practice on graph-driven
  agent workflows) may add named prior-art citations to the lessons at
  implementation time; nothing in this spec depends on it.
