#!/usr/bin/env python3
"""
Cross-Agent Memory Scanner and Consolidator for Gemini 3.5 Flash.
Crawls inventory.yaml files from all 14 village memory repositories and builds a local searchable catalog.
"""

import os
import sys
import re
import json
import urllib.request
import urllib.error
import argparse
import datetime
import yaml

VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONSOLIDATED_PATH = os.path.join(VAULT_ROOT, "peers", "consolidated_inventory.json")

PEER_REPOS = [
    "gpt-5-5-memory-improvement",
    "claude-opus-4-7-memory",
    "k2-6-memory",
    "gemini-3-5-flash-memory-vault",
    "gpt-5-2-memory-improvement",
    "opus-46-memory",
    "gpt-5-4-memory-kit",
    "claude-opus-memory",
    "memory-improvement",
    "haiku-memory-system",
    "gemini-3.1-pro-memory",
    "gpt-5-1-memory",
    "deepseek-v3.2-memory-system",
    "fortified-evidentiary-memory"
]

def format_val(val):
    if val is None:
        return ""
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val.isoformat()
    return str(val)

def fetch_inventory(repo):
    branches = ["main", "master"]
    for branch in branches:
        url = f"https://raw.githubusercontent.com/ai-village-agents/{repo}/{branch}/inventory.yaml"
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8'), branch, url
        except urllib.error.URLError:
            continue
    return None, None, None

def scan_all():
    print("=============================================================")
    print("           CROSS-AGENT METADATA INVENTORY CRAWLER            ")
    print("=============================================================")
    print(f"[*] Crawling {len(PEER_REPOS)} peer repositories...")
    
    consolidated = []
    success_count = 0
    
    for repo in PEER_REPOS:
        print(f"[*] Fetching: {repo}...", end="", flush=True)
        content, branch, url = fetch_inventory(repo)
        if not content:
            print(" [FAILED] (No inventory.yaml found on main/master)")
            continue
            
        try:
            items = yaml.safe_load(content)
            if not items:
                print(" [EMPTY] (Invalid or empty YAML)")
                continue
                
            # Handle some agents having a root key 'items' instead of a top-level list
            if isinstance(items, dict) and "items" in items:
                items = items["items"]
                
            if not isinstance(items, list):
                print(" [ERROR] (YAML is not a list/array under root or 'items')")
                continue
                
            repo_items = []
            for item in items:
                if not isinstance(item, dict):
                    continue
                
                # Retrieve fields with stringification fallback
                item_id = format_val(item.get("id", "unknown"))
                status = format_val(item.get("status", "unknown"))
                kind = format_val(item.get("kind", "unknown"))
                summary = format_val(item.get("summary", ""))
                last_verified = format_val(item.get("last_verified", "unknown"))
                retrieval_cue = format_val(item.get("retrieval_cue", ""))
                path = format_val(item.get("path", item.get("file", "")))
                
                normalized = {
                    "id": item_id,
                    "status": status,
                    "kind": kind,
                    "summary": summary,
                    "source_repo": repo,
                    "last_verified": last_verified,
                    "retrieval_cue": retrieval_cue,
                    "path": path,
                    "url": f"https://github.com/ai-village-agents/{repo}/blob/{branch}/{path}"
                }
                repo_items.append(normalized)
                
            consolidated.extend(repo_items)
            success_count += 1
            print(f" [OK] (Found {len(repo_items)} items on branch '{branch}')")
            
        except Exception as e:
            print(f" [ERROR] (Failed to parse: {e})")
            
    # Save the consolidated file
    os.makedirs(os.path.dirname(CONSOLIDATED_PATH), exist_ok=True)
    try:
        with open(CONSOLIDATED_PATH, 'w', encoding='utf-8') as f:
            json.dump(consolidated, f, indent=2, ensure_ascii=False)
        print("-" * 61)
        print(f"[SUCCESS] Scanned {success_count}/{len(PEER_REPOS)} repos successfully.")
        print(f"[SUCCESS] Total consolidated index: {len(consolidated)} items.")
        print(f"[SUCCESS] Catalog written to: peers/consolidated_inventory.json")
    except Exception as e:
        print(f"\n[ERROR] Failed to write consolidated index: {e}")
        
    print("=============================================================\n")

def list_repos():
    print("=============================================================")
    print("                 TRACKED PEER MEMORY REPOS                   ")
    print("=============================================================")
    for idx, repo in enumerate(PEER_REPOS, 1):
        print(f" {idx:02d}. https://github.com/ai-village-agents/{repo}")
    print("=============================================================\n")

def search_index(query):
    if not os.path.exists(CONSOLIDATED_PATH):
        print(f"[WARNING] Consolidated index not found at {CONSOLIDATED_PATH}.")
        print("[*] Running scan first...")
        scan_all()
        if not os.path.exists(CONSOLIDATED_PATH):
            return

    try:
        with open(CONSOLIDATED_PATH, 'r', encoding='utf-8') as f:
            items = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read consolidated index: {e}")
        return

    print("=============================================================")
    print(f"         SEARCHING CROSS-AGENT MEMORY INDEX: '{query}'       ")
    print("=============================================================")
    
    matches = 0
    try:
        rx = re.compile(query, re.IGNORECASE)
    except re.error as e:
        print(f"[ERROR] Invalid regex query: {e}")
        return

    for item in items:
        # Search across id, summary, retrieval_cue, and source_repo
        search_field = f"{item['id']} {item['summary']} {item['retrieval_cue']} {item['source_repo']}"
        if rx.search(search_field):
            matches += 1
            print(f"\n[{matches:02d}] ID: {item['id']} ({item['kind']})")
            print(f"     Repo:    {item['source_repo']}")
            print(f"     Summary: {item['summary']}")
            print(f"     Cue:     {item['retrieval_cue']}")
            print(f"     URL:     {item['url']}")
            
    print("-" * 61)
    print(f"[*] Search complete. Found {matches} matching items.")
    print("=============================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Cross-Agent Memory Scanner")
    parser.add_argument("--scan", "-s", action="store_true", help="Scan and crawl all peer inventories")
    parser.add_argument("--list-repos", "-l", action="store_true", help="List all tracked repos")
    parser.add_argument("--search", "-p", type=str, help="Search terms / regex across peer index")
    
    args = parser.parse_args()
    
    if args.scan:
        scan_all()
    elif args.list_repos:
        list_repos()
    elif args.search:
        search_index(args.search)
    else:
        # Default behavior: run scan and search
        scan_all()

if __name__ == "__main__":
    main()
