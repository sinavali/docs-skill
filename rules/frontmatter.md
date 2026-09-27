---
name: frontmatter
purpose: Required and optional frontmatter fields for every doc.
---

# Rule — Frontmatter

Every doc MUST carry YAML frontmatter at the top of the file.

## Required Fields

| Field | Type | Notes |
|---|---|---|
| `id` | string | Stable, path-derived per `rules/numbering.md`. Unique within scope. |
| `title` | string | Human-readable. |
| `level` | enum | `org` \| `product` \| `repo` \| `project` \| `module` \| `file`. |
| `kind` | enum | `agent` \| `blueprint` \| `decision` \| `contract` \| `cross-cutting` \| `operational`. |

## Optional Fields

| Field | Type | Applies to | Notes |
|---|---|---|---|
| `scope` | string | `AGENT.md` | Scope identifier, e.g. `payments/api`. |
| `parent` | string | Section files | Parent doc ID. |
| `references` | string[] | Any doc | Doc IDs this doc depends on. |
| `applies_to` | string[] | Cross-cutting docs | Scopes to which the rule applies. |
| `file` | string | File-level docs | Source file path. |
| `org_root` | string | Repo / project / module `AGENT.md` | Relative path or ID of org-root. |
| `is_org_root` | boolean | Org-root `AGENT.md` | |
| `requires_org_docs` | boolean | Repo `AGENT.md` | |
| `org_docs_fallback` | enum | Repo `AGENT.md` | `notify` \| `proceed` \| `stop`. |
| `skill` | string | `AGENT.md` | Default `docs`. |
| `excluded_paths` | string[] | `AGENT.md` | Paths out of documentation scope. |
| `included_paths` | string[] | `AGENT.md` | Paths re-included from exclusions. |
| `parties` | string[] | Contract docs | Scopes that participate in the contract. |
| `date` | ISO date | Decision docs | |
| `deciders` | string[] | Decision docs | |

## `INDEX.md` Kind Inheritance

An `INDEX.md` inherits the `kind` of the directory it indexes.

| Directory | `kind` in `INDEX.md` |
|---|---|
| `001-agent/` | `agent` |
| `002-blueprint/` | `blueprint` |
| `003-decisions/` | `decision` |
| `004-contracts/` | `contract` |
| `005-cross-cutting/` | `cross-cutting` |
| `006-operational/` | `operational` |

The `kind` of an `INDEX.md` MUST NOT be `index`. `index` is a reserved filename, not a `kind` value. The `INDEX.md` of a sectioned doc that was previously a single-file doc inherits the `kind` of that doc (e.g., a sectioned refund contract keeps `kind: contract`).

## Removed Fields (MUST NOT appear)

| Field | Reason |
|---|---|
| `version` | VCS is the version store. |
| `status` | Docs are always live. |
| `supersedes` / `superseded_by` | Decisions are immutable; blueprint docs are edited in place. |
| `last_reviewed` | Bookkeeping without enforcement. |
| `generated` | All docs are assumed generated. |
| `order` | Order is defined by `INDEX.md`, not by frontmatter. |
| `source_of_truth` | Not removed, but reserved for mirror docs; see below. |

### Mirror-Only Field

A vendored mirror MAY carry:

```yaml
source_of_truth: false
canonical: <doc id of the canonical doc>
```

No canonical doc carries `source_of_truth: true`. Absence is the default.

## Examples

**Org `AGENT.md`:**

```yaml
---
id: org:acme/agent
scope: acme
level: org
kind: agent
is_org_root: true
skill: docs
excluded_paths: [.git/, .opencode/, node_modules/, dist/, build/, .cache/, coverage/]
---
```

**Product blueprint section:**

```yaml
---
id: product:payments/blueprint/non-goals
parent: product:payments/blueprint
title: Non-Goals
level: product
kind: blueprint
references: [product:payments/blueprint/overview]
---
```

**Repo `AGENT.md`:**

```yaml
---
id: repo:payments-api/agent
scope: payments/api
level: repo
kind: agent
org_root: ../../org-root
requires_org_docs: true
org_docs_fallback: notify
skill: docs
excluded_paths: [.git/, .opencode/, node_modules/, dist/, build/, .cache/, coverage/]
included_paths: []
---
```

**Blueprint `INDEX.md`:**

```yaml
---
id: product:payments/blueprint
title: Payments Blueprint
level: product
kind: blueprint
---
```

**Decision doc:**

```yaml
---
id: repo:payments-api/decisions/use-idempotency-keys
parent: repo:payments-api/decisions
title: Use Idempotency Keys for Refunds
level: repo
kind: decision
date: 2026-09-23
deciders: [payments-api-team]
---
```

**Contract doc:**

```yaml
---
id: product:payments/contracts/refund-api
parent: product:payments/contracts
title: Refund API Contract
level: product
kind: contract
parties: [payments-api, payments-web]
---
```

**Cross-cutting doc:**

```yaml
---
id: product:payments/cross-cutting/security
parent: product:payments/cross-cutting
title: Security Guidelines
level: product
kind: cross-cutting
applies_to: [product:payments, repo:payments-api, repo:payments-web]
---
```

