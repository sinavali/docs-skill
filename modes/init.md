---
name: init
purpose: Scaffold a fresh product docs tree.
modifies_files: true
requires_access: write, org-level
---

# Mode — `init`

**Purpose:** Scaffold a fresh documentation tree for a new product, using the canonical directory shape.

**Inputs:**
- `root_path` — the directory to scaffold.
- `brief` — a product brief containing: product name, one-paragraph intent, users, non-goals, invariants.

**Outputs:**
- Root `README.md`.
- Root `AGENT.md`.
- `/docs/` tree with `INDEX.md` files and initial blueprint docs.
- If multi-repo, the org-root structure.

**References:**
- `templates/agent.md`
- `templates/index.md`
- `templates/section.md`
- `rules/frontmatter.md`
- `rules/numbering.md`

---

## Steps

1. **Verify access.** `init` requires write access to `root_path` and (for multi-repo) org-level access to the org-root.
2. **Check emptiness.** If `root_path` is not empty, stop and ask the caller before creating anything. Do not overwrite existing files.
3. **Collect the brief.** If the brief is missing any of: product name, intent, users, non-goals, invariants — ask for them. Do not invent.
4. **Create `README.md`** at `root_path`. Human-facing content only:
   - Product name and short overview.
   - Getting started (installation, run, test) — placeholder if unknown.
   - Licensing — placeholder if unknown.
   - **No product intent, no invariants, no contracts.**
5. **Create `AGENT.md`** at `root_path` from `templates/agent.md`. Set frontmatter:
   - `is_org_root: true` for monorepo / monolithic / superrepo.
   - For a standalone repo, set `org_root` to `../../org-root` and set `requires_org_docs: true` and `org_docs_fallback: notify` if an org-root is expected.
   - Default `excluded_paths`.
6. **Create `/docs/INDEX.md`** from `templates/index.md`.
7. **Create `/docs/001-agent/`** with sections extracted from `AGENT.md` if `AGENT.md` exceeds 150 lines. Otherwise skip `001-agent/`.
8. **Create `/docs/002-blueprint/`** with:
   - `INDEX.md`.
   - `002-001-overview.md` — the one-paragraph intent.
   - `002-002-users.md` — the users.
   - `002-003-non-goals.md` — the non-goals.
   - `002-004-invariants.md` — the invariants.
9. **Create `/docs/003-decisions/INDEX.md`** as an empty index with a placeholder purpose line.
10. **Create `/docs/004-contracts/INDEX.md`** as an empty index.
11. **Create `/docs/005-cross-cutting/INDEX.md`** as an empty index.
12. **Create `/docs/006-operational/INDEX.md`** as an empty index.
13. **If multi-repo,** additionally scaffold the org-root structure:
    - `org-root/AGENT.md` with `is_org_root: true`.
    - `org-root/docs/INDEX.md`.
    - `org-root/docs/002-blueprint/` with org-level intent.
    - `org-root/docs/003-decisions/`.
    - `org-root/docs/004-contracts/`.
    - `org-root/docs/005-cross-cutting/`.
14. **Do NOT create `NEED_CLEARIFICATION.md`.** It is created on demand, on first ambiguity.
15. **Return:** created paths, and any items the caller must still supply (e.g., license, getting-started commands).

---

## Rules

- **MUST** ask before creating anything if `root_path` is not empty.
- **MUST NOT** overwrite existing files.
- **MUST NOT** create `NEED_CLEARIFICATION.md` unless the brief left a gap.
- **MUST** use the canonical directory shape.
- **MUST** keep `README.md` free of product intent, invariants, and contracts.
- **MUST** set `is_org_root` or `org_root` correctly per the topology.

---

## Example

Brief: *"My Tool — a CLI that stores todos in SQLite. Users: individual developers. Non-goals: cloud sync, mobile apps. Invariants: local-first, no network calls."*

Result:

```text
my-tool/
├── README.md
├── AGENT.md                    # is_org_root: true
└── docs/
    ├── INDEX.md
    ├── 002-blueprint/
    │   ├── INDEX.md
    │   ├── 002-001-overview.md
    │   ├── 002-002-users.md
    │   ├── 002-003-non-goals.md
    │   └── 002-004-invariants.md
    ├── 003-decisions/INDEX.md
    ├── 004-contracts/INDEX.md
    ├── 005-cross-cutting/INDEX.md
    └── 006-operational/INDEX.md
```