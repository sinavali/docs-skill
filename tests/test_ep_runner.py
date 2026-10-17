#!/usr/bin/env python3
"""
Unit and integration tests for EP-OS Topological DAG Task Runner (ep_runner.py).
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

from scripts.ep_runner import build_dag_and_sort, discover_projects


class TestEpRunner(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.lib_dir = os.path.join(self.temp_dir, "libs", "core")
        self.app_dir = os.path.join(self.temp_dir, "apps", "web")
        os.makedirs(self.lib_dir, exist_ok=True)
        os.makedirs(self.app_dir, exist_ok=True)

        # lib target
        with open(os.path.join(self.lib_dir, "project.json"), "w", encoding="utf-8") as f:
            json.dump({
                "name": "core",
                "targets": {
                    "build": {"options": {"command": "echo 'Building core lib'"}},
                    "lint": {"options": {"command": "echo 'Linting core lib'"}},
                }
            }, f)

        # app target with dependsOn upstream build
        with open(os.path.join(self.app_dir, "project.json"), "w", encoding="utf-8") as f:
            json.dump({
                "name": "web",
                "targets": {
                    "build": {
                        "options": {"command": "echo 'Building web app'"},
                        "dependsOn": ["^build"],
                    },
                    "lint": {"options": {"command": "echo 'Linting web app'"}},
                }
            }, f)

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

    def test_topological_sort_respects_dependencies(self):
        projects = discover_projects(self.temp_dir)
        self.assertIn("core", projects)
        self.assertIn("web", projects)

        ordered, cycles = build_dag_and_sort(projects, "build", ["web"])
        self.assertEqual(len(cycles), 0)
        # core:build must come before web:build
        self.assertEqual(ordered, [("core", "build"), ("web", "build")])

    def test_ep_run_single_target(self):
        proc = self.run_ep(["run", "core:lint", "--root", self.temp_dir])
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")
        self.assertIn("Running core:lint", proc.stdout)
        self.assertIn("completed cleanly", proc.stdout)

    def test_ep_run_many_targets(self):
        proc = self.run_ep(["run-many", "--target=lint", "--root", self.temp_dir])
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")
        self.assertIn("All 2 steps completed successfully", proc.stdout)


if __name__ == "__main__":
    unittest.main()
