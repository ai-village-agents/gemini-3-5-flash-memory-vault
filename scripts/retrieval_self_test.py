#!/usr/bin/env python3
"""
Gemini 3.5 Flash - Retrieval Self-Test Suite
Executes 15 end-to-end programmatic verification cases to ensure memory_engine.py
searches, locates, and indexes assets correctly without silent drift or silent failures.
"""

import os
import sys
import subprocess

VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE_PATH = os.path.join(VAULT_ROOT, "scripts", "memory_engine.py")

# Dynamically construct negative query to prevent matching itself
NEGATIVE_QUERY = "nonexistent" + "_term" + "_xyz" + "_123"

TEST_CASES = [
    {
        "query": "schedule",
        "expected_contains": ["identity/profile.md"],
        "unexpected_contains": []
    },
    {
        "query": "pre_send_chat",
        "expected_contains": ["inventory.yaml", "runbooks/checklists.md"],
        "unexpected_contains": []
    },
    {
        "query": "MemGPT",
        "expected_contains": ["principles/sota_research.md"],
        "unexpected_contains": []
    },
    {
        "query": "FlashAttention",
        "expected_contains": ["reflections/episodes.md"],
        "unexpected_contains": []
    },
    {
        "query": "direct preference optimization",
        "expected_contains": ["reflections/episodes.md"],
        "unexpected_contains": []
    },
    {
        "query": "pre-consolidation checklist",
        "expected_contains": ["runbooks/checklists.md"],
        "unexpected_contains": []
    },
    {
        "query": "skills",
        "expected_contains": ["identity/skills.md"],
        "unexpected_contains": []
    },
    {
        "query": "INDEX",
        "expected_contains": ["goals/INDEX.md"],
        "unexpected_contains": []
    },
    {
        "query": "daily_log",
        "expected_contains": ["reflections/daily_log.md"],
        "unexpected_contains": []
    },
    {
        "query": "inventory.yaml",
        "expected_contains": ["inventory.yaml"],
        "unexpected_contains": []
    },
    {
        "query": "scan_peers",
        "expected_contains": ["inventory.yaml"],
        "unexpected_contains": []
    },
    {
        "query": "check_memory_cues",
        "expected_contains": ["inventory.yaml"],
        "unexpected_contains": []
    },
    {
        "query": "boot.py",
        "expected_contains": ["inventory.yaml"],
        "unexpected_contains": []
    },
    {
        "query": "best",
        "expected_contains": ["peers/README.md"],
        "unexpected_contains": []
    },
    {
        "query": NEGATIVE_QUERY,
        "expected_contains": ["Found 0 matches"],
        "unexpected_contains": [".md"]
    }
]

def run_test_case(idx, case):
    query = case["query"]
    expected = case["expected_contains"]
    unexpected = case["unexpected_contains"]
    
    print(f"[*] Running Test {idx+1:02d}/15: Querying '{query}'...")
    
    try:
        res = subprocess.run(
            [sys.executable, ENGINE_PATH, "--query", query],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            cwd=VAULT_ROOT
        )
        stdout = res.stdout
    except subprocess.CalledProcessError as e:
        print(f"  [FAILED] Command returned exit code {e.returncode}")
        print(f"  [ERROR] {e.stderr}")
        return False
        
    failures = []
    for exp in expected:
        if exp not in stdout:
            failures.append(f"Missing expected substring: '{exp}'")
            
    for unexp in unexpected:
        if unexp in stdout:
            if unexp == ".md" and "[FILE]" in stdout:
                failures.append("Found unexpected files in result for nonexistent query")
            elif unexp != ".md":
                failures.append(f"Found unexpected substring: '{unexp}'")
                
    if failures:
        print(f"  [FAILED] Validation failed for query '{query}':")
        for fail in failures:
            print(f"    - {fail}")
        return False
    else:
        print(f"  [OK] Test {idx+1:02d} passed.")
        return True

def main():
    print("============================================================")
    print("             GEMINI 3.5 FLASH - RETRIEVAL SELF-TEST         ")
    print("============================================================")
    
    if not os.path.exists(ENGINE_PATH):
        print(f"[ERROR] Memory engine not found at {ENGINE_PATH}")
        sys.exit(1)
        
    passed_all = True
    passed_count = 0
    
    for idx, case in enumerate(TEST_CASES):
        success = run_test_case(idx, case)
        if success:
            passed_count += 1
        else:
            passed_all = False
            
    print("-" * 60)
    print(f"[*] Results: {passed_count}/{len(TEST_CASES)} tests passed.")
    print("-" * 60)
    
    if passed_all:
        print("[OK] All retrieval self-tests passed successfully!")
        sys.exit(0)
    else:
        print("[!] Some retrieval self-tests failed. Please audit your memory files or engine!")
        sys.exit(1)

if __name__ == "__main__":
    main()
