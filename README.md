# enterprise-product

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Monorepo: Nx](https://img.shields.io/badge/Monorepo-Nx-143055.svg)](https://nx.dev)
[![Architecture: DDD%20%2B%20Hexagonal](https://img.shields.io/badge/Architecture-DDD%20%2B%20Hexagonal-8A2BE2.svg)](references/architectural-profiles.md)

**The supreme enterprise gatekeeper and engineering operating system for polyglot monorepos.**

`enterprise-product` enforces production-grade rigor, mechanical compliance, and zero-compromise engineering standards. It guarantees that AI agents and human contributors uphold architectural integrity, value-driven testing, and strict quality gates before any work is considered done.

---

## Core Tenets

1. **Single Monorepo Standard**: Every product is managed at the root by a deterministic DAG task orchestrator (with **Nx** as reference standard: `nx affected`, project graphs, distributed caching, and standard target contracts across Go, C#, Dart, Swift, Rust, PHP, and TypeScript).
2. **Hierarchical Governance (`AGENT.md`)**: Root enterprise inviolables cascade down to per-project `AGENT.md` manifests. Subprojects specialize configuration but cannot override Tier 1 directives.
3. **Four Architectural Profiles**:
   - **Profile A (Backend & Core Services)**: Domain-Driven Design (DDD) + Hexagonal Architecture (Ports & Adapters). Zero framework coupling in domain logic. Transactional outbox for event publishing.
   - **Profile B (Web Applications)**: Clean Component & State Layering, SSR/SPA hydration safety, accessibility (WCAG 2.2 AA), strict bundle budgets.
   - **Profile C (Mobile Clients - Native & Cross-Platform)**: Clean Architecture + Unidirectional State Flow, hardware-backed encrypted storage (Keychain/KeyStore/SQLCipher), offline-first sync.
   - **Profile D (Shared Contracts & Core Libraries)**: Contract-first (OpenAPI 3.1 / Protobuf v3), strict SemVer, zero ambient side-effects.
4. **Value-Driven Testing Matrix**:
   - Domain logic: $\ge 95\%$ Line and $\ge 95\%$ Branch coverage.
   - Infrastructure & Adapters: $\ge 80\%$ Line coverage via **real ephemeral containers (Testcontainers/Podman)**; engine-substitution emulators (e.g. SQLite for PostgreSQL) are strictly forbidden.
   - UI: Complete 4-state coverage (Loading, Empty, Success, Error).
5. **Structural Bounding & Anti-Sprawl Hygiene**:
   - Hard file size ceiling $\le 800$ lines (soft target $\le 400$ lines).
   - Maximum directory depth $\le 6$ levels from project root.
   - Co-location of tightly coupled domain artifacts over micro-file fragmentation ($< 20$ lines).
   - Zero generic dumping grounds (`utils/`, `helpers/`, `misc/`, `common/`).
6. **Pre-Implementation Change Surface**: No non-trivial code modification is permitted without an approved and mechanically validated Change Surface (`CHANGE_SURFACE.md` or `docs/changes/`).
7. **2-Pass PR Self-Audit & Merge Protocol**: Mandatory self-auditing across the 10 Enterprise Dimensions. Automated squash-merging (`gh pr merge --squash`) only when 0 blocking defects remain and CI is green; immediate escalation on persistent defects.
8. **Complete Documentation & NC Protocol**: Ambiguities are recorded as `NEED_CLARIFICATION` (NC) items. Open items older than 14 days mechanically block PR merges. Expand/Contract zero-downtime database migrations.

---

## Repository Structure

```text
enterprise-product/
├── SKILL.md                          # Main skill entrypoint (modes: plan, implement, audit, verify, pr-audit)
├── LICENSE                           # MIT License
├── README.md                         # This guide
├── references/                       # In-depth architectural & operational specifications
│   ├── core-directives.md            # Prime Directives P0–P10 & Tier 1/2/3 Master Rulebook
│   ├── execution-engine.md           # Tool batching, compound commands, context hygiene & lossless density
│   ├── static-analysis-matrix.md     # Polyglot strict compiler & static analysis matrix
│   ├── architectural-profiles.md     # Profile A (DDD), Profile B (Web), Profile C (Flutter), Profile D (Contracts)
│   ├── monorepo-nx-standard.md       # Root Nx orchestration & project.json target contracts
│   ├── agent-hierarchy-spec.md       # AGENT.md schema, inheritance rules, and precedence
│   ├── audit-taxonomy.md             # The 10-Dimension Enterprise Audit Guide & checklists
│   ├── testing-matrix.md             # Value-driven testing rules, testcontainers, coverage gates
│   ├── vcs-pr-protocol.md            # GitHub Flow, 2-Pass PR Self-Audit algorithm, branch gates
│   ├── documentation-system.md       # Change Surface, ADR workflow, doc indexing, drift checks
│   └── nc-protocol.md                # NEED_CLARIFICATION schema, lifecycle, and 14-day escalation
├── templates/                        # Ready-to-use production templates
│   ├── profiles/                     # Canonical Nx project.json templates (Go, Rust, Next.js, Flutter, Contracts)
│   ├── outbox-migration.sql          # Transactional Outbox pattern SQL schema
│   ├── CHANGE_SURFACE.template.md    # Pre-implementation Change Surface template
│   ├── NEED_CLARIFICATION.template.md# NC item definition template
│   ├── ADR.template.md               # Architecture Decision Record template
│   ├── AGENT.template.md             # Per-project AGENT.md manifest template
│   ├── AUDIT_REPORT.template.md      # Multi-dimensional audit output template
│   ├── PR_CONTRACT.template.md       # GitHub PR description & checklist contract
│   ├── project-target.template.json  # Standardized Nx project.json target contract
│   ├── ci-workflow.template.yml      # GitHub Actions enterprise CI workflow (Nx + Audits)
│   └── pre-commit-config.template.yaml # Git pre-commit hook configuration for local compliance
├── scripts/                          # Mechanical verification and validation CLI tooling
│   ├── bin/                          # Executable wrappers (ep, validate-change-surface, etc.)
│   ├── ep.py                         # Unified EP-OS CLI (surface, migration, graph, init, worktree, audit, verify)
│   ├── validate-change-surface.py    # Validates Change Surface presence and schema
│   ├── check-nc-items.py             # Parses open NC items, flags 14-day merge blockers
│   ├── audit-runner.py               # Runs/scaffolds the 10-dimension audit (with --diff and baselines)
│   ├── verify-nx-targets.py          # Ensures every project implements standard Nx targets
│   └── verify-agent-manifests.py     # Validates syntax and inheritance of all AGENT.md files
└── tests/                            # Self-tests validating the skill's scripts and templates
```

---

## The 10-Dimension Enterprise Audit Suite

Every audit evaluates changes across 10 critical dimensions:

1. **Scalability & Capacity**: Algorithmic complexity, indexing, connection pooling, memory streaming.
2. **Structural Maintainability & Modularity**: Profile conformance, pure domain boundaries, zero circular dependencies.
3. **Fault Tolerance & Resilience**: Explicit timeouts on all remote calls, retries with exponential backoff & jitter, circuit breakers.
4. **Data Integrity & Concurrency**: Race condition prevention, atomic transaction boundaries, UTC Storage Convention.
5. **Security & Zero-Trust**: SQL injection prevention, authentication/authorization checks, zero hardcoded credentials.
6. **Observability & Operability**: Structured JSON logging, distributed trace context propagation, `/healthz` and `/readyz` probes.
7. **Contract & Schema Drift**: OpenAPI/Protobuf synchronization, SemVer compliance, zero unversioned breaking changes.
8. **Code Quality & Typing Strictness**: Strict null safety, no raw `any` types, no swallowed exceptions.
9. **Documentation & Spec Drift**: Change Surface conformance, mandatory ADRs for Tier 2 deviations, 0 aged NC items.
10. **Test Fidelity & Assertion Quality**: Real ephemeral containers (Testcontainers/Podman), failure path testing, $\ge 95\%$ domain coverage.

---

## Operational Modes

When AI agents interact with the repository, they declare and operate under one of seven distinct modes:

| Mode | Purpose | Command / Workflow |
|---|---|---|
| `plan` | Analyzes task, traces impact, generates and validates `Change Surface` | `ep surface validate CHANGE_SURFACE.md` |
| `investigate` | Read-only codebase reconnaissance, structural search, root cause isolation | `ast-grep scan` / log analysis |
| `scaffold` | Generates compliant subprojects from profile target templates | `ep init <name> --profile <A\|B\|C\|D> --lang <stack>` |
| `implement` | Executes TDD implementation strictly bounded to declared surface | `ep surface check-diff` && `nx affected -t test` |
| `audit` | Runs the 10-Dimension Enterprise Audit; outputs scorecard | `ep audit --diff origin/main` |
| `verify` | Runs mechanical gates: Nx targets, manifests, NC items, migrations | `ep verify` && `ep migration check --diff` |
| `pr-audit` | Executes 2-Pass PR Self-Audit protocol; verifies CI, merges or escalates | `gh pr merge --squash` |

---

## Installation & Usage

### 1. Adding to an AI Agent Platform
Clone or install this skill into your agent's skills directory:
```bash
git clone https://github.com/sinavali/enterprise-product.git ~/.gemini/config/skills/enterprise-product
```

### 2. Monorepo Integration
Copy the standard CI workflow, pre-commit configuration, and target templates into your monorepo:
```bash
cp templates/ci-workflow.template.yml .github/workflows/ci.yml
cp templates/pre-commit-config.template.yaml .pre-commit-config.yaml
cp templates/profiles/go-service-project.json services/my-service/project.json
cp templates/AGENT.template.md services/my-service/AGENT.md

# Install local git hooks
pre-commit install --hook-type pre-commit --hook-type pre-push
```

### 3. Unified Mechanical CLI (`ep`)
All compliance checks are accessible via the zero-dependency `ep` CLI tool:
```bash
# Check git diff against declared Change Surface (blast-radius guard)
ep surface check-diff

# Scan database migrations for destructive zero-downtime alterations
ep migration check --diff

# Generate live architecture topology diagram in Mermaid format
ep graph --format mermaid

# Scaffold a new fully compliant Profile A backend service in Go
ep init billing-service --profile A --lang go

# Run 10-Dimension Audit scoped to active PR git diff
ep audit --diff origin/main

# Run full mechanical gatekeeper suite (Nx targets, AGENT manifests, NC expiration)
ep verify
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.