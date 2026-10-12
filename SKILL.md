---
name: enterprise-product
description: Supreme enterprise gatekeeper and engineering operating system for polyglot monorepos. Enforces production-grade rigor, DDD/Hexagonal architecture, Nx orchestration, 10-dimension audits, value-driven testing, Change Surfaces, and 2-Pass PR self-audits.
---

# Skill — `enterprise-product`

The **supreme enterprise gatekeeper and engineering operating system** for polyglot monorepos. This skill enforces production-grade rigor, mechanical compliance, and zero-compromise engineering standards. It forbids AI agents from taking unverified shortcuts and mandates strict verification gates before any work is considered done.

---

## 1. Core Operating Principles

1. **Monorepo Standard**: Every product is strictly a single monorepo governed at the root by **Nx** (`nx affected`, target delegations, dependency graph validation).
2. **Hierarchical Governance (`AGENT.md`)**: Root enterprise inviolables cascade down to project-level `AGENT.md` files. Subprojects specialize configuration but can never violate Tier 1 directives.
3. **Architectural Profiles**:
   - **Profile A (Backend & Core Services)**: Domain-Driven Design (DDD) + Hexagonal Architecture (Ports & Adapters). Zero framework coupling in pure domain logic. Transactional outbox for events.
   - **Profile B (Web Applications)**: Clean Component & State Layering, SSR/SPA hydration safety, strict accessibility (WCAG 2.2 AA), bundle budgets, zero-trust web security.
   - **Profile C (Mobile Clients - Native & Cross-Platform)**: Clean Architecture + Unidirectional State Flow, hardware-backed encrypted storage (Keychain/KeyStore/SQLCipher), offline-first sync, battery/lifecycle awareness.
   - **Profile D (Shared Contracts & Core Libraries)**: Contract-first (OpenAPI/Protobuf), strict SemVer, zero ambient side-effects.
4. **Value-Driven Testing Matrix**:
   - Domain logic: $\ge 95\%$ line & branch coverage.
   - Adapters & Infrastructure: $\ge 80\%$ line coverage with **real ephemeral containers (Testcontainers/Podman)**; engine-substitution emulators (e.g. SQLite for Postgres) are strictly prohibited.
   - Mandatory test types: Domain/Unit, Integration, Contract, Failure/Resilience (timeouts, circuit breakers), Concurrency/Race conditions.
5. **Structural Bounding & Anti-Sprawl Rules**:
   - Files $\le 800$ lines (soft target $\le 400$ lines).
   - Maximum directory depth $\le 6$ levels from project root.
   - Co-location of tightly coupled domain artifacts over excessive micro-file fragmentation ($< 20$ lines).
   - Zero generic dumping grounds (`utils/`, `helpers/`, `misc/`, `common/`).
6. **Pre-Implementation Change Surface**: Non-trivial modifications require a declared and validated `Change Surface` artifact before code changes begin.
7. **2-Pass PR Self-Audit & Automated Merge Protocol**:
   - Pass 1: Full diff audit against enterprise checklist ➔ Apply fixes ➔ Commit ➔ Push.
   - Pass 2: Cumulative diff re-audit + CI verification. If 0 blocking defects and CI is green ➔ `gh pr merge --squash`. Escalates to human review on persistent defects or branch protection requirements.
8. **Complete Documentation & NC Protocol**:
   - Ambiguities are recorded as formal `NEED_CLARIFICATION` (NC) items. Open NC items older than 14 days mechanically block merges.
   - ADRs for all architectural modifications. Expand/Contract pattern for zero-downtime database migrations.

---

## 2. Operational Modes

Agents operate under one of five distinct modes. When invoked, determine or declare the active mode:

