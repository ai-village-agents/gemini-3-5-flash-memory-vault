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
                continue
                
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
    expected_dirs = ["identity", "principles", "runbooks", "reflections", "goals"]
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
            if not file.endswith('.md'):
                continue
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, VAULT_ROOT)
            parent_dir = rel_path.split(os.sep)[0]
            
            if parent_dir not in expected_dirs:
                if parent_dir != "scripts":
                    print(f"[WARNING] Markdown file '{rel_path}' is outside the standard taxonomy folders.")
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
        validate_vault()
    elif args.query:
        search_vault(args.query, args.case_sensitive)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
