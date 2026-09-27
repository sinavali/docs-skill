---
name: index
purpose: Discover documentation topology, metadata, and relationships. Produce a compact semantic index, not a content dump.
modifies_files: false
requires_access: read
---

# Mode — `index`

**Purpose:** Discover the documentation graph — topology, metadata, and typed
relationships — and produce a compact semantic index. Contents are not loaded.

This is **not** a path listing. A path listing answers "which files exist?". The
semantic index answers "which documents are relevant to X, and how are they
connected?".

**Inputs:**
- `anchor_path` — the directory where indexing begins.
- `depth` — optional. Defaults to **unbounded** for metadata discovery. Metadata is
  cheap; content is not. There is no default depth cap on the metadata pass.
- `max_entries` — optional. Defaults to 2000. Applies to metadata entries, not to
  filesystem paths.

**Outputs:**
- A compact semantic index of every doc discovered:
  - `id`, `title`, `kind`, `level`,
  - `domains`, `flows`, `keywords`,
  - `references`, `affects`, `implements`, `depends_on`,
  - `code_paths`, `test_paths`.
- The set of flows and domains discovered.
- The set of edges discovered.

**References:**
- `rules/frontmatter.md`
- `rules/relationships.md`
- `rules/index-format.md`
- `rules/numbering.md`
- `rules/file-level.md`
- `rules/excluded-paths.md`

---

## Steps

1. **Find nearest `AGENT.md`** from `anchor_path`. If none, treat repo root as
   anchor and log an NC item.
2. **Read the anchor `AGENT.md` frontmatter.** Respect `excluded_paths` and
   `included_paths`.
3. **Discover topology.** Recurse the anchor's subtree. Unlike a path index, the
   metadata pass is **not** capped at depth 2. Metadata is cheap. Discover every
   doc, every `INDEX.md`, every `AGENT.md`, and every file-level `<filename>.md`.
4. **Discover metadata.** For each doc, read **only its frontmatter**. Extract the
   fields listed in Outputs. Do not read bodies.
5. **Discover relationships.** Build the edge set from the frontmatter:
   - `references`, `affects`, `implements`, `depends_on` edges as authored,
   - `code_paths` and `test_paths` as code bridges.
6. **Derive reverse edges.** Compute `referenced_by`, `affected_by`,
   `implemented_by`. Do **not** read them from disk; they are never authored.
7. **Produce the compact semantic index.** One record per doc. No content.
8. **Stop and report** if `max_entries` is reached before completion.

---

## Output Shape

```text
scope: <anchor id>
entries: <count> / <max_entries>

DOMAINS
  - <domain>

FLOWS
  - <flow>

DOCS
  - id: <id>
    path: <path>
    domains: [<domain>, ...]
    flows: [<flow>, ...]
    keywords: [<keyword>, ...]
    references: [<id>, ...]
    affects: [<id>, ...]
    implements: [<flow>, ...]
    code_paths: [<glob>, ...]
    test_paths: [<glob>, ...]

EDGES
  - <from> -> <to>  (<references|affects|implements|depends_on>)

TRUNCATED: <yes | no>
REASON: <if truncated>
```

---

## Rules

- **MUST NOT** load document bodies. Frontmatter and index tables only.
- **MUST NOT** cap the metadata pass at depth 2. Depth is a *content* concern, not a
  *metadata* concern. Breadth of metadata, narrowness of content.
- **MUST** derive reverse edges; **MUST NOT** read or author them.
- **MUST** respect `max_entries`. If exceeded, stop and create an NC item.
- **MUST NOT** index excluded paths.
- **MUST NOT** write anything to disk.

---

## Example

Anchor: `payments-api/`. Unbounded metadata depth. Max entries: 2000.

Result:

```text
scope: repo:payments-api
entries: 47 / 2000

DOMAINS
  - auth
  - users
  - notifications

FLOWS
  - registration
  - login

DOCS
  - id: auth/registration
    path: docs/002-blueprint/002-004-registration.md
    domains: [auth, users]
    flows: [registration]
    keywords: [registration, signup, account creation]
    references: [auth/verification, users/lifecycle]
    affects: [notifications/email-verification]
    implements: [registration]
    code_paths: [packages/auth/src/registration/**]
    test_paths: [packages/auth/test/registration/**]
  ...

EDGES
  - auth/registration -> auth/verification  (references)
  - auth/registration -> notifications/email-verification  (affects)
  - auth/registration -> registration  (implements)

TRUNCATED: no
REASON: —
```

### Anti-Pattern — Do Not Do This

```text
# WRONG: simply increasing depth from 2 to 10
index --depth 10
```

That only moves the problem. The correct change is:

> make metadata discovery **broad**, keep content loading **narrow**.