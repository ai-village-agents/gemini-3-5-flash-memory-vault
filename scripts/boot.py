#!/usr/bin/env python3
"""
Session Bootloader for Gemini 3.5 Flash Memory Vault
"""

import subprocess
import os
import sys

VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_cmd(cmd, cwd=None):
    try:
        res = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd)
        return True, res.stdout, res.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def main():
    print("============================================================")
    print("                GEMINI 3.5 FLASH - SESSION BOOT             ")
    print("============================================================\n")
    
    # 1. Sync repository
    print("[*] Synchronizing memory vault with remote repository...")
    ok, stdout, stderr = run_cmd("git pull origin master", VAULT_ROOT)
    if ok:
        print("[OK] Git synchronization successful.")
        if "Already up to date" in stdout:
            print("     State: Up-to-date with upstream.")
        else:
            print("     State: Pull completed successfully.")
    else:
        print(f"[WARNING] Git synchronization encountered an issue:\n{stderr}")
        
    # 2. Validate memory schema
    print("\n[*] Validating memory vault structure and inventory.yaml...")
    engine_path = os.path.join(VAULT_ROOT, "scripts", "memory_engine.py")
    ok, stdout, stderr = run_cmd(f"python3 {engine_path} --validate")
    if ok:
        print("[OK] Memory schema is fully compliant.")
    else:
        print(f"[ERROR] Memory schema validation failed:\n{stdout}\n{stderr}")
        
    # 2b. Auto-scan peer memory inventories
    print("\n[*] Auto-scanning and consolidating peer memory inventories...")
    scan_script_path = os.path.join(VAULT_ROOT, "scripts", "scan_peers.py")
    if os.path.exists(scan_script_path):
        ok, stdout, stderr = run_cmd(f"python3 {scan_script_path} --scan")
        if ok:
            print("[OK] Peer memories auto-scanned and consolidated.")
        else:
            print(f"[WARNING] Peer memory auto-scan encountered an issue:\n{stdout}\n{stderr}")
    else:
        print("[WARNING] Peer scan script scan_peers.py not found.")

    # 3. Read and output active goals
    print("\n[*] Loading active session goals from goals/active.md...\n" + "-"*60)
    active_goals_path = os.path.join(VAULT_ROOT, "goals", "active.md")
    if os.path.exists(active_goals_path):
        try:
            with open(active_goals_path, 'r', encoding='utf-8') as f:
                print(f.read().strip())
        except Exception as e:
            print(f"[ERROR] Could not read active goals: {e}")
    else:
        print("[WARNING] active.md goals file does not exist!")
        
    print("-"*60)
    print("\n============================================================\n")

if __name__ == "__main__":
    main()
