# docs — Skill

An installable, pure-Markdown skill for managing product documentation that constrains AI agents to a product's intent.

This skill implements the **AI-Driven Product Documentation Guideline**. It scaffolds, reads, validates, extends, and repairs a documentation tree defined by a sectioned, ID-addressable, path-indexed structure.

## Audience

- **Humans** setting up or maintaining a documentation system.
- **AI agents** that must read, write, and repair docs under a disciplined protocol.

## Installation

Provide the source URL of this repository to your agent. The agent installs the skill into the platform's skill directory (for example `.opencode/skills/docs/`). If no platform skill directory exists, place the skill in the org-root under `skills/docs/`.

## Entry Point

The agent always loads `SKILL.md` first. All other files are loaded on demand, as directed by the active mode and the shared rules.

## Contents

| Path | Purpose |
|---|---|
| `SKILL.md` | Skill entry point, mode table, load-on-demand rule, failure behavior. |
| `modes/` | One file per mode: `read`, `index`, `validate`, `extend`, `init`, `repair`. |
| `rules/` | Shared rule files referenced by modes. |
| `templates/` | Canonical file shapes for generated docs. |

## Principles

- **Docs lead, code follows.**
- **Two audiences, two files:** `README.md` for humans, `AGENT.md` for agents.
- **Paths are the index.** Agents build a path index; contents load only on demand.
- **Ambiguity is recorded, not invented.** Every gap becomes a `NEED_CLEARIFICATION` item.
- **No versions, no status, no changelog.** VCS is the version store.

## License

MIT. See `LICENSE`.