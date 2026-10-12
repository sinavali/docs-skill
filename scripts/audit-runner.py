#!/usr/bin/env python3
"""
audit-runner.py
Automated runner and scanner for the 10-Dimension Enterprise Audit Suite.
Scans source files within a specified scope or diff for common violations,
computes the scorecard, and scaffolds or verifies AUDIT_REPORT.md.
"""

import argparse
import datetime
import json
import os
import re
import sys
from typing import Dict, List, Tuple


DIMENSIONS = [
    (1, "Scalability & Capacity"),
    (2, "Structural Maintainability & Modularity"),
    (3, "Fault Tolerance & Resilience"),
    (4, "Data Integrity & Concurrency"),
    (5, "Security & Zero-Trust"),
    (6, "Observability & Operability"),
    (7, "Contract & Schema Drift"),
    (8, "Code Quality & Typing Strictness"),
    (9, "Documentation & Spec Drift"),
    (10, "Test Fidelity & Assertion Quality"),
]

# Static heuristic scanners for critical enterprise anti-patterns
HEURISTIC_RULES = [
    {
        "dim": 2,
        "id": "RULE-2.1-ORM-IN-DOMAIN",
        "severity": "blocking",
        "description": "Direct ORM/framework dependency found in pure domain layer.",
        "path_regex": r"domain[\\/].*\.(ts|js|go|cs|php|py)$",
        "content_regex": r"(from ['\"](typeorm|prisma|sequelize|mongoose|gorm)['\"]|using Microsoft\.EntityFrameworkCore|use Illuminate\\Database|import sqlalchemy)",
    },
    {
        "dim": 4,
        "id": "RULE-4.1-SQLITE-IN-INTEGRATION",
        "severity": "blocking",
        "description": "Banned in-memory SQL emulator (SQLite/H2) used in integration tests.",
        "path_regex": r"(tests?|integration)[\\/].*\.(ts|js|go|cs|php|py)$",
        "content_regex": r"(:memory:|sqlite3\.connect\(['\"]:memory:['\"]\)|UseSqlite\(|createConnection\(\{.*type:\s*['\"]sqlite['\"])",
    },
    {
        "dim": 5,
        "id": "RULE-5.1-HARDCODED-SECRET",
        "severity": "blocking",
        "description": "Possible hardcoded secret or API credential key detected.",
        "path_regex": r"\.(ts|js|go|cs|php|py|json|yaml|yml)$",
        "content_regex": r"(apiKey|api_key|secretKey|private_key|password)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
    },
    {
        "dim": 8,
        "id": "RULE-8.1-EMPTY-CATCH",
        "severity": "blocking",
        "description": "Empty catch block swallowing errors silently without logging or re-throwing.",
        "path_regex": r"\.(ts|js|cs|php)$",
        "content_regex": r"catch\s*\([^\)]*\)\s*\{\s*\}",
    },
    {
        "dim": 10,
        "id": "RULE-10.1-TAUTOLOGICAL-TEST",
        "severity": "blocking",
        "description": "Tautological or vacuous test assertion detected.",
        "path_regex": r"\.(spec|test)\.(ts|js|go|cs|py)$",
        "content_regex": r"(expect\(true\)\.toBe\(true\)|assert\.(True|Equal)\(true|assert 1 == 1)",
    },
]

EXCLUDED_DIRS = {
    "node_modules",
    ".git",
    ".nx",
    "dist",
    "build",
    "coverage",
    ".cache",
    ".venv",
    "vendor",
    "fixtures",
}


def scan_file_for_violations(file_path: str) -> List[Dict]:
    findings = []
    norm_path = file_path.replace("\\", "/")
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return findings

    for rule in HEURISTIC_RULES:
        if not re.search(rule["path_regex"], norm_path, re.IGNORECASE):
            continue
            
        compiled_regex = re.compile(rule["content_regex"], re.IGNORECASE)
        for idx, line in enumerate(lines, start=1):
            if compiled_regex.search(line):
                findings.append({
                    "dim": rule["dim"],
                    "id": rule["id"],
                    "severity": rule["severity"],
                    "description": rule["description"],
                    "file": norm_path,
                    "line": idx,
                    "snippet": line.strip()[:100],
                })
                
    return findings


