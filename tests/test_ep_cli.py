#!/usr/bin/env python3
"""
Unit and integration tests for ep CLI (Enterprise-Product Unified Engineering OS).
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EP_SCRIPT = REPO_ROOT / "scripts" / "ep.py"
EP_BIN = REPO_ROOT / "scripts" / "bin" / "ep"


class TestEpCli(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run_ep(self, args, cwd=None):
        cmd = [sys.executable, str(EP_SCRIPT)] + args
        return subprocess.run(
            cmd,
            cwd=cwd or self.temp_dir,
            capture_output=True,
            text=True,
        )

    def test_ep_help(self):
        proc = self.run_ep(["--help"])
        self.assertEqual(proc.returncode, 0)
        self.assertIn("surface", proc.stdout)
        self.assertIn("migration", proc.stdout)
        self.assertIn("graph", proc.stdout)
        self.assertIn("init", proc.stdout)

    def test_init_profile_a_go(self):
        target = os.path.join(self.temp_dir, "services", "billing")
        proc = self.run_ep(["init", "billing", "--profile", "A", "--lang", "go", "--dir", target])
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")

        # Check project.json
        pj_file = os.path.join(target, "project.json")
        self.assertTrue(os.path.exists(pj_file))
        with open(pj_file, "r", encoding="utf-8") as f:
            pj = json.load(f)
        self.assertEqual(pj["name"], "billing")
        self.assertIn("profile:a", pj["tags"])
        self.assertIn("golangci-lint", pj["targets"]["lint"]["options"]["command"])

        # Check AGENT.md
        agent_file = os.path.join(target, "AGENT.md")
        self.assertTrue(os.path.exists(agent_file))
        with open(agent_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn('profile: "A"', content)

        # Check canonical folders
        self.assertTrue(os.path.isdir(os.path.join(target, "src", "domain", "entities")))
        self.assertTrue(os.path.isdir(os.path.join(target, "tests", "unit")))

    def test_init_profile_b_next(self):
        target = os.path.join(self.temp_dir, "apps", "portal")
        proc = self.run_ep(["init", "portal", "--profile", "B", "--lang", "ts", "--dir", target])
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")

        pj_file = os.path.join(target, "project.json")
        self.assertTrue(os.path.exists(pj_file))
        with open(pj_file, "r", encoding="utf-8") as f:
            pj = json.load(f)
        self.assertEqual(pj["name"], "portal")
        self.assertIn("profile:b", pj["tags"])
        self.assertIn("next build", pj["targets"]["build"]["options"]["command"])

        self.assertTrue(os.path.isdir(os.path.join(target, "src", "components", "ui")))

    def test_init_profile_c_flutter(self):
        target = os.path.join(self.temp_dir, "apps", "mobile")
        proc = self.run_ep(["init", "mobile", "--profile", "C", "--lang", "dart", "--dir", target])
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")

        pj_file = os.path.join(target, "project.json")
        self.assertTrue(os.path.exists(pj_file))
        with open(pj_file, "r", encoding="utf-8") as f:
            pj = json.load(f)
        self.assertEqual(pj["name"], "mobile")
        self.assertIn("profile:c", pj["tags"])
        self.assertIn("flutter analyze", pj["targets"]["lint"]["options"]["command"])

        self.assertTrue(os.path.isdir(os.path.join(target, "lib", "core")))

    def test_init_profile_d_contracts(self):
        target = os.path.join(self.temp_dir, "libs", "contracts")
        proc = self.run_ep(["init", "contracts", "--profile", "D", "--dir", target])
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")

        pj_file = os.path.join(target, "project.json")
        self.assertTrue(os.path.exists(pj_file))
        with open(pj_file, "r", encoding="utf-8") as f:
            pj = json.load(f)
        self.assertEqual(pj["name"], "contracts")
        self.assertIn("profile:d", pj["tags"])
        self.assertIn("generate-ts", pj["targets"])

        self.assertTrue(os.path.isdir(os.path.join(target, "schemas", "openapi")))

    def test_migration_linter_safe(self):
        mig_dir = os.path.join(self.temp_dir, "migrations")
        os.makedirs(mig_dir, exist_ok=True)
        safe_sql = os.path.join(mig_dir, "001_add_column.sql")
        with open(safe_sql, "w", encoding="utf-8") as f:
            f.write("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT false;\n")

        proc = self.run_ep(["migration", "check", "--dir", mig_dir])
        self.assertEqual(proc.returncode, 0, f"Expected 0: {proc.stdout}")
        self.assertIn("[OK]", proc.stdout)

    def test_migration_linter_destructive_blocks(self):
        mig_dir = os.path.join(self.temp_dir, "migrations")
        os.makedirs(mig_dir, exist_ok=True)
        bad_sql = os.path.join(mig_dir, "002_drop_column.sql")
        with open(bad_sql, "w", encoding="utf-8") as f:
            f.write("ALTER TABLE users DROP COLUMN old_token;\n")

        proc = self.run_ep(["migration", "check", "--dir", mig_dir])
        self.assertEqual(proc.returncode, 1, f"Expected 1: {proc.stderr}")
        self.assertIn("[FAIL]", proc.stderr)
        self.assertIn("DROP COLUMN", proc.stderr)

    def test_graph_generator(self):
        # Create 2 mock services
        s1 = os.path.join(self.temp_dir, "services", "svc1")
        os.makedirs(s1, exist_ok=True)
        with open(os.path.join(s1, "project.json"), "w", encoding="utf-8") as f:
            json.dump({"name": "svc1", "tags": ["profile:a", "scope:backend"]}, f)
        with open(os.path.join(s1, "AGENT.md"), "w", encoding="utf-8") as f:
            f.write("---\nproject_name: svc1\nprofile: A\n---\nAllowed Outbound Dependencies: `libs/contracts`\n")

        s2 = os.path.join(self.temp_dir, "libs", "contracts")
        os.makedirs(s2, exist_ok=True)
        with open(os.path.join(s2, "project.json"), "w", encoding="utf-8") as f:
            json.dump({"name": "contracts", "tags": ["profile:d", "scope:shared"]}, f)
        with open(os.path.join(s2, "AGENT.md"), "w", encoding="utf-8") as f:
            f.write("---\nproject_name: contracts\nprofile: D\n---\n")

        proc = self.run_ep(["graph", "--root", self.temp_dir, "--format", "mermaid"])
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")
        self.assertIn("flowchart TD", proc.stdout)
        self.assertIn("svc1", proc.stdout)
        self.assertIn("contracts", proc.stdout)

    def test_surface_check_diff(self):
        # Setup git repo in temp_dir
        subprocess.run(["git", "init"], cwd=self.temp_dir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.temp_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Tester"], cwd=self.temp_dir, check=True)

        # Base commit
        file_a = os.path.join(self.temp_dir, "file_a.txt")
        with open(file_a, "w") as f:
            f.write("hello\n")
        subprocess.run(["git", "add", "."], cwd=self.temp_dir, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=self.temp_dir, check=True)

        # Modify file_a and create CHANGE_SURFACE.md declaring file_a.txt under ## 3. Code Surface
        with open(file_a, "w") as f:
            f.write("hello world\n")
        cs_file = os.path.join(self.temp_dir, "CHANGE_SURFACE.md")
        with open(cs_file, "w") as f:
            f.write("""# Change Surface

