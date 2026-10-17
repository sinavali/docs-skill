#!/usr/bin/env python3
"""
Unit and integration tests for EP-OS Bidirectional Skill Sync (ep_sync.py).
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EP_SCRIPT = REPO_ROOT / "scripts" / "ep.py"


class TestEpSync(unittest.TestCase):
    def setUp(self):
        self.skill_dir = tempfile.mkdtemp()
        self.workspace_dir = tempfile.mkdtemp()

        # Populate initial identical mock skill and workspace
        os.makedirs(os.path.join(self.skill_dir, "scripts"), exist_ok=True)
        os.makedirs(os.path.join(self.workspace_dir, "scripts"), exist_ok=True)

        with open(os.path.join(self.skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write("# Skill\n")
        with open(os.path.join(self.workspace_dir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write("# Skill\n")

    def tearDown(self):
        shutil.rmtree(self.skill_dir, ignore_errors=True)
        shutil.rmtree(self.workspace_dir, ignore_errors=True)

    def run_ep(self, args):
        cmd = [sys.executable, str(EP_SCRIPT)] + args
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

    def test_sync_parity_and_propagation(self):
        # 1. Initial parity
        proc_check = self.run_ep([
            "sync-skill", "--check",
            "--skill-dir", self.skill_dir,
            "--workspace-dir", self.workspace_dir,
        ])
        self.assertEqual(proc_check.returncode, 0, f"Check failed: {proc_check.stderr}")
        self.assertIn("100% cryptographic parity", proc_check.stdout)

        # 2. Add new script to skill directory (causing drift)
        new_script = os.path.join(self.skill_dir, "scripts", "new_tool.py")
        with open(new_script, "w", encoding="utf-8") as f:
            f.write("# New Tool\n")

        proc_drift = self.run_ep([
            "sync-skill", "--check",
            "--skill-dir", self.skill_dir,
            "--workspace-dir", self.workspace_dir,
        ])
        self.assertEqual(proc_drift.returncode, 1)
        self.assertIn("Parity Drift:        1 file(s)", proc_drift.stdout)
        self.assertIn("scripts/new_tool.py", proc_drift.stdout)

        # 3. Synchronize to workspace
        proc_sync = self.run_ep([
            "sync-skill", "--direction", "to-workspace",
            "--skill-dir", self.skill_dir,
            "--workspace-dir", self.workspace_dir,
        ])
        self.assertEqual(proc_sync.returncode, 0, f"Sync failed: {proc_sync.stderr}")
        self.assertIn("Cryptographic SHA-256 parity achieved", proc_sync.stdout)

        # 4. Verify file was copied
        copied_script = os.path.join(self.workspace_dir, "scripts", "new_tool.py")
        self.assertTrue(os.path.isfile(copied_script))


if __name__ == "__main__":
    unittest.main()
