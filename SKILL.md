---
name: docs
purpose: Manage product documentation that constrains AI agents, with impact analysis for reliable change discovery.
---

# Skill — `docs`

An installable, pure-Markdown skill for managing product documentation that
constrains AI agents to a product's intent.

This skill implements the **AI-Driven Product Documentation Guideline** and an
**impact-analysis layer** that turns a change request into a bounded Change Surface
before any code is written.

## Entry Point

The agent always loads `SKILL.md` first. All other files load on demand.

## Load-On-Demand

- Load a mode file only when that mode is active.
- Load a rule file only when a mode references it and the task needs it.
- Load a template only when producing a file of that kind.
- Never load the whole skill into context.

## The Three Layers

```text
1. DOCUMENTATION GRAPH   domains / flows / docs / typed relations
2. CODE SURFACE          docs -> directories/files (code_paths, test_paths)
3. CODE REFERENCES       grep / LSP / compiler, only when needed
```

Descend only when the task requires it. This preserves progressive disclosure.

## Modes

| Mode | Purpose | Modifies files |
|---|---|---|
| `read` | Load only the sections the task needs, following the impact graph for changes. | no |
| `index` | Discover topology, metadata, and relationships. Produce a compact semantic index. | no |
| `impact` | Turn a change request into a Change Surface. | no |
| `validate` | Check tree and graph integrity. Report only. | no |
| `extend` | Add a doc or section, with mandatory impact metadata. | yes |
| `init` | Scaffold a fresh product docs tree. | yes |
| `repair` | Fix an existing docs tree losslessly. | yes |

## Modes — Order for a Change

```text
impact  ->  Change Surface  ->  (coder)  ->  diff  ->  (reviewer)
```

- The orchestrator runs `impact`.
- The coder implements the declared surface.
- The reviewer verifies coverage against the surface and may mark it incomplete,
  returning control to the orchestrator.

## Rules

| Rule | Purpose |
|---|---|
| `rules/frontmatter.md` | Required and optional fields, including impact metadata. |
| `rules/numbering.md` | 3-digit accumulation, gaps, insertion, stable doc IDs. |
| `rules/sectioning.md` | Sectioning doctrine: threshold, recursion, practical boundaries. |
| `rules/file-level.md` | Sibling `<filename>.md` discovery. |
| `rules/precedence.md` | Conflict resolution order. |
| `rules/nc.md` | NEED_CLEARIFICATION lifecycle and schema. |
| `rules/excluded-paths.md` | Default exclusion list and re-inclusion. |
| `rules/relationships.md` | Typed relationship model. |
| `rules/impact.md` | Change Surface and impact analysis. |
| `rules/index-format.md` | Semantic routing map and global map. |
| `rules/graph.md` | Generated graph artifacts and the docs-map tool. |

## Templates

| Template | Kind |
|---|---|
| `templates/agent.md` | `AGENT.md` |
| `templates/index.md` | Directory routing `INDEX.md` |
| `templates/index-global.md` | Global `docs/INDEX.md` map |
| `templates/section.md` | Section file |
| `templates/contract.md` | Contract doc |
| `templates/decision.md` | Decision doc |
| `templates/cross-cutting.md` | Cross-cutting doc |
| `templates/runbook.md` | Operational doc |
| `templates/flow.md` | Cross-domain flow doc |
| `templates/change-surface.md` | Change Surface artifact |
| `templates/nc-item.md` | NEED_CLEARIFICATION item |

## Failure Behavior

- Missing required doc -> NC item, do not invent.
- Same-level conflict -> NC item, stop.
- Missing `AGENT.md` -> treat repo root as org-root, NC item.
- Missing impact metadata on a code-governing doc -> validate warning.
- Broken graph edge -> validate error.

## Core Principles

- **Docs lead, code follows.**
- **Two audiences, two files:** `README.md` for humans, `AGENT.md` for agents.
- **Breadth of metadata, narrowness of content.** Discover broadly, load narrowly.
- **Ambiguity is recorded, not invented.** Every gap becomes an NC item.
- **No versions, no status, no changelog.** VCS is the version store.
- **Impact before implementation.** No non-trivial change without a Change Surface.