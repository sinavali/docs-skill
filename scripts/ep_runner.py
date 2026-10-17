#!/usr/bin/env python3
"""
ep_runner.py — Zero-Dependency Standalone Topological Task DAG Runner for EP-OS
Discovers project.json target contracts across polyglot monorepos, constructs
dependency graphs (DAGs), performs topological sorting, and executes targets
(lint, test, build, audit) with zero external Node.js/Nx package dependencies.
"""

import argparse
import collections
import concurrent.futures
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple

EXCLUDED_DIRS = {
    ".git",
    "node_modules",
    "vendor",
    "dist",
    "build",
    ".cache",
    ".venv",
    ".nx",
    "coverage",
    "__pycache__",
    "templates",
}


def discover_projects(root_dir: str = ".") -> Dict[str, Dict[str, Any]]:
    projects: Dict[str, Dict[str, Any]] = {}
    for current_root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]
        if "project.json" in files:
            p_file = os.path.join(current_root, "project.json")
            try:
                with open(p_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                name = data.get("name") or os.path.basename(current_root)
                data["_root"] = current_root.replace("\\", "/")
                projects[name] = data
            except Exception:
                pass
    return projects


def execute_target(project_name: str, target_name: str, target_cfg: Dict[str, Any], project_root: str) -> Tuple[int, str, float]:
    options = target_cfg.get("options", {})
    command = options.get("command")
    if not command:
        return 0, f"No command defined for {project_name}:{target_name}", 0.0

    cwd = options.get("cwd") or project_root
    t_start = time.time()
    res = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True, check=False)
    elapsed = time.time() - t_start

    output = res.stdout if res.returncode == 0 else f"{res.stdout}\n{res.stderr}".strip()
    return res.returncode, output, elapsed


