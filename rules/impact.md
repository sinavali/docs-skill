---
name: impact
purpose: The Change Surface — discovering the complete impact of a change before writing code.
---

# Rule — Impact Analysis

## The Problem

Discovering *which files to read* is not the same as discovering *which behavior a
change touches*. A path index answers the first. Only a relationship graph answers
the second.

The Change Surface is the artifact that closes that gap.

## The Change Surface

Before any non-trivial implementation, the orchestrator MUST produce a Change
Surface. It is the contract between discovery and implementation.

```markdown
# Change Surface

## Request
<the original user request, verbatim>

## Seeds
- <flow or doc IDs found from keywords / domains / flows>

## Documentation inspected
- <doc ID>: <one line why>

## Related documentation identified
- <doc ID>: <edge type that pulled it in>

## Code surface
- <glob or path>

## Test surface
- <glob or path>

## Related flows
- <flow ID>

## Explicitly checked and unaffected
- <flow or doc ID>: <why it was ruled out>

## Risks
- <risk>

## Open questions
- <question, or NC item ID>

## Status
READY_FOR_IMPLEMENTATION | NEEDS_CLARIFICATION
```

## Discovery Pipeline

1. **Classify.** Domain-local, cross-domain, contract, or behavioral.
2. **Find seeds.** Match the request against `keywords`, `domains`, and `flows`
   metadata. Never start from the file tree.
3. **Expand relations.** Follow `implements` upward and `affects` outward until the
   frontier stops producing new `code_paths`.
4. **Inspect code.** Confirm the declared `code_paths` actually contain the behavior.
   If a needed path is missing, the Change Surface is incomplete — record it.
5. **Build the surface.** Emit the artifact above.
6. **Negative scope.** Record what was *checked and ruled out*, not just what was
   included.

## Status Values

| Status | Meaning | Next step |
|---|---|---|
| `READY_FOR_IMPLEMENTATION` | Surface closed; impact frontier exhausted. | Hand to coder. |
| `NEEDS_CLARIFICATION` | A required doc is missing or ambiguous. | Create an NC item; stop. |

## Coder Contract

The coder receives the Change Surface, not the raw request.

- **MUST** start from the declared surface.
- MAY inspect additional code.
- **MUST NOT** run independent architecture discovery unless the surface explicitly
  marks an area incomplete.
- If the coder finds a needed file outside the surface, it MUST stop and mark the
  Change Surface incomplete rather than silently expanding it.

## Reviewer Contract

The reviewer receives: original request + Change Surface + diff. It MUST verify:

1. Every declared documentation dependency was honored.
2. Every declared code path was considered.
3. Every affected flow was considered.
4. New consumers introduced by the diff were checked.
5. Existing consumers of changed contracts or events were searched.
6. Tests cover the affected behavior.
7. No undocumented behavior was accidentally changed.
8. No documentation constraint was violated.

If the diff reveals a surface not present in the Change Surface, the reviewer
**MUST** mark the Change Surface incomplete and return control to the orchestrator.

## Negative Scope

This is the highest-value, lowest-cost discipline in the protocol. A surface that
records only inclusions proves nothing. A surface that records exclusions proves the
search was bounded and intentional.

## Rules

- **MUST** produce a Change Surface before non-trivial implementation.
- **MUST** start discovery from metadata, not from the file tree.
- **MUST** record negative scope.
- **MUST NOT** implement while the surface is incomplete.
- **MUST** return to the orchestrator when the reviewer marks the surface incomplete.