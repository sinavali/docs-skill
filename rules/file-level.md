---
name: file-level
purpose: Sibling <filename>.md discovery rule.
---

# Rule — File-Level Docs

## Purpose

A source file MAY have a sibling `<filename>.md` describing approach, alternatives, flow, invariants, and non-goals. These are **not** under `/docs/`, and are **not** indexed in `/docs/INDEX.md`. They are discovered by directory listing next to the file.

## Placement

```text
src/refunds/
├── refund.ts
├── refund.ts.md          ← file-level doc
├── validation.ts
└── validation.ts.md      ← file-level doc
```

## Frontmatter

```yaml
---
id: file:payments-api/refunds/refund
parent: module:payments-api/refunds
title: Refund Implementation Notes
level: file
kind: blueprint
file: refund.ts
---
```

## Body Shape

A file-level doc SHOULD contain these sections, in order, when applicable:

1. **Approach** — what the file does.
2. **Why This Approach** — rationale and alternatives considered.
3. **Flow** — step-by-step behavior.
4. **Invariants** — non-negotiable rules.
5. **Non-Goals** — what the file explicitly does not do.

## Example

```markdown
---
id: file:payments-api/refunds/refund
parent: module:payments-api/refunds
title: Refund Implementation Notes
file: refund.ts
level: file
kind: blueprint
---

# Refund Implementation Notes

## Approach
Refunds use a two-phase state machine: `pending` → `completed` | `failed`.

## Why This Approach
Chosen over synchronous provider calls because refunds may take seconds to minutes
and we must not block the API response. Alternatives considered:

1. **Synchronous call** — Rejected; provider latency unpredictable.
2. **Job queue** — Rejected; overkill for current volume.

## Flow
1. Validate idempotency key.
2. Insert `pending` row.
3. Enqueue provider call.
4. Provider webhook completes the row.

## Invariants
- A refund row MUST exist before any provider call.
- Idempotency keys MUST be persisted before enqueue.

## Non-Goals
- Partial refunds (planned for v2).
- Multi-currency refunds.
```

## Rules

- **MUST** be sibling to the source file, named `<filename>.md`.
- **MUST NOT** live under `/docs/`.
- **MUST NOT** be indexed in `/docs/INDEX.md`.
- **MUST** carry `file:` in frontmatter pointing to the source file.
- Every `AGENT.md` **MUST** instruct agents to check for sibling `<filename>.md` files before modifying a source file.
- **MUST NOT** duplicate content that lives in `/docs/`. Reference the doc ID instead.

## Agent Behavior

Before modifying any source file:

1. List the file's directory.
2. If `<filename>.md` exists, read it before editing.
3. Use its invariants and non-goals to constrain the change.
4. If the change contradicts the file-level doc, create an NC item.