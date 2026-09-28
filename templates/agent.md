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
---

## Mandatory Impact Workflow

For any non-trivial code change, this repository requires the following sequence.

1. Determine the affected flow or domain.
2. Consult the documentation graph (`docs/INDEX.md`, then `modes/index.md` metadata).
3. Follow documentation relationships until the impact surface is closed.
4. Resolve affected `code_paths` and `test_paths`.
5. Produce a **Change Surface** (`templates/change-surface.md`).
6. Do not implement before the Change Surface is complete.
7. The reviewer MUST verify coverage against the Change Surface.

### Coder

- Start from the Change Surface, not the raw request.
- Do not run independent architecture discovery unless the surface marks an area
  incomplete.
- If a needed file lies outside the surface, stop and mark the surface incomplete.

### Reviewer

- Input: original request + Change Surface + diff.
- Verify every declared doc dependency, code path, affected flow, new consumer, and
  existing consumer of changed contracts.
- Verify tests cover the affected behavior.
- If the diff reveals a surface absent from the Change Surface, mark the Change
  Surface incomplete and return control to the orchestrator.

### Before Modifying Any Source File

1. Check for a sibling `<filename>.md` file-level doc. Read it first.
2. Confirm the file is inside a `code_paths` glob declared by a doc in the Change
   Surface. If not, the surface is incomplete.

---
