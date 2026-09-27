---
name: impact
purpose: Discover the complete impact surface of a change, then emit a Change Surface.
modifies_files: false
requires_access: read
---

# Mode — `impact`

**Purpose:** Turn a change request into a **Change Surface** — the complete, bounded,
and provably-considered set of docs, flows, code, and tests a change touches.

This is the orchestrator's discovery mode. It runs **before** any implementation.

**Inputs:**
- `anchor_path` — the directory where work begins.
- `request` — the change request, verbatim.

**Outputs:**
- A Change Surface per `templates/change-surface.md`.
- `nc_items_created` — NC item IDs, if any.

**References:**
- `rules/impact.md`
- `rules/relationships.md`
- `rules/index-format.md`
- `rules/frontmatter.md`
- `rules/precedence.md`
- `rules/nc.md`
- `templates/change-surface.md`

---

## Steps

1. **Read the global map.** `docs/INDEX.md`. Get the domain list, the flow list, and
the cross-domain participation table. This is the first and cheapest read.
2. **Classify the request.** Domain-local, cross-domain, contract, or behavioral.
   Record the classification.
3. **Find seeds.** Match the request against `keywords`, `domains`, and `flows`
   metadata via `modes/index.md`. **Do not** start from the file tree. Seeds are
   flow IDs and doc IDs, not paths.
4. **Expand relations.** Follow edges per `rules/relationships.md`:
   - `implements` upward to the flow, then to sibling domains,
   - `affects` outward,
   - `references` only when load-bearing,
   - `depends_on` always.
   Stop when the frontier no longer yields new `code_paths`.
5. **Inspect code.** Confirm the declared `code_paths` contain the behavior. If a
   needed path is absent, the surface is incomplete — record it as a risk.
6. **Compute negative scope.** For each apparently related flow or domain that is
   *not* in the surface, record why it was ruled out. This section is mandatory.
7. **Load only what is needed.** For each doc in the surface, load the specific
   sections the change touches (per `modes/read.md` descent rules). Not whole trees.
8. **Emit the Change Surface.** Per `templates/change-surface.md`. Set status:
   - `READY_FOR_IMPLEMENTATION` if the frontier closed,
   - `NEEDS_CLARIFICATION` if a required doc is missing or ambiguous.
9. **Return.** The Change Surface, plus any NC item IDs.

---

## Rules

- **MUST** start from metadata, never from the file tree.
- **MUST** record negative scope ("checked and unaffected").
- **MUST NOT** implement anything in this mode.
- **MUST NOT** hand the raw request to a coder. Hand the Change Surface.
- **MUST** stop and set `NEEDS_CLARIFICATION` if a required doc is missing. Do not
  invent.
- **MUST** obey `max_entries` if given; otherwise metadata discovery is unbounded.

---

## Example

Request: *"Change registration so verification expires after 24h instead of 48h."*

```text
# Change Surface

## Request
Change registration so verification expires after 24h instead of 48h.

## Seeds
- flow:registration
- auth/registration

## Documentation inspected
- auth/registration: expiry rule lives here
- auth/verification: verification mechanics
- users/lifecycle: post-verification state

## Related documentation identified
- notifications/email-verification: affects edge from auth/registration
- security/token-policy: references edge

## Code surface
- packages/auth/src/registration/**
- packages/auth/src/verification/**
- packages/notifications/src/email/**

## Test surface
- packages/auth/test/registration/**
- packages/auth/test/verification/**

## Related flows
- registration
- email-verification

## Explicitly checked and unaffected
- login: no expiry token involved
- password-reset: separate token policy, unchanged
- billing: unrelated

## Risks
- Existing pending verifications created under 48h must not break.

## Open questions
- Should pending 48h tokens be migrated or left to expire? → NC-0042

## Status
NEEDS_CLARIFICATION
```