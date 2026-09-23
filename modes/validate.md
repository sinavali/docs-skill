---
name: validate
purpose: Check integrity of a docs tree. Report only.
modifies_files: false
requires_access: read
---

# Mode — `validate`

**Purpose:** Check the integrity of a docs tree. Produce an ephemeral report. Never modify anything.

**Inputs:**
- `anchor_path` — the directory where validation begins.

**Outputs:**
- An ephemeral report covering:
  - missing `INDEX.md` in doc directories,
  - missing `AGENT.md` ancestors,
  - broken doc-ID references,
  - orphan docs (not listed in any `INDEX.md`),
  - unresolved NC items,
  - precedence violations,
  - frontmatter contract violations,
  - numbering violations,
  - excluded-path leaks.

**References:**
- `rules/frontmatter.md`
- `rules/precedence.md`
- `rules/numbering.md`
- `rules/nc.md`
- `rules/file-level.md`
- `rules/excluded-paths.md`

---

## Steps

1. **Resolve the anchor** via `modes/index.md` semantics.
2. **Recurse** the tree, respecting `excluded_paths`.
3. **For each doc, check:**
   - **Frontmatter.** Required fields present per `rules/frontmatter.md`. `id` unique within scope. `parent` resolves.
   - **Index membership.** Every section file is listed in its parent `INDEX.md`. Every `INDEX.md` is reachable from a higher `INDEX.md` (up to org-root).
   - **References.** Every `references` entry resolves to an existing doc ID.
   - **Numbering.** Filenames follow `rules/numbering.md`. No sibling collisions.
   - **Placement.** No doc sits outside `/docs/` except the three root files (`README.md`, `AGENT.md`, `NEED_CLEARIFICATION.md`) and file-level `<filename>.md` siblings.
4. **For each `AGENT.md`, check:**
   - Frontmatter per `rules/frontmatter.md`.
   - Upward reading order present.
   - Doc map present.
   - Index protocol stated.
   - File-level-doc rule stated.
   - Excluded paths declared.
5. **For each `NEED_CLEARIFICATION.md`, check:**
   - Item schema per `rules/nc.md`.
   - Item IDs unique within the file.
   - Promotion targets exist as doc paths.
6. **Conflict detection.** For each pair of docs that appear to cover the same case, compare their rules. Report any same-level conflicts and any lower-authority docs that contradict higher-authority docs.
7. **Emit the report.** The report is ephemeral; it is returned to the caller and never written to disk.

---

## Report Shape

```text
scope: <anchor id>
validated: <date>

ERRORS
  - <severity>: <location>: <message>
  ...

WARNINGS
  - <location>: <message>
  ...

NC_UNRESOLVED
  - <id>: <summary>
  ...

CONFLICTS
  - <doc A> vs <doc B>: <nature>
  ...

SUMMARY
  errors: <n>
  warnings: <n>
  unresolved NC items: <n>
  conflicts: <n>
```

---

## Rules

- **MUST NOT** modify any file.
- **MUST NOT** create files. If validation fails, the caller decides whether to open an NC item.
- **MUST** treat the report as ephemeral. Never persist it as a doc.
- **MUST** respect `excluded_paths`.
- **MUST NOT** attempt to repair drift. Validation reports; repair is a separate mode.

---

## Example

```text
scope: repo:payments-api
validated: 2026-09-23

ERRORS
  - error: docs/004-contracts/004-001-refund-api.md: frontmatter missing field `level`
  - error: docs/005-cross-cutting/INDEX.md: references doc ID `cross-cutting/vcs` which does not exist

WARNINGS
  - docs/003-decisions/003-002-use-webhooks.md: not listed in docs/003-decisions/INDEX.md
  - src/refunds/refund.ts: sibling `refund.ts.md` exists but `AGENT.md` does not instruct agents to check it (rule present, but Directory map lacks it)

NC_UNRESOLVED
  - NC-0007: Refund reason optionality
  - NC-0008: Idempotency window

CONFLICTS
  - repo:payments-api/blueprint/invariants vs repo:payments-api/blueprint/architecture: retry count disagrees (3 vs 5)

SUMMARY
  errors: 2
  warnings: 2
  unresolved NC items: 2
  conflicts: 1
```