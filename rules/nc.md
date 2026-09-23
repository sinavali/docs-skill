---
name: nc
purpose: NEED_CLEARIFICATION item lifecycle and schema.
---

# Rule — NEED_CLEARIFICATION

## Purpose

Capture every case where an agent had to decide without sufficient doc authority, so a human can confirm or correct it. Ambiguity is recorded, never invented.

## When to Create

Create an NC item when an active doc does not cover a case the agent must decide. Do not create NC items for routine coding choices covered by existing docs.

**Valid triggers:**
- A field's optionality is not stated.
- A response code is not specified.
- A default value is missing.
- A boundary between two modules is unclear.
- A required doc is missing.
- Two docs at the same level conflict.
- An ancestor `AGENT.md` is missing.

**Invalid triggers:**
- Choosing a variable name.
- Choosing a test framework when the doc names one.
- Following an existing pattern in code.
- Any choice fully covered by an active doc.

## Placement

- One file per repo root: `<repo>/NEED_CLEARIFICATION.md`.
- For cross-repo work: duplicate into each accessible affected repo's file with a shared item ID.
- If a repo is inaccessible, only reachable repos carry the item.
- The file does not exist until the first item is created.

## Schema

```markdown
## NC-NNNN — Short title

- **Status:** open
- **Date:** YYYY-MM-DD
- **Agent:** <agent name>
- **Scope:** <scope id>
- **Affected repos:** <comma-separated list, optional>
- **Situation:** <what the doc does not cover>
- **Options considered:**
  1. <option>
  2. <option>
- **Chosen approach:** <what the agent did>
- **Rationale:** <why this was the safest choice>
- **Reversibility:** <high | medium | low>
- **Promotion target:** <doc path or doc id>
```

## File Shape

```markdown
# NEED_CLEARIFICATION

Open items are provisional intent. They are NOT product intent.
When confirmed, promote into the target doc and remove the item.

## Index

| ID | Status | Date | Scope | Summary |
|---|---|---|---|---|
| NC-0007 | open | 2026-09-23 | module:payments-api/refunds | Refund reason optionality |
| NC-0008 | open | 2026-09-23 | module:payments-api/refunds | Idempotency window |

## NC-0007 — Refund reason optionality
...

## NC-0008 — Idempotency window
...
```

## Lifecycle

1. **Create** — when ambiguity arises.
2. **Persist** — items remain until human confirmation. No expiry.
3. **Confirm** — human confirms or requests a change.
4. **Promote** — the decision is written into the target doc via the `docs` skill's `extend` mode.
5. **Remove** — the item is deleted entirely. No archive.

## Authority

Open NC items are **provisional intent**. Precedence for a given case:

1. Active doc.
2. Open NC item.
3. Agent guess.

## Cross-Repo Example

If a refund API change touches `payments-api` and `payments-web`:

```markdown
## NC-0012 — Refund reason field type

- **Status:** open
- **Date:** 2026-09-23
- **Agent:** coder
- **Scope:** module:payments-api/refunds
- **Affected repos:** payments-api, payments-web
- **Situation:** Contract does not specify if `reason` is free-text or enum.
- **Options considered:**
  1. Free-text with 500-char limit
  2. Enum of fixed reasons
- **Chosen approach:** Free-text with 500-char limit.
- **Rationale:** Safest; supports all existing call sites.
- **Reversibility:** High.
- **Promotion target:** docs/004-contracts/004-001-refund-api.md
```

Both `payments-api/NEED_CLEARIFICATION.md` and `payments-web/NEED_CLEARIFICATION.md` contain this item with the same ID `NC-0012`.

## Human Confirmation Workflow

1. Human reads `NEED_CLEARIFICATION.md`.
2. Human tells the agent "item NC-0007 is confirmed" or "refactor to X."
3. Agent promotes the decision:
   - If confirmed: writes it into the target doc via `docs extend`.
   - If refactored: implements the change, updates the target doc, updates affected code.
4. Agent removes the NC item entirely.

## Rules

- **MUST** use sequential 4-digit IDs starting at `NC-0001`.
- **MUST** keep IDs unique within a file.
- **MUST** keep cross-repo items at the same ID across repos.
- **MUST NOT** archive or expire items. Items remain open until confirmed or refactored.
- **MUST** state a promotion target for every item.
- **MUST** record reversibility for every item.