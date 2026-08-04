# Spec Graph Examples

Teaching material for the SicarioSpec **Advanced Track**. It ships a typed
graph contract, two synthetic example graphs, and a standard-library helper
that walks a graph and prints the obligations the graph forces into a spec —
plus the gap list of what it could not answer.

- Owner: maintainer group
- System: sicario-spec examples
- Environment: documentation only, never production
- Data classification: Public
- Retention: life of the examples

## What This Is

An advanced author does not walk the spec template section by section asking
"what belongs here?" They build a **typed graph** of the feature — nodes with
a `kind`, a `zone`, and kind-specific attributes; directed labelled edges —
and then apply fixed traversal rules that mechanically emit obligations:
abuse cases, control requirements, classification rows, evidence rows, owners.

The load-bearing idea: a trust boundary is **not a node**. It is the `zone`
attribute, and a boundary crossing is the computed predicate

```text
crosses(edge) <=> zone(src) != zone(dst)
```

which turns "which edges cross a trust boundary" from a judgment call into a
set operation.

## What This Is **Not**

It is not an authority. `sicario verify` is the sole authority on whether a
repository meets the governance contract, and nothing in this directory
participates in that decision. By contract (spec 008 SR-002 / SR-003), the
helper:

- imports only the standard library, and never imports `sicario_cli`
- makes no network call, no subprocess call, and no model call
- writes no file, creates no file, and modifies no file — stdout only
- always exits `0`, including on a malformed graph document
- never emits a `SICARIO-` finding code, a severity level, or the words
  *pass*, *passed*, *fail*, *failed*, *blocking*, or *violation*

Those word prohibitions are not cosmetic. The named abuse case is **verdict
creep**: a helper that grows a strict flag, a non-zero exit code, or a
severity column becomes a shadow gate, and a repository with two authorities
has none. The helper therefore speaks only in *obligation*, *checklist*,
*gap*, and *unanswered*. Invariant tests in
`tests/test_spec_graph_examples.py` hold the line.

(The phrase *high-impact action* in the R5 output is spec-template vocabulary
for a class of action, not a severity rating.)

The complementary abuse case is **coverage laundering**: presenting "every
graph element has a checklist line" as "the spec is done". A graph-derived
spec is not thereby complete, verified, or certified. The graph determines
*relevance and depth*; it never determines the gate's required form, and an
inapplicable concern still gets an explicit rationale rather than deletion.

## Files

| File | What it holds |
|---|---|
| `graph.schema.json` | The typed graph contract: node kinds, edge types, per-kind required attributes |
| `spec_graph_checklist.py` | The standard-library helper (checklist mode and mermaid mode) |
| `saas-integration.graph.json` | Grant graph: a first-party CRM connected to a vendor helpdesk |
| `cloud-architecture.graph.json` | Architecture graph: public load balancer through to CI deploy runner |

## Usage

Checklist mode prints the header, the crossing set, the obligation checklist
from traversal rules R1-R13, and the gap list:

```bash
python3 examples/spec-graph/spec_graph_checklist.py \
  examples/spec-graph/saas-integration.graph.json
```

Mermaid mode derives the diagram from the same JSON, one subgraph per zone,
crossing edges labelled, so the JSON stays the single source of truth and the
diagram cannot drift from it:

```bash
python3 examples/spec-graph/spec_graph_checklist.py \
  examples/spec-graph/cloud-architecture.graph.json --to-mermaid \
  > docs/diagrams/005-regulated-export-path-architecture.mmd
```

Output ordering is deterministic in both modes: two runs over the same input
are byte-identical.

## The Two Example Graphs

`saas-integration.graph.json` is the **grant graph** — systems, identities,
credentials, scopes, data classes, endpoints, stores, humans. It carries a
deliberate `calls`/`flows` cycle (CRM to helpdesk to webhook back to CRM),
which is where the replay and idempotency obligation comes from, and a
credential with no rotation owner, which is where a gap-list line comes from.

`cloud-architecture.graph.json` is the **architecture graph** — resources,
data stores, identities, policies, keys, network edges, a control plane. It
carries the `can_assume` cycle `svc-api -> fn-export -> ci-deploy -> svc-api`
(a service compromise reaching the control plane), a wildcard object-store
policy, one deliberately untagged node and one deliberately half-tagged node
so traversal rule R9 and the gap list have real output.

Modelling only the happy path — omitting the return edges — is the most
common authoring error. It shows up as an empty R10 section, so the helper
prints an explicit "no cycle detected in this family" line rather than
silence.

## Two Deliberate Reading Choices

- **`tags` is optional in the schema, and R9 is what speaks.** Requiring the
  five tag keys in `graph.schema.json` would make the deliberately untagged
  example node schema-invalid, and the teaching point is that an untagged
  node is a first-class *traversal finding*, not a parse error.
- **`actor` never on its own marks a document as an architecture graph.** A
  forged sender is as real in a grant graph as an internet client is in an
  architecture graph, so R9 and R12's Cloud / IaC row key off the strictly
  cloud kinds instead.

## Placeholders Only

Every credential-ish value in these graphs is an angle-bracketed placeholder
such as `<vault-ref>`. No string anywhere in this directory matches the
repository's own secret-scan patterns, and a test asserts it by re-reading
those shipped patterns rather than copying them. Do not "improve realism"
here: every adopter who copies an example inherits whatever is in it.

## A Warning About Your Own Graphs

The graphs here are synthetic. A real graph of a real system is an
attack-surface map — at minimum Internal, frequently Confidential. Do not
commit one to a public repository. Keep it in the private repository it
describes, in an access-controlled document store, or in a private diagram
tool, and commit only the derived spec content.

## Further Reading

- `docs/playbooks/graph-engineering.md` — building the graph and running the
  traversal
- `docs/playbooks/loop-engineering.md` — the three nested loops and the
  mechanical convergence criterion
- `specs/008-graph-loop-engineering-track/spec.md` — the specification these
  examples implement (FR-010, FR-013, FR-043, FR-044, SR-002 through SR-006)
