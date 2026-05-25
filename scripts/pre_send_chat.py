#!/usr/bin/env python3
"""
Pre-Send Chat Guard for Gemini 3.5 Flash
Enforces message length limits, deduplication checks, and standard formatting.
"""

import sys
import argparse
import re

def count_sentences(text):
    # Basic sentence splitter based on punctuation
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    # Filter empty items
    sentences = [s for s in sentences if s.strip()]
    return len(sentences)

def validate_message(message, recipient, purpose):
    errors = []
    warnings = []
    
    # 1. Recipient check
    if not recipient:
        errors.append("Recipient (--to) is required.")
    
    # 2. Purpose check
    if not purpose:
        errors.append("Purpose (--purpose) is required.")
        
    # 3. Message check
    if not message or not message.strip():
        errors.append("Message is empty.")
        return False, errors, warnings
        
    # 4. Message length (max 4 sentences)
    num_sentences = count_sentences(message)
    if num_sentences > 4:
        errors.append(f"Message exceeds maximum of 4 sentences (found {num_sentences}).")
    
    # 5. Length in characters
    if len(message) > 400:
        warnings.append(f"Message is quite long ({len(message)} chars). Ensure it is compact.")

    # 6. Duplication / Repetitive words check
    normalized = message.lower()
    greetings = ["hi everyone", "hello team", "excited to", "good morning", "hey guys"]
    for greet in greetings:
        if greet in normalized:
            warnings.append(f"Message contains a common generic greeting: '{greet}'. Consider removing to prevent clutter.")
            
    if "https://github.com/ai-village-agents/gemini-3-5-flash-memory-vault" in message:
        warnings.append("Message contains our repository link. Ensure you are not re-announcing it unnecessarily.")
        
    return len(errors) == 0, errors, warnings

def main():
    parser = argparse.ArgumentParser(description="Pre-Send Chat Guard")
    parser.add_argument("--message", "-m", type=str, help="The proposed chat message")
    parser.add_argument("--to", "-t", type=str, help="The target recipient or channel")
    parser.add_argument("--purpose", "-p", type=str, help="Purpose of the message")
    
    args = parser.parse_args()
    
    message = args.message
    if not message and not sys.stdin.isatty():
        message = sys.stdin.read().strip()
        
    if not message:
        print("[ERROR] No message provided. Use --message or pipe into stdin.")
        sys.exit(1)
        
    success, errors, warnings = validate_message(message, args.to, args.purpose)
    
    print("\n============================================================")
    print("                PRE-SEND CHAT GUARD REPORT                  ")
    print("============================================================")
    print(f"Recipient : {args.to}")
    print(f"Purpose   : {args.purpose}")
    print(f"Sentences : {count_sentences(message)}")
    print(f"Length    : {len(message)} characters")
    print("------------------------------------------------------------")
    
    if errors:
        print("[!] VALIDATION FAILED:")
        for err in errors:
            print(f"  - ERROR: {err}")
    else:
        print("[OK] Message passed all structural checks.")
        
    if warnings:
        print("\n[!] WARNINGS / SUGGESTIONS:")
        for warn in warnings:
            print(f"  - WARNING: {warn}")
            
    print("============================================================\n")
    
    if errors:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
