---
name: repair
purpose: Fix an existing docs tree losslessly.
modifies_files: true
requires_access: write, org-level
---

# Mode — `repair`

**Purpose:** Bring an existing docs tree into the canonical structure without losing semantic content, including recursively sectioning any unit that exceeds the threshold.

**Inputs:**
- `root_path` — the directory to repair.

**Outputs:**
- Reconciled docs tree.
- Ephemeral diff report listing moves, renames, sectioning operations, and NC items created.

**References:**
- `rules/frontmatter.md`
- `rules/precedence.md`
- `rules/numbering.md`
- `rules/sectioning.md`
- `rules/nc.md`
- `rules/file-level.md`
- `rules/excluded-paths.md`
- `rules/relationships.md`
- `rules/impact.md`
- `rules/index-format.md`
- `rules/graph.md`
- `templates/agent.md`
- `templates/index.md`
- `templates/index-global.md`
- `templates/section.md`
- `templates/flow.md`
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
   - Every loadable unit is under the threshold per `rules/sectioning.md`?
   - Every doc carries the impact metadata per `rules/frontmatter.md` (`domains`, `flows`, `keywords`, and `code_paths` / `test_paths` where it governs code)?
   - Every edge (`references`, `affects`, `implements`, `depends_on`) resolves to an existing ID?
   - No doc authors a reverse edge (`affected_by`, `referenced_by`, `implemented_by`)?
   - Every doc carries the impact metadata per `rules/frontmatter.md` (`domains`, `flows`, `keywords`, and `code_paths` / `test_paths` where it governs code)?
   - Every edge (`references`, `affects`, `implements`, `depends_on`) resolves to an existing ID?
   - No doc authors a reverse edge (`affected_by`, `referenced_by`, `implemented_by`)?
4. **Create missing `INDEX.md` files.** For a directory with content but no `INDEX.md`, generate one from `templates/index.md` and list its sections.
5. **Move content into canonical locations.** Move unclassified docs into the correct type directory. Rename to canonical numbering. Never delete content.
6. **Rename files** to canonical naming per `rules/numbering.md`. Update references.
7. **Update cross-references** to use doc IDs instead of paths.
8. **Section recursively.** Walk the tree from the shallowest level down. For every loadable unit that crosses the threshold:
   - Apply the conversion procedure in `rules/sectioning.md`.
   - After conversion, recurse on each newly created section file.
   - Continue until every loadable unit is under the threshold.
   - Preserve doc IDs across conversions.
   - Preserve semantic order.
   - Do not slice by byte count; split at concern boundaries.
9. **Merge undersized siblings.** For any pair of sibling sections that are both under ~20 lines and share a concern, apply the merge procedure in `rules/sectioning.md`. Do not merge across concerns.
10. **Add `AGENT.md`** at each anchor boundary. If an anchor boundary is unclear, create an NC item and leave the tree unrepaired for that subtree.
11. **Add `NEED_CLEARIFICATION` items** for anything unresolved:
    - content that could not be classified,
    - anchors whose boundary is ambiguous,
    - docs whose frontmatter could not be inferred,
    - sections where a semantic split could not be determined without inventing intent.
12. **Emit an ephemeral diff report.** Never store the report.
13. **Return:** the reconciled tree path, the diff report, and the branch name (if any).

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

SECTIONED
  - <file>: became directory <dir> with <n> sections
  ...

MERGED
  - <file A> + <file B>: <merged file>
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
  sectioned: <n>
  merged: <n>
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
- **MUST** section recursively per `rules/sectioning.md`. No loadable unit may remain above the hard threshold.
- **MUST** section semantically, not by byte count or heading depth.
- **MUST** preserve doc IDs where the doc's scope is unchanged. A conversion does not change the doc's ID.
- **MUST** create `NEED_CLEARIFICATION.md` items for anything unresolved rather than guessing.

---

## Example

Input: a repo with `docs.md` at root, a `wiki/` folder, an oversized `wiki/architecture.md`, and no `/docs/` tree.

Steps:

1. Branch `docs/repair-2026-09-23`.
2. Inventory: `docs.md`, `wiki/architecture.md` (480 lines), `wiki/decisions/use-postgres.md`, `README.md`, `AGENT.md` (missing).
3. Create `/docs/` tree.
4. Move `docs.md` → `docs/002-blueprint/002-001-overview.md`.
5. Move `wiki/architecture.md` → `docs/002-blueprint/002-005-architecture.md`.
6. Move `wiki/decisions/use-postgres.md` → `docs/003-decisions/003-001-use-postgres.md`.
7. Section the oversized `002-005-architecture.md` (480 lines, above hard threshold) into:
   - `docs/002-blueprint/002-005-architecture/INDEX.md`
   - `docs/002-blueprint/002-005-architecture/002-005-001-overview.md`
   - `docs/002-blueprint/002-005-architecture/002-005-010-layers.md`
   - `docs/002-blueprint/002-005-architecture/002-005-020-data-flow.md`
   - `docs/002-blueprint/002-005-architecture/002-005-030-deployment.md`
8. Recurse on each new section. `002-005-010-layers.md` is still 340 lines, above hard threshold, so it becomes:
   - `docs/002-blueprint/002-005-architecture/002-005-010-layers/INDEX.md`
   - `docs/002-blueprint/002-005-architecture/002-005-010-layers/002-005-010-001-domain.md`
   - `docs/002-blueprint/002-005-architecture/002-005-010-layers/002-005-010-010-adapters.md`
   - `docs/002-blueprint/002-005-architecture/002-005-010-layers/002-005-010-020-ui.md`
9. Create `/docs/INDEX.md`, `/docs/002-blueprint/INDEX.md`, `/docs/003-decisions/INDEX.md`.
10. Create `AGENT.md` at repo root from `templates/agent.md`.
11. Emit diff report listing sectioned units and the recursion depth.
12. Return.