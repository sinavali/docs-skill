---
name: relationships
purpose: Typed relationship model between docs, flows, and code.
---

# Rule — Relationships

## Why Typed Relationships

A doc is not just a node. It has typed edges to other docs, to flows, and to code.
A generic `related: [DOC-X]` edge tells the orchestrator nothing. It cannot decide
whether to follow the edge, in which direction, or how far.

Every edge MUST carry a type. The type answers *why* the two nodes are connected.

## Edge Types

| Edge | Direction | Meaning |
|---|---|---|
| `references` | doc to doc | This doc depends on that doc's rules. Follow when the rule is load-bearing. |
| `affects` | doc to doc | A change here may change behavior there. Follow to find downstream impact. |
| `implements` | doc to flow | This doc is one implementation of that flow. Follow up to the flow. |
| `depends_on` | doc to doc | Optional. Stronger than `references`: cannot be understood without it. |

`references` and `affects` are NOT interchangeable:

- `references` — read this to understand me.
- `affects` — change me and you may have to change this.

## Flow Edges

A flow doc MAY declare the domains it spans:

```yaml
domains: [auth, users, notifications]
```

This is derived, not maintained separately. The index generator reverses
`implements` edges into the flow's participant list.

## Reverse Edges Are Derived, Never Authored

Never write both:

```yaml
A: { affects: [B] }
B: { affected_by: [A] }
```

Author only `A.affects: [B]`. The generated graph derives `B.affected_by: [A]`.

Same for `references` / `referenced_by`, and `implements` / `implemented_by`.

This is a hard rule. Authoring reverse edges guarantees drift.

## Code Edges

| Edge | Meaning |
|---|---|
| `code_paths` | Directories or globs this doc governs. |
| `test_paths` | Test directories or globs that verify this doc's behavior. |

`code_paths` is the bridge between the documentation graph and the code tree.
Without it, doc discovery and code retrieval are separate systems.

## Traversal Policy

Impact expansion follows edges in this order:

1. `implements` upward — from a doc to its flow, then from the flow to sibling domains.
2. `affects` outward — to downstream docs that may need changes.
3. `references` — only when the referencing doc's rule is load-bearing for the task.
4. `depends_on` — always, before the depending doc is trusted.

Stop expanding when the frontier contains only nodes whose `code_paths` are already
in the change surface.

## Rules

- **MUST** type every edge. No `related`.
- **MUST NOT** author reverse edges.
- **MUST** keep `references` (read) and `affects` (change) semantically distinct.
- **MUST** attach `code_paths` to every doc that governs code.
- **MUST** resolve every edge target to an existing ID at validate time.