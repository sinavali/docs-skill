#!/usr/bin/env python3
"""
Unit and integration tests for EP-OS Native Git Hook Manager (ep_hooks.py).
"""

import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EP_SCRIPT = REPO_ROOT / "scripts" / "ep.py"


class TestEpHooks(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        subprocess.run(["git", "init"], cwd=self.temp_dir, capture_output=True, check=True)

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

    def test_install_and_uninstall_hooks(self):
        # Install
        proc = self.run_ep(["hooks", "install", "--root", self.temp_dir])
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")
        self.assertIn("EP-OS native git hooks installed", proc.stdout)

        hooks_dir = os.path.join(self.temp_dir, ".git", "hooks")
        for h in ["pre-commit", "pre-push", "commit-msg"]:
            hook_path = os.path.join(hooks_dir, h)
            self.assertTrue(os.path.isfile(hook_path), f"Hook '{h}' missing")
            # Verify executable bit
            st = os.stat(hook_path)
            self.assertTrue(st.st_mode & stat.S_IXUSR, f"Hook '{h}' is not executable")

        # Uninstall
        proc_un = self.run_ep(["hooks", "uninstall", "--root", self.temp_dir])
        self.assertEqual(proc_un.returncode, 0, f"Error: {proc_un.stderr}")
        self.assertIn("Uninstalled 3 EP-OS git hooks", proc_un.stdout)
        for h in ["pre-commit", "pre-push", "commit-msg"]:
            self.assertFalse(os.path.exists(os.path.join(hooks_dir, h)))

    def test_commit_msg_hook_enforcement(self):
        self.run_ep(["hooks", "install", "--root", self.temp_dir])
        commit_msg_hook = os.path.join(self.temp_dir, ".git", "hooks", "commit-msg")

        # Test valid conventional commit
        valid_file = os.path.join(self.temp_dir, "msg_valid.txt")
        with open(valid_file, "w", encoding="utf-8") as f:
            f.write("feat(core): implement zero-dependency hooks\n")
        res_valid = subprocess.run([sys.executable, commit_msg_hook, valid_file], capture_output=True, text=True)
        self.assertEqual(res_valid.returncode, 0, f"Valid commit rejected: {res_valid.stderr}")

        # Test invalid commit format
        invalid_file = os.path.join(self.temp_dir, "msg_invalid.txt")
        with open(invalid_file, "w", encoding="utf-8") as f:
            f.write("fixed some stuff\n")
        res_invalid = subprocess.run([sys.executable, commit_msg_hook, invalid_file], capture_output=True, text=True)
        self.assertEqual(res_invalid.returncode, 1, "Invalid commit unexpectedly accepted")
        self.assertIn("Invalid commit message format", res_invalid.stderr)


if __name__ == "__main__":
    unittest.main()
