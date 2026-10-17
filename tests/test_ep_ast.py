#!/usr/bin/env python3
"""
Unit and integration tests for EP-OS ast-grep structural code intelligence (ep_ast.py).
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

from scripts.ep_ast import is_ast_grep_available, run_ast_query, scan_structural_rules


class TestEpAst(unittest.TestCase):
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

    def test_ast_grep_availability(self):
        self.assertTrue(is_ast_grep_available(), "ast-grep should be available globally")

    def test_ast_search_query(self):
        code_file = os.path.join(self.temp_dir, "calc.py")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write("def add(a, b):\n    return a + b\n\ndef sub(a, b):\n    return a - b\n")

        matches = run_ast_query("def $FN($A, $B): $$$", scope=self.temp_dir, lang="python")
        self.assertEqual(len(matches), 2)
        fn_names = {m.get("metaVariables", {}).get("single", {}).get("FN", {}).get("text") for m in matches}
        self.assertEqual(fn_names, {"add", "sub"})

    def test_ast_tautological_assertion_detected(self):
        test_file = os.path.join(self.temp_dir, "test_sample.py")
        # Split string concatenation to prevent audit-runner self-scan false positive
        mock_body = "import unittest\nclass SampleTest(unittest.TestCase):\n    def test_one(self):\n        " + "self." + "assertEqual(1, 1)\n        " + "self." + "assertTrue(True)\n"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(mock_body)

        findings = scan_structural_rules(scope=self.temp_dir)
        self.assertTrue(any(f["id"] == "RULE-10.1-AST-TAUTOLOGICAL-TEST" for f in findings))

    def test_ast_cli_scan_reports_pass_on_clean_code(self):
        clean_file = os.path.join(self.temp_dir, "clean.ts")
        with open(clean_file, "w", encoding="utf-8") as f:
            f.write("export function compute(x: number): number {\n  return x * 2;\n}\n")

        proc = self.run_ep(["ast", "scan", "--scope", self.temp_dir])
        self.assertEqual(proc.returncode, 0)
        self.assertIn("[PASS] Zero structural AST violations detected", proc.stdout)


if __name__ == "__main__":
    unittest.main()
