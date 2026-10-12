---
title: "Change Surface: Comprehensive Audit Remediations & Polyglot Hardening"
author: "Antigravity"
created_date: "2026-10-13"
target_branch: "main"
risk_level: "LOW"
affected_projects:
  - "root"
---

# Change Surface: Comprehensive Audit Remediations & Polyglot Hardening

## 1. Intent & Business Rationale
Implement all 10 fixes identified in the third comprehensive audit round:
1. `audit-runner.py`: Expand `RULE-10.1` and `RULE-10.2` regexes to capture Go (`*_test.go`), Python (`test_*.py`), and `tests/` directories; add `packages/` to subproject scopes; expand polyglot ORM patterns for Java, Kotlin, and Rust; compute directory nesting depth relative to subproject root; support dict-wrapped baseline JSON files; add backticks to `NEED_CLARIFICATION` in Section 3 report output.
2. `verify-agent-manifests.py`: Add all missing Tier 1 directives (`max-dir-depth`, `expand-contract`, `change-surface`, and aliases) to `TIER_1_BANNED_OVERRIDES`.
3. `check-nc-items.py`: Add inline bracket list parsing (`affected_projects: ["a", "b"]`).
4. `validate-change-surface.py`: Validate `created_date` format; validate that Section 4 (Test Surface) explicitly lists test targets, suites, or justified N/A status.

## 2. Affected Monorepo Projects & Profiles
| Project Path | Architectural Profile | Responsibility in this Change |
|---|---|---|
| `root` | Root Governance | Update scripts, validators, and unit tests |

## 3. Code Surface (Targeted Symbols & Files)

### Added Files
- `docs/changes/2026-10-13-comprehensive-audit-remediations.md`: Change Surface document.

### Modified Files
- `scripts/audit-runner.py`: Scanners, subproject depth calculation, baseline dict parsing, and template alignment.
- `scripts/verify-agent-manifests.py`: Complete Tier 1 banned overrides list.
- `scripts/check-nc-items.py`: Bracket list parsing.
- `scripts/validate-change-surface.py`: Date format and Test Surface target checks.
- `tests/test_audit_runner.py`: Tests for Go/Python test conventions, packages directory, subproject depth, and dict baseline.
- `tests/test_verify_agent_manifests.py`: Tests for additional Tier 1 overrides.
- `tests/test_check_nc_items.py`: Tests for bracket list parsing.
- `tests/test_validate_change_surface.py`: Tests for date format and Test Surface targets.

## 4. Test Surface

### Unit & Domain Tests
- `tests/test_validate_change_surface.py`: 12 tests passing.
- `tests/test_check_nc_items.py`: 11 tests passing.
- `tests/test_verify_nx_targets.py`: 5 tests passing.
- `tests/test_verify_agent_manifests.py`: 8 tests passing.
- `tests/test_audit_runner.py`: 22 tests passing.

### Integration Tests (Real Ephemeral Containers)
- N/A for static verification tooling; container bans and database integration rules tested via mock fixtures.

### Failure & Resilience Tests
- All test suites verify failure exit codes and defect reporting on corrupt, missing, or malformed inputs.

### Concurrency Tests
- N/A for CLI scripts.

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
| Regressions in script parsing | Low | Medium | Automated test suite with 58 tests passing |

### Rollback Strategy
Revert commit on `main`.
