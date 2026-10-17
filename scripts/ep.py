#!/usr/bin/env python3
"""
ep.py — Unified Mechanical CLI for Enterprise-Product Engineering OS (EP-OS)
Zero-dependency Python 3.12 CLI standardizing governance, blast-radius verification,
auditing, static analysis, monorepo worktrees, architecture topology, multi-session workspaces,
and multi-tier VCS promotion gates.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure repository root and scripts directory are in sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
for p in [REPO_ROOT, SCRIPTS_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from scripts.ep_adopt import cmd_adopt
    from scripts.ep_hooks import cmd_hooks
    from scripts.ep_security import cmd_license, cmd_security
    from scripts.ep_session import cmd_session
    from scripts.ep_stack import STACK_DEFINITIONS, detect_stack
    from scripts.ep_sync import cmd_sync_skill
    from scripts.ep_vcs import (
        BaseGitProvider,
        GitHubProvider,
        GitLabProvider,
        LocalGitProvider,
        cmd_pr,
        cmd_vcs,
        get_git_provider,
    )
except ImportError:
    from ep_adopt import cmd_adopt
    from ep_hooks import cmd_hooks
    from ep_security import cmd_license, cmd_security
    from ep_session import cmd_session
    from ep_stack import STACK_DEFINITIONS, detect_stack
    from ep_sync import cmd_sync_skill
    from ep_vcs import (
        BaseGitProvider,
        GitHubProvider,
        GitLabProvider,
        LocalGitProvider,
        cmd_pr,
        cmd_vcs,
        get_git_provider,
    )


# ==============================================================================
# SUBCOMMAND: surface (Change Surface Validator & Blast-Radius Gate)
# ==============================================================================

def cmd_surface(args: argparse.Namespace) -> int:
    if args.action == "validate":
        target_file = args.file or "CHANGE_SURFACE.md"
        if not os.path.exists(target_file):
            print(f"[ERROR] Change Surface file '{target_file}' not found.", file=sys.stderr)
            return 1
        cmd = [sys.executable, os.path.join(SCRIPTS_DIR, "validate-change-surface.py"), target_file]
        if args.strict:
            cmd.append("--strict")
        return subprocess.run(cmd).returncode

    elif args.action == "check-diff":
        base_branch = args.base or "origin/main"
        target_file = getattr(args, "surface_file", None) or args.file or "CHANGE_SURFACE.md"

        if not os.path.exists(target_file):
            if os.path.exists("docs/changes"):
                changes = sorted([os.path.join("docs/changes", f) for f in os.listdir("docs/changes") if f.endswith(".md")])
                if changes:
                    target_file = changes[-1]

        if not os.path.exists(target_file):
            print(f"[ERROR] No Change Surface artifact found to verify against git diff.", file=sys.stderr)
            return 1

        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()

        code_surface_match = re.search(r"## 3\.\s*Code Surface.*?(?=## 4\.\s*Test Surface|\Z)", content, re.DOTALL | re.IGNORECASE)
        if not code_surface_match:
            print("[ERROR] Could not parse '## 3. Code Surface' from Change Surface.", file=sys.stderr)
            return 1

        surface_text = code_surface_match.group(0)
        declared_paths = set(re.findall(r"[`']([a-zA-Z0-9_\-./]+)[`']", surface_text))

        try:
            if base_branch in ("HEAD", "HEAD~1") or "..." not in base_branch:
                diff_cmd = ["git", "diff", "--name-only", base_branch]
                res = subprocess.run(diff_cmd, capture_output=True, text=True, check=False)
                modified_files = [line.strip() for line in res.stdout.splitlines() if line.strip()]
                res_staged = subprocess.run(["git", "diff", "--name-only", "--cached"], capture_output=True, text=True, check=False)
                modified_files.extend([line.strip() for line in res_staged.stdout.splitlines() if line.strip()])
            else:
                diff_cmd = ["git", "diff", "--name-only", f"{base_branch}...HEAD"]
                res = subprocess.run(diff_cmd, capture_output=True, text=True, check=False)
                modified_files = [line.strip() for line in res.stdout.splitlines() if line.strip()] if res.returncode == 0 else []

            res_status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=False)
            if res_status.returncode == 0:
                for line in res_status.stdout.splitlines():
                    if len(line) >= 4:
                        modified_files.append(line[3:].strip())

            modified_files = sorted(list(set(modified_files)))
        except Exception as e:
            print(f"[ERROR] Failed to query git status/diff: {e}", file=sys.stderr)
            return 1

        exempt_suffixes = (".md", ".jsonl", ".log", "pnpm-lock.yaml", "Cargo.lock", "package-lock.json")
        out_of_bounds = []

        for m_file in modified_files:
            if m_file.endswith(exempt_suffixes) or m_file.startswith("docs/") or m_file == "CHANGE_SURFACE.md":
                continue

            covered = False
            for d_path in declared_paths:
                if m_file == d_path or m_file.startswith(d_path.rstrip("/") + "/"):
                    covered = True
                    break
            if not covered:
                out_of_bounds.append(m_file)

        if out_of_bounds:
            print("[FAIL] MECHANICAL BLAST-RADIUS VIOLATION!", file=sys.stderr)
            print("The following modified files were NOT declared in the Change Surface:", file=sys.stderr)
            for f in out_of_bounds:
                print(f"  ❌ {f}", file=sys.stderr)
            print("\nRemediation: Update '## 3. Code Surface' in your Change Surface or revert out-of-scope edits.", file=sys.stderr)
            return 1

        print(f"[OK] Blast-Radius Clean: All {len(modified_files)} modified files are strictly within declared Change Surface.")
        return 0

    return 0


# ==============================================================================
# SUBCOMMAND: migration (Expand/Contract Static DDL Scanner)
# ==============================================================================

DESTRUCTIVE_DDL_PATTERNS = [
    (r"\bDROP\s+COLUMN\b", "DROP COLUMN detected. Breaking schema alteration violates Expand/Contract (Phase 1-4)."),
    (r"\bRENAME\s+COLUMN\b", "RENAME COLUMN detected. Instant rename breaks rolling deployments. Use dual-write Expand/Contract."),
    (r"\bALTER\s+COLUMN\s+.*?\bSET\s+NOT\s+NULL\b", "SET NOT NULL on existing column without phased backfill causes deployment failure."),
    (r"\bADD\s+COLUMN\s+.*?\bNOT\s+NULL\b(?!\s+DEFAULT\b)", "ADD COLUMN NOT NULL without DEFAULT breaks concurrent insert versions."),
    (r"\bDROP\s+TABLE\b", "DROP TABLE detected without phased deprecation period."),
]

def cmd_migration(args: argparse.Namespace) -> int:
    scan_dir = args.dir or "."
    target_files = []

    if args.diff:
        base = args.base or "origin/main"
        try:
            res = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], capture_output=True, text=True, check=False)
            if res.returncode == 0:
                diff_files = res.stdout.splitlines()
                target_files = [f for f in diff_files if f.endswith(".sql") and os.path.exists(f)]
        except Exception:
            pass

    if not target_files:
        for root, _, files in os.walk(scan_dir):
            if any(p in root for p in ["node_modules", ".git", "dist", "build"]):
                continue
            for f in files:
                if f.endswith(".sql"):
                    target_files.append(os.path.join(root, f))

    violations = []
    for file_path in target_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue

        if re.search(r"--\s*adr-ref:\s*docs/adr/\S+", content, re.IGNORECASE):
            continue

        for pattern, desc in DESTRUCTIVE_DDL_PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_no = content[:match.start()].count("\n") + 1
                violations.append((file_path, line_no, desc, match.group(0)))

    if violations:
        print("[FAIL] EXPAND/CONTRACT MIGRATION GATE VIOLATION!", file=sys.stderr)
        print("Destructive database operations detected that break rolling zero-downtime deployments:\n", file=sys.stderr)
        for f, l, desc, match in violations:
            print(f"  ❌ {f}:{l} -> Found '{match}'", file=sys.stderr)
            print(f"     Reason: {desc}", file=sys.stderr)
        print("\nRemediation: Follow Expand/Contract phased lifecycle (see references/core-directives.md).", file=sys.stderr)
        print("If this is Phase 5 (Contract cleanup), add an approved ADR comment: '-- adr-ref: docs/adr/NNNN-contract.md'.", file=sys.stderr)
        return 1

    print(f"[OK] Expand/Contract Verified: {len(target_files)} migration files checked. 0 destructive operations.")
    return 0


# ==============================================================================
# SUBCOMMAND: graph (Native Mermaid Topology Generator)
# ==============================================================================

def cmd_graph(args: argparse.Namespace) -> int:
    root_dir = args.root or "."
    projects = []

    for current_root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in {"node_modules", ".git", ".nx", "dist", "build"} and not d.startswith(".")]
        if "project.json" in files:
            p_file = os.path.join(current_root, "project.json")
            try:
                with open(p_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    name = data.get("name", os.path.basename(current_root))
                    tags = data.get("tags", [])
                    profile = "Unknown"
                    scope = "General"
                    for t in tags:
                        if t.startswith("profile:"):
                            profile = t.split(":", 1)[1].upper()
                        elif t.startswith("scope:"):
                            scope = t.split(":", 1)[1]
                    projects.append({
                        "name": name,
                        "path": current_root,
                        "profile": profile,
                        "scope": scope,
                    })
            except Exception:
                pass

    if args.format == "json":
        print(json.dumps(projects, indent=2))
        return 0

    print("```mermaid")
    print("flowchart TD")
    print("    subgraph Enterprise Product Monorepo")

    profiles = {
        "A": "Profile A (Backend & Core Services)",
        "B": "Profile B (Web Applications)",
        "C": "Profile C (Mobile Clients)",
        "D": "Profile D (Shared Contracts & Libs)",
    }
    for prof_key, prof_label in profiles.items():
        matching = [p for p in projects if p["profile"] == prof_key]
        if matching:
            print(f'        subgraph P_{prof_key}["{prof_label}"]')
            for p in matching:
                p_id = re.sub(r"[^a-zA-Z0-9_]", "_", p["name"])
                print(f'            {p_id}["{p["name"]} ({p["scope"]})"]')
            print("        end")

    d_projects = [p for p in projects if p["profile"] == "D"]
    other_projects = [p for p in projects if p["profile"] != "D"]
    for d in d_projects:
        d_id = re.sub(r"[^a-zA-Z0-9_]", "_", d["name"])
        for o in other_projects:
            o_id = re.sub(r"[^a-zA-Z0-9_]", "_", o["name"])
            print(f"    {d_id} -.-> {o_id}")

    print("    end")
    print("```")
    return 0


# ==============================================================================
# SUBCOMMAND: init (Monorepo Project Scaffolder)
# ==============================================================================

def cmd_init(args: argparse.Namespace) -> int:
    name = args.name
    profile = args.profile.upper()
    lang = (args.lang or "ts").lower()
    target_dir = args.dir or (f"apps/{name}" if profile in {"B", "C"} else f"services/{name}" if profile == "A" else f"libs/{name}")

    if os.path.exists(target_dir):
        print(f"[ERROR] Target directory '{target_dir}' already exists.", file=sys.stderr)
        return 1

    os.makedirs(target_dir, exist_ok=True)
    scope = "backend" if profile == "A" else "frontend" if profile == "B" else "mobile" if profile == "C" else "shared"

    templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "profiles")
    template_file = None
    if profile == "A" and lang in ("go", "golang"):
        template_file = "go-service-project.json"
    elif profile == "A" and lang in ("rust", "rs"):
        template_file = "rust-service-project.json"
    elif profile == "B":
        template_file = "next-web-project.json"
    elif profile == "C":
        template_file = "flutter-mobile-project.json"
    elif profile == "D":
        template_file = "contracts-project.json"

    project_json = None
    if template_file:
        template_path = os.path.join(templates_dir, template_file)
        if os.path.exists(template_path):
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    project_json = json.load(f)
                project_json["name"] = name
                project_json["sourceRoot"] = f"{target_dir}/src" if profile != "C" else f"{target_dir}/lib"
                for _, t_val in project_json.get("targets", {}).items():
                    if isinstance(t_val, dict) and "options" in t_val and "cwd" in t_val["options"]:
                        t_val["options"]["cwd"] = target_dir
            except Exception:
                project_json = None

    if not project_json:
        project_json = {
            "name": name,
            "$schema": "../../node_modules/nx/schemas/project-schema.json",
            "projectType": "application" if profile != "D" else "library",
            "sourceRoot": f"{target_dir}/src",
            "tags": [f"profile:{profile.lower()}", f"scope:{scope}", f"lang:{lang}"],
            "targets": {
                "lint": {"executor": "nx:run-commands", "options": {"command": f"echo 'Linting {name}...'"}},
                "test": {"executor": "nx:run-commands", "options": {"command": f"echo 'Testing {name}...'"}},
                "build": {"executor": "nx:run-commands", "options": {"command": f"echo 'Building {name}...'"}},
                "audit": {"executor": "nx:run-commands", "options": {"command": f"echo 'Auditing {name}...'"}},
            },
        }
    with open(os.path.join(target_dir, "project.json"), "w", encoding="utf-8") as f:
        json.dump(project_json, f, indent=2)

    agent_md = f"""---
