---
name: index-format
purpose: The semantic routing map and the global documentation map.
---

# Rule — Index Format

## Two Indexes, Two Jobs

| File | Job | Answers |
|---|---|---|
| `/docs/INDEX.md` (global map) | Orientation | Which domains exist? Which flows exist? Which domains participate in each flow? |
| `<dir>/INDEX.md` (routing map) | Routing | Where should I look for X? |

Neither carries document content. Both must stay small.

## Global Map — `/docs/INDEX.md`

Tiny. Hand-maintained at the domain and flow level only.

```markdown
# Documentation Map

## Domains
auth · users · billing · notifications · security

## Flows
registration · login · password-reset · subscription · invoice-payment

## Cross-domain flows

registration:
  - auth
  - users
  - notifications

password-reset:
  - auth
  - users
  - notifications
  - security
```

## Routing Map — a Directory `INDEX.md`

For each section in the directory, one row. No content.

```markdown
| ID | Purpose | Domains | Flows | Code |
|---|---|---|---|---|
| auth/registration | Registration rules | auth, users | registration | packages/auth/src/registration/** |
| users/lifecycle | User lifecycle | users | registration, deletion | packages/users/** |
| notifications/email | Email delivery | notifications | registration, password-reset | packages/notifications/** |
```

Columns:

| Column | Required | Notes |
|---|---|---|
| `ID` | yes | Doc ID per `rules/numbering.md`. |
| `Purpose` | yes | One line. Routing only. |
| `Domains` | when known | Comma-separated. |
| `Flows` | when known | Comma-separated. |
| `Code` | when known | Comma-separated globs. |

## Why Columns, Not Prose

The routing map is the cheap, always-loadable layer. It must be enough for the
orchestrator to choose seeds without loading a single document body.

## Rules

- **MUST NOT** put document content in any `INDEX.md`.
- **MUST** keep each `INDEX.md` under the soft threshold (`rules/sectioning.md`).
- **MUST** keep the global map to domains, flows, and participation only.
- **MUST** derive columns from frontmatter where possible; if they disagree, the
  frontmatter wins and the index is stale.