---
name: precedence
purpose: Conflict resolution order.
---

# Rule — Precedence

When two docs cover the same case with different rules, apply the following order.

## Order

1. **Decision docs (accepted)** override parent docs within their scope.
2. **Org** — org-root docs.
3. **Product** — product-level docs.
4. **Repo** — repo-level docs.
5. **Project** — project-level docs (monorepo apps, services).
6. **Module** — module-level docs.
7. **File-level** — sibling `<filename>.md` docs.

A doc at a higher level wins over a doc at a lower level. A decision doc wins over any non-decision doc at the same or lower scope.

## Same-Level Conflict

If two docs at the same level conflict:

1. **Stop the task.**
2. **Create a `NEED_CLEARIFICATION` item** naming both docs.
3. **Do not pick one silently.**

## No Version Ties

There is no "newer wins" rule. Docs are either consistent or in conflict. VCS history is not a tiebreaker.

## NC Item Authority

Open NC items are **provisional intent**. The authority order for a given case is:

1. Active doc.
2. Open NC item.
3. Agent guess.

An NC item never overrides an active doc.

## Org Docs Fallback

When `requires_org_docs: true` and the org-root is unreachable, apply the `org_docs_fallback` declared in the anchor `AGENT.md`:

| Value | Behavior |
|---|---|
| `notify` | Notify the caller, continue with local docs. |
| `stop` | Halt until org docs are provided. |
| `proceed` | Continue with local docs, log an NC item. |

If `requires_org_docs: false`, continue with local docs and the `docs` skill, regardless of `org_docs_fallback`.

## Examples

**Example 1 — Decision overrides blueprint.**

- `product:payments/blueprint/non-goals` says "no partial refunds."
- `repo:payments-api/decisions/003-005-partial-refunds` accepts partial refunds.

Result: the decision overrides the blueprint **within the repo's scope**. The blueprint doc is a defect and should be updated to reference the decision.

**Example 2 — Org beats product.**

- Org `AGENT.md`: "All products MUST use the shared auth service."
- Product `AGENT.md`: "Payments uses its own auth."

Result: org rule wins. The product doc is a defect.

**Example 3 — Same-level conflict.**

- `repo:payments-api/blueprint/invariants` says "retry 3 times."
- `repo:payments-api/blueprint/architecture` says "retry 5 times."

Result: stop. Create an NC item naming both docs.

## Resolution Flow

1. Apply the precedence order.
2. If a decision doc covers the case, follow it.
3. If two docs at the same level conflict, stop and create an NC item.
4. Never edit a higher-authority doc to resolve a conflict without an NC item.