---
name: change-impact
description: Discover the complete impact surface of a change before any code is written, and emit a Change Surface.
---

# Skill — `change-impact`

Use this skill for any non-trivial code change in a repository that uses the `docs`
skill. It turns a change request into a bounded **Change Surface**.

It does **not** implement. It only discovers. Implementation happens after the
surface is complete.

## When To Use

- The user asks to change, add, remove, or refactor behavior.
- The change is not trivially local to one line.
- A contract, event, or shared type may be touched.

## Pipeline

```text
USER CHANGE
  -> find semantic seeds
  -> resolve docs
  -> follow relations
  -> resolve code paths
  -> resolve tests
  -> produce CHANGE SURFACE
```

## Steps

1. Run the `docs` skill's `impact` mode, or `docs-map impact "<request>"` if the
   tool is installed.
2. Read `docs/INDEX.md` (the global map) first.
3. Find seeds from `keywords`, `domains`, `flows` — never from the file tree.
4. Expand `implements` upward and `affects` outward until the frontier stops
   yielding new `code_paths`.
5. Resolve the code and test surface from the docs in the frontier.
6. Record **negative scope**: what was checked and ruled out.
7. Emit the Change Surface from `templates/change-surface.md`.

## Hard Rules

- **FORBIDDEN:** implementing during discovery.
- **FORBIDDEN:** seeding from the file tree instead of metadata.
- **FORBIDDEN:** handing the raw request to a coder without a Change Surface.
- **REQUIRED:** negative scope section.
- **REQUIRED:** status is `READY_FOR_IMPLEMENTATION` or `NEEDS_CLARIFICATION`.

## Handoff

| Status | Next step |
|---|---|
| `READY_FOR_IMPLEMENTATION` | Coder implements the declared surface. |
| `NEEDS_CLARIFICATION` | Create an NC item; stop. |

After the diff exists, the reviewer verifies coverage against the Change Surface and
may mark it incomplete, returning control to the orchestrator.