| Mode | Purpose | Modifies Files | Required Pre-condition |
|---|---|---|---|
| `plan` | Analyzes task, traces impact graph, generates & validates `Change Surface` artifact. | Yes (`CHANGE_SURFACE.md`) | Task request received. |
| `implement` | Executes TDD implementation according to Architectural Profile and testing matrix. | Yes (Code & Tests) | Validated `Change Surface` exists. |
| `audit` | Runs the 10-Dimension Enterprise Audit across affected projects; outputs audit report. | Yes (`AUDIT_REPORT.md`) | Code implementation completed. |
| `verify` | Runs mechanical scripts: Nx target checks, Change Surface validation, NC aging check, AGENT.md linting. | No | Staged or committed changes. |
| `pr-audit` | Executes 2-Pass PR Self-Audit protocol, verifies CI, merges or escalates. | Yes (Fix commits / PR) | PR created or ready to push. |

---

## 3. Mode Execution Workflows

### Mode: `plan`
1. Load `references/documentation-system.md` and `templates/CHANGE_SURFACE.template.md`.
2. Inspect the request to identify affected monorepo projects (`project.json`), domain entities, APIs, and infrastructure.
3. If any business requirement or contract ambiguity is identified, record a formal NC item using `templates/NEED_CLARIFICATION.template.md` (see `references/nc-protocol.md`). Do not invent unverified assumptions.
4. Draft the Change Surface artifact covering:
   - Problem statement and explicit business intent.
   - Affected Projects and Architectural Profile mappings.
   - Code Surface: Exact file paths and symbols targeted for modification.
   - Test Surface: Unit, integration (ephemeral containers), failure, and contract test suites.
   - Invariants and non-negotiables preserved.
   - Risk matrix and rollback strategy.
5. Run `python3 scripts/validate-change-surface.py <path_to_change_surface>` to verify structural compliance.

### Mode: `implement`
1. Read the approved `Change Surface` and the relevant project's `AGENT.md`.
2. Load `references/architectural-profiles.md` and `references/testing-matrix.md`.
3. Follow strict Test-Driven Development (TDD):
   - Step A: Author red tests in the designated Test Surface (domain invariants, failure edge cases).
   - Step B: Implement pure domain entities and use cases (Profile A/B/C/D rules apply).
   - Step C: Implement adapters and infrastructure using real containerized integrations (Podman/Testcontainers).
   - Step D: Ensure all timestamps are UTC, all external boundaries use typed contracts, and zero mock databases are used for integration tests.
4. Run project test suite via `nx test <project>` and linters via `nx lint <project>`.

### Mode: `audit`
1. Load `references/audit-taxonomy.md` and `templates/AUDIT_REPORT.template.md`.
2. Execute the 10-Dimension Enterprise Audit across the target diff or affected projects:
   - Dimension 1: Scalability & Capacity
   - Dimension 2: Structural Maintainability & Modularity
   - Dimension 3: Fault Tolerance & Resilience
   - Dimension 4: Data Integrity & Concurrency
   - Dimension 5: Security & Zero-Trust
   - Dimension 6: Observability & Operability
   - Dimension 7: Contract & Schema Drift
   - Dimension 8: Code Quality & Typing Strictness
   - Dimension 9: Documentation & Spec Drift
   - Dimension 10: Test Fidelity & Assertion Quality
3. Classify all findings strictly: `blocking` (must resolve before PR), `suggestion`, or `nit`.
4. Run `python3 scripts/audit-runner.py --scope <project-or-diff>` to scaffold and record findings.

### Mode: `verify`
1. Run mechanical validation tooling:
   - `python3 scripts/verify-nx-targets.py`: Verifies every project in the monorepo defines the required standard Nx targets (`lint`, `test`, `build`, `audit`).
   - `python3 scripts/verify-agent-manifests.py`: Verifies syntax and inheritance of all `AGENT.md` files.
   - `python3 scripts/check-nc-items.py --max-age 14`: Scans all open NC items and flags any items $\ge 14$ days old as blocking.
   - `python3 scripts/validate-change-surface.py`: Validates active Change Surface artifact.
2. Halt if any mechanical check fails.

