---
description: Run impact discovery and produce a Change Surface for a change request.
---

# Command — `/change`

Deterministic entry point for the impact workflow.

## Usage

```text
/change <request>
```

## Flow

```text
/change <request>
  -> run impact discovery
  -> generate Change Surface
  -> orchestrator
  -> coder
  -> reviewer
```

## Steps

1. Load the `docs` skill.
2. Run `modes/impact.md` with the request.
3. If `tools/docs-map` is installed, run `docs-map impact "<request>"` to seed and
   expand the graph deterministically.
4. Emit the Change Surface (`templates/change-surface.md`).
5. If status is `READY_FOR_IMPLEMENTATION`, hand the Change Surface to the coder.
6. If status is `NEEDS_CLARIFICATION`, create an NC item and stop.
7. After the diff exists, hand `request + Change Surface + diff` to the reviewer.

## Rules

- The coder receives the **Change Surface**, never the raw request.
- The reviewer may mark the Change Surface incomplete and return to the
  orchestrator.
- No implementation happens before the surface is complete.