def build_dag_and_sort(
    projects: Dict[str, Dict[str, Any]], target_name: str, selected_projects: List[str]
) -> Tuple[List[Tuple[str, str]], List[str]]:
    # Nodes: (project_name, target_name)
    nodes: Set[Tuple[str, str]] = set()
    graph: Dict[Tuple[str, str], Set[Tuple[str, str]]] = collections.defaultdict(set)
    in_degree: Dict[Tuple[str, str], int] = collections.defaultdict(int)

    for p_name in selected_projects:
        p_data = projects.get(p_name)
        if not p_data or "targets" not in p_data:
            continue
        if target_name in p_data["targets"]:
            node = (p_name, target_name)
            nodes.add(node)
            depends_on = p_data["targets"][target_name].get("dependsOn", [])
            for dep in depends_on:
                if dep.startswith("^"):
                    # Depends on upstream target across dependency projects
                    upstream_target = dep[1:]
                    for other_p in projects.keys():
                        if other_p != p_name and upstream_target in projects[other_p].get("targets", {}):
                            parent_node = (other_p, upstream_target)
                            nodes.add(parent_node)
                            graph[parent_node].add(node)
                else:
                    # Depends on local target
                    local_dep = (p_name, dep)
                    nodes.add(local_dep)
                    graph[local_dep].add(node)

    for node in nodes:
        if node not in in_degree:
            in_degree[node] = 0
    for parent, children in graph.items():
        for ch in children:
            in_degree[ch] += 1

    queue = collections.deque([n for n in nodes if in_degree[n] == 0])
    ordered: List[Tuple[str, str]] = []

    while queue:
        curr = queue.popleft()
        ordered.append(curr)
        for neighbor in graph[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    cycles = [n for n in nodes if in_degree[n] > 0]
    cycle_errors = [f"Cyclic dependency detected involving target {c[0]}:{c[1]}" for c in cycles]
    return ordered, cycle_errors


def cmd_run(args: argparse.Namespace) -> int:
    target_spec = args.target_spec  # Format: "project:target"
    if ":" not in target_spec:
        print(f"[ERROR] Target specification '{target_spec}' must follow format 'project:target'.", file=sys.stderr)
        return 1

    project_name, target_name = target_spec.split(":", 1)
    projects = discover_projects(getattr(args, "root", ".") or ".")

    if project_name not in projects:
        print(f"[ERROR] Project '{project_name}' not found in monorepo.", file=sys.stderr)
        return 1

    p_data = projects[project_name]
    targets = p_data.get("targets", {})
    if target_name not in targets:
        print(f"[ERROR] Target '{target_name}' not defined for project '{project_name}'.", file=sys.stderr)
        return 1

    ordered, cycle_errs = build_dag_and_sort(projects, target_name, [project_name])
    if cycle_errs:
        for err in cycle_errs:
            print(f"[FAIL] {err}", file=sys.stderr)
        return 1

    print(f"=== EP-OS Topological DAG Runner: {project_name}:{target_name} ===")
    print(f"Resolved execution pipeline ({len(ordered)} step(s)):")
    for p, t in ordered:
        print(f"  • {p}:{t}")

    for p, t in ordered:
        t_cfg = projects[p]["targets"][t]
        p_root = projects[p]["_root"]
        print(f"\n--> Running {p}:{t}...")
        rc, out, elapsed = execute_target(p, t, t_cfg, p_root)
        if out:
            print(out)
        if rc != 0:
            print(f"\n[FAIL] Step '{p}:{t}' failed with exit code {rc}.", file=sys.stderr)
            return rc
        print(f"[PASS] {p}:{t} ({elapsed:.2f}s)")

    print(f"\n[SUCCESS] Pipeline {project_name}:{target_name} completed cleanly.")
    return 0


def cmd_run_many(args: argparse.Namespace) -> int:
    target_name = args.target
    root_dir = getattr(args, "root", ".") or "."
    projects = discover_projects(root_dir)

    selected: List[str] = []
    if getattr(args, "projects", None):
        selected = [p.strip() for p in args.projects.split(",") if p.strip()]
    elif getattr(args, "affected", False):
        base = getattr(args, "base", "origin/main") or "origin/main"
        res = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], capture_output=True, text=True, check=False)
        diff_files = [f.strip() for f in res.stdout.splitlines() if f.strip()]
        for p_name, p_data in projects.items():
            p_prefix = p_data["_root"].lstrip("./") + "/"
            if any(f.startswith(p_prefix) for f in diff_files):
                selected.append(p_name)
        if not selected:
            print("[INFO] Zero affected projects detected in git diff.")
            return 0
    else:
        selected = list(projects.keys())

    # Filter to projects implementing target_name
    valid_selected = [p for p in selected if p in projects and target_name in projects[p].get("targets", {})]
    if not valid_selected:
        print(f"[INFO] Zero projects implement target '{target_name}'.")
        return 0

    ordered, cycle_errs = build_dag_and_sort(projects, target_name, valid_selected)
    if cycle_errs:
        for err in cycle_errs:
            print(f"[FAIL] {err}", file=sys.stderr)
        return 1

    parallel = getattr(args, "parallel", False)
    print(f"=== EP-OS Topological DAG Runner (Target: '{target_name}') ===")
    print(f"Executing {len(ordered)} step(s) across {len(valid_selected)} project(s) (parallel={parallel}):")

    failures = 0
    if parallel:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_step = {
                executor.submit(execute_target, p, t, projects[p]["targets"][t], projects[p]["_root"]): (p, t)
                for p, t in ordered
            }
            for fut in concurrent.futures.as_completed(future_to_step):
                p, t = future_to_step[fut]
                rc, out, elapsed = fut.result()
                if rc == 0:
                    print(f"  [PASS] {p}:{t} ({elapsed:.2f}s)")
                else:
                    print(f"  [FAIL] {p}:{t} -> {out}", file=sys.stderr)
                    failures += 1
    else:
        for p, t in ordered:
            t_cfg = projects[p]["targets"][t]
            p_root = projects[p]["_root"]
            rc, out, elapsed = execute_target(p, t, t_cfg, p_root)
            if rc == 0:
                print(f"  [PASS] {p}:{t} ({elapsed:.2f}s)")
            else:
                print(f"  [FAIL] {p}:{t} -> {out}", file=sys.stderr)
                failures += 1

    if failures > 0:
        print(f"\n[FAIL] {failures} target(s) failed execution.", file=sys.stderr)
        return 1

    print(f"\n[SUCCESS] All {len(ordered)} steps completed successfully.")
    return 0
