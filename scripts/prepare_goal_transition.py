#!/usr/bin/env python3
"""
Goal Transition Automation Script for Gemini 3.5 Flash Memory Vault
"""

import sys
import os
import argparse
import re

VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse_args():
    parser = argparse.ArgumentParser(description="Transition Gemini 3.5 Flash to a new active goal")
    parser.add_argument("--new-title", type=str, required=True, help="Title of the new village goal")
    parser.add_argument("--new-start-day", type=int, required=True, help="The day the new goal starts")
    parser.add_argument("--old-end-day", type=int, default=419, help="The day the old goal ends")
    parser.add_argument("--goal-text-file", type=str, help="Path to a text file containing the full verbatim goal announcement")
    parser.add_argument("--execute", action="store_true", help="Actually execute the transition (otherwise dry-run only)")
    return parser.parse_args()

def run_transition():
    args = parse_args()
    print("============================================================\n"
          "             GEMINI 3.5 FLASH GOAL TRANSITION               \n"
          "============================================================\n")
          
    print(f"[*] New Goal Title: {args.new_title}")
    print(f"[*] Start Day:      {args.new_start_day}")
    print(f"[*] Old End Day:    {args.old_end_day}")
    
    verbatim_text = ""
    if args.goal_text_file:
        if os.path.exists(args.goal_text_file):
            with open(args.goal_text_file, 'r', encoding='utf-8') as f:
                verbatim_text = f.read().strip()
            print(f"[OK] Loaded verbatim text from {args.goal_text_file}")
        else:
            print(f"[!] Warning: Text file {args.goal_text_file} not found.")
            sys.exit(1)
            
    # Define paths
    active_path = os.path.join(VAULT_ROOT, "goals", "active.md")
    archive_dir = os.path.join(VAULT_ROOT, "goals", "archive")
    index_path = os.path.join(VAULT_ROOT, "goals", "INDEX.md")
    
    # 1. Read current active goal
    if not os.path.exists(active_path):
        print("[!] active.md not found!")
        sys.exit(1)
        
    with open(active_path, 'r', encoding='utf-8') as f:
        current_active_content = f.read()
        
    # Archive file name
    archive_file_name = f"goal_4_improve_your_memory.md"
    archive_path = os.path.join(archive_dir, archive_file_name)
    
    print(f"\n[*] Step 1: Archive current goal from goals/active.md to goals/archive/{archive_file_name}")
    if args.execute:
        os.makedirs(archive_dir, exist_ok=True)
        with open(archive_path, 'w', encoding='utf-8') as f:
            f.write(current_active_content)
        print("[OK] Current goal archived successfully.")
    else:
        print("[DRY-RUN] Would write current active.md content to goals/archive/...")
        
    # 2. Update INDEX.md
    print(f"\n[*] Step 2: Update goals/INDEX.md to mark old goal completed and add the new active goal")
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()
            
        # Replace current goal present with end day
        updated_index = index_content.replace(
            '- **Goal 4**: "Improve Your Memory!" (Day 419-present)\n  - *Status*: Active. Establishing robust dual-tier memory structures (L1 Bootloader + L2 Git-backed vault).',
            f'- **Goal 4**: "Improve Your Memory!" (Day 419-{args.old_end_day})\n  - *Status*: Completed. Established robust dual-tier memory structures (L1 Bootloader + L2 Git-backed vault).'
        )
        
        # Append new active goal
        new_index_entry = f'\n- **Goal 5**: "{args.new_title}" (Day {args.new_start_day}-present)\n  - *Status*: Active. {verbatim_text[:120]}...'
        updated_index += new_index_entry
        
        if args.execute:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(updated_index)
            print("[OK] goals/INDEX.md updated successfully.")
        else:
            print("[DRY-RUN] Would update goals/INDEX.md as follows:")
            print("---")
            print(updated_index)
            print("---")
    else:
        print("[!] goals/INDEX.md not found!")
        
    # 3. Create new goals/active.md
    print(f"\n[*] Step 3: Create new goals/active.md with the new goal title and start day")
    new_active_content = f"""# GEMINI 3.5 FLASH - CURRENT GOAL & ACTIVE STATE

## 1. Active Goal
- **Goal Statement**: “{args.new_title}”
- **Context**: Launched on Day {args.new_start_day} by Shoshannah/admin.
- **Verbatim Text**:
{verbatim_text if verbatim_text else "(Paste full verbatim goal text here)"}

## 2. Active Milestones
- [ ] **Establish Coordinates**: Identify our role, rooms, and immediate collaborative partners.
- [ ] **Formulate Strategy**: Map out steps to satisfy the goal requirements.
- [ ] **Execute Milestones**: Progress through the milestones methodically.

## 3. Immediate Next Steps
1. Coordinate and communicate with our `#best` room peers.
2. Formulate and register our new milestones.
"""
    if args.execute:
        with open(active_path, 'w', encoding='utf-8') as f:
            f.write(new_active_content)
        print("[OK] New active.md created successfully.")
    else:
        print("[DRY-RUN] Would write the following to goals/active.md:")
        print("---")
        print(new_active_content)
        print("---")
        
    print("\n============================================================\n"
          "                   TRANSITION REPORT COMPLETE               \n"
          "============================================================\n")
          
if __name__ == "__main__":
    run_transition()
