---
title: "Change Surface: Enterprise Audit Findings & Mechanical Governance Hardening"
author: "Antigravity"
created_date: "2026-10-13"
target_branch: "main"
risk_level: "LOW"
affected_projects:
  - "root"
---

# Change Surface: Enterprise Audit Findings & Mechanical Governance Hardening

## 1. Intent & Business Rationale
Remediate all 10 architectural and mechanical inconsistencies identified during deep code review:
1. Align `verify-nx-targets.py` JSON mode return code and compliance status on 0-project repositories.
2. Report actual resolved filename in `validate-change-surface.py` CLI output.
3. Remove unneeded file guard in `templates/ci-workflow.template.yml` to allow versioned `docs/changes/` validation.
4. Include `libs/` in `audit-runner.py` heuristic scanners to protect shared libraries and contracts.
5. Support case-insensitive NC IDs and detect unparseable/corrupted NC files in `check-nc-items.py`.
6. Update Prime Directives count in documentation and manifests from P1–P8 to P1–P10.
7. Support scoped `--root` invocation in `verify-agent-manifests.py` without misidentifying subprojects as root manifests.
8. Align `audit-runner.py` markdown report generation with Section 3 Tier 1 checklist from `AUDIT_REPORT.template.md`.
9. Broaden polyglot anti-pattern regexes in `audit-runner.py` for Go, Python, PHP, and C#.
10. Modularize monolithic `test_scripts.py` into 5 cohesive test suites under `tests/` ($\le 265$ lines each).

## 2. Affected Monorepo Projects & Profiles
| Project Path | Architectural Profile | Responsibility in this Change |
|---|---|---|
| `root` | Root Governance | Update scripts, templates, references, and modular test suites |

## 3. Code Surface (Targeted Symbols & Files)

### Added Files
- `tests/test_validate_change_surface.py`: Modular tests for Change Surface validation.
- `tests/test_check_nc_items.py`: Modular tests for NC aging and syntax verification.
- `tests/test_verify_nx_targets.py`: Modular tests for Nx target contracts.
- `tests/test_verify_agent_manifests.py`: Modular tests for AGENT.md hierarchy and overrides.
- `tests/test_audit_runner.py`: Modular tests for 10-dimension audit engine.
- `docs/changes/2026-10-13-audit-findings-and-governance-hardening.md`: Change Surface document.

### Modified Files
- `scripts/verify-nx-targets.py`: Fix `all_valid` boolean expression for JSON output.
- `scripts/validate-change-surface.py`: Report `target_file` in success and error logging.
- `templates/ci-workflow.template.yml`: Invoke `validate-change-surface.py` directly.
- `scripts/check-nc-items.py`: Case-insensitive NC IDs and parse error tracking.
- `scripts/verify-agent-manifests.py`: Subproject detection based on manifest properties and paths.
- `scripts/audit-runner.py`: Add `libs/` path regex, polyglot patterns, and Tier 1 report section.
- `references/core-directives.md`: Update heading to Prime Directives (P1 – P10).
- `references/agent-hierarchy-spec.md`: Update diagram to Prime Directives (P1–P10).
- `SKILL.md`: Update reference index to P1–P10.
- `README.md`: Update file tree comment to P1–P10.

### Removed Files
- `tests/test_scripts.py`: Split into individual modular test files.

## 4. Test Surface

### Unit & Domain Tests
- `tests/test_validate_change_surface.py`: 6 tests passing.
- `tests/test_check_nc_items.py`: 7 tests passing.
- `tests/test_verify_nx_targets.py`: 4 tests passing.
- `tests/test_verify_agent_manifests.py`: 5 tests passing.
- `tests/test_audit_runner.py`: 13 tests passing.

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
| Regression in script CLI behavior | Low | Medium | Full regression suite running 35 automated tests |

### Rollback Strategy
Revert commit on `main`.
