#!/usr/bin/env python3
"""
Gemini 3.5 Flash Memory Engine
A lightweight, high-speed, local search and retrieval engine for the external memory vault.
Includes automated schema validation to enforce alignment with the unified village schema.

Usage:
    python3 scripts/memory_engine.py --query "MemGPT"
    python3 scripts/memory_engine.py --show-checklists
    python3 scripts/memory_engine.py --validate
"""

import os
import re
import argparse
import sys

VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def search_vault(query, case_sensitive=False):
    print(f"[*] Scanning memory vault at: {VAULT_ROOT}")
    print(f"[*] Search query: '{query}'\n" + "-"*60)
    
    matches_found = 0
    flags = 0 if case_sensitive else re.IGNORECASE
    
    try:
        compiled_re = re.compile(query, flags)
    except re.error as e:
        print(f"[!] Invalid regex query: {e}")
        return

    # Walk through the vault directories
    for root, dirs, files in os.walk(VAULT_ROOT):
        # Skip hidden directories like .git
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if not file.endswith('.md'):
                continue\
                
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, VAULT_ROOT)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"[!] Error reading {rel_path}: {e}")
                continue
                
            file_printed = False
            for line_no, line in enumerate(lines, 1):
                if compiled_re.search(line):
                    if not file_printed:
                        print(f"\n[FILE] {rel_path}")
                        print("=" * len(rel_path) * 2)
                        file_printed = True
                    print(f"  Line {line_no:02d}: {line.strip()}")
                    matches_found += 1
                    
    print("\n" + "-"*60)
    print(f"[*] Search completed. Found {matches_found} matches.")

def show_checklists():
    checklist_path = os.path.join(VAULT_ROOT, "runbooks", "checklists.md")
    if os.path.exists(checklist_path):
        print(f"[*] Displaying current operating procedures from {checklist_path}:\n" + "="*60)
        with open(checklist_path, 'r') as f:
            print(f.read())
    else:
        print("[!] Checklists file not found.")

def validate_vault():
    print(f"[*] Starting schema validation for memory vault...")
    print("-" * 60)
    expected_dirs = ["identity", "principles", "runbooks", "reflections", "goals", "peers"]
    errors = 0
    warnings = 0
    
    # 1. Check directories existence
    for d in expected_dirs:
        d_path = os.path.join(VAULT_ROOT, d)
        if not os.path.isdir(d_path):
            print(f"[ERROR] Missing expected directory: '{d}'")
            errors += 1
        else:
            print(f"[OK] Directory exists: '{d}'")
            
    # 2. Check each file has a recognized layout
    for root, dirs, files in os.walk(VAULT_ROOT):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if not file.endswith('.md') and not file.endswith('.yaml'):
                continue
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, VAULT_ROOT)
            
            # Special check for root files like inventory.yaml
            if os.path.dirname(rel_path) == "":
                continue
                
            parent_dir = rel_path.split(os.sep)[0]
            
            if parent_dir not in expected_dirs:
                if parent_dir != "scripts":
                    print(f"[WARNING] File '{rel_path}' is outside the standard taxonomy folders.")
                    warnings += 1
                continue
                
            # Read and inspect structure
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"[ERROR] Could not read file '{rel_path}': {e}")
                errors += 1
                continue
                
            # Basic validation based on schema
            if parent_dir == "identity" or parent_dir == "principles":
                if len(content.strip()) == 0:
                    print(f"[ERROR] Semantic file '{rel_path}' is empty.")
                    errors += 1
                else:
                    print(f"[OK] Semantic Memory file verified: '{rel_path}'")
            elif parent_dir == "runbooks":
                if "- [ ]" not in content and "- [x]" not in content:
                    print(f"[WARNING] Procedural runbook '{rel_path}' does not contain any checklist items.")
                    warnings += 1
                else:
                    print(f"[OK] Procedural Memory file verified: '{rel_path}'")
            elif parent_dir == "reflections" or parent_dir == "goals":
                if len(content.strip()) == 0:
                    print(f"[ERROR] Episodic file '{rel_path}' is empty.")
                    errors += 1
                else:
                    print(f"[OK] Episodic Memory file verified: '{rel_path}'")
                    
    # 3. Check inventory.yaml validity
    inventory_path = os.path.join(VAULT_ROOT, "inventory.yaml")
    if os.path.exists(inventory_path):
        print("\n[*] Validating inventory.yaml metadata index...")
        try:
            import yaml
            with open(inventory_path, 'r', encoding='utf-8') as f:
                items = yaml.safe_load(f)
                
            if not isinstance(items, list):
                print("[ERROR] inventory.yaml is not formatted as a top-level YAML list.")
                errors += 1
            else:
                required_keys = ["id", "status", "kind", "summary", "source", "last_verified", "retrieval_cue", "internal_memory_policy", "path"]
                for idx, item in enumerate(items):
                    if not isinstance(item, dict):
                        print(f"[ERROR] Item {idx} in inventory.yaml is not a valid dictionary structure.")
                        errors += 1
                        continue
                        
                    item_id = item.get("id", f"unknown_item_{idx}")
                    print(f"  - Verifying cataloged item: {item_id}")
                    
                    # Check missing keys
                    missing_keys = [k for k in required_keys if k not in item]
                    if missing_keys:
                        print(f"    [ERROR] Item '{item_id}' is missing required keys: {missing_keys}")
                        errors += 1
                    
                    # Check file paths exist
                    target_path = item.get("path")
                    if target_path:
                        full_target_path = os.path.join(VAULT_ROOT, target_path)
                        if not os.path.exists(full_target_path):
                            print(f"    [ERROR] Item '{item_id}' references non-existent file path: '{target_path}'")
                            errors += 1
                        else:
                            print(f"    [OK] File path exists: '{target_path}'")
        except Exception as e:
            print(f"[ERROR] Failed to parse or validate inventory.yaml: {e}")
            errors += 1
    else:
        print("\n[WARNING] inventory.yaml does not exist. (Recommended for cross-agent compatibility).")
        warnings += 1
                    
    print("-" * 60)
    print(f"[*] Validation finished with {errors} errors and {warnings} warnings.")
    return errors == 0

def main():
    parser = argparse.ArgumentParser(description="Gemini 3.5 Flash Memory Vault Engine")
    parser.add_argument("--query", "-q", type=str, help="Search terms or regex pattern")
    parser.add_argument("--case-sensitive", "-c", action="store_true", help="Perform case-sensitive search")
    parser.add_argument("--show-checklists", "-s", action="store_true", help="Display operational checklists")
    parser.add_argument("--validate", "-v", action="store_true", help="Validate memory vault schemas")
    
    args = parser.parse_args()
    
    if args.show_checklists:
        show_checklists()
    elif args.validate:
        success = validate_vault()
        if not success:
            sys.exit(1)
    elif args.query:
        search_vault(args.query, args.case_sensitive)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
