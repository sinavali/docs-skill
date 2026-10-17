#!/usr/bin/env python3
"""
Unit and integration tests for EP-OS Brownfield Adoption Engine (ep_adopt.py).
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


class TestEpAdopt(unittest.TestCase):
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

    def test_adopt_discovers_and_scaffolds_subprojects(self):
        # Create brownfield structure: Go backend + Next.js web app
        be_dir = os.path.join(self.temp_dir, "services", "backend")
        fe_dir = os.path.join(self.temp_dir, "apps", "web")
        os.makedirs(be_dir, exist_ok=True)
        os.makedirs(fe_dir, exist_ok=True)

        with open(os.path.join(be_dir, "go.mod"), "w", encoding="utf-8") as f:
            f.write("module backend\ngo 1.22\n")

        with open(os.path.join(fe_dir, "package.json"), "w", encoding="utf-8") as f:
            json.dump({"name": "web-ui", "version": "1.0.0"}, f)

        # Run adopt
        proc = self.run_ep(["adopt", "--root", self.temp_dir, "--profile", "B"])
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")
        self.assertIn("Adoption Complete!", proc.stdout)

        # Verify AGENT.md in backend
        be_agent = os.path.join(be_dir, "AGENT.md")
        self.assertTrue(os.path.isfile(be_agent))
        with open(be_agent, "r", encoding="utf-8") as f:
            be_content = f.read()
        self.assertIn('scope: "backend"', be_content)
        self.assertIn('architectural_profile: "B"', be_content)

        # Verify project.json in web
        fe_target = os.path.join(fe_dir, "project.json")
        self.assertTrue(os.path.isfile(fe_target))
        with open(fe_target, "r", encoding="utf-8") as f:
            target_data = json.load(f)
        self.assertEqual(target_data["name"], "web")
        self.assertIn("profile:b", target_data["tags"])
        self.assertIn("scope:frontend", target_data["tags"])
        self.assertIn("lint", target_data["targets"])
        self.assertIn("test", target_data["targets"])
        self.assertIn("build", target_data["targets"])
        self.assertIn("audit", target_data["targets"])

        # Verify baseline created
        baseline_file = os.path.join(self.temp_dir, ".ep", "baseline.json")
        self.assertTrue(os.path.isfile(baseline_file))


if __name__ == "__main__":
    unittest.main()
