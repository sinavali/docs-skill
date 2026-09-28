# USAGE — docs skill

End-to-end guide for using the `docs` skill in a real repository.

## 1. Install the skill

Give your agent the source URL of this repository. The agent installs the skill
into the platform skill directory:

- Qwen Code: `.qwen/skills/docs/`
- Fallback: `<org-root>/skills/docs/`

The agent always loads `SKILL.md` first, then loads other files on demand.

## 2. Scaffold a docs tree

In a new repository, ask the agent to run `init` with a product brief
(name, intent, users, non-goals, invariants). `init` creates:

```text
AGENT.md                      # agent-facing contract (impact workflow included)
README.md                     # human-facing only
docs/
  INDEX.md                    # global map (domains, flows, participation)
  002-blueprint/
  003-decisions/
  004-contracts/
  005-cross-cutting/
  006-operational/
  007-flows/                  # cross-domain flow docs
```

In an existing repository with docs already scattered, run `repair` instead.
It moves content into the canonical shape losslessly and reports what it moved.

## 3. Give documents impact metadata

Every doc that governs code should carry:

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

The templates under `templates/` already emit these fields. Fill them in.

## 4. Build the graph cache (optional but recommended)

From the repository root:

```bash
node <skill>/tools/docs-map/index.js generate
```

This writes `.qwen/docs-index/{manifest.json,relations.json}`. The cache is
git-ignored and safe to delete. If it is missing, the skill falls back to
reading frontmatter directly.

## 5. Run a change

Preferred entry point:

```text
/change <request>
```

This runs impact discovery and produces a **Change Surface**:

```text
request
  -> find semantic seeds
  -> expand documentation graph
  -> resolve code surface
  -> resolve test surface
  -> verify impact closure
  -> CHANGE SURFACE
```

Without the command, run `modes/impact.md` (or `docs-map impact "<request>"`).

## 6. Hand off

```text
CHANGE SURFACE  ->  coder  ->  diff  ->  reviewer
```

- The **coder** starts from the Change Surface, not the raw request.
- The **reviewer** verifies coverage against the Change Surface and may mark it
  incomplete, returning control to the orchestrator.

## 7. Validate

At any time:

```bash
node <skill>/tools/docs-map/index.js validate
```

or run `modes/validate.md`. Deterministic checks include broken IDs, broken
edges, reverse-edge drift, flow integrity, and duplicate semantic source.

## 8. Everyday queries

```bash
node <skill>/tools/docs-map/index.js search "signup"
node <skill>/tools/docs-map/index.js flow registration
node <skill>/tools/docs-map/index.js doc auth/registration
node <skill>/tools/docs-map/index.js related auth/registration
node <skill>/tools/docs-map/index.js code packages/auth/src/registration
```

## What lives where

| Path | Job |
|---|---|
| `SKILL.md` | Entry point; mode/rule/template tables. |
| `modes/` | `read`, `index`, `impact`, `validate`, `extend`, `init`, `repair`. |
| `rules/` | Frontmatter, numbering, sectioning, relationships, impact, index-format, graph, precedence, nc, file-level, excluded-paths. |
| `templates/` | Canonical file shapes. |
| `tools/docs-map/` | Graph generator and query CLI. |
| `skills/change-impact/` | Discovery-only project skill. |
| `commands/change.md` | `/change` entry point. |

## Key rules to remember

- **Breadth of metadata, narrowness of content.** Discover broadly, load narrowly.
- **Typed edges.** `references` = read to understand; `affects` = change cascades.
- **Reverse edges are derived, never authored.**
- **Impact before implementation.** No non-trivial change without a Change Surface.
- **Ambiguity is recorded, not invented.** Every gap becomes an NC item.