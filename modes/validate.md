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
  - excluded-path leaks,
  - sectioning violations (units above the threshold, semantic incoherence signals).

**References:**
- `rules/frontmatter.md`
- `rules/precedence.md`
- `rules/numbering.md`
- `rules/sectioning.md`
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
   - **Size.** Line count and word count of every loadable unit (top-level doc, `INDEX.md`, section file). Report units above the soft threshold as warnings and above the hard threshold as errors. See `rules/sectioning.md`.
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
6. **Sectioning coherence checks (heuristic).** Flag, as warnings, any of:
   - A section file that contains 3 or more H2 headings and exceeds the soft threshold.
   - A section file that duplicates content present in a sibling section (possible single-source-of-truth violation).
   - A section file under ~20 lines that shares a concern with a sibling (candidate for merge).
   - A sectioned doc whose `INDEX.md` alone exceeds the soft threshold (its section list has become too large to load whole).
   These are heuristics. The report names them as warnings, not errors, so the human can judge.
7. **Conflict detection.** For each pair of docs that appear to cover the same case, compare their rules. Report any same-level conflicts and any lower-authority docs that contradict higher-authority docs.
8. **Emit the report.** The report is ephemeral; it is returned to the caller and never written to disk.

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

SECTIONING
  - <path>: lines=<n>, words=<n>, threshold=<soft|hard>
  ...

SUMMARY
  errors: <n>
  warnings: <n>
  unresolved NC items: <n>
  conflicts: <n>
  sectioning violations: <n>
```

---

## Rules

- **MUST NOT** modify any file.
- **MUST NOT** create files. If validation fails, the caller decides whether to open an NC item.
- **MUST** treat the report as ephemeral. Never persist it as a doc.
- **MUST** respect `excluded_paths`.
- **MUST NOT** attempt to repair drift. Validation reports; repair is a separate mode.
- **MUST** apply `rules/sectioning.md` when measuring units. The threshold applies at every depth.

---

## Example

```text
scope: repo:payments-api
validated: 2026-09-23

ERRORS
  - error: docs/004-contracts/004-001-refund-api/004-001-010-reason-field.md: 412 lines, above hard threshold — must be sectioned per rules/sectioning.md
  - error: docs/005-cross-cutting/INDEX.md: references doc ID `cross-cutting/vcs` which does not exist

WARNINGS
  - docs/003-decisions/003-002-use-webhooks.md: not listed in docs/003-decisions/INDEX.md
  - docs/004-contracts/004-001-refund-api/004-001-020-schemas.md: 168 lines, above soft threshold — consider sectioning
  - docs/004-contracts/004-001-refund-api/004-001-030-compatibility.md: 14 lines and shares concern with 004-001-010 — candidate for merge

NC_UNRESOLVED
  - NC-0007: Refund reason optionality
  - NC-0008: Idempotency window

CONFLICTS
  - repo:payments-api/blueprint/invariants vs repo:payments-api/blueprint/architecture: retry count disagrees (3 vs 5)

SECTIONING
  - docs/004-contracts/004-001-refund-api/004-001-010-reason-field.md: lines=412, words=2840, threshold=hard
  - docs/004-contracts/004-001-refund-api/004-001-020-schemas.md: lines=168, words=1120, threshold=soft

SUMMARY
  errors: 2
  warnings: 3
  unresolved NC items: 2
  conflicts: 1
  sectioning violations: 1
```
---

## Graph Integrity Checks

`validate` MUST also check the relationship graph, not just structure.

### Broken IDs

For every edge in `references`, `affects`, `implements`, `depends_on`:

```text
DOC-AUTH-001
  references DOC-USER-999

ERROR:
DOC-USER-999 does not exist
```

### Broken Edges

- A `references`/`affects`/`depends_on` target that is not a doc ID.
- An `implements` target that is not a known flow ID.
- A `code_paths` / `test_paths` glob that matches nothing in the tree.

### Reverse-Edge Drift

If a doc authors a reverse edge (`affected_by`, `referenced_by`, `implemented_by`),
that is an error. Reverse edges are derived, never authored.

### Flow Integrity

- A flow that references a nonexistent domain.
- An orphaned high-level flow (declared in the global map but implemented by no doc).
- A flow with no `code_paths` reachable through its implementers.

### Duplicate Semantic Source

Two docs whose `code_paths` fully overlap and whose `domains` and `flows` match are a
possible single-source-of-truth violation. Report as a warning.

These checks require **no LLM**. They are deterministic.

Add to the report shape:

```text
GRAPH
  - ERROR: <doc>: <edge> -> <missing id>
  - ERROR: <doc>: authors reverse edge <edge>
  - ERROR: <flow>: references nonexistent domain <domain>
  - WARN: <flow>: orphaned (no implementer)
  - WARN: <doc A> and <doc B>: duplicate semantic source
```

---
