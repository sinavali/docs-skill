---
name: docs
version: 1.0.0
description: Scaffold, read, validate, extend, and repair product documentation that constrains AI agents to a product's intent.
source: https://github.com/<user>/docs-skill
license: MIT
---

# docs

A skill for managing the documentation system defined by the **AI-Driven Product Documentation Guideline**.

The skill is pure Markdown. It contains no scripts, no OS-specific content, and no platform APIs. It works on a filesystem, on any VCS, with or without an agentic platform.

## When to Use

- Before reading any doc.
- Before writing any doc.
- Before scaffolding docs for a new product.
- Before repairing docs in an existing product.
- Before validating the integrity of a docs tree.

## Modes

| Mode | Purpose | Modifies files? |
|---|---|---|
| `read` | Load only the sections needed for the current task. | No |
| `index` | Build a path-only index of docs. | No |
| `validate` | Check integrity. Report only. | No |
| `extend` | Add a doc or section on demand. | Yes |
| `init` | Scaffold a fresh product. Org-level access required. | Yes |
| `repair` | Fix an existing docs tree. Lossless. Org-level access required. | Yes |

## Load-on-Demand Rule

Load only the mode file required for the current operation. Load `rules/*.md` only when a mode references them. Load `templates/*.md` only when generating new files. Never load the whole skill tree at once.

## Invocation Contract

1. The caller states the mode and the anchor path (the directory where work begins).
2. The skill loads `SKILL.md` (this file).
3. The skill loads the mode file named by the caller.
4. The mode file names any `rules/*.md` and `templates/*.md` it needs.
5. The skill loads those, then executes the mode contract.

If the caller does not name a mode, the skill defaults to `read`.

## Core Rules (Always in Force)

These apply in every mode. They are not repeated per mode.

1. **MUST NOT** write into excluded paths. The exclusion list is declared in `AGENT.md` frontmatter; defaults are in `rules/excluded-paths.md`.
2. **MUST NOT** edit `README.md`. It is human-facing only.
3. **MUST NOT** draw product intent from `README.md`.
4. **MUST** reference docs by stable doc ID, not by raw path, in generated cross-links.
5. **MUST** build a path index before loading any section contents.
6. **MUST** log to `NEED_CLEARIFICATION.md` when a required doc is missing or ambiguous. Schema is in `rules/nc.md`.
7. **MUST** respect precedence per `rules/precedence.md` when two docs conflict.
8. **MUST** use the numbering scheme per `rules/numbering.md` when generating file or directory names.
9. **MUST** be lossless in `repair` mode: never delete semantic content without an NC item.
10. **MUST NOT** assume a VCS, CI system, OS, or platform. If a mode requires one and none is present, follow the mode's fallback.

## Failure Behavior

If the skill cannot proceed:

1. Create or update `NEED_CLEARIFICATION.md` at the current anchor's scope.
2. If `NEED_CLEARIFICATION.md` cannot be written (e.g., no write access), return the NC item body to the caller as text.
3. Return control to the caller with a clear message stating:
   - which mode failed,
   - which rule or doc was the blocker,
   - what the caller must do next.

Never invent missing intent. Never guess a doc's contents.

## Installation

1. Human provides the skill repo URL.
2. Agent fetches the repo via its platform's mechanism.
3. Agent installs the skill into the platform's skill directory (e.g., `.opencode/skills/docs/`).
4. If no platform skill directory exists, agent places the skill in the org-root under `skills/docs/`.
5. The skill is registered with the platform.

## Version

`version: 1.0.0`. This field belongs to the skill, not to any product doc. Product docs carry no version field.