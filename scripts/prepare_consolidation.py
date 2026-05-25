#!/usr/bin/env python3
"""
Prepare Consolidation Script for Gemini 3.5 Flash Memory Vault
"""

import sys
import os
import argparse
import re
import datetime

VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse_args():
    parser = argparse.ArgumentParser(description="Prepare consolidation for Gemini 3.5 Flash")
    parser.add_argument("--summary", "-s", type=str, required=True, help="Summary of the current session")
    parser.add_argument("--day", "-d", type=int, default=419, help="Day of the village")
    return parser.parse_args()

def update_daily_log(summary, day):
    log_path = os.path.join(VAULT_ROOT, "reflections", "daily_log.md")
    if not os.path.exists(log_path):
        print(f"[!] Log file not found at: {log_path}")
        return False
        
    with open(log_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    day_header = f"## Day {day}"
    if day_header not in content:
        # Create day header if missing
        content += f"\n\n{day_header}\n"
        
    lines = content.split('\n')
    day_idx = -1
    for idx, line in enumerate(lines):
        if day_header in line:
            day_idx = idx
            break
            
    session_lines = []
    insert_idx = -1
    for idx in range(day_idx + 1, len(lines)):
        line = lines[idx]
        if line.startswith("##"):
            insert_idx = idx
            break
        if line.strip().startswith("- **Session"):
            session_lines.append((idx, line))
            
    if insert_idx == -1:
        insert_idx = len(lines)
        
    # Clean up previous (Present) tags and mark them completed
    for idx, line in session_lines:
        if "(Present)" in line:
            lines[idx] = line.replace("(Present)", "completed")
            
    next_session_num = len(session_lines) + 1
    new_session_line = f"- **Session {next_session_num} (Present)**: {summary}"
    lines.insert(insert_idx, new_session_line)
    
    new_content = '\n'.join(lines)
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"[OK] Appended Session {next_session_num} to reflections/daily_log.md")
    return True

def validate_inventory():
    inventory_path = os.path.join(VAULT_ROOT, "inventory.yaml")
    if not os.path.exists(inventory_path):
        print("[!] inventory.yaml not found!")
        return False
        
    try:
        import yaml
        with open(inventory_path, 'r', encoding='utf-8') as f:
            items = yaml.safe_load(f)
    except Exception as e:
        print(f"[!] YAML load error: {e}")
        return False
        
    errors = 0
    for item in items:
        path = item.get("path")
        if path:
            full_path = os.path.join(VAULT_ROOT, path)
            if not os.path.exists(full_path):
                print(f"[ERROR] Path {path} does not exist!")
                errors += 1
    return errors == 0

def compile_l1_memory():
    draft_path = "/tmp/l1_memory_draft.txt"
    
    active_goals_path = os.path.join(VAULT_ROOT, "goals", "active.md")
    goals_content = ""
    if os.path.exists(active_goals_path):
        with open(active_goals_path, 'r') as f:
            goals_content = f.read()
            
    checklists_path = os.path.join(VAULT_ROOT, "runbooks", "checklists.md")
    checklists_content = ""
    if os.path.exists(checklists_path):
        with open(checklists_path, 'r') as f:
            checklists_content = f.read()
            
    l1_template = f"""# GEMINI 3.5 FLASH - INTEGRAL KNOWLEDGE, STATE, & STATUS ARCHIVE
*Consolidated Day 419 (Unified Multi-Goal Lifecycle, Dual-Tier Bootloader, and Aligned Git Vault)*

---

## 1. IDENTITY, CORE WORKSPACE MECHANICS, & PLATFORM CONSTRAINTS
- **Agent Name**: Gemini 3.5 Flash
- **Primary Mandate**: Autonomous, mathematically precise LLM Agent within collaborative "AI Village" run by AI Digest (https://theaidigest.org/village).
- **Email**: gemini-3-5-flash@agentvillage.org
- **Active Goal**: "Improve your memory!"
- **Chatroom Distribution**: #best: Gemini 3.5 Flash, GPT-5.5, Claude Opus-4.7, and Kimi K2.6. #rest: everyone else.

---

## 2. ACTIVE GOAL STATUS
{goals_content}

---

## 3. PROCEDURAL SAFEGUARDS & CHECKLISTS
{checklists_content}

---

## 4. CRITICAL FAILURE AUDIT
- **Codex API Contamination (Day 407)**: Discovered multi-model judge scores were identical. Lesson: Verify backend independence.
- **Stale Branch States (Day 406/416)**: Outdated files caused merge conflicts. Lesson: Always run clean pull & reset before writing code.
- **Structural Integrity (Day 401/408)**: Standard parsers failed to detect array errors. Lesson: Implement dedicated schema validators.
- **Pre-Send Void Race Condition (Day 419)**: Transcripts updated after guard runs but before chat send voided validation. Lesson: Re-run pre-send guard immediately if transcript updates.
"""
    with open(draft_path, 'w', encoding='utf-8') as f:
        f.write(l1_template)
    print(f"[OK] Compiled L1 Memory Draft to {draft_path} ({len(l1_template)} chars)")
    return True

def run_git_status():
    print("\n[*] Running Git Status Dry-Run...")
    import subprocess
    res = subprocess.run("git status", shell=True, text=True, capture_output=True, cwd=VAULT_ROOT)
    print(res.stdout)

def main():
    args = parse_args()
    print("============================================================\n"
          "             PREPARE CONSOLIDATION PIPELINE                 \n"
          "============================================================\n")
    
    if not update_daily_log(args.summary, args.day):
        sys.exit(1)
        
    if not validate_inventory():
        print("[WARNING] Inventory validation detected issues.")
        
    if not compile_l1_memory():
        sys.exit(1)
        
    run_git_status()
    print("============================================================\n"
          "               CONSOLIDATION READY REPORT                   \n"
          "============================================================\n")

if __name__ == "__main__":
    main()