### Mode: `pr-audit`
1. Load `references/vcs-pr-protocol.md`.
2. **Push & PR Initiation**: Push feature branch `feat/<scope>-<desc>` or `fix/<scope>-<desc>` and create PR with `templates/PR_CONTRACT.template.md`.
3. **Pass 1 (Full Diff Self-Audit)**:
   - Inspect the entire cumulative diff (`git diff origin/main...HEAD`).
   - Audit against the 10 dimensions and `PR_CONTRACT.md` checklist.
   - If any defects (blocking or quality regressions) are found, apply code fixes immediately, run `nx affected --target=test`, commit with descriptive Conventional Commit, and push.
4. **Pass 2 (Cumulative Diff Re-Audit & Verification)**:
   - Re-inspect cumulative diff.
   - Run full CI verification: `nx affected --target=lint && nx affected --target=test && nx affected --target=build`.
   - Run `python3 scripts/check-nc-items.py --block-on-open-aged`.
   - If **0 blocking defects** and CI is fully green:
     - If repository allows automated merge and no branch protection blocker exists: execute `gh pr merge --squash --delete-branch`.
   - **Escalation Gate**: If defects remain after Pass 2, CI is red, or external human review is mandated by branch protection, immediately halt, post the audit failure report to the PR, and attach the label `needs/review`.

---

## 4. Reference Index & Progressive Disclosure

Do not load all reference files simultaneously. Read on demand based on current mode:

- `references/core-directives.md` — Prime Directives P1–P8, Tier 1/2/3 Master Rulebook, UTC conventions, self-hosted preferences.
- `references/architectural-profiles.md` — Deep profiles for Backend (DDD/Hexagonal), Web (Next/Nuxt), Mobile (Flutter), Shared Contracts.
- `references/monorepo-nx-standard.md` — Root Nx orchestration, project.json contracts, target delegation.
- `references/agent-hierarchy-spec.md` — AGENT.md schema, cascading inheritance, overrides vs invariants.
- `references/audit-taxonomy.md` — 10-Dimension Audit Guide, verification steps, scoring.
- `references/testing-matrix.md` — Value-driven testing rules, testcontainers, failure testing, coverage gates.
- `references/vcs-pr-protocol.md` — GitHub Flow, Conventional Commits, 2-Pass PR Self-Audit algorithm.
- `references/documentation-system.md` — Change Surface lifecycle, ADRs, file-level docs, doc drift checks.
- `references/nc-protocol.md` — NEED_CLARIFICATION schema, lifecycle, 14-day escalation mechanics.

---

## 5. Templates & Script Tooling Index

### Templates (`templates/`)
- `templates/CHANGE_SURFACE.template.md` — Pre-implementation Change Surface template.
- `templates/NEED_CLARIFICATION.template.md` — NC item definition template.
- `templates/ADR.template.md` — Architecture Decision Record template.
- `templates/AGENT.template.md` — Per-project AGENT.md manifest template.
- `templates/AUDIT_REPORT.template.md` — Multi-dimensional audit output template.
- `templates/PR_CONTRACT.template.md` — PR description contract and self-audit checklist.
- `templates/project-target.template.json` — Standardized Nx `project.json` targets.
- `templates/ci-workflow.template.yml` — GitHub Actions enterprise CI workflow.
- `templates/pre-commit-config.template.yaml` — Git pre-commit hook configuration for local governance.

### Verification CLI Tooling (`scripts/` and `scripts/bin/`)
- `scripts/validate-change-surface.py` — Change Surface schema and completeness validator.
- `scripts/check-nc-items.py` — NC item parser, age tracker, and 14-day merge blocking detector.
- `scripts/audit-runner.py` — Automated 10-dimension audit scaffold and runner.
- `scripts/verify-nx-targets.py` — Standard Nx target validator across all `project.json` files.
- `scripts/verify-agent-manifests.py` — Schema validator and inheritance checker for `AGENT.md`.
- `scripts/bin/` — Executable wrapper binaries for all validation scripts.