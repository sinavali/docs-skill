---
title: "Change Surface: Edge Case Hardening, Validation Robustness & Binary Filtering"
author: "Antigravity"
created_date: "2026-10-13"
target_branch: "main"
risk_level: "LOW"
affected_projects:
  - "root"
---

# Change Surface: Edge Case Hardening, Validation Robustness & Binary Filtering

## 1. Intent & Business Rationale
Harden all verification scripts and validators against edge cases identified in the second comprehensive audit round:
1. `validate-change-surface.py`: Support inline bracket list parsing (`[a, b]`), enforce non-empty `affected_projects`, and support numbered list markdown (`1. \`path\``) in Code Surface.
2. `audit-runner.py`: Add `BINARY_EXTENSIONS` filter to skip reading non-text assets line-by-line; check target path existence (exit code 1 if missing); evaluate `full_norm_path` to avoid blind spots during subdirectory execution; broaden `RULE-1.1` regex to catch unconstrained SQL queries without semicolons; exempt dummy/mock credentials in `RULE-5.1`; safely catch JSON decode errors on corrupted baseline files.
3. `verify-agent-manifests.py`: Fail with code 1 if specified `--root` does not exist; strip leading slashes from `adr_reference` paths so `os.path.join` does not treat them as filesystem root.
4. `verify-nx-targets.py`: Fail with code 1 if specified `--root` does not exist.
5. `check-nc-items.py`: Fail with code 1 if explicit `--dir` does not exist (preserving fallback for default `docs/nc`); parse flexible date formats (`YYYY/MM/DD`) in `--as-of-date`; require and validate `resolved_date` on `RESOLVED` NC items.

## 2. Affected Monorepo Projects & Profiles
| Project Path | Architectural Profile | Responsibility in this Change |
|---|---|---|
| `root` | Root Governance | Update scripts, validators, and unit tests across the repository |

## 3. Code Surface (Targeted Symbols & Files)

### Added Files
- `docs/changes/2026-10-13-robustness-and-edge-case-hardening.md`: Change Surface document.

### Modified Files
- `scripts/validate-change-surface.py`: Bracket list parsing, non-empty list validation, and numbered list support.
- `scripts/audit-runner.py`: Binary extension filter, target path existence check, full path normalization, regex hardening, and corrupted baseline protection.
- `scripts/verify-agent-manifests.py`: Root existence check and leading slash ADR path stripping.
- `scripts/verify-nx-targets.py`: Root existence check.
- `scripts/check-nc-items.py`: Explicit dir existence check, flexible as_of_date parsing, and resolved_date verification.
- `tests/test_validate_change_surface.py`: Added tests for numbered lists, inline bracket lists, and empty project lists.
- `tests/test_audit_runner.py`: Added tests for missing scope, binary exclusion, dummy secrets, unconstrained SQL, and corrupted baseline JSON.
- `tests/test_verify_agent_manifests.py`: Added tests for missing root and leading slash ADR references.
- `tests/test_verify_nx_targets.py`: Added test for missing root.
- `tests/test_check_nc_items.py`: Added tests for slash dates, explicit missing dir, and resolved items missing resolved_date.

## 4. Test Surface

### Unit & Domain Tests
- `tests/test_validate_change_surface.py`: 9 tests passing.
- `tests/test_check_nc_items.py`: 10 tests passing.
- `tests/test_verify_nx_targets.py`: 5 tests passing.
- `tests/test_verify_agent_manifests.py`: 7 tests passing.
- `tests/test_audit_runner.py`: 18 tests passing.

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
| Regressions in script parsing | Low | Medium | Automated test suite with 49 tests passing |

### Rollback Strategy
Revert commit on `main`.
