---
id: {{ID}}
title: {{TITLE}}
level: {{LEVEL}}
kind: {{KIND}}    # MUST be the kind of the indexed directory: agent | blueprint | decision | contract | cross-cutting | operational. Never `index`.
---

# {{TITLE}} — Index

{{ONE_LINE_PURPOSE}}

| ID | File | Purpose |
|---|---|---|
{{SECTION_ROWS}}

<!--
Sectioning notes (do not emit in generated files):

- This INDEX.md is one loadable unit. It MUST stay under the one-screen threshold (~150 lines / ~1000 words). See rules/sectioning.md.
- If the section list itself grows past the threshold, the INDEX.md MUST be split: group sections into subdirectories and list those instead.
- This INDEX.md is subject to the same recursive sectioning rule as any section file. A large index becomes a directory of indexes.
- Keep each row's Purpose to one line. A multi-line purpose is a signal that the section is doing more than one thing.
-->