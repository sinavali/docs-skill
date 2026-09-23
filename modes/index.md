---
name: index
purpose: Build a path-only index of docs.
modifies_files: false
requires_access: read
---

# Mode — `index`

**Purpose:** Build a path-only index of docs within a scope. Contents are not loaded.

**Inputs:**
- `anchor_path` — the directory where indexing begins.
- `depth` — optional. Defaults to 2 levels below the anchor.
- `max_entries` — optional. Defaults to 500.

**Outputs:**
- A structured list of:
  - every `AGENT.md` in scope,
  - every `INDEX.md` in scope,
  - every section filename with its one-line purpose (from the parent `INDEX.md`),
  - every sibling `<filename>.md` (file-level doc) in scope,
  - every doc ID discovered, derived per `rules/numbering.md`.

**References:**
- `rules/frontmatter.md`
- `rules/numbering.md`
- `rules/file-level.md`
- `rules/excluded-paths.md`

---

## Steps

1. **Find nearest `AGENT.md`** from `anchor_path`. If none, treat repo root as anchor and log an NC item.
2. **Read the anchor `AGENT.md` frontmatter.** Respect `excluded_paths` and `included_paths`.
3. **Recurse** the anchor's subtree up to `depth` levels (default 2).
4. **Collect:**
   - All `AGENT.md` files.
   - All `INDEX.md` files, reading only their frontmatter and their section tables.
   - All filenames in directories that contain an `INDEX.md`, taking the one-line purpose from the index table.
   - All sibling `<filename>.md` files next to source files (file-level docs).
5. **Stop and report** if either the depth or the `max_entries` cap is reached before completion.

---

## Output Shape

```text
scope: <anchor id>
depth: <effective depth>
entries: <count> / <max_entries>

AGENTS
  - path: <path>
    id: <id>
    scope: <scope>

INDICES
  - path: <path>
    id: <id>
    sections: <count>

SECTIONS
  - path: <path>
    id: <id>
    parent: <index id>
    purpose: <one-line>

FILE_LEVEL
  - path: <path>
    id: <id>
    file: <source path>

TRUNCATED: <yes | no>
REASON: <if truncated>
```

---

## Rules

- **MUST NOT** load section contents. Only frontmatter and index tables.
- **MUST** respect the `max_entries` cap. If exceeded, stop and create an NC item requesting guidance.
- **MUST** respect the `depth` limit. Deeper trees are not indexed without an explicit caller instruction.
- **MUST NOT** index excluded paths.
- **MUST NOT** write anything to disk.

---

## Example

Anchor: `payments-api/`. Depth: 2. Max entries: 500.

Result:

```text
scope: repo:payments-api
depth: 2
entries: 47 / 500

AGENTS
  - path: payments-api/AGENT.md
    id: repo:payments-api/agent
    scope: payments/api

INDICES
  - path: payments-api/docs/INDEX.md
    id: repo:payments-api
    sections: 6
  - path: payments-api/docs/002-blueprint/INDEX.md
    id: repo:payments-api/blueprint
    sections: 5

SECTIONS
  - path: payments-api/docs/002-blueprint/002-001-overview.md
    id: repo:payments-api/blueprint/overview
    parent: repo:payments-api/blueprint
    purpose: What Payments API is
  ...

FILE_LEVEL
  - path: payments-api/src/refunds/refund.ts.md
    id: file:payments-api/refunds/refund
    file: refund.ts

TRUNCATED: no
REASON: —
```