# docs — Skill

An installable, pure-Markdown skill for managing product documentation that constrains AI agents to a product's intent, **with an impact-analysis layer** for reliable change discovery.

This skill implements the **AI-Driven Product Documentation Guideline**. It scaffolds, reads, validates, extends, and repairs a documentation tree defined by a sectioned, ID-addressable, path-indexed structure — and it turns a change request into a bounded **Change Surface** before any code is written.

## Audience

- **Humans** setting up or maintaining a documentation system.
- **AI agents** that must read, write, and repair docs under a disciplined protocol.

## The Core Idea

The original system optimized **how cheaply to read a document**. The impact layer adds **how reliably to discover the complete impact surface of a change**.

```text
request
  -> find semantic seeds
  -> expand documentation graph
  -> resolve code surface
  -> resolve test surface
  -> verify impact closure
  -> CHANGE SURFACE
  -> code
  -> review against CHANGE SURFACE
```

Two principles make this cheap:

- **Breadth of metadata, narrowness of content.** Discover broadly; load narrowly.
- **Typed edges, not vague relations.** `references` (read) vs `affects` (change).

## Installation

Provide the source URL of this repository to your agent. The agent installs the skill into the platform's skill directory (for example `.qwen/skills/docs/`). If no platform skill directory exists, place the skill in the org-root under `skills/docs/`.

## Entry Point

The agent always loads `SKILL.md` first. All other files are loaded on demand.

## Contents

| Path | Purpose |
|---|---|
| `SKILL.md` | Skill entry point, mode table, load-on-demand rule, failure behavior. |
| `modes/` | One file per mode: `read`, `index`, `impact`, `validate`, `extend`, `init`, `repair`. |
| `rules/` | Shared rule files referenced by modes. |
| `templates/` | Canonical file shapes for generated docs. |
| `tools/docs-map/` | Local CLI that generates and queries the documentation graph. |
| `commands/change.md` | `/change` entry point that runs the impact workflow. |
| `skills/change-impact/SKILL.md` | Project skill for impact discovery. |

## Documentation Metadata

Every doc may carry:

```yaml
domains:  [auth, users]
flows:    [registration]
keywords: [registration, signup, account creation]
references: [auth/verification]
affects:    [notifications/email-verification]
implements: [flow:registration]
code_paths: [packages/auth/src/registration/**]
test_paths: [packages/auth/test/registration/**]
```

Reverse edges (`affected_by`, `referenced_by`, `implemented_by`) are **derived, never authored**.

## Modes

| Mode | Purpose |
|---|---|
| `read` | Load only what the task needs; follow the impact graph for changes. |
| `index` | Discover topology, metadata, and relationships. |
| `impact` | Produce a Change Surface. |
| `validate` | Check tree and graph integrity. |
| `extend` | Add a doc or section, with mandatory impact metadata. |
| `init` | Scaffold a fresh docs tree. |
| `repair` | Fix an existing docs tree losslessly. |

## Principles

- **Docs lead, code follows.**
- **Two audiences, two files:** `README.md` for humans, `AGENT.md` for agents.
- **Breadth of metadata, narrowness of content.**
- **Ambiguity is recorded, not invented.** Every gap becomes a `NEED_CLEARIFICATION` item.
- **No versions, no status, no changelog.** VCS is the version store.
- **Impact before implementation.** No non-trivial change without a Change Surface.

## License

MIT. See `LICENSE`.