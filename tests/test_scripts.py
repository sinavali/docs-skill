#!/usr/bin/env python3
"""
Unit and integration tests for enterprise-product CLI scripts and mechanical validators.
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
BIN_DIR = SCRIPTS_DIR / "bin"


class TestValidateChangeSurface(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_valid_change_surface(self):
        file_path = os.path.join(self.temp_dir, "CHANGE_SURFACE.md")
        content = """---
title: "Feature Test"
author: "Engineer 1"
created_date: "2026-10-12"
target_branch: "main"
risk_level: "LOW"
affected_projects:
  - "services/billing"
---

# Change Surface: Feature Test

## 1. Intent & Business Rationale
Implement billing discount recalculation.

## 2. Affected Monorepo Projects & Profiles
| Project | Profile | Responsibility |
|---|---|---|
| services/billing | Profile A | Recalculate invoice |

## 3. Code Surface
- `services/billing/src/domain/discount.ts`: Add discount logic
### Added Files
- `services/billing/src/domain/discount.ts`

## 4. Test Surface
- `services/billing/tests/unit/discount.spec.ts`

## 5. Invariants Preserved
- Pure domain isolation preserved.

## 6. Risk Matrix & Rollback Strategy
- Risk: Low.
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        proc = subprocess.run(
            [str(BIN_DIR / "validate-change-surface"), file_path],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Expected 0, got {proc.returncode}: {proc.stdout} {proc.stderr}")
        self.assertIn("[SUCCESS]", proc.stdout)

    def test_asterisk_bullet_list_passes(self):
        file_path = os.path.join(self.temp_dir, "CHANGE_SURFACE_ASTERISK.md")
        content = """---
title: "Feature Asterisk"
author: "Engineer 2"
created_date: "2026-10-12"
target_branch: "main"
risk_level: "MEDIUM"
affected_projects:
- "services/orders"
---

# Change Surface: Feature Asterisk

## 1. Intent & Business Rationale
Rationale.

## 2. Affected Monorepo Projects & Profiles
Projects.

## 3. Code Surface
* `services/orders/src/domain/order.ts`: Add cancel logic
* `services/orders/src/domain/events.ts`: Add cancelled event

## 4. Test Surface
- `services/orders/tests/unit/order.spec.ts`

## 5. Invariants
Invariants.

## 6. Risk Matrix
Risk.
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        proc = subprocess.run(
            [str(BIN_DIR / "validate-change-surface"), file_path],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Expected 0: {proc.stdout} {proc.stderr}")
        self.assertIn("[SUCCESS]", proc.stdout)

    def test_missing_section_fails(self):
        file_path = os.path.join(self.temp_dir, "CHANGE_SURFACE_BAD.md")
        content = """---
title: "Incomplete"
author: "Engineer"
created_date: "2026-10-12"
target_branch: "main"
risk_level: "LOW"
affected_projects:
  - "services/billing"
---

# Incomplete
## 1. Intent & Business Rationale
Rationale.
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        proc = subprocess.run(
            [str(BIN_DIR / "validate-change-surface"), file_path],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("[ERROR]", proc.stdout)

    def test_bare_wildcard_in_code_surface_fails(self):
        file_path = os.path.join(self.temp_dir, "CHANGE_SURFACE_WILDCARD.md")
        content = """---
title: "Wildcard Test"
author: "Engineer"
created_date: "2026-10-12"
target_branch: "main"
risk_level: "LOW"
affected_projects:
  - "services/billing"
---

# Test
## 1. Intent & Business Rationale
Rationale.
## 2. Affected Monorepo Projects
Projects.
## 3. Code Surface
- `services/billing/*`
*
## 4. Test Surface
Tests.
## 5. Invariants
Invariants.
## 6. Risk Matrix
Risk.
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        proc = subprocess.run(
            [str(BIN_DIR / "validate-change-surface"), file_path],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("bare wildcard", proc.stdout)

    def test_invalid_risk_level_fails(self):
        file_path = os.path.join(self.temp_dir, "CHANGE_SURFACE_RISK.md")
        content = """---
title: "Invalid Risk"
author: "Engineer"
created_date: "2026-10-12"
target_branch: "main"
risk_level: "UNKNOWN_RISK"
affected_projects:
  - "services/billing"
---
# Invalid Risk
## 1. Intent & Business Rationale
Rationale.
## 2. Affected Monorepo Projects
Projects.
## 3. Code Surface
- `services/billing/test.ts`
## 4. Test Surface
Tests.
## 5. Invariants
Invariants.
## 6. Risk Matrix
Risk.
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        proc = subprocess.run(
            [str(BIN_DIR / "validate-change-surface"), file_path],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Invalid risk_level", proc.stdout)


class TestCheckNcItems(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_open_item_under_14_days_passes(self):
        nc_file = os.path.join(self.temp_dir, "NC-001.md")
        content = """---
id: "NC-20261010-001"
status: "OPEN"
created_date: "2026-10-10"
discovered_by: "agent"
affected_projects:
  - "services/order"
---
# NC Item 1
"""
        with open(nc_file, "w", encoding="utf-8") as f:
            f.write(content)

        proc = subprocess.run(
            [
                str(BIN_DIR / "check-nc-items"),
                "--dir",
                self.temp_dir,
                "--as-of-date",
                "2026-10-12",
                "--max-age",
                "14",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Expected 0: {proc.stdout} {proc.stderr}")
        self.assertIn("[OK]", proc.stdout)

    def test_open_item_over_14_days_blocks(self):
        nc_file = os.path.join(self.temp_dir, "NC-OLD.md")
        content = """---
id: "NC-20260901-001"
status: "OPEN"
created_date: "2026-09-01"
discovered_by: "agent"
affected_projects:
  - "services/order"
---
# Old NC Item
"""
        with open(nc_file, "w", encoding="utf-8") as f:
            f.write(content)

        proc = subprocess.run(
            [
                str(BIN_DIR / "check-nc-items"),
                "--dir",
                self.temp_dir,
                "--as-of-date",
                "2026-10-12",
                "--max-age",
                "14",
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("[MERGE BLOCK DETECTED]", proc.stdout)

    def test_iso_timestamp_and_slash_date_formats(self):
        nc_file = os.path.join(self.temp_dir, "NC-ISO.md")
        content = """---
id: "NC-20261010-002"
status: "OPEN"
created_date: "2026-10-10T14:30:00Z"
discovered_by: "agent"
affected_projects:
- "services/order"
---
# ISO Date Item
"""
        with open(nc_file, "w", encoding="utf-8") as f:
            f.write(content)

        proc = subprocess.run(
            [
                str(BIN_DIR / "check-nc-items"),
                "--dir",
                self.temp_dir,
                "--as-of-date",
                "2026-10-12",
                "--max-age",
                "14",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Expected 0: {proc.stdout} {proc.stderr}")
        self.assertIn("[OK]", proc.stdout)

    def test_resolved_item_over_14_days_passes(self):
        nc_file = os.path.join(self.temp_dir, "NC-RESOLVED.md")
        content = """---
id: "NC-20260901-002"
status: "RESOLVED"
created_date: "2026-09-01"
resolved_date: "2026-09-05"
discovered_by: "agent"
---
# Resolved NC Item
"""
        with open(nc_file, "w", encoding="utf-8") as f:
            f.write(content)

        proc = subprocess.run(
            [
                str(BIN_DIR / "check-nc-items"),
                "--dir",
                self.temp_dir,
                "--as-of-date",
                "2026-10-12",
                "--max-age",
                "14",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("[OK]", proc.stdout)

    def test_templates_and_placeholders_ignored(self):
        tmpl_file = os.path.join(self.temp_dir, "NEED_CLARIFICATION.template.md")
        content = """---
id: "NC-YYYYMMDD-001"
status: "OPEN"
created_date: "YYYY-MM-DD"
---
# Template
"""
        with open(tmpl_file, "w", encoding="utf-8") as f:
            f.write(content)

        proc = subprocess.run(
            [
                str(BIN_DIR / "check-nc-items"),
                "--dir",
                self.temp_dir,
                "--as-of-date",
                "2026-10-12",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Found 0 NC items", proc.stdout)


class TestVerifyNxTargets(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compliant_project_json(self):
        proj_dir = os.path.join(self.temp_dir, "services", "auth")
        os.makedirs(proj_dir, exist_ok=True)
        pj_file = os.path.join(proj_dir, "project.json")

        data = {
            "name": "auth-service",
            "tags": ["scope:backend", "profile:a"],
            "targets": {
                "lint": {"executor": "nx:run-commands", "options": {"command": "golangci-lint run"}},
                "test": {"executor": "nx:run-commands", "options": {"command": "go test ./..."}},
                "build": {"executor": "nx:run-commands", "options": {"command": "go build"}},
                "audit": {"executor": "nx:run-commands", "options": {"command": "govulncheck ./..."}},
            },
        }
        with open(pj_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        proc = subprocess.run(
            [str(BIN_DIR / "verify-nx-targets"), "--root", self.temp_dir],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Expected 0: {proc.stdout}")
        self.assertIn("[PASS]", proc.stdout)

    def test_missing_audit_target_fails(self):
        proj_dir = os.path.join(self.temp_dir, "services", "bad")
        os.makedirs(proj_dir, exist_ok=True)
        pj_file = os.path.join(proj_dir, "project.json")

        data = {
            "name": "bad-service",
            "tags": ["scope:backend", "profile:a"],
            "targets": {
                "lint": {"command": "lint"},
                "test": {"command": "test"},
                "build": {"command": "build"},
            },
        }
        with open(pj_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        proc = subprocess.run(
            [str(BIN_DIR / "verify-nx-targets"), "--root", self.temp_dir],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Missing mandatory Nx target: 'audit'", proc.stdout)

    def test_target_with_depends_on_passes(self):
        proj_dir = os.path.join(self.temp_dir, "services", "agg")
        os.makedirs(proj_dir, exist_ok=True)
        pj_file = os.path.join(proj_dir, "project.json")

        data = {
            "name": "agg-service",
            "tags": ["scope:shared", "profile:d"],
            "targets": {
                "lint": {"dependsOn": ["^lint"]},
                "test": {"dependsOn": ["^test"]},
                "build": {"dependsOn": ["^build"]},
                "audit": {"dependsOn": ["^audit"]},
            },
        }
        with open(pj_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        proc = subprocess.run(
            [str(BIN_DIR / "verify-nx-targets"), "--root", self.temp_dir],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Expected 0: {proc.stdout}")
        self.assertIn("[PASS]", proc.stdout)


class TestVerifyAgentManifests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_valid_agent_manifest(self):
        proj_dir = os.path.join(self.temp_dir, "services", "billing")
        os.makedirs(proj_dir, exist_ok=True)
        agent_file = os.path.join(proj_dir, "AGENT.md")

        content = """---
project_name: "billing-service"
profile: "A"
stack: "node-20"
scope: "backend"
owner: "billing-team"
tier_overrides: []
---

# Billing Service Manifest

## 1. Scope & Business Intent
Handles billing and subscriptions.

## 2. Architectural Profile & Boundaries
Profile A (DDD/Hexagonal).

## 3. Local Nx Target Delegations
Local targets.

## 4. Test & Verification Rules
Test rules.
"""
        with open(agent_file, "w", encoding="utf-8") as f:
            f.write(content)

        proc = subprocess.run(
            [str(BIN_DIR / "verify-agent-manifests"), "--root", self.temp_dir],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Expected 0: {proc.stdout}")
        self.assertIn("[PASS]", proc.stdout)

    def test_root_agent_manifest_passes_without_subproject_properties(self):
        root_agent = os.path.join(self.temp_dir, "AGENT.md")
        content = """---
governance: "enterprise-product"
organization: "enterprise"
---

# Root Enterprise Governance Manifest

## Directives
P1 through P8.
"""
        with open(root_agent, "w", encoding="utf-8") as f:
            f.write(content)

        proc = subprocess.run(
            [str(BIN_DIR / "verify-agent-manifests"), "--root", self.temp_dir],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Expected 0: {proc.stdout} {proc.stderr}")
        self.assertIn("[PASS]", proc.stdout)

    def test_illegal_tier_1_override_fails(self):
        proj_dir = os.path.join(self.temp_dir, "services", "illegal")
        os.makedirs(proj_dir, exist_ok=True)
        agent_file = os.path.join(proj_dir, "AGENT.md")

        # Test with underscore variant to verify normalization
        content = """---
project_name: "illegal-service"
profile: "A"
stack: "node-20"
scope: "backend"
owner: "rogue-team"
tier_overrides:
  - rule: "pure_domain"
    adr_reference: "docs/adr/0001.md"
    justification: "We want ORM in domain"
---

# Illegal Manifest
## 1. Scope & Business Intent
Scope.
## 2. Architectural Profile
Profile.
## 3. Local Nx Target
Target.
## 4. Test & Verification
Tests.
"""
        with open(agent_file, "w", encoding="utf-8") as f:
            f.write(content)

        proc = subprocess.run(
            [str(BIN_DIR / "verify-agent-manifests"), "--root", self.temp_dir, "--no-check-adrs"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Illegal Tier 1 override", proc.stdout)

    def test_file_relative_and_symlinked_adr_resolution(self):
        proj_dir = os.path.join(self.temp_dir, "services", "override-service")
        adr_dir = os.path.join(self.temp_dir, "docs", "adr")
        os.makedirs(proj_dir, exist_ok=True)
        os.makedirs(adr_dir, exist_ok=True)

        real_adr = os.path.join(adr_dir, "0042.md")
        with open(real_adr, "w", encoding="utf-8") as f:
            f.write("# ADR 42: Coverage Adjustment\n")

        agent_file = os.path.join(proj_dir, "AGENT.md")
        content = """---
project_name: "override-service"
profile: "B"
stack: "nextjs-14"
scope: "frontend"
tier_overrides:
  - rule: "coverage-threshold"
    adr_reference: "../../docs/adr/0042.md"
---

# Override Service
## 1. Scope & Business Intent
Scope.
## 2. Architectural Profile
Profile.
## 3. Local Nx Target
Target.
## 4. Test & Verification
Tests.
"""
        with open(agent_file, "w", encoding="utf-8") as f:
            f.write(content)

        proc = subprocess.run(
            [str(BIN_DIR / "verify-agent-manifests"), "--root", self.temp_dir],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Expected 0: {proc.stdout} {proc.stderr}")
        self.assertIn("[PASS]", proc.stdout)


class TestAuditRunner(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_clean_directory_passes_audit(self):
        clean_file = os.path.join(self.temp_dir, "service.ts")
        with open(clean_file, "w", encoding="utf-8") as f:
            f.write("export class PureService { compute(): number { return 42; } }\n")

        proc = subprocess.run(
            [str(BIN_DIR / "audit-runner"), "--scope", self.temp_dir, "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        res = json.loads(proc.stdout)
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["total_blocking"], 0)

    def test_banned_patterns_detected_as_blocking(self):
        # 1. ORM in domain
        domain_dir = os.path.join(self.temp_dir, "domain")
        os.makedirs(domain_dir, exist_ok=True)
        bad_domain = os.path.join(domain_dir, "user.ts")
        with open(bad_domain, "w", encoding="utf-8") as f:
            f.write("import { Column } from 'typeorm';\nexport class User {}\n")

        # 2. SQLite in integration test (constructed dynamically)
        tests_dir = os.path.join(self.temp_dir, "tests", "integration")
        os.makedirs(tests_dir, exist_ok=True)
        bad_test = os.path.join(tests_dir, "repo.test.ts")
        bad_snippet = "const db = createConnection({ type: '" + "sqlite', database: ':" + "memory:' });\n"
        with open(bad_test, "w", encoding="utf-8") as f:
            f.write(bad_snippet)

        proc = subprocess.run(
            [str(BIN_DIR / "audit-runner"), "--scope", self.temp_dir, "--json"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        res = json.loads(proc.stdout)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertGreaterEqual(res["total_blocking"], 2)

    def test_empty_catch_block_detected(self):
        bad_file = os.path.join(self.temp_dir, "handler.ts")
        with open(bad_file, "w", encoding="utf-8") as f:
            f.write("try { doWork(); } catch (e) {}\n")

        proc = subprocess.run(
            [str(BIN_DIR / "audit-runner"), "--scope", self.temp_dir, "--json"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        res = json.loads(proc.stdout)
        self.assertEqual(res["verdict"], "FAIL")
        found_ids = [f["id"] for f in res["findings"]]
        self.assertIn("RULE-8.1-EMPTY-CATCH", found_ids)

    def test_skipped_test_detected(self):
        bad_spec = os.path.join(self.temp_dir, "order.spec.ts")
        with open(bad_spec, "w", encoding="utf-8") as f:
            f.write("it.skip('should charge card', () => {});\n")

        proc = subprocess.run(
            [str(BIN_DIR / "audit-runner"), "--scope", self.temp_dir, "--json"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        res = json.loads(proc.stdout)
        self.assertEqual(res["verdict"], "FAIL")
        found_ids = [f["id"] for f in res["findings"]]
        self.assertIn("RULE-10.2-SKIPPED-TEST", found_ids)

    def test_audit_repo_itself_clean(self):
        proc = subprocess.run(
            [str(BIN_DIR / "audit-runner"), "--scope", str(REPO_ROOT), "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Expected clean audit of repo, got: {proc.stdout}")
        res = json.loads(proc.stdout)
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["total_blocking"], 0)


if __name__ == "__main__":
    unittest.main()
