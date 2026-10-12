#!/usr/bin/env python3
"""
check-nc-items.py
Scans, tracks, and audits NEED_CLARIFICATION (NC) items in an enterprise repository.
Enforces the 14-day merge blocking escalation gate for open NC items.
"""

import argparse
import datetime
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple


def parse_nc_file(file_path: str) -> Optional[Dict]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None

    if not content.startswith("---"):
        return None

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None

    yaml_text = parts[1].strip()
    data = {"file_path": file_path, "affected_projects": []}
    current_list_key = None

    for line in yaml_text.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue

        list_match = re.match(r"^\s+-\s*[\"']?(.*?)[\"']?\s*$", line)
        if list_match and current_list_key:
            data[current_list_key].append(list_match.group(1))
            continue

        kv_match = re.match(r"^([a-zA-Z0-9_-]+):\s*(.*)$", line)
        if kv_match:
            k = kv_match.group(1).strip()
            raw_v = kv_match.group(2).strip()
            if "#" in raw_v:
                m = re.match(r"^([\"'].*?[\"'])\s*(?:#.*)?$", raw_v)
                if m:
                    raw_v = m.group(1)
                else:
                    raw_v = raw_v.split("#", 1)[0].strip()
            v = raw_v.strip("\"'")
            if v == "" or v == "[]":
                data[k] = []
                current_list_key = k
            else:
                data[k] = v
                current_list_key = None

    if "id" not in data or not str(data["id"]).startswith("NC-"):
        return None

    return data


def scan_nc_items(scan_dir: str) -> List[Dict]:
    items = []
    if not os.path.exists(scan_dir):
        return items

    if os.path.isfile(scan_dir):
        parsed = parse_nc_file(scan_dir)
        if parsed:
            items.append(parsed)
        return items

    for root, _, files in os.walk(scan_dir):
        for f in files:
            if f.endswith(".md"):
                full_path = os.path.join(root, f)
                parsed = parse_nc_file(full_path)
                if parsed:
                    items.append(parsed)

    return items


def audit_nc_items(
    items: List[Dict], max_age_days: int = 14, as_of_date: Optional[datetime.date] = None
) -> Tuple[List[Dict], List[Dict], List[str]]:
    if as_of_date is None:
        as_of_date = datetime.date.today()

    open_items = []
    blocking_items = []
    errors = []

    for item in items:
        nc_id = item.get("id", "UNKNOWN")
        status = str(item.get("status", "OPEN")).upper()
        created_str = item.get("created_date")

        if not created_str:
            errors.append(f"{nc_id} ({item['file_path']}): Missing created_date.")
            continue

        try:
            created_date = datetime.date.fromisoformat(str(created_str))
        except ValueError:
            errors.append(f"{nc_id} ({item['file_path']}): Invalid created_date '{created_str}'. Expected YYYY-MM-DD.")
            continue

        age_days = (as_of_date - created_date).days
        item["age_days"] = max(0, age_days)

        if status == "OPEN":
            open_items.append(item)
            if age_days >= max_age_days:
                blocking_items.append(item)

    return open_items, blocking_items, errors


def main():
    parser = argparse.ArgumentParser(description="Audit and track NEED_CLARIFICATION (NC) items.")
    parser.add_argument(
        "--dir",
        default="docs/nc",
        help="Directory or file path to scan for NC items (defaults to 'docs/nc')",
    )
    parser.add_argument(
        "--max-age",
        type=int,
        default=14,
        help="Maximum allowed age in days for open NC items before blocking merge (default: 14)",
    )
    parser.add_argument(
        "--as-of-date",
        help="Reference date for calculating age in YYYY-MM-DD format (defaults to current date)",
    )
    parser.add_argument(
        "--block-on-open-aged",
        action="store_true",
        default=True,
        help="Exit with code 1 if any open NC item is >= max-age (default: True)",
    )
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    ref_date = None
    if args.as_of_date:
        try:
            ref_date = datetime.date.fromisoformat(args.as_of_date)
        except ValueError:
            print(f"[ERROR] Invalid --as-of-date '{args.as_of_date}'. Expected YYYY-MM-DD.", file=sys.stderr)
            sys.exit(2)

    # If default dir doesn't exist, try scanning root docs or current dir
    target_dir = args.dir
    if not os.path.exists(target_dir):
        if os.path.exists("docs"):
            target_dir = "docs"
        else:
            target_dir = "."

    items = scan_nc_items(target_dir)
    open_items, blocking_items, parse_errors = audit_nc_items(
        items, max_age_days=args.max_age, as_of_date=ref_date
    )

    is_blocked = len(blocking_items) > 0 or len(parse_errors) > 0

    if args.json:
        output = {
            "total_items": len(items),
            "open_items": open_items,
            "blocking_items": blocking_items,
            "parse_errors": parse_errors,
            "max_age_days": args.max_age,
            "is_blocked": is_blocked,
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"=== NC Protocol Audit (Found {len(items)} NC items, {len(open_items)} open) ===")
        if parse_errors:
            print(f"[PARSE ERRORS] {len(parse_errors)} error(s):")
            for err in parse_errors:
                print(f"  - {err}")

        if blocking_items:
            print(f"\n[MERGE BLOCK DETECTED] {len(blocking_items)} open NC item(s) >= {args.max_age} days old:")
            for item in blocking_items:
                print(f"  - {item.get('id')}: Age {item.get('age_days')} days (Created {item.get('created_date')})")
                print(f"    File: {item.get('file_path')}")
                if item.get("affected_projects"):
                    print(f"    Affected Projects: {', '.join(item['affected_projects'])}")
            print("\nAction Required: These items must be resolved with stakeholder decisions before PR merge.")
        else:
            print(f"[OK] No blocking NC items. (All open items are < {args.max_age} days old).")

    if args.block_on_open_aged and is_blocked:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
