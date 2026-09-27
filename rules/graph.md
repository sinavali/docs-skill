---
name: graph
purpose: Generated documentation graph artifacts and the docs-map tool.
---

# Rule — Generated Graph

## Purpose

The Markdown frontmatter is the **source of truth**. The generated graph is a
**derived cache** that makes discovery cheap and deterministic.

```text
docs/**/*.md  --(generator)-->  .qwen/docs-index/manifest.json
                               .qwen/docs-index/relations.json
```

Generation costs essentially **zero LLM tokens**. The model only sees query
results.

## Artifacts

| File | Contents |
|---|---|
| `.qwen/docs-index/manifest.json` | One record per doc: id, path, domains, flows, keywords, code_paths, test_paths, kind, level. |
| `.qwen/docs-index/relations.json` | Authored edges plus derived reverse edges. |

## Never Hand-Maintained

These files are **generated**. Do not edit them by hand. Regenerate after any doc
change. If they disagree with the Markdown, the Markdown wins.

## Reverse Edges Are Derived Here

The generator is the only place reverse edges (`referenced_by`, `affected_by`,
`implemented_by`) ever exist. They are never written into Markdown.

## The `docs-map` Tool

A small Node CLI. No database. Commands:

```bash
docs-map generate                  # rebuild .qwen/docs-index/ from docs/**/*.md
docs-map search "signup"           # match keywords, domains, flows, titles
docs-map flow registration         # a flow and its implementers
docs-map doc <id>                  # one doc + its edges
docs-map related <id>              # neighborhood of a doc
docs-map code <path>               # docs that govern a code path
docs-map impact "<request>"        # seed, expand, resolve code+tests
```

Output is intentionally tiny.

## Query Output Shape — `docs-map impact`

```text
MATCHES
  DOC-AUTH-001
  DOC-USER-002
  FLOW-REGISTRATION

RELATIONS
  DOC-AUTH-001
    -> DOC-AUTH-003
    -> DOC-USER-002
    -> DOC-NOTIFY-003

CODE
  packages/auth/src/registration/**
  packages/auth/src/verification/**
  packages/users/src/registration/**

TESTS
  packages/auth/test/registration/**
  packages/auth/test/verification/**
```

This is vastly cheaper than repeatedly grepping and reading the repository.

## Validation

The generator MUST detect and report:

- broken document ID,
- broken relationship,
- missing referenced doc,
- invalid code path glob,
- flow referencing a nonexistent domain,
- duplicate semantic source,
- orphaned high-level flow.

`modes/validate.md` runs the same checks.

## Degradation

If the generated graph is missing or stale, the agent MUST fall back to reading
frontmatter directly via `modes/index.md`. The system works without the tool; the
tool only makes it faster.