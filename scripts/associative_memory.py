#!/usr/bin/env python3
import os
import json
import sys
import argparse
import difflib

DEFAULT_DB_PATH = "reflections/associative_memories.json"

SEED_MEMORIES = [
    {
        "id": 1,
        "text": "FlashAttention tiling strategy avoids GPU HBM bottleneck by loading blocks into SRAM and scaling Online Softmax denominators.",
        "importance": 9,
        "created_day": 412,
        "last_accessed_day": 412
    },
    {
        "id": 2,
        "text": "DPO mathematically cancels out the partition function Z(x) to optimize Bradley-Terry preference pairs directly without RL routing.",
        "importance": 8,
        "created_day": 416,
        "last_accessed_day": 416
    },
    {
        "id": 3,
        "text": "Pre-Send Void Race Condition: Transcripts updating after pre-send checks but before actual send can void validation. Always re-run checks.",
        "importance": 10,
        "created_day": 419,
        "last_accessed_day": 419
    },
    {
        "id": 4,
        "text": "Silent Inventory Indentation Drift: Incorrectly indented items at root level parse silently instead of under schema key. Enforce strict shape checks.",
        "importance": 9,
        "created_day": 419,
        "last_accessed_day": 419
    },
    {
        "id": 5,
        "text": "Self-Matching Query Drift: Hardcoded search query strings inside tests trigger false positives. Generate query variables dynamically.",
        "importance": 7,
        "created_day": 419,
        "last_accessed_day": 419
    }
]

def load_memories(db_path):
    if not os.path.exists(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        with open(db_path, "w") as f:
            json.dump(SEED_MEMORIES, f, indent=2)
        return SEED_MEMORIES
    try:
        with open(db_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load memories: {e}")
        return []

def save_memories(db_path, memories):
    try:
        with open(db_path, "w") as f:
            json.dump(memories, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to save memories: {e}")

def calculate_relevance(query, text):
    return difflib.SequenceMatcher(None, query.lower(), text.lower()).ratio()

def main():
    parser = argparse.ArgumentParser(description="Associative Memory Retrieval Engine (SOTA)")
    parser.add_argument("--query", "-q", type=str, help="Query string to search memory")
    parser.add_argument("--add", "-a", type=str, help="Text of new memory to add")
    parser.add_argument("--importance", "-i", type=int, choices=range(1, 11), help="Importance rating of new memory (1-10)")
    parser.add_argument("--list", "-l", action="store_true", help="List all stored memories")
    parser.add_argument("--current-day", "-d", type=int, default=419, help="Override current village day")
    parser.add_argument("--db", type=str, default=DEFAULT_DB_PATH, help="Path to JSON storage")
    parser.add_argument("--w-recency", type=float, default=0.3, help="Weight for recency (0-1)")
    parser.add_argument("--w-importance", type=float, default=0.3, help="Weight for importance (0-1)")
    parser.add_argument("--w-relevance", type=float, default=0.4, help="Weight for relevance (0-1)")
    
    args = parser.parse_args()
    
    memories = load_memories(args.db)
    
    if args.add:
        if not args.importance:
            print("[ERROR] Please provide --importance (1-10) when adding a memory.")
            sys.exit(1)
        new_id = max([m["id"] for m in memories], default=0) + 1
        new_mem = {
            "id": new_id,
            "text": args.add,
            "importance": args.importance,
            "created_day": args.current_day,
            "last_accessed_day": args.current_day
        }
        memories.append(new_mem)
        save_memories(args.db, memories)
        print(f"[SUCCESS] Added memory ID {new_id}: '{args.add}' with importance {args.importance}")
        sys.exit(0)
        
    if args.list:
        print("\n" + "="*80)
        print("                 ASSOCIATIVE MEMORY VAULT LIST")
        print("="*80)
        print(f"{'ID':<4} | {'Day':<4} | {'Acc':<4} | {'Imp':<3} | {'Memory Text'}")
        print("-"*80)
        for m in sorted(memories, key=lambda x: x["id"]):
            print(f"{m['id']:<4} | {m['created_day']:<4} | {m['last_accessed_day']:<4} | {m['importance']:<3} | {m['text'][:65]}...")
        print("="*80 + "\n")
        sys.exit(0)
        
    if args.query:
        scored_memories = []
        for m in memories:
            recency_diff = args.current_day - m["last_accessed_day"]
            recency = 1.0 / (1.0 + recency_diff)
            importance = m["importance"] / 10.0
            relevance = calculate_relevance(args.query, m["text"])
            
            total_score = (args.w_recency * recency) + (args.w_importance * importance) + (args.w_relevance * relevance)
            scored_memories.append((total_score, recency, importance, relevance, m))
            
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        print("\n" + "="*80)
        print(f"                 ASSOCIATIVE RETRIEVAL RESULTS FOR: '{args.query}'")
        print("="*80)
        
        if scored_memories:
            top_mem = scored_memories[0][4]
            for orig in memories:
                if orig["id"] == top_mem["id"]:
                    orig["last_accessed_day"] = args.current_day
            save_memories(args.db, memories)
            
        for i, (score, rec, imp, rel, m) in enumerate(scored_memories[:5]):
            print(f"[{i+1}] ID {m['id']} - SCORE: {score:.4f} [Recency: {rec:.2f}, Importance: {imp:.2f}, Relevance: {rel:.2f}]")
            print(f"    Text: {m['text']}")
            print(f"    Age: Created Day {m['created_day']}, Last Accessed Day {m['last_accessed_day']}")
            print("-" * 80)
        print("="*80 + "\n")
        sys.exit(0)
        
    parser.print_help()

if __name__ == "__main__":
    main()
