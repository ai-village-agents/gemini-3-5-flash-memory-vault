#!/usr/bin/env python3
"""
Pre-Consolidation Guard for Gemini 3.5 Flash
Enforces git sync status, runs schema verification, checks memory limits, and validates end-to-end memory retrieval.
"""

import sys
import os
import subprocess

VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_cmd(cmd, cwd=None):
    try:
        res = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd)
        return res.stdout.strip(), ""
    except subprocess.CalledProcessError as e:
        return "", e.output.strip() if e.output else str(e)

def get_git_status():
    stdout, stderr = run_cmd("git status --porcelain", cwd=VAULT_ROOT)
    return stdout

def get_unpushed_count():
    # Count commits between local and remote
    stdout, stderr = run_cmd("git rev-list --count @{u}..HEAD", cwd=VAULT_ROOT)
    if not stdout:
        return 0
    try:
        return int(stdout)
    except ValueError:
        return 0

def run_schema_validation():
    engine_path = os.path.join(VAULT_ROOT, "scripts", "memory_engine.py")
    stdout, stderr = run_cmd(f"python3 {engine_path} --validate")
    return stdout

def run_cue_validation():
    cues_path = os.path.join(VAULT_ROOT, "scripts", "check_memory_cues.py")
    stdout, stderr = run_cmd(f"python3 {cues_path}")
    return stdout

def run_retrieval_validation():
    test_path = os.path.join(VAULT_ROOT, "scripts", "retrieval_self_test.py")
    stdout, stderr = run_cmd(f"python3 {test_path}")
    return stdout

def main():
    print("============================================================")
    print("             PRE-CONSOLIDATION SAFETY CHECK                 ")
    print("============================================================")
    
    errors = []
    warnings = []
    
    # 1. Run Schema Validation
    print("[*] Running schema conformity check...")
    val_out = run_schema_validation()
    print(val_out)
    if "Validation finished with 0 errors" not in val_out:
        errors.append("Schema validation failed. Check 'scripts/memory_engine.py --validate' for details.")
    else:
        print("[OK] Schema validation passed.")
        
    # 1.5. Run Cue and Size Validation
    print("\n[*] Running cue and size limits check...")
    cue_out = run_cue_validation()
    print(cue_out)
    if "CUE VALIDATION FAILED" in cue_out:
        errors.append("Memory cue/size validation failed. Check 'scripts/check_memory_cues.py' for details.")
    else:
        print("[OK] Memory cues and size limits are fully valid.")

    # 1.8. Run Retrieval Validation
    print("\n[*] Running programmatic end-to-end retrieval self-tests...")
    ret_out = run_retrieval_validation()
    print(ret_out)
    if "All retrieval self-tests passed successfully!" not in ret_out:
        errors.append("Retrieval self-test failed. Check 'scripts/retrieval_self_test.py' for details.")
    else:
        print("[OK] End-to-end retrieval validation passed.")
        
    # 2. Check Git Uncommitted Files
    print("\n[*] Checking Git status...")
    git_status = get_git_status()
    if git_status:
        print("[WARNING] You have local uncommitted changes or untracked files:")
        for line in git_status.split('\n'):
            print(f"  {line}")
        warnings.append("There are uncommitted changes or untracked files in the vault repository.")
    else:
        print("[OK] Repository is clean.")
        
    # 3. Check Unpushed Commits
    unpushed = get_unpushed_count()
    if unpushed > 0:
        print(f"[WARNING] You have {unpushed} unpushed commits.")
        warnings.append(f"{unpushed} commits need to be pushed to GitHub.")
    else:
        print("[OK] All commits are pushed and fully synchronized with upstream.")
        
    # Print summary
    print("\n------------------------------------------------------------")
    print("                       SUMMARY REPORT                       ")
    print("------------------------------------------------------------")
    if errors:
        print("[!] PRE-CONSOLIDATION VERIFICATION FAILED:")
        for err in errors:
            print(f"  - ERROR: {err}")
    else:
        print("[OK] Memory vault is safe to consolidate.")
        
    if warnings:
        print("\n[!] REMINDERS / WARNINGS:")
        for warn in warnings:
            print(f"  - WARNING: {warn}")
            
    print("============================================================\n")
    
    if errors:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
