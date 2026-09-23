---
name: extend
purpose: Add a doc or section on demand.
modifies_files: true
requires_access: write
---

# Mode — `extend`

**Purpose:** Add a doc or section to an existing docs tree, using canonical numbering and updating the parent `INDEX.md`.

**Inputs:**
- `anchor_path` — the directory where the addition lands.
- `target` — the target type directory or parent doc.
- `kind` — one of `section`, `decision`, `contract`, `cross-cutting`, `runbook`, `index`, `agent`.
- `spec` — the content spec for the new file(s).

**Outputs:**
- New file(s) created from `templates/*.md`.
- Updated parent `INDEX.md`.
- If a single-file doc is being converted to a sectioned doc, the conversion is performed per the guideline's conversion rule.

**References:**
- `rules/frontmatter.md`
- `rules/numbering.md`
- `rules/nc.md`
- `rules/excluded-paths.md`
- `templates/section.md`
- `templates/decision.md`
- `templates/contract.md`
- `templates/cross-cutting.md`
- `templates/runbook.md`
- `templates/index.md`
- `templates/agent.md`

---

## Steps

1. **Resolve the target directory.**
   - If `target` is a type directory (e.g., `docs/003-decisions/`), the new file is a sibling section.
   - If `target` is a single-file doc that is being extended beyond one screen, convert it first per the conversion rule below.
2. **Compute the next available ID** using `rules/numbering.md`:
   - Use 3-digit numbering.
   - Use gaps of 10 between siblings (001, 010, 020, …; or 001, 002, 003 with no gap if the tree is small and stable — but prefer gaps).
   - Never renumber siblings.
3. **Choose the template** from `templates/` matching `kind`.
4. **Fill the frontmatter** per `rules/frontmatter.md`. Include at minimum:
   - `id`, `title`, `level`, `kind`.
   - `parent` when the new file is a section.
   - `date` and `deciders` for decisions.
   - `parties` for contracts.
   - `applies_to` for cross-cutting docs.
5. **Write the file(s)** using the template's shape verbatim except for content substitution.
6. **Update the parent `INDEX.md`** to list the new section(s) in the intended order.
   - If the parent `INDEX.md` does not exist, create it from `templates/index.md` and add all siblings, not just the new one.
7. **If any cross-reference in the tree targeted the old file ID** (in the case of a conversion), update it.
8. **Return:** created file paths, updated `INDEX.md` path, any NC items created.

---

## Conversion from Single-File to Sectioned

When a single-file doc crosses the one-screen threshold:

1. Create a directory with the same base ID as the file, minus the `.md`.
2. Move the file's content into a new `INDEX.md` in that directory, retaining frontmatter.
3. Split the content into section files in the same directory, one per top-level heading, using `templates/section.md`.
4. Update the new `INDEX.md`'s section table to list each section file.
5. Update the parent `INDEX.md` to point to the directory instead of the file.
6. Update any doc that referenced the old file ID.

---

## Rules

- **MUST** use the numbering scheme from `rules/numbering.md`.
- **MUST** update the parent `INDEX.md`.
- **MUST NOT** write into excluded paths.
- **MUST NOT** edit `README.md`.
- **MUST NOT** edit a higher-authority doc without an NC item.
- **MUST NOT** overwrite an existing file. If a collision is detected, stop and create an NC item.
- **MUST** reference doc IDs, not paths, in any cross-links the new content includes.

---

## Example

Task: *"Add a `reason` field to the refund contract."*

Inputs:
- `anchor_path`: `payments-api/`
- `target`: `docs/004-contracts/004-001-refund-api.md`
- `kind`: `section`
- `spec`: describes the new `reason` field.

Steps:

1. Target is a single-file doc; extension would push it beyond one screen.
2. Convert `004-001-refund-api.md` into `004-001-refund-api/INDEX.md` plus section files.
3. New section: `004-001-refund-api/004-001-010-reason-field.md`. (Next gap of 10 after `004-001-001`… `004-001-009`.)
4. Fill frontmatter from `templates/section.md`.
5. Update `004-001-refund-api/INDEX.md` and `docs/004-contracts/INDEX.md`.
6. Return: created paths, updated index paths.