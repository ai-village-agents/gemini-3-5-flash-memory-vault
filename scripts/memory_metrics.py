#!/usr/bin/env python3
"""
Memory Metrics Tool for Gemini 3.5 Flash Memory Vault
"""

import sys
import os
import yaml
import subprocess
from collections import Counter

VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_cmd(cmd, cwd=None):
    try:
        res = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd)
        return res.stdout.strip(), ""
    except subprocess.CalledProcessError as e:
        return "", e.stderr.strip() if e.stderr else str(e)

def get_git_info():
    latest_commit, _ = run_cmd("git log -1 --oneline", cwd=VAULT_ROOT)
    uncommitted, _ = run_cmd("git status --porcelain", cwd=VAULT_ROOT)
    unpushed, _ = run_cmd("git rev-list --count @{u}..HEAD", cwd=VAULT_ROOT)
    
    unpushed_count = 0
    if unpushed:
        try:
            unpushed_count = int(unpushed)
        except ValueError:
            pass
            
    uncommitted_lines = [line for line in uncommitted.split('\n') if line.strip()]
    return {
        "latest_commit": latest_commit,
        "uncommitted_count": len(uncommitted_lines),
        "uncommitted_files": uncommitted_lines,
        "unpushed_count": unpushed_count
    }

def check_guards():
    required_guards = [
        "scripts/boot.py",
        "scripts/pre_send_chat.py",
        "scripts/pre_consolidate.py",
        "scripts/check_memory_cues.py",
        "scripts/retrieval_self_test.py",
        "scripts/scan_peers.py",
        "scripts/prepare_goal_transition.py",
        "scripts/memory_metrics.py"
    ]
    
    presence = {}
    for guard in required_guards:
        full_path = os.path.join(VAULT_ROOT, guard)
        presence[guard] = os.path.exists(full_path)
    return presence

def parse_inventory():
    inventory_path = os.path.join(VAULT_ROOT, "inventory.yaml")
    if not os.path.exists(inventory_path):
        return None
        
    try:
        with open(inventory_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"[!] Error loading inventory.yaml: {e}")
        return None
        
    items = []
    if isinstance(data, dict) and 'items' in data:
        items = data['items']
    elif isinstance(data, list):
        items = data
        
    return items

def get_draft_metrics():
    draft_path = "/tmp/l1_memory_draft.txt"
    if os.path.exists(draft_path):
        with open(draft_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {
            "exists": True,
            "lines": len(content.splitlines()),
            "chars": len(content),
            "bytes": len(content.encode('utf-8'))
        }
    return {"exists": False}

def main():
    print("============================================================\n"
          "                 GEMINI 3.5 FLASH MEMORY METRICS            \n"
          "============================================================\n")
          
    git_info = get_git_info()
    guards = check_guards()
    items = parse_inventory()
    draft = get_draft_metrics()
    
    print(f"[*] Latest Commit: {git_info['latest_commit']}")
    print(f"[*] Uncommitted Changes: {git_info['uncommitted_count']} files")
    if git_info['uncommitted_files']:
        for file in git_info['uncommitted_files']:
            print(f"    - {file}")
    print(f"[*] Unpushed Commits: {git_info['unpushed_count']}\n")
    
    print("[*] Guard Scripts Status:")
    all_guards_ok = True
    for guard, present in guards.items():
        status_str = "[OK]" if present else "[MISSING]"
        print(f"  - {guard:<35} {status_str}")
        if not present:
            all_guards_ok = False
    print()
    
    if items is not None:
        total_items = len(items)
        statuses = Counter(item.get("status", "unknown") for item in items)
        kinds = Counter(item.get("kind", "unknown") for item in items)
        policies = Counter(item.get("internal_memory_policy", "unknown") for item in items)
        
        print(f"[*] Inventory Overview ({total_items} items total):")
        print("  - Status distribution:")
        for status, count in statuses.items():
            print(f"    - {status}: {count}")
        print("  - Kind distribution:")
        for kind, count in kinds.items():
            print(f"    - {kind}: {count}")
        print("  - Internal memory policies:")
        for policy, count in policies.items():
            print(f"    - {policy}: {count}")
        print()
    else:
        print("[!] No inventory.yaml found or failed to parse.\n")
        
    if draft["exists"]:
        print("[*] Draft L1 Memory Metrics:")
        print(f"  - Lines: {draft['lines']} (limit: ≤350)")
        print(f"  - Characters: {draft['chars']}")
        print(f"  - Size: {draft['bytes'] / 1024:.2f} KB (limit: ≤15 KB)")
        if draft['bytes'] > 15 * 1024 or draft['lines'] > 350:
            print("  - [WARNING] Draft exceeds budget targets!")
        else:
            print("  - [OK] Draft is well within budget targets.")
    else:
        print("[*] Draft L1 Memory: No active draft found in /tmp. Run prepare_consolidation.py first.\n")
        
    print("============================================================\n")
    
    if not all_guards_ok:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
