#!/usr/bin/env python3
"""
Unit and integration tests for verify-nx-targets CLI tool.
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BIN_DIR = REPO_ROOT / "scripts" / "bin"


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

    def test_json_output_with_zero_projects_passes(self):
        # Verifies that scanning an empty root with --json exits with 0 and compliant: true
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir, exist_ok=True)

        proc = subprocess.run(
            [str(BIN_DIR / "verify-nx-targets"), "--root", empty_dir, "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Expected 0, got {proc.returncode}: {proc.stdout}")
        res = json.loads(proc.stdout)
        self.assertTrue(res["compliant"])
        self.assertEqual(res["total_errors"], 0)


    def test_nonexistent_root_fails(self):
        nonexistent = os.path.join(self.temp_dir, "does_not_exist")
        proc = subprocess.run(
            [str(BIN_DIR / "verify-nx-targets"), "--root", nonexistent],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("does not exist", proc.stderr)


if __name__ == "__main__":
    unittest.main()
