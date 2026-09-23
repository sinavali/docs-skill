---
name: extend
purpose: Add a doc or section on demand.
modifies_files: true
requires_access: write
---

# Mode — `extend`

**Purpose:** Add a doc or section to an existing docs tree, using canonical numbering, updating the parent `INDEX.md`, and recursively sectioning any unit that crosses the threshold.

**Inputs:**
- `anchor_path` — the directory where the addition lands.
- `target` — the target type directory or parent doc.
- `kind` — one of `section`, `decision`, `contract`, `cross-cutting`, `runbook`, `index`, `agent`.
- `spec` — the content spec for the new file(s).

**Outputs:**
- New file(s) created from `templates/*.md`.
- Updated parent `INDEX.md`.
- Any recursive sectioning performed on the new file or on any affected ancestor.
- If a single-file doc is being converted to a sectioned doc, the conversion is performed per `rules/sectioning.md`.

**References:**
- `rules/frontmatter.md`
- `rules/numbering.md`
- `rules/sectioning.md`
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
   - If `target` is a section file inside a sectioned doc, the new file is a sibling of that section.
   - If `target` is a single-file doc that would grow beyond the threshold after the addition, convert it first per `rules/sectioning.md`.
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
7. **Check size against the threshold.** Apply `rules/sectioning.md`.
   - Compute the line and word count of every file written or modified in this run.
   - For each file that crosses the **soft** threshold, consider sectioning.
   - For each file that crosses the **hard** threshold, section it.
   - This check applies to the newly created file, to the parent `INDEX.md`, and to any ancestor `INDEX.md` that gained a row.
8. **Section recursively.** For each file that must be sectioned:
   - Apply the conversion procedure in `rules/sectioning.md`.
   - If a newly created section file also crosses the threshold, repeat.
   - Continue until every loadable unit is under the threshold.
9. **If any cross-reference in the tree targeted an ID that moved** (only possible when a section is converted or merged), update it.
10. **Return:** created file paths, sectioned file paths, updated `INDEX.md` paths, any NC items created.

---

## Sectioning at Every Depth

`extend` is the mode where sectioning happens. It MUST be:

- **Recursive.** A section file that crosses the threshold becomes a directory with its own `INDEX.md` and its own section files. The same operation applies at every depth.
- **Semantic.** Split at concern boundaries: a topic change, a distinct contract, a distinct procedure, a distinct invariant set. Do not split every N lines. Do not split every heading. Do not split to hit a byte count.
- **Lossless.** The union of the section files equals the original content. No content is dropped.
- **ID-stable.** A section's doc ID does not change when it is sectioned. Only content moves.
- **Practical.** A section that is too small (< ~20 lines) and shares a concern with a sibling SHOULD be merged instead of kept separate.

See `rules/sectioning.md` for the full doctrine, including the conversion procedure, the merge procedure, and the definition of the threshold.

---

## Conversion from Single-File to Sectioned

When a single-file doc crosses the threshold, apply the conversion procedure in `rules/sectioning.md`. The short form:

1. Create a directory with the same base name as the file, minus the `.md`.
2. Move the file's content into a new `INDEX.md`, retaining frontmatter.
3. Split the content into section files, one per semantic unit.
4. Update the new `INDEX.md`'s section table.
5. Update the parent `INDEX.md` to point to the directory instead of the file.
6. Update any doc that referenced a child section by ID.
7. Recurse on any new section file that also crosses the threshold.

---

## Rules

- **MUST** use the numbering scheme from `rules/numbering.md`.
- **MUST** update the parent `INDEX.md`.
- **MUST** apply `rules/sectioning.md` after every write. No loadable unit may remain above the hard threshold.
- **MUST** section recursively. A section file is not exempt from sectioning.
- **MUST** section semantically, not by byte count or heading depth.
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

1. Target is a single-file doc; extension would push it beyond the soft threshold.
2. Convert `004-001-refund-api.md` into `004-001-refund-api/INDEX.md` plus section files.
3. New section: `004-001-refund-api/004-001-010-reason-field.md`.
4. Fill frontmatter from `templates/section.md`.
5. Update `004-001-refund-api/INDEX.md` and `docs/004-contracts/INDEX.md`.
6. Check sizes. `004-001-refund-api/INDEX.md` is short. `004-001-010-reason-field.md` is short. No further sectioning needed.
7. Return: created paths, updated index paths.

Second example — the recursive case:

1. A new section `005-003-vcs-specifics/005-003-002-label-taxonomy.md` is added.
2. Its content grows past the hard threshold because the label list is large.
3. `rules/sectioning.md` requires it to be sectioned.
4. Convert `005-003-002-label-taxonomy.md` into `005-003-002-label-taxonomy/INDEX.md` plus section files:
   - `005-003-002-label-taxonomy/005-003-002-001-issue-labels.md`
   - `005-003-002-label-taxonomy/005-003-002-010-pr-labels.md`
   - `005-003-002-label-taxonomy/005-003-002-020-label-rules.md`
5. Update `005-003-vcs-specifics/INDEX.md` to point to the directory.
6. Update `005-003-vcs-specifics/INDEX.md`'s own size check. It is short; no further sectioning.
7. Recurse on each new section file. If any crosses the threshold, repeat.
8. Return.