project_name: "{name}"
profile: "{profile}"
stack: "{lang}"
scope: "{scope}"
owner: "engineering"
tier_overrides: []
---

# Project Agent Manifest: {name}

## 1. Scope & Business Intent
Domain responsibility and business purpose of {name}.

## 2. Architectural Profile & Boundaries
- **Profile**: {profile}
- **Primary Inputs**: Internal domain events, API clients.
- **Allowed Outbound Dependencies**: `libs/core-contracts`
- **Forbidden Dependencies**: Direct cross-boundary domain couplings.

## 3. Local Target Delegations
- `nx lint {name}`
- `nx test {name}`
- `nx build {name}`
- `nx audit {name}`

## 4. Test & Verification Rules
- Real ephemeral container verification for databases.
- Domain coverage target $\\ge 95\\%$, adapter coverage $\\ge 80\\%$.
"""
    with open(os.path.join(target_dir, "AGENT.md"), "w", encoding="utf-8") as f:
        f.write(agent_md)

    if profile == "A":
        for d in ["src/domain/entities", "src/domain/events", "src/application/use-cases", "src/infrastructure/adapters", "tests/unit", "tests/integration"]:
            os.makedirs(os.path.join(target_dir, d), exist_ok=True)
    elif profile == "B":
        for d in ["src/components/ui", "src/features", "src/routes", "tests/unit", "tests/e2e"]:
            os.makedirs(os.path.join(target_dir, d), exist_ok=True)
    elif profile == "C":
        for d in ["lib/core", "lib/features/sample/domain", "lib/features/sample/data", "lib/features/sample/presentation", "test/unit"]:
            os.makedirs(os.path.join(target_dir, d), exist_ok=True)
    elif profile == "D":
        for d in ["schemas/openapi", "schemas/proto", "src/generated", "tests/compatibility"]:
            os.makedirs(os.path.join(target_dir, d), exist_ok=True)

    print(f"[OK] Successfully initialized Profile {profile} project '{name}' at '{target_dir}'.")
    return 0


# ==============================================================================
# SUBCOMMAND: worktree (Monorepo Worktree Manager)
# ==============================================================================

def cmd_worktree(args: argparse.Namespace) -> int:
    action = args.action
    branch = args.branch

    if action == "create":
        worktree_path = f"../worktrees/{branch.replace('/', '-')}"
        print(f"Creating isolated monorepo worktree for branch '{branch}' at '{worktree_path}'...")
        res = subprocess.run(["git", "worktree", "add", worktree_path, "-b", branch], check=False)
        if res.returncode != 0:
            return res.returncode
        print(f"[OK] Worktree created at {worktree_path}. Run 'cd {worktree_path} && pnpm install --frozen-lockfile'.")
        return 0

    elif action == "remove":
        worktree_path = f"../worktrees/{branch.replace('/', '-')}"
        print(f"Removing monorepo worktree at '{worktree_path}'...")
        res = subprocess.run(["git", "worktree", "remove", worktree_path], check=False)
        subprocess.run(["git", "worktree", "prune"], check=False)
        return res.returncode

    return 0


# ==============================================================================
# SUBCOMMAND: manifest (Universal Manifest Projection Engine)
# ==============================================================================

def cmd_manifest(args: argparse.Namespace) -> int:
    root_dir = args.root or "."
    count = 0
    root_agent = os.path.join(root_dir, "AGENT.md")
    if os.path.exists(root_agent):
        with open(root_agent, "r", encoding="utf-8") as f:
            agent_content = f.read()

        claude_path = os.path.join(root_dir, "CLAUDE.md")
        with open(claude_path, "w", encoding="utf-8") as f:
            f.write(f"<!-- AUTO-GENERATED FROM AGENT.md by ep manifest sync. DO NOT EDIT DIRECTLY. -->\n\n{agent_content}")
        count += 1

        cursor_path = os.path.join(root_dir, ".cursorrules")
        with open(cursor_path, "w", encoding="utf-8") as f:
            f.write(f"# Cursor AI Rules - Auto-generated from AGENT.md\n\n{agent_content}")
        count += 1

        windsurf_path = os.path.join(root_dir, ".windsurfrules")
        with open(windsurf_path, "w", encoding="utf-8") as f:
            f.write(f"# Windsurf Rules - Auto-generated from AGENT.md\n\n{agent_content}")
        count += 1

    for cur_root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "dist", "build"} and not d.startswith(".")]
        if "AGENT.md" in files and cur_root != root_dir:
            sub_agent = os.path.join(cur_root, "AGENT.md")
            sub_claude = os.path.join(cur_root, "CLAUDE.md")
            with open(sub_agent, "r", encoding="utf-8") as f:
                c = f.read()
            with open(sub_claude, "w", encoding="utf-8") as f:
                f.write(f"<!-- AUTO-GENERATED FROM AGENT.md by ep manifest sync -->\n\n{c}")
            count += 1

    print(f"[OK] Manifest projection complete: {count} agent manifest files synchronized.")
    return 0


# ==============================================================================
# SUBCOMMAND: preflight (Tool Capability & Access Refusal Gate)
# ==============================================================================

def cmd_preflight(args: argparse.Namespace) -> int:
    checks = []
    try:
        res = subprocess.run(["bash", "-c", "echo ok"], capture_output=True, text=True, check=False)
        checks.append(("Shell Execution (`bash`)", res.returncode == 0 and "ok" in res.stdout))
    except Exception:
        checks.append(("Shell Execution (`bash`)", False))

    try:
        res = subprocess.run(["git", "--version"], capture_output=True, text=True, check=False)
        checks.append(("Version Control (`git`)", res.returncode == 0))
    except Exception:
        checks.append(("Version Control (`git`)", False))

    py_ok = sys.version_info >= (3, 10)
    checks.append((f"Python Runtime ({sys.version_info.major}.{sys.version_info.minor})", py_ok))

    test_file = ".ep_preflight_probe"
    try:
        with open(test_file, "w") as f:
            f.write("probe")
        os.remove(test_file)
        checks.append(("Workspace Write Access", True))
    except Exception:
        checks.append(("Workspace Write Access", False))

    all_passed = all(status for _, status in checks)
    print("=== EP-OS Platform Preflight Access Verification ===")
    for name, status in checks:
        print(f"  [{'PASS' if status else 'FAIL'}] {name}")

    if not all_passed:
        print("\n[CRITICAL] Missing required execution capabilities!", file=sys.stderr)
        print("Repeatable Manual Fallback Instructions:", file=sys.stderr)
        print("  1. Ensure Python 3.10+ and Git are installed and available in PATH.", file=sys.stderr)
        print("  2. Grant the agent subprocess/shell execution permissions in the IDE settings.", file=sys.stderr)
        print("  3. Note: Agent context memory is ephemeral. If ungranted, you must manually run tests and audits on each turn.", file=sys.stderr)
        print("\n[ENGAGEMENT REFUSED] Halting operations. Enterprise-Product standards require mechanical verification.", file=sys.stderr)
        return 2

    print("\n[OK] Preflight Verified: All required agent execution capabilities are granted.")
    return 0


# ==============================================================================
# SUBCOMMAND: release & milestone (SemVer & Release Governance)
# ==============================================================================

def cmd_release(args: argparse.Namespace) -> int:
    action = args.action
    version = getattr(args, "version", None)

    if action == "create":
        if not version or not re.match(r"^v?\d+\.\d+\.\d+", version):
            print(f"[ERROR] Version '{version}' does not match SemVer format (vMAJOR.MINOR.PATCH).", file=sys.stderr)
            return 1
        formatted_version = f"v{version.lstrip('v')}"
        res = subprocess.run(["git", "tag", "-a", formatted_version, "-m", f"Release {formatted_version}"], check=False)
        if res.returncode != 0:
            return res.returncode
        print(f"[OK] Created release tag '{formatted_version}'.")
        return 0
    elif action == "finalize":
        cur_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=False).stdout.strip()
        print(f"[OK] Finalized production release progression on branch '{cur_branch}'.")
        return 0
    return 0


def cmd_milestone(args: argparse.Namespace) -> int:
    name = args.name
    ms_dir = "docs/milestones"
    os.makedirs(ms_dir, exist_ok=True)
    ms_file = os.path.join(ms_dir, f"{name}.md")
    if os.path.exists(ms_file):
        print(f"[INFO] Milestone '{name}' already exists at '{ms_file}'.")
        return 0
    with open(ms_file, "w", encoding="utf-8") as f:
        f.write(
            f"# Milestone: {name}\n\n"
            f"- **Created**: `{datetime.date.today().isoformat()}`\n"
            f"- **Target Due Date**: `{getattr(args, 'due', None) or 'TBD'}`\n"
            "- **Status**: `IN_PROGRESS`\n"
            "- **Associated Subprojects**:\n"
            "  - `TBD`\n\n"
            "## Delivery Objectives\n"
            "- [ ] Implement core features\n"
            "- [ ] 10-Dimension Audit clean\n"
            "- [ ] Ephemeral container tests passing\n"
        )
    print(f"[OK] Created milestone manifest at '{ms_file}'.")
    return 0


# ==============================================================================
# MAIN DISPATCHER
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        prog="ep",
        description="Unified Mechanical CLI for Enterprise-Product Engineering OS (EP-OS)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Operational subcommands")

    # surface
    p_surface = subparsers.add_parser("surface", help="Change Surface validation and blast-radius bounding")
    p_surface.add_argument("action", choices=["validate", "check-diff"], help="Action to perform")
    p_surface.add_argument("file", nargs="?", default=None, help="Path to CHANGE_SURFACE markdown file")
    p_surface.add_argument("--surface-file", dest="surface_file", default=None, help="Path to CHANGE_SURFACE markdown file")
    p_surface.add_argument("--base", default="origin/main", help="Base git branch for diff check")
    p_surface.add_argument("--strict", action="store_true", help="Disallow template placeholders")

    # migration
    p_mig = subparsers.add_parser("migration", help="Zero-Downtime Expand/Contract migration linter")
    p_mig.add_argument("action", choices=["check"], help="Action to perform")
    p_mig.add_argument("--dir", default=None, help="Directory to scan for migrations")
    p_mig.add_argument("--diff", action="store_true", help="Scan only migration files modified in git diff")
    p_mig.add_argument("--base", default="origin/main", help="Base git branch for diff check")

    # graph
    p_graph = subparsers.add_parser("graph", help="Generate live architecture and documentation topology graph")
    p_graph.add_argument("--root", default=".", help="Root monorepo directory")
    p_graph.add_argument("--format", choices=["mermaid", "json"], default="mermaid", help="Output format")

    # init
    p_init = subparsers.add_parser("init", help="Scaffold a new fully compliant monorepo subproject")
    p_init.add_argument("name", help="Name of the new project")
    p_init.add_argument("--profile", required=True, choices=["A", "B", "C", "D", "a", "b", "c", "d"], help="Architectural Profile")
    p_init.add_argument("--lang", default="ts", help="Language/runtime stack (go, rust, ts, dart, php)")
    p_init.add_argument("--dir", default=None, help="Custom target directory")

    # worktree
    p_wt = subparsers.add_parser("worktree", help="Manage isolated git worktrees for monorepo development")
    p_wt.add_argument("action", choices=["create", "remove"], help="Worktree action")
    p_wt.add_argument("branch", help="Branch name")

    # vcs
    p_vcs = subparsers.add_parser("vcs", help="Multi-Tier VCS operations and topology validation")
    p_vcs.add_argument("action", choices=["sync-check"], help="VCS action")
    p_vcs.add_argument("--base", default="main", help="Base trunk branch")

    # pr
    p_pr = subparsers.add_parser("pr", help="Pull request and promotion operations")
    p_pr.add_argument("action", choices=["create-prod"], help="PR action")
    p_pr.add_argument("--head", default=None, help="Head source branch")
    p_pr.add_argument("--title", default=None, help="PR title")
    p_pr.add_argument("--body", default=None, help="PR body description")

    # session
    p_sess = subparsers.add_parser("session", help="Multi-Session state machine and memory management")
    p_sess.add_argument("action", choices=["save", "resume", "list", "prune"], help="Session action")
    p_sess.add_argument("--session-id", default=None, help="Session identifier")
    p_sess.add_argument("--task", default=None, help="Task description or ID")
    p_sess.add_argument("--mode", default=None, help="Operational mode")
    p_sess.add_argument("--notes", default=None, help="Additional session notes")

    # manifest
    p_man = subparsers.add_parser("manifest", help="Universal manifest projection (CLAUDE.md, .cursorrules)")
    p_man.add_argument("action", choices=["sync"], help="Manifest action")
    p_man.add_argument("--root", default=".", help="Root monorepo directory")

    # preflight
    subparsers.add_parser("preflight", help="Agent execution capabilities and access refusal gate")

    # release
    p_rel = subparsers.add_parser("release", help="Hybrid Dual-Tier SemVer and release management")
    p_rel.add_argument("action", choices=["create", "finalize"], help="Release action")
    p_rel.add_argument("version", nargs="?", default=None, help="Target release version")
    p_rel.add_argument("--prod", action="store_true", help="Finalize production release")

    # milestone
    p_ms = subparsers.add_parser("milestone", help="Milestone tracking and objectives")
    p_ms.add_argument("action", choices=["create"], help="Milestone action")
    p_ms.add_argument("name", help="Milestone name")
    p_ms.add_argument("--due", default=None, help="Target due date")

    # delegate to existing scripts: audit, verify, nc
    p_audit = subparsers.add_parser("audit", help="Run 10-Dimension Enterprise Audit Suite")
    p_audit.add_argument("--scope", default=".", help="Directory or file path to audit")
    p_audit.add_argument("--diff", nargs="?", const="origin/main...HEAD", default=None, help="Audit only modified git diff lines")
    p_audit.add_argument("--output", default=None, help="Path to save AUDIT_REPORT.md")
    p_audit.add_argument("--json", action="store_true", help="Output results in JSON")

    p_verify = subparsers.add_parser("verify", help="Run parallel mechanical gatekeeper suite")
    p_verify.add_argument("--root", default=".", help="Root directory to scan")

    p_nc = subparsers.add_parser("nc", help="Audit NEED_CLARIFICATION items for expiration")
    p_nc.add_argument("action", choices=["check"], help="Action to perform")
    p_nc.add_argument("--max-age", type=int, default=14, help="Max allowed age in days before blocking")

    # hooks
    p_hooks = subparsers.add_parser("hooks", help="Manage zero-dependency native git hooks")
    p_hooks.add_argument("action", choices=["install", "uninstall"], help="Hook action")
    p_hooks.add_argument("--root", default=".", help="Repository root directory")

    # security
    p_sec = subparsers.add_parser("security", help="Pre-commit secret and credential scanner")
    p_sec.add_argument("action", choices=["scan"], help="Security action")
    p_sec.add_argument("--staged", action="store_true", help="Scan only git staged changes")
    p_sec.add_argument("--diff", default=None, help="Scan git diff against base branch")
    p_sec.add_argument("--dir", default=None, help="Scan directory files")

    # license
    p_lic = subparsers.add_parser("license", help="Dependency license and copyleft compliance checker")
    p_lic.add_argument("action", choices=["check"], help="License action")
    p_lic.add_argument("--root", default=".", help="Repository root directory")
    p_lic.add_argument("--sbom", action="store_true", help="Generate .ep/sbom.json")

    # adopt
    p_adopt = subparsers.add_parser("adopt", help="Brownfield monorepo onboarding and baseline ratcheting")
    p_adopt.add_argument("--root", default=".", help="Monorepo root directory")
    p_adopt.add_argument("--profile", default="B", choices=["A", "B", "C", "D", "a", "b", "c", "d"], help="Target Architectural Profile")
    p_adopt.add_argument("--dry-run", action="store_true", help="Simulate adoption without writing files")

    # sync-skill
    p_sync = subparsers.add_parser("sync-skill", help="Synchronize skill directory with workspace repository")
    p_sync.add_argument("--direction", choices=["to-workspace", "to-skill"], default="to-workspace", help="Sync direction")
    p_sync.add_argument("--check", action="store_true", help="Check parity without modifying files")
    p_sync.add_argument("--skill-dir", default=None, help="Path to skill directory")
    p_sync.add_argument("--workspace-dir", default=None, help="Path to workspace clone directory")

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    # Route subcommands
    if args.subcommand == "surface":
        sys.exit(cmd_surface(args))
    elif args.subcommand == "migration":
        sys.exit(cmd_migration(args))
    elif args.subcommand == "graph":
        sys.exit(cmd_graph(args))
    elif args.subcommand == "init":
        sys.exit(cmd_init(args))
    elif args.subcommand == "worktree":
        sys.exit(cmd_worktree(args))
    elif args.subcommand == "vcs":
        sys.exit(cmd_vcs(args))
    elif args.subcommand == "pr":
        sys.exit(cmd_pr(args))
    elif args.subcommand == "session":
        sys.exit(cmd_session(args))
    elif args.subcommand == "manifest":
        sys.exit(cmd_manifest(args))
    elif args.subcommand == "preflight":
        sys.exit(cmd_preflight(args))
    elif args.subcommand == "release":
        sys.exit(cmd_release(args))
    elif args.subcommand == "milestone":
        sys.exit(cmd_milestone(args))
    elif args.subcommand == "audit":
        cmd = [sys.executable, os.path.join(SCRIPTS_DIR, "audit-runner.py")]
        if args.scope:
            cmd.extend(["--scope", args.scope])
        if args.output:
            cmd.extend(["--output", args.output])
        if args.diff:
            cmd.extend(["--diff", args.diff])
        if args.json:
            cmd.append("--json")
        sys.exit(subprocess.run(cmd).returncode)

    elif args.subcommand == "verify":
        print("=== 1. Verifying Nx Target Contracts ===")
        nx_res = subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, "verify-nx-targets.py"), "--root", args.root]).returncode

        print("\n=== 2. Linting AGENT.md Manifests ===")
        agent_res = subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, "verify-agent-manifests.py")]).returncode

        print("\n=== 3. Checking Open NC Item Expiration ===")
        nc_dir = os.path.join(args.root, "docs/nc")
        if os.path.exists(nc_dir):
            nc_res = subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, "check-nc-items.py"), "--dir", nc_dir, "--max-age", "14"]).returncode
        else:
            print("[INFO] No docs/nc directory found under root. 0 open NC items.")
            nc_res = 0

        sys.exit(1 if (nx_res != 0 or agent_res != 0 or nc_res != 0) else 0)

    elif args.subcommand == "nc":
        cmd = [sys.executable, os.path.join(SCRIPTS_DIR, "check-nc-items.py"), "--max-age", str(args.max_age)]
        sys.exit(subprocess.run(cmd).returncode)
    elif args.subcommand == "hooks":
        sys.exit(cmd_hooks(args))
    elif args.subcommand == "security":
        sys.exit(cmd_security(args))
    elif args.subcommand == "license":
        sys.exit(cmd_license(args))
    elif args.subcommand == "adopt":
        sys.exit(cmd_adopt(args))
    elif args.subcommand == "sync-skill":
        sys.exit(cmd_sync_skill(args))


if __name__ == "__main__":
    main()