## 1. Intent & Context
Test change

## 2. Invariant Risk Assessment
Low

## 3. Code Surface
- `file_a.txt`

## 4. Test Surface
- None
""")

        proc = self.run_ep(["surface", "check-diff", "--surface-file", cs_file, "--base", "HEAD"], cwd=self.temp_dir)
        self.assertEqual(proc.returncode, 0, f"Expected 0: stdout={proc.stdout}, stderr={proc.stderr}")
        self.assertIn("[OK]", proc.stdout)

        # Modify an undeclared file_b
        file_b = os.path.join(self.temp_dir, "file_b.txt")
        with open(file_b, "w") as f:
            f.write("surprise\n")
        subprocess.run(["git", "add", file_b], cwd=self.temp_dir, check=True)

        proc_fail = self.run_ep(["surface", "check-diff", "--surface-file", cs_file, "--base", "HEAD"], cwd=self.temp_dir)
        self.assertEqual(proc_fail.returncode, 1, f"Expected 1: stdout={proc_fail.stdout}, stderr={proc_fail.stderr}")
        self.assertIn("BLAST-RADIUS VIOLATION", proc_fail.stderr)

    def test_graph_check_boundaries(self):
        # 1. Clean boundary test
        clean_dir = os.path.join(self.temp_dir, "services", "billing", "domain")
        os.makedirs(clean_dir, exist_ok=True)
        with open(os.path.join(clean_dir, "entity.ts"), "w") as f:
            f.write("export class Invoice { id: string; }\n")

        proc_clean = self.run_ep(["graph", "--check-boundaries", "--root", self.temp_dir])
        self.assertEqual(proc_clean.returncode, 0, f"Error: {proc_clean.stderr}")
        self.assertIn("Architectural Boundary Integrity Verified", proc_clean.stdout)

        # 2. Add illegal ORM import into domain
        with open(os.path.join(clean_dir, "entity.ts"), "a") as f:
            f.write("import { PrismaClient } from 'prisma';\n")

        proc_violation = self.run_ep(["graph", "--check-boundaries", "--root", self.temp_dir])
        self.assertEqual(proc_violation.returncode, 1)
        self.assertIn("Architectural Boundary Violations Detected", proc_violation.stderr)
        self.assertIn("Domain layer imports ORM", proc_violation.stderr)


if __name__ == "__main__":
    unittest.main()
