#!/usr/bin/env python3
"""
Unit and integration tests for validate-change-surface CLI tool.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BIN_DIR = REPO_ROOT / "scripts" / "bin"


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

    def test_docs_changes_fallback_resolution(self):
        docs_changes = os.path.join(self.temp_dir, "docs", "changes")
        os.makedirs(docs_changes, exist_ok=True)
        versioned_file = os.path.join(docs_changes, "20261012-feature.md")
        content = """---
title: "Versioned Change Surface"
author: "Engineer"
created_date: "2026-10-12"
target_branch: "main"
risk_level: "LOW"
affected_projects:
  - "services/billing"
---
# Versioned Change Surface
## 1. Intent & Business Rationale
Rationale.
## 2. Affected Monorepo Projects & Profiles
| Project | Profile | Responsibility |
|---|---|---|
| services/billing | Profile A | Logic |
## 3. Code Surface
- `services/billing/index.ts`
## 4. Test Surface
- `services/billing/index.spec.ts`
## 5. Invariants
Invariants.
## 6. Risk Matrix
Risk.
"""
        with open(versioned_file, "w", encoding="utf-8") as f:
            f.write(content)

        proc = subprocess.run(
            [str(BIN_DIR / "validate-change-surface")],
            cwd=self.temp_dir,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Expected 0: {proc.stdout} {proc.stderr}")
        self.assertIn("[SUCCESS]", proc.stdout)
        # Verify the actual resolved target_file is reported, not hardcoded args.file
        self.assertIn("20261012-feature.md", proc.stdout)


if __name__ == "__main__":
    unittest.main()
