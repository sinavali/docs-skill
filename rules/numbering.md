---
name: numbering
purpose: 3-digit accumulation, gaps, insertion, and stable doc IDs.
---

# Rule — Numbering

## Directory Naming

```text
{{3-digit-id}}-{{kebab-case-title}}/
```

Examples: `001-agent/`, `002-blueprint/`, `003-decisions/`, `005-cross-cutting/`.

## File Naming

Single-level:

```text
{{3-digit-id}}-{{kebab-case-title}}.md
```

Nested:

```text
{{parent-id}}-{{3-digit-id}}-{{kebab-case-title}}.md
```

Examples:
- `002-001-overview.md`
- `005-003-002-label-taxonomy.md`

## Depth

Each level uses 3 digits. Each nesting depth concatenates the parent's number with the item's own 3-digit number.

| Depth | Example |
|---|---|
| 1 | `001-blueprint/` |
| 2 | `001-blueprint/001-001-overview.md` |
| 3 | `001-blueprint/001-003-vcs-specifics/001-003-001-platform.md` |
| 4 | `001-blueprint/001-003-vcs-specifics/001-003-001-002-labels.md` |
| 10 | `001-...-...-...-...-...-...-...-...-001-item.md` (30 digits) |

## Gaps

- Use gaps of 10 between siblings when possible (`001`, `010`, `020`, …).
- When the tree is small and stable, contiguous numbering (`001`, `002`, `003`) is acceptable.
- **Never renumber siblings.**

## Insertion

To insert a section between `001` and `002`, use `001-005` or `001-015`. Do not renumber.

Before:

```text
002-001-overview.md
002-002-users.md
```

After inserting a new section:

```text
002-001-overview.md
002-001-005-guest-users.md    ← new
002-002-users.md
```

Update `INDEX.md` to list the new section between `002-001` and `002-002`.

## Order

Order is defined by `INDEX.md`, not by filenames. Filenames carry IDs for sortability only.

## Stable Doc IDs

IDs are **path-derived** from the directory structure under `/docs/`:

```text
docs/002-blueprint/002-003-non-goals.md
→ id: blueprint/non-goals
```

For cross-level references, prefix with the level scope:

```text
→ id: product:payments/blueprint/non-goals
```

For cross-repo references, prefix with the org-root ID:

```text
→ id: org:acme/product:payments/blueprint/non-goals
```

## ID Rules

- IDs are used in cross-references, NC items, and frontmatter `parent` / `references`.
- Filenames may change; IDs are stable.
- IDs MUST be unique within their scope.
- IDs MUST NOT be reused after deletion.
- IDs are the primary reference format in generated content.

## Reference Format

| Context | Format |
|---|---|
| Same scope | `blueprint/non-goals` |
| Cross-level, same repo | `product:payments/blueprint/non-goals` |
| Cross-repo | `org:acme/product:payments/blueprint/non-goals` |
| URL (if host supports) | `https://...` |
| Fallback (filesystem only) | Relative path from current doc. |

## Renaming

When a doc's **title** changes:

1. Rename the file or directory.
2. Update the parent `INDEX.md`.
3. Update all docs that reference the old ID.
4. Do **not** change the ID unless the doc's scope changes.

When a doc's **scope** changes:

1. Move the doc to the new scope.
2. Update the ID.
3. Update all references.
4. Record the change in the parent `INDEX.md` (not in the doc itself).