---
name: sectioning
purpose: Doctrine for sectioning docs — purpose, threshold, recursion, practical boundaries, depth.
---

# Rule — Sectioning

## Purpose

Sectioning exists for one reason: **reduce the amount of content loaded into a single context window, without losing any content**. A sectioned doc is a directory whose `INDEX.md` is small enough to load whole, and whose section files are each small enough to load whole. The agent loads only the sections the current task requires.

Sectioning is **lossless**. No semantic content is removed. Content is reorganized into independently loadable units.

Sectioning is **recursive**. Any section that grows beyond the threshold is itself sectioned. Depth is unbounded; it emerges from content, not from a fixed limit.

## What Sectioning Is

- A reorganization of one large file into a directory of small files.
- A way to load only what a task requires.
- A way to keep every loadable unit under the context threshold.
- A lossless operation. The union of the section files equals the original file's content.

## What Sectioning Is Not

- A byte-count slice. It does not split a doc every N lines.
- A heading-depth mirror. It does not create a file per heading.
- A word-count hash. It does not split mid-section.
- A one-time operation. It applies at every depth.
- A duplication. Content lives in exactly one section.

## The Threshold

A single-file doc, or a section file, MUST be sectioned when it exceeds the **one-screen threshold**.

| Threshold | Guidance |
|---|---|
| **Soft** | ~150 lines of Markdown, or ~1000 words, or approximately one context block. |
| **Hard** | ~300 lines of Markdown, or ~2000 words, or approximately two context blocks. |

- A doc **SHOULD** be sectioned when it crosses the soft threshold.
- A doc **MUST** be sectioned when it crosses the hard threshold.
- A doc **MUST NOT** be sectioned when it is small enough to load whole with no eviction risk.

The threshold applies to **every loadable unit**, at every depth. A section file at depth 3 is subject to the same threshold as a top-level doc.

## Recursive Sectioning

Recursive sectioning means: **a section file that grows beyond the threshold becomes a directory, exactly as a top-level doc would**.

- The section file `002-001-overview.md` becomes the directory `002-001-overview/` containing `INDEX.md` plus its own section files.
- The section's doc ID is unchanged. `blueprint/overview` remains `blueprint/overview`.
- The section's `parent` in frontmatter is unchanged.
- The section's own sections carry `parent: blueprint/overview`.
- References to the section by ID continue to resolve.
- References to the section's *parts* now target the new child sections by ID.

The operation is identical at every depth. There is no "top-level sectioning" and "nested sectioning" — there is only sectioning.

## Practical Sectioning

Sectioning is **semantic**, not mechanical. A section is not a byte-range; it is a unit of meaning.

### One Concern per Section

- A section answers **one** question.
- If you cannot state the section's topic in one sentence, it is two sections.
- If the section contains multiple H2 headings that could each stand alone, it is likely several sections.

### Independently Loadable

- A section MUST be loadable without loading its siblings.
- A section MUST NOT depend on a sibling's content to make sense.
- Cross-references use doc IDs. A section references other sections by ID; it does not copy their content.

### Self-Contained Frontmatter

- Every section carries the required frontmatter: `id`, `parent`, `title`, `level`, `kind`.
- Every section's `parent` points to the INDEX that lists it.

### No Slicing by Length

- **Do not** split a section every N lines.
- **Do not** split a section at an arbitrary heading depth.
- **Do not** create a new file merely to keep a byte count under a number.
- **Do** split at semantic boundaries: a topic change, a distinct contract, a distinct procedure, a distinct invariant set.

## Section Size

### Too Big

A section is too big when any of the following holds:

- It exceeds the soft threshold.
- It contains 3 or more distinct concerns.
- It is expected to grow.
- It is read partially, never wholly.

Action: recursively section it.

### Too Small

A section is too small when both of the following hold:

- It is under ~20 lines.
- It shares a single concern with a sibling section.

Action: merge it into the sibling. Do not create a section for a single paragraph that has no independent concern.

## Depth

There is no fixed maximum depth.

- Depth is emergent. A large document may section 3, 4, or more levels deep before every loadable unit is under the threshold.
- The numbering scheme supports 10+ levels without renumbering (`rules/numbering.md`).
- The practical limit is navigability: past roughly 10 levels, the INDEX files alone become the dominant content. At that point, the caller SHOULD re-scope — move the subtree to a separate type directory, split it into multiple parent docs, or promote it to a higher level.

The rule is: **depth is determined by content size at each level, not by a fixed cap.**

## Conversion Procedure

When a single-file doc or a section file crosses the threshold:

1. **Create a directory** with the same base name as the file, minus the `.md` extension.
   - `002-001-overview.md` → `002-001-overview/`
2. **Move the file's frontmatter** into `002-001-overview/INDEX.md`.
   - Keep `id`, `parent`, `title`, `level`, `kind` unchanged.
   - Add an `INDEX` body: one-line purpose plus a section table.
3. **Split the content** into section files, one per semantic unit.
   - Each section file is named `{{parent-number}}-{{NNN}}-{{kebab-title}}.md`.
   - Each section file carries `parent: {{parent id}}`.
   - See `rules/numbering.md` for numbering.
4. **Update the parent `INDEX.md`** to point to the new directory. The parent already listed `002-001-overview.md`; it now lists `002-001-overview/`. The doc ID is unchanged, so the entry's ID does not change.
5. **Recurse.** For each new section file, if it exceeds the threshold, apply this procedure to it.
6. **Update cross-references.** Any reference to the old file continues to resolve by ID. References to content that moved into a new child section SHOULD be updated to target that child by ID.

## Merge Procedure

When two sibling sections are both too small and share a single concern:

1. Merge the content of the later section into the earlier section, preserving semantic order.
2. Delete the later section file.
3. Remove the later section's row from the parent `INDEX.md`.
4. If any doc referenced the deleted section by ID, update it to reference the surviving section by ID.
5. Do not reuse the deleted section's ID.

## Agent Behavior

- **MUST** section any doc or section that crosses the hard threshold.
- **SHOULD** section any doc or section that crosses the soft threshold.
- **MUST** section recursively: a section file that crosses the threshold becomes a directory.
- **MUST** section semantically, not by byte count or heading depth.
- **MUST NOT** section a doc that is small enough to load whole.
- **MUST NOT** create a section for a single paragraph with no independent concern.
- **MUST NOT** duplicate content across sections. Reference by doc ID.
- **MUST** keep the doc ID stable across a conversion. Only content moves; the ID does not.
- **MUST** update the parent `INDEX.md` after any conversion or merge.
- **MUST** keep every loadable unit (top-level doc, `INDEX.md`, section file) under the threshold.