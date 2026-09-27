---
id: {{ID}}
title: {{TITLE}}
level: {{LEVEL}}
kind: {{KIND}}
domains: [{{DOMAINS}}]
flows: [{{FLOWS}}]
code_paths: [{{CODE_PATHS}}]
---

# {{TITLE}}

One-line purpose. Routing only.

## Sections

| ID | Purpose | Domains | Flows | Code |
|---|---|---|---|---|
| {{CHILD_ID}} | {{PURPOSE}} | {{DOMAINS}} | {{FLOWS}} | {{CODE}} |

<!--
Index rules (do not emit in generated files):

- This is a routing map. It answers "where should I look?", never "what does the system do?".
- MUST NOT contain document content.
- MUST stay under the soft threshold in rules/sectioning.md.
- Columns are derived from child frontmatter. If they disagree, the frontmatter wins and this index is stale.
- See rules/index-format.md.
-->