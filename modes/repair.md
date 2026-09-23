---
name: repair
purpose: Fix an existing docs tree losslessly.
modifies_files: true
requires_access: write, org-level
---

# Mode — `repair`

**Purpose:** Bring an existing docs tree into the canonical structure without losing semantic content.

**Inputs:**
- `root_path` — the directory to repair.

**Outputs:**
- Reconciled docs tree.
- Ephemeral diff report listing moves, renames, and NC items created.

**References:**
- `rules/frontmatter.md`
- `rules/precedence.md`
- `rules/numbering.md`
- `rules/nc.md`
- `rules/file-level.md`
- `rules/excluded-paths.md`
- `templates/agent.md`
- `templates/index.md`
- `templates/section.md`
- `templates/nc-item.md`

---

## Steps

1. **Branch check.**
   - If a VCS is present, create a branch named `docs/repair-YYYY-MM-DD`. If the caller's VCS does not support branches, proceed on the current branch only with explicit caller opt-in.
   - If no VCS is present, require explicit caller opt-in before any write.
2. **Inventory.** Walk `root_path`, respecting `excluded_paths`. Classify every `.md` file as one of:
   - a root file (`README.md`, `AGENT.md`, `NEED_CLEARIFICATION.md`),
   - a doc under `/docs/`,
   - a file-level doc (`<filename>.md` next to a source file),
   - unclassified.
3. **Compare** the inventory to the canonical structure:
   - `/docs/INDEX.md` exists?
   - Each type directory has an `INDEX.md`?
   - Numbering follows `rules/numbering.md`?
   - Every section file is listed in its parent `INDEX.md`?
   - Frontmatter follows `rules/frontmatter.md`?
   - `AGENT.md` exists at each anchor boundary?
4. **Create missing `INDEX.md` files.** For a directory with content but no `INDEX.md`, generate one from `templates/index.md` and list its sections.
5. **Move content into canonical locations.** Move unclassified docs into the correct type directory. Rename to canonical numbering. Never delete content.
6. **Rename files** to canonical naming per `rules/numbering.md`. Update references.
7. **Update cross-references** to use doc IDs instead of paths.
8. **Add `AGENT.md`** at each anchor boundary. If an anchor boundary is unclear, create an NC item and leave the tree unrepaired for that subtree.
9. **Add `NEED_CLEARIFICATION` items** for anything unresolved:
   - content that could not be classified,
   - anchors whose boundary is ambiguous,
   - docs whose frontmatter could not be inferred.
10. **Emit an ephemeral diff report.** Never store the report.
11. **Return:** the reconciled tree path, the diff report, and the branch name (if any).

---

## Diff Report Shape

```text
scope: <root id>
date: <date>
branch: <branch or "(no VCS)">

MOVED
  - <from>: <to>
  ...

RENAMED
  - <from>: <to>
  ...

CREATED
  - <path>
  ...

NC_ITEMS
  - <id>: <summary>
  ...

UNRESOLVED
  - <path>: <reason>
  ...

SUMMARY
  moved: <n>
  renamed: <n>
  created: <n>
  nc_items: <n>
  unresolved: <n>
```

---

## Rules

- **MUST** be lossless. No semantic content is removed without an NC item.
- **MUST** run on a separate branch if a VCS is present.
- **MUST NOT** run without explicit opt-in if no VCS is present.
- **MUST NOT** delete content. Move it or NC it.
- **MUST NOT** edit `README.md`.
- **MUST NOT** write into excluded paths.
- **MUST** create `NEED_CLEARIFICATION.md` items for anything unresolved rather than guessing.
- **MUST** preserve existing doc IDs where the doc's scope is unchanged.

---

## Example

Input: a repo with `docs.md` at root, a `wiki/` folder, and no `/docs/` tree.

Steps:

1. Branch `docs/repair-2026-09-23`.
2. Inventory: `docs.md`, `wiki/architecture.md`, `wiki/decisions/use-postgres.md`, `README.md`, `AGENT.md` (missing).
3. Create `/docs/` tree.
4. Move `docs.md` → `docs/002-blueprint/002-001-overview.md`.
5. Move `wiki/architecture.md` → `docs/002-blueprint/002-005-architecture.md`.
6. Move `wiki/decisions/use-postgres.md` → `docs/003-decisions/003-001-use-postgres.md`.
7. Create `/docs/INDEX.md`, `/docs/002-blueprint/INDEX.md`, `/docs/003-decisions/INDEX.md`.
8. Create `AGENT.md` at repo root from `templates/agent.md`.
9. Emit diff report.
10. Return.