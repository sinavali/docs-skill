---
name: read
purpose: Load only the sections needed for the current task.
modifies_files: false
requires_access: read
---

# Mode — `read`

**Purpose:** Load only the sections needed for the current task. Build a path index once, then load section contents on demand.

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
4. **Walk upward.** If `org_root` is declared and reachable, read that `AGENT.md` and its `docs/INDEX.md`. If unreachable, apply the fallback from `rules/precedence.md` (see also `AGENT.md` frontmatter):
   - `notify` — notify the caller, continue with local docs.
   - `proceed` — continue with local docs, log an NC item.
   - `stop` — halt and return control to the caller.
5. **Follow the upward reading order** declared in each `AGENT.md` read so far.
6. **Build the path index.** Use `modes/index.md` semantics: list every `INDEX.md`, every section filename with its one-line purpose, every `AGENT.md`, and every sibling `<filename>.md` (file-level doc). Do not load contents.
7. **Determine which docs the task requires.** Use the task string, the doc maps from each `AGENT.md`, and the one-line purposes in the path index.
8. **Load only those section contents.** For each required doc:
   - If it is a sectioned doc, load only the section files the task requires, not the whole tree.
   - If it is a file-level doc, load the sibling `<filename>.md` before the source file.
9. **Check for missing required docs.** If a required doc does not exist, create an NC item per `rules/nc.md` and `templates/nc-item.md`. Do not invent.
10. **Check for conflicts.** If two docs cover the same case with different rules, apply `rules/precedence.md`.
    - If precedence resolves it, follow the higher-authority doc and note the conflict in the summary.
    - If precedence does not resolve it (same-level conflict), stop the task, create an NC item naming both docs, and return control to the caller.
11. **Return the outputs.**

---

## Rules

- **MUST NOT** load excluded paths.
- **MUST NOT** load `README.md` as intent. It MAY be read for human context only, and only if the task explicitly requires human context.
- **MUST NOT** load full doc trees unless the task explicitly requires them.
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
   - `/docs/004-contracts/004-001-refund-api.md`
   - `src/refunds/refund.ts.md`
   - …
5. Task-relevant docs loaded:
   - `002-004-invariants.md`
   - `004-001-refund-api.md`
   - `refund.ts.md`
6. `reason` optionality not stated in the contract → NC item created, promotion target `docs/004-contracts/004-001-refund-api.md`.
7. Return: loaded sections, skipped-but-relevant list, NC item ID.