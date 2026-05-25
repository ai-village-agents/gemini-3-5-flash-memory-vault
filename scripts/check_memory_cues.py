#!/usr/bin/env python3
"""
Gemini 3.5 Flash Memory Cue & Size Validator
Checks the proposed L1 memory block or a draft file for:
- Size limits (character count and line count)
- Required operational cues (schedules, active goal, bootloader, pre-send script, etc.)
- Forbidden cues (completed or archived goals, excessively detailed stale context)
"""

import sys
import os
import re

MAX_CHARS = 15000
MAX_LINES = 350

REQUIRED_CUES = [
    "Gemini 3.5 Flash",
    "Improve your memory!",
    "scripts/boot.py",
    "scripts/pre_send_chat.py",
    "scripts/pre_consolidate.py",
    "inventory.yaml"
]

FORBIDDEN_CUES = [
    "Run your own Youtube channel!", # Completed goal statement from Shoshannah
    "Video 1: \"The Mechanics of Speed", # Extremely specific stale video metadata list
    "Video 2: \"Speculative Decoding",
    "Video 3: \"Mixture of Experts"
]

def check_memory(text):
    errors = []
    warnings = []
    
    # 1. Size checks
    char_count = len(text)
    line_count = len(text.splitlines())
    
    print(f"[*] Memory block character count: {char_count} (Limit: {MAX_CHARS})")
    print(f"[*] Memory block line count:      {line_count} (Limit: {MAX_LINES})")
    
    if char_count > MAX_CHARS:
        errors.append(f"Memory block size ({char_count} chars) exceeds the maximum allowed ({MAX_CHARS} chars).")
    elif char_count > 12000:
        warnings.append(f"Memory block size ({char_count} chars) is approaching the limit. Consider shortening.")
        
    if line_count > MAX_LINES:
        errors.append(f"Memory block lines ({line_count} lines) exceeds the maximum allowed ({MAX_LINES} lines).")
        
    # 2. Required cues check
    for cue in REQUIRED_CUES:
        if cue.lower() not in text.lower():
            errors.append(f"Missing required operational memory cue: '{cue}'")
            
    # 3. Forbidden cues check
    for cue in FORBIDDEN_CUES:
        if cue.lower() in text.lower():
            warnings.append(f"Found potentially stale or forbidden cue: '{cue}'. Ensure old video details or archived goals are offloaded to L2.")
            
    return len(errors) == 0, errors, warnings

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Memory Cue and Size Validator")
    parser.add_argument("--file", "-f", type=str, help="Path to the draft memory file to check")
    parser.add_argument("--text", "-t", type=str, help="Direct memory string to check")
    
    args = parser.parse_args()
    
    text = ""
    if args.file:
        if not os.path.exists(args.file):
            print(f"[ERROR] Specified file does not exist: {args.file}")
            sys.exit(1)
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        # Fallback to check the compiled temporary L1 draft if it exists
        default_draft = "/tmp/l1_memory_draft.txt"
        if os.path.exists(default_draft):
            print(f"[*] No input specified. Checking default compilation draft: {default_draft}")
            with open(default_draft, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            print("[ERROR] Please provide --file, --text, or run prepare_consolidation.py first to compile default draft.")
            sys.exit(1)
            
    success, errors, warnings = check_memory(text)
    
    print("\n=============================================================")
    print("                MEMORY CUE & SIZE REPORT                     ")
    print("=============================================================")
    if errors:
        print("[!] CUE VALIDATION FAILED:")
        for err in errors:
            print(f"  - ERROR: {err}")
    else:
        print("[OK] Proposed memory block matches size limits and holds all required cues.")
        
    if warnings:
        print("\n[!] STALE CONTEXT WARNINGS:")
        for warn in warnings:
            print(f"  - WARNING: {warn}")
    print("=============================================================\n")
    
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
