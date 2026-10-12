---
title: "Change Surface: Local Pre-Commit Governance Hook Configuration"
author: "Antigravity"
created_date: "2026-10-13"
target_branch: "main"
risk_level: "LOW"
affected_projects:
  - "root"
---

# Change Surface: Local Pre-Commit Governance Hook Configuration

## 1. Intent & Business Rationale
Add standard pre-commit hook configuration template to enforce mechanical enterprise compliance (manifest checks, Nx target contracts, NC aging, and change surface validation) locally on developers' machines before commit and push.

## 2. Affected Monorepo Projects & Profiles
| Project Path | Architectural Profile | Responsibility in this Change |
|---|---|---|
| `root` | Root Governance | Add pre-commit configuration template and update skill metadata |

## 3. Code Surface (Targeted Symbols & Files)

### Added Files
- `templates/pre-commit-config.template.yaml`: Reusable `.pre-commit-config.yaml` template configuring local pre-commit and pre-push hooks calling skill validation scripts.
- `docs/changes/2026-10-13-pre-commit-enforcement.md`: Change Surface document.

### Modified Files
- `SKILL.md`: Register pre-commit template in template index.
- `README.md`: Document pre-commit configuration in repository tree and monorepo setup instructions.

## 4. Test Surface

### Unit & Domain Tests
- `tests/test_scripts.py`: Verifies all validation tools (`validate-change-surface.py`, `check-nc-items.py`, `verify-agent-manifests.py`, `verify-nx-targets.py`, and `audit-runner.py`) invoked by pre-commit hooks.

### Integration Tests (Real Ephemeral Containers)
- N/A for static configuration templates; mechanical test suite executed directly.

### Failure & Resilience Tests
- `tests/test_scripts.py`: Verifies failure detection and error codes for non-compliant surfaces, invalid manifests, missing targets, and blocking NC items.

### Concurrency Tests
- N/A for pre-commit static configuration.

## 5. Invariants & Non-Negotiables Preserved
- [x] Tier 1: Pure domain logic remains 100% free of framework or ORM imports.
- [x] Tier 1: Real container integration tests (no engine-substitution emulators like SQLite for Postgres).
- [x] Tier 1: All stored and wire timestamps use UTC ISO-8601 (`Z`).
- [x] Tier 1: Directory nesting depth does not exceed 6 levels from project root.
- [x] Tier 1: Database migrations follow Expand/Contract pattern for zero-downtime rollout.
- [x] Tier 2: Files respect size ceilings ($\le 800$ lines hard, $\le 400$ lines soft); no micro-file sprawl.
- [x] Tier 2: Domain test coverage maintains $\ge 95\%$ line & branch coverage; adapters $\ge 80\%$.
- [x] Tier 2: Transactional outbox pattern used for domain events published to brokers.
- [x] Tier 2: Backward compatibility of existing API contracts preserved.

## 6. Risk Matrix & Rollback Strategy
| Risk Description | Probability | Impact | Mitigation Strategy |
|---|---|---|---|
| Misconfigured pre-commit hook paths | Low | Low | Validated hook entrypoints against repository layout |

### Rollback Strategy
Revert commit or remove `.pre-commit-config.yaml` from monorepo root.
