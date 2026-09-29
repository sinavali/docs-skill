# docs-map

A dependency-free Node CLI that generates and queries the documentation graph
for a repository that uses the `docs` skill.

## Requirements

- Node.js 18+ (no npm install; standard library only)

## Usage

Run from the repository root:

```bash
node tools/docs-map/index.js generate
node tools/docs-map/index.js search "signup"
node tools/docs-map/index.js impact "change verification expiry to 24h"
node tools/docs-map/index.js flow registration
node tools/docs-map/index.js doc auth/registration
node tools/docs-map/index.js related auth/registration
node tools/docs-map/index.js code packages/auth/src/registration
node tools/docs-map/index.js validate
```

Pass `--root <dir>` anywhere to point at a different repository root:

```bash
node tools/docs-map/index.js --root /path/to/repo generate
```

## Commands

| Command | Purpose |
|---|---|
| `generate` | Rebuild `.qwen/docs-index/manifest.json` and `relations.json` from frontmatter. |
| `search "<q>"` | Match docs by keyword, domain, flow, title, or id. |
| `flow <name>` | A flow, its implementers, and their code/test paths. |
| `doc <id>` | Full record for one doc. |
| `related <id>` | Neighborhood of a doc (affects + references, both directions). |
| `code <path>` | Docs that govern a code path. |
| `impact "<request>"` | Seeds from a request, expands the graph, resolves code + tests. |
| `validate` | Deterministic graph-integrity check. Exits non-zero on error. |

## Tests

```bash
npm test
```

Runs `node --test` over `index.test.js` using Node's built-in test runner (no
dependencies). The suite covers frontmatter parsing across LF, CRLF, and lone
`CR` line endings.

## Source of truth

Markdown frontmatter. The generated JSON under `.qwen/docs-index/` is a derived
cache; it is git-ignored and safe to delete. If the cache is missing, the skill
falls back to reading frontmatter directly.

## Output shape (`impact`)

```text
MATCHES
  auth/registration

RELATIONS
  auth/registration
    -> notifications/email-verification
    -> auth/verification
    -> registration

CODE
  packages/auth/src/registration/**

TESTS
  packages/auth/test/registration/**
```