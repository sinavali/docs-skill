# VCS & Pull Request Protocol

This specification defines the GitHub Flow lifecycle, commit hygiene, labeling taxonomy, and the mandatory **2-Pass PR Self-Audit and Automated Merge Protocol**.

---

## 1. Branching & Commit Conventions

### 1.1 Branch Naming Standard
All development branches branch off `main` using one of the following prefixes:
- `feat/<scope>-<description>`: New business capabilities or feature additions.
- `fix/<scope>-<description>`: Bug fixes, security patches, or error corrections.
- `refactor/<scope>-<description>`: Structural code improvements without behavioral change.
- `chore/<scope>-<description>`: Dependency bumps, build script changes, tooling updates.
- `rework/<scope>`: Comprehensive architectural migrations.

### 1.2 Conventional Commits
All commits must strictly follow the Conventional Commits specification:
```text
<type>(<scope>): <short summary in imperative mood>

[optional body with rationale, affected components, and context]

[optional footer: Closes #123, Refs #456]
```
Allowed types: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `perf`, `build`, `ci`.

---

## 2. PR Label Taxonomy

Pull Requests must maintain accurate lifecycle labels:

| Label | Meaning |
|---|---|
| `status/draft` | Work in progress, not ready for self-audit. |
| `status/pass-1-in-progress` | Agent is conducting Pass 1 Self-Audit. |
| `status/pass-2-in-progress` | Agent is conducting Pass 2 Cumulative Diff Re-Audit. |
| `status/ready-to-merge` | Both audit passes succeeded (0 blocking defects), CI green. |
| `needs/review` | Escalated to human review due to residual defects or protected branch rules. |
| `blocked/nc` | Blocked by unresolved `NEED_CLARIFICATION` item older than 14 days. |
| `security` | Touches authentication, authorization, cryptography, or sensitive data. |

---

## 3. The 2-Pass PR Self-Audit Protocol

Every Pull Request authored or processed by an AI agent must strictly follow this closed-loop audit protocol:

```text
               ┌─────────────────────────────────────────┐
               │         Branch Push & Open PR           │
               │   (Attach PR_CONTRACT.template.md)      │
               └────────────────────┬────────────────────┘
                                    │
                                    ▼
               ┌─────────────────────────────────────────┐
               │    PASS 1: Full Diff Self-Audit         │
               │  - Inspect full diff vs 10 Dimensions   │
               │  - Identify defects & violations        │
               └────────────────────┬────────────────────┘
                                    │
                         Defects found?
                         ├── YES ──► Fix code ➔ Commit ➔ Push
                         └── NO  ──┐
                                   ▼
               ┌─────────────────────────────────────────┐
               │  PASS 2: Cumulative Re-Audit & Gates    │
               │  - Re-verify cumulative diff            │
               │  - Run CI (nx affected lint/test/build) │
               │  - Run check-nc-items & verify scripts  │
               └────────────────────┬────────────────────┘
                                    │
                     Pass 2 Clean & CI Green?
                     ├── NO  ──► ESCALATION GATE (Label needs/review)
                     └── YES ──┐
                               ▼
               ┌─────────────────────────────────────────┐
               │  Automated Merge (or Escalation Gate)   │
               │  - If unblocked: gh pr merge --squash   │
               │  - If branch protection: request review │
               └─────────────────────────────────────────┘
```

### Step 1: Pre-Audit Gate
Before opening the PR:
1. Ensure the Change Surface (`CHANGE_SURFACE.md`) is checked into the branch or embedded in the PR description.
2. Run local tests: `nx affected --target=lint && nx affected --target=test && nx affected --target=build`.
3. Open the PR using `templates/PR_CONTRACT.template.md`.

### Step 2: Pass 1 (Full Diff Self-Audit)
1. Fetch and inspect the entire diff between the PR branch and the base branch:
   ```bash
   git fetch origin main
   git diff origin/main...HEAD
   ```
2. Systematically audit the diff against the **10-Dimension Enterprise Audit Suite** (see `references/audit-taxonomy.md`).
3. If **any blocking defects or quality regressions** are identified:
   - Apply fixes to the code directly.
   - Run tests for affected modules: `nx affected --target=test`.
   - Commit fixes using a conventional commit: `fix(<scope>): self-audit pass 1 remediation`.
   - Push to the remote branch.

### Step 3: Pass 2 (Cumulative Diff Re-Audit & Verification)
1. Fetch and re-audit the cumulative diff across the entire PR (`origin/main...HEAD`).
2. Run mechanical checks:
   ```bash
   python3 scripts/verify-nx-targets.py
   python3 scripts/verify-agent-manifests.py
   python3 scripts/check-nc-items.py --max-age 14
   ```
3. Run full workspace CI target simulation:
   ```bash
   nx affected --target=lint --base=origin/main
   nx affected --target=test --base=origin/main
   nx affected --target=build --base=origin/main
   ```
4. Verify that:
   - Zero blocking defects exist across all 10 dimensions.
   - All tests pass, including container integration tests.
   - No open `NEED_CLARIFICATION` item in the repo is $\ge 14$ days old.

### Step 4: Merge Decision or Escalation Gate
- **Scenario A: 0 Blocking Defects & CI Green & Repository Permits Automated Merge**:
  - The agent executes:
    ```bash
    gh pr merge --squash --delete-branch
    ```
- **Scenario B: Escalation Gate (Human Review Required)**:
  - If any of the following conditions are met:
    1. Blocking defects remain unresolved after Pass 2.
    2. Any CI check fails.
    3. Branch protection rules require human peer code review approval.
    4. An open NC item is $\ge 14$ days old.
  - The agent must **immediately halt**, post the detailed `AUDIT_REPORT.md` as a PR comment, apply the `needs/review` label, and notify the engineering team.