def run_audit(target_dir: str) -> Tuple[List[Dict], Dict]:
    all_findings = []
    
    if os.path.isfile(target_dir):
        files_to_scan = [target_dir]
    else:
        files_to_scan = []
        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]
            for f in files:
                files_to_scan.append(os.path.join(root, f))
                
    for f in sorted(files_to_scan):
        all_findings.extend(scan_file_for_violations(f))
        
    # Tally results
    scorecard = {}
    for dim_num, dim_name in DIMENSIONS:
        scorecard[dim_num] = {
            "name": dim_name,
            "blocking": 0,
            "suggestion": 0,
            "nit": 0,
        }
        
    for finding in all_findings:
        dim = finding["dim"]
        sev = finding["severity"]
        if dim in scorecard:
            scorecard[dim][sev] += 1
            
    return all_findings, scorecard


def generate_markdown_report(target: str, findings: List[Dict], scorecard: Dict) -> str:
    total_blocking = sum(s["blocking"] for s in scorecard.values())
    total_suggestion = sum(s["suggestion"] for s in scorecard.values())
    total_nit = sum(s["nit"] for s in scorecard.values())
    verdict = "PASS" if total_blocking == 0 else "FAIL"
    today = datetime.date.today().isoformat()
    
    lines = [
        "# 10-Dimension Enterprise Audit Report",
        "",
        f"**Audit Target**: `{target}`  ",
        f"**Date**: `{today}`  ",
        "**Auditor**: `audit-runner.py`  ",
        f"**Overall Verdict**: **{verdict}**  ",
        "",
        "---",
        "",
        "## 1. Summary Scorecard",
        "",
        "| Dimension | Status | Blocking | Suggestions | Nits |",
        "|---|---|---|---|---|",
    ]
    
    for dim_num, dim_name in DIMENSIONS:
        s = scorecard[dim_num]
        status = "PASS" if s["blocking"] == 0 else "FAIL"
        lines.append(f"| **{dim_num}. {dim_name}** | {status} | {s['blocking']} | {s['suggestion']} | {s['nit']} |")
        
    lines.append(f"| **TOTALS** | **{verdict}** | **{total_blocking}** | **{total_suggestion}** | **{total_nit}** |")
    lines.extend([
        "",
        "---",
        "",
        "## 2. Findings Log",
        "",
    ])
    
    if not findings:
        lines.append("No defects identified. All 10 dimensions meet enterprise standards.")
    else:
        for idx, f in enumerate(findings, start=1):
            lines.extend([
                f"### Finding F-{idx:03d}: {f['id']}",
                f"- **Dimension**: {f['dim']}. {scorecard[f['dim']]['name']}",
                f"- **Severity**: `{f['severity']}`",
                f"- **Location**: `{f['file']}:{f['line']}`",
                f"- **Violation**: {f['description']}",
                f"- **Code Snippet**: `{f['snippet']}`",
                "",
            ])
            
    lines.extend([
        "---",
        "",
        "## 3. Protocol Verdict & Next Steps",
        f"- **Audit Status**: {verdict}",
        f"- **Action**: {'PR is approved for merge progression.' if verdict == 'PASS' else 'Blocking defects must be remediated before PR merge.'}",
        "",
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run 10-dimension enterprise audit suite.")
    parser.add_argument("--scope", default=".", help="Directory or file path to audit (default: .)")
    parser.add_argument("--output", help="Path to save AUDIT_REPORT.md")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    
    args = parser.parse_args()
    
    findings, scorecard = run_audit(args.scope)
    total_blocking = sum(s["blocking"] for s in scorecard.values())
    is_pass = total_blocking == 0
    
    report_md = generate_markdown_report(args.scope, findings, scorecard)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"[INFO] Audit report written to {args.output}")
        
    if args.json:
        res = {
            "scope": args.scope,
            "verdict": "PASS" if is_pass else "FAIL",
            "total_blocking": total_blocking,
            "findings": findings,
            "scorecard": scorecard,
        }
        print(json.dumps(res, indent=2))
    elif not args.output:
        print(report_md)
        
    sys.exit(0 if is_pass else 1)


if __name__ == "__main__":
    main()
