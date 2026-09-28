---
id: {{ID}}
parent: {{PARENT}}
title: {{TITLE}}
level: {{LEVEL}}
kind: {{KIND}}
domains: [{{DOMAINS}}]
flows: [{{FLOWS}}]
keywords: [{{KEYWORDS}}]
references: []
affects: []
implements: []
code_paths: []
test_paths: []
---

# {{TITLE}}

{{CONTENT}}

<!--
Sectioning notes (do not emit in generated files):

- This section is one loadable unit. It MUST stay under the one-screen threshold (~150 lines / ~1000 words). See rules/sectioning.md.
- If this section grows past the soft threshold, consider sectioning it: convert it into a directory with its own INDEX.md and child section files, preserving this file's id as the new INDEX's id.
- If this section grows past the hard threshold, it MUST be sectioned. Recursion is required at every depth. The section's doc id remains stable.
- Section semantically, not by byte count. One concern per section. A section that contains 3+ distinct H2 headings is likely several sections.
- A section that drops under ~20 lines and shares its concern with a sibling SHOULD be merged into that sibling instead.
- Every section MUST be independently loadable. It MUST NOT depend on a sibling's content to make sense. Reference siblings by doc id, never by copied content.
- Carry `domains`, `flows`, `keywords` (and `code_paths` / `test_paths` when the section governs code) so impact discovery can reach it. See rules/frontmatter.md and rules/relationships.md.
- MUST NOT author reverse edges (affected_by / referenced_by / implemented_by).
-->