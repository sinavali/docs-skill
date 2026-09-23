---
id: {{SCOPE_ID}}/agent
scope: {{SCOPE}}
level: {{LEVEL}}
kind: agent
{{ORG_ROOT_BLOCK}}
skill: docs
excluded_paths: [.git/, .opencode/, node_modules/, dist/, build/, .cache/, coverage/]
included_paths: []
---

# {{TITLE}} — Agent Router

`README.md` is human-facing and is not normative for agents.

## Skill (MUST)
Invoke the `docs` skill before reading or writing any doc.
Modes: read, index, validate, extend, init, repair.

## Upward reading order (MUST)
1. This file
{{UPWARD_ORDER}}

## Doc map
| Purpose | Path |
|---|---|
{{DOC_MAP}}

## Index protocol (MUST)
Build an index of doc **paths**, not contents. Load contents only when a task requires them.

## File-level docs (MUST)
When modifying any source file, check for `<filename>.md` in the same directory.

## Excluded paths
Tool-generated, VCS, and build paths. Do not create docs inside them.

## Directory map
| Path | Purpose | Rules |
|---|---|---|
{{DIRECTORY_MAP}}