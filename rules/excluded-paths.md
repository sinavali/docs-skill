---
name: excluded-paths
purpose: Default exclusion list and re-inclusion.
---

# Rule — Excluded Paths

The following paths are out of documentation scope by default.

## Default Exclusion List

```yaml
excluded_paths:
  - .git/
  - .opencode/
  - node_modules/
  - dist/
  - build/
  - .cache/
  - coverage/
```

`AGENT.md` declares this list in frontmatter. Agents MUST NOT create, edit, or treat excluded paths as intent.

## Re-Inclusion

`AGENT.md` MAY list `included_paths` to re-include specific subtrees.

```yaml
excluded_paths:
  - .git/
  - node_modules/
  - dist/
included_paths:
  - .github/workflows/       # CI files are in scope
```

## Notes

- `.github/` is **not** excluded by default. CI and workflow files remain in scope unless explicitly excluded.
- New tool directories discovered at runtime MUST be reported to the human via `NEED_CLEARIFICATION` so the exclusion list can be updated.
- `included_paths` overrides `excluded_paths` for exact subtrees. It does not override a parent exclusion for a sibling path.

## Agent Behavior

- **MUST NOT** write docs inside an excluded path.
- **MUST NOT** load docs from an excluded path as intent.
- **MUST NOT** traverse excluded paths when building a path index.
- **MUST** create an NC item when a new tool directory is discovered that is not in either list.