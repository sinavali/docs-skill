#!/usr/bin/env python3
"""
Unit and integration tests for EP-OS Secret Scanner and License Compliance (ep_security.py).
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


class TestEpSecurity(unittest.TestCase):
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

    def test_clean_directory_passes_security_scan(self):
        code_file = os.path.join(self.temp_dir, "service.ts")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write("export const apiKey = process.env.API_KEY;\n")

        proc = self.run_ep(["security", "scan", "--dir", self.temp_dir])
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")
        self.assertIn("[PASS] Security Secret Scanner", proc.stdout)

    def test_leaked_aws_and_github_token_fails(self):
        leak_file = os.path.join(self.temp_dir, "config.py")
        with open(leak_file, "w", encoding="utf-8") as f:
            f.write('AWS_KEY = "AKIA1234567890ABCDEF"\n')
            f.write('GITHUB_TOKEN = "ghp_123456789012345678901234567890123456"\n')

        proc = self.run_ep(["security", "scan", "--dir", self.temp_dir])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("CRITICAL SECURITY GATE", proc.stderr)
        self.assertIn("AWS Access Key ID", proc.stderr)
        self.assertIn("GitHub Personal Access Token", proc.stderr)

    def test_permissive_license_passes(self):
        pkg_file = os.path.join(self.temp_dir, "package.json")
        with open(pkg_file, "w", encoding="utf-8") as f:
            json.dump({"name": "clean-lib", "license": "MIT"}, f)

        proc = self.run_ep(["license", "check", "--root", self.temp_dir])
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")
        self.assertIn("[PASS] License Compliance", proc.stdout)

    def test_copyleft_agpl_license_fails_and_exports_sbom(self):
        pkg_file = os.path.join(self.temp_dir, "package.json")
        with open(pkg_file, "w", encoding="utf-8") as f:
            json.dump({"name": "viral-lib", "license": "AGPL-3.0"}, f)

        proc = self.run_ep(["license", "check", "--root", self.temp_dir, "--sbom"])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Copyleft license contagion detected", proc.stderr)

        sbom_file = os.path.join(self.temp_dir, ".ep", "sbom.json")
        self.assertTrue(os.path.exists(sbom_file))
        with open(sbom_file, "r", encoding="utf-8") as f:
            sbom_data = json.load(f)
        self.assertEqual(len(sbom_data.get("components", [])), 1)
        self.assertEqual(sbom_data["components"][0]["license"], "AGPL-3.0")


if __name__ == "__main__":
    unittest.main()