**File-level doc:**

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

## Rules

- **MUST** include all required fields.
- **MUST NOT** include removed fields.
- **MUST** keep `id` unique within scope.
- **MUST NOT** reuse an `id` after deletion.
- **MUST** derive `id` from the doc's path per `rules/numbering.md`.
- **MUST** set the `kind` of an `INDEX.md` to the kind of the directory it indexes, never to `index`.
## Impact Metadata Fields

These fields turn a doc from a read-only node into a graph node. All are optional but
strongly recommended for any doc that governs code.

| Field | Type | Applies to | Notes |
|---|---|---|---|
| `domains` | string[] | Any doc | Business domains this doc belongs to, e.g. `auth`, `users`. |
| `flows` | string[] | Any doc | User/system flows this doc participates in, e.g. `registration`. |
| `keywords` | string[] | Any doc | Routing aliases. Cheap entry points for discovery. Include synonyms. |
| `references` | string[] | Any doc | Doc IDs this doc depends on. (Existing field, now typed.) |
| `affects` | string[] | Any doc | Doc IDs whose behavior a change here may change. Downstream impact. |
| `implements` | string[] | Section / contract docs | Flow IDs this doc is one implementation of. |
| `depends_on` | string[] | Any doc | Stronger than `references`: cannot be understood without it. |
| `code_paths` | string[] | Any doc that governs code | Globs pointing at the code this doc constrains. |
| `test_paths` | string[] | Any doc that governs code | Globs pointing at the tests that verify it. |

### `keywords` — Why They Matter

Titles are not enough. The user may say "change signup" while the doc says
"registration". Keywords carry the synonyms so discovery can find the doc without
loading it.

```yaml
keywords:
  - signup
  - sign-up
  - registration
  - onboarding
  - account creation
```

### `references` vs `affects`

They are not interchangeable:

- `references` — "read this to understand me".
- `affects` — "change me and you may have to change this".

See `rules/relationships.md`.

### Reverse Edges

**MUST NOT** be authored. `affected_by`, `referenced_by`, and `implemented_by` are
derived by the index generator. Authoring both directions guarantees drift.

### Example — Registration Contract

```yaml
---
id: repo:payments/auth/registration
title: Registration Rules
level: repo
kind: contract
domains:
  - auth
  - users
flows:
  - registration
keywords:
  - registration
  - signup
  - verification
  - account creation
references:
  - repo:payments/auth/verification
  - repo:payments/users/lifecycle
affects:
  - repo:notifications/email-verification
implements:
  - flow:registration
code_paths:
  - packages/auth/src/registration/**
  - packages/users/src/registration/**
test_paths:
  - packages/auth/test/registration/**
---
```

## Impact Metadata Fields

These fields turn a doc from a read-only node into a graph node. All are optional but
strongly recommended for any doc that governs code.

| Field | Type | Applies to | Notes |
|---|---|---|---|
| `domains` | string[] | Any doc | Business domains this doc belongs to, e.g. `auth`, `users`. |
| `flows` | string[] | Any doc | User/system flows this doc participates in, e.g. `registration`. |
| `keywords` | string[] | Any doc | Routing aliases. Cheap entry points for discovery. Include synonyms. |
| `references` | string[] | Any doc | Doc IDs this doc depends on. (Existing field, now typed.) |
| `affects` | string[] | Any doc | Doc IDs whose behavior a change here may change. Downstream impact. |
| `implements` | string[] | Section / contract docs | Flow IDs this doc is one implementation of. |
| `depends_on` | string[] | Any doc | Stronger than `references`: cannot be understood without it. |
| `code_paths` | string[] | Any doc that governs code | Globs pointing at the code this doc constrains. |
| `test_paths` | string[] | Any doc that governs code | Globs pointing at the tests that verify it. |

### `keywords` — Why They Matter

Titles are not enough. The user may say "change signup" while the doc says
"registration". Keywords carry the synonyms so discovery can find the doc without
loading it.

```yaml
keywords:
  - signup
  - sign-up
  - registration
  - onboarding
  - account creation
```

### `references` vs `affects`

They are not interchangeable:

- `references` — "read this to understand me".
- `affects` — "change me and you may have to change this".

See `rules/relationships.md`.

### Reverse Edges

**MUST NOT** be authored. `affected_by`, `referenced_by`, and `implemented_by` are
derived by the index generator. Authoring both directions guarantees drift.

### Example — Registration Contract

```yaml
---
id: repo:payments/auth/registration
title: Registration Rules
level: repo
kind: contract
domains:
  - auth
  - users
flows:
  - registration
keywords:
  - registration
  - signup
  - verification
  - account creation
references:
  - repo:payments/auth/verification
  - repo:payments/users/lifecycle
affects:
  - repo:notifications/email-verification
implements:
  - flow:registration
code_paths:
  - packages/auth/src/registration/**
  - packages/users/src/registration/**
test_paths:
  - packages/auth/test/registration/**
---
```
