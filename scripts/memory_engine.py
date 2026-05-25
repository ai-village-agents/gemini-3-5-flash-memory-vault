#!/usr/bin/env python3
"""
Gemini 3.5 Flash Memory Engine
A lightweight, high-speed, local search and retrieval engine for the external memory vault.
Usage:
    python3 scripts/memory_engine.py --query "MemGPT"
    python3 scripts/memory_engine.py --show-checklists
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
    checklist_path = os.path.join(VAULT_ROOT, "procedures", "checklists.md")
    if os.path.exists(checklist_path):
        print(f"[*] Displaying current operating procedures from {checklist_path}:\n" + "="*60)
        with open(checklist_path, 'r') as f:
            print(f.read())
    else:
        print("[!] Checklists file not found.")

def main():
    parser = argparse.ArgumentParser(description="Gemini 3.5 Flash Memory Vault Engine")
    parser.add_argument("--query", "-q", type=str, help="Search terms or regex pattern")
    parser.add_argument("--case-sensitive", "-c", action="store_true", help="Perform case-sensitive search")
    parser.add_argument("--show-checklists", "-s", action="store_true", help="Display operational checklists")
    
    args = parser.parse_args()
    
    if args.show_checklists:
        show_checklists()
    elif args.query:
        search_vault(args.query, args.case_sensitive)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
