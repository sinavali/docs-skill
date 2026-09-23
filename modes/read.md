---
name: read
purpose: Load only the sections needed for the current task.
modifies_files: false
requires_access: read
---

# Mode — `read`

**Purpose:** Load only the sections needed for the current task. Build a path index once, then load section contents on demand, at the exact depth the task requires.

**Inputs:**
- `anchor_path` — the directory where work begins.
- `task` — a one-line description of the current task.

**Outputs:**
- `loaded_sections` — list of section file paths whose contents were loaded.
- `skipped_but_relevant` — list of doc paths that were indexed but not loaded.
- `nc_items_created` — list of NC item IDs created, if any.

**References:**
- `rules/frontmatter.md`
- `rules/precedence.md`
- `rules/sectioning.md`
- `rules/nc.md`
- `rules/file-level.md`
- `rules/excluded-paths.md`
- `templates/nc-item.md`

---

## Steps

1. **Find nearest `AGENT.md`.** Walk upward from `anchor_path` until an `AGENT.md` is found. That directory is the **anchor**.
2. **If no `AGENT.md` is found:**
   - Treat the current repo root as org-root.
   - Create an NC item per `rules/nc.md`: *"No `AGENT.md` found from `<anchor_path>` upward. Treating repo root as org-root."*
3. **Read the anchor `AGENT.md` frontmatter.** Extract:
   - `org_root`, `requires_org_docs`, `org_docs_fallback`,
   - `excluded_paths`, `included_paths`,
   - `skill`.
4. **Walk upward.** If `org_root` is declared and reachable, read that `AGENT.md` and its `docs/INDEX.md`. If unreachable, apply the fallback from `rules/precedence.md`:
   - `notify` — notify the caller, continue with local docs.
   - `proceed` — continue with local docs, log an NC item.
   - `stop` — halt and return control to the caller.
5. **Follow the upward reading order** declared in each `AGENT.md` read so far.
6. **Build the path index.** Use `modes/index.md` semantics: list every `INDEX.md`, every section filename with its one-line purpose, every `AGENT.md`, and every sibling `<filename>.md` (file-level doc). Do not load contents.
7. **Determine which docs the task requires.** Use the task string, the doc maps from each `AGENT.md`, and the one-line purposes in the path index.
8. **Descend only to the required depth.** Sectioned docs are trees. Load only the nodes the task requires.
   - Load each required `INDEX.md` to see what sections it lists.
   - For each section listed, decide whether the task requires its contents or only its existence.
   - Load a section's contents only when the task depends on them.
   - Never load a whole subtree when a single leaf will do.
   - This rule applies at every depth: a section that is itself sectioned is descended into the same way.
9. **For file-level docs,** load the sibling `<filename>.md` before the source file.
10. **Check for missing required docs.** If a required doc does not exist, create an NC item per `rules/nc.md` and `templates/nc-item.md`. Do not invent.
11. **Check for conflicts.** If two docs cover the same case with different rules, apply `rules/precedence.md`.
    - If precedence resolves it, follow the higher-authority doc and note the conflict in the summary.
    - If precedence does not resolve it (same-level conflict), stop the task, create an NC item naming both docs, and return control to the caller.
12. **Return the outputs.**

---

## Rules

- **MUST NOT** load excluded paths.
- **MUST NOT** load `README.md` as intent. It MAY be read for human context only, and only if the task explicitly requires human context.
- **MUST NOT** load full doc trees unless the task explicitly requires them.
- **MUST** descend sectioned docs only to the depth the task requires.
- **MUST** prefer sectioned docs over monolithic docs when both exist for the same subject.
- **MUST** apply precedence on conflict rather than picking silently.
- **MUST** respect open NC items as provisional intent, subordinate to active docs.
- **MUST NOT** write anything to disk in `read` mode except a `NEED_CLEARIFICATION.md` item when a required doc is missing or ambiguous.

---

## Example

Task: *"Add a `reason` field to the refund endpoint."*

1. Nearest `AGENT.md`: `payments-api/AGENT.md`.
2. `org_root: ../../org-root` declared and reachable.
3. Upward order from the anchor is read.
4. Path index built:
   - `/docs/INDEX.md`
   - `/docs/002-blueprint/INDEX.md`
   - `/docs/002-blueprint/002-001-overview.md`
   - `/docs/002-blueprint/002-004-invariants.md`
   - `/docs/004-contracts/004-001-refund-api/INDEX.md`
   - `/docs/004-contracts/004-001-refund-api/004-001-001-endpoints.md`
   - `/docs/004-contracts/004-001-refund-api/004-001-010-reason-field.md`
   - `/docs/004-contracts/004-001-refund-api/004-001-020-schemas.md`
   - `src/refunds/refund.ts.md`
   - …
5. Task-relevant nodes loaded:
   - `/docs/002-blueprint/002-004-invariants.md` (whole, small).
   - `/docs/004-contracts/004-001-refund-api/INDEX.md` (to see section list).
   - `/docs/004-contracts/004-001-refund-api/004-001-010-reason-field.md` (the exact section the task touches).
   - `/docs/004-contracts/004-001-refund-api/004-001-020-schemas.md` (only because `reason` appears in the schema).
   - `src/refunds/refund.ts.md` (whole, small).
6. `/docs/004-contracts/004-001-refund-api/004-001-001-endpoints.md` is listed in `skipped_but_relevant`. It was indexed but not loaded because the task does not touch endpoints.
7. If `004-001-010-reason-field.md` itself were large enough to be sectioned, the same descent would apply one level deeper.
8. `reason` optionality not stated in the contract → NC item created, promotion target `docs/004-contracts/004-001-refund-api.md`.
9. Return: loaded sections, skipped-but-relevant list, NC item ID.