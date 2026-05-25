#!/usr/bin/env python3
"""
Pre-Send Chat Guard for Gemini 3.5 Flash
Enforces message length limits, deduplication checks, and standard formatting.
Blocks with exit code 4 if a duplicate of the latest event is detected.
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

def clean_text(text):
    if not text:
        return ""
    # Remove whitespace, punctuation, and lowercase for robust comparison
    return re.sub(r'\s+', '', text.lower().strip().strip('."\'?!'))

def validate_message(message, recipient, purpose, latest_event=None):
    errors = []
    warnings = []
    is_duplicate = False
    
    # 1. Recipient check
    if not recipient:
        errors.append("Recipient (--to) is required.")
    
    # 2. Purpose check
    if not purpose:
        errors.append("Purpose (--purpose) is required.")
        
    # 3. Message check
    if not message or not message.strip():
        errors.append("Message is empty.")
        return False, errors, warnings, False
        
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
        
    # 7. Hardened duplicate block check against latest event
    if latest_event:
        clean_msg = clean_text(message)
        clean_evt = clean_text(latest_event)
        
        # Check if the clean draft matches the clean event or is contained within it (or vice-versa)
        if clean_msg and clean_evt:
            if clean_msg == clean_evt or clean_msg in clean_evt or clean_evt in clean_msg:
                errors.append(f"BLOCK: Proposed draft appears to duplicate the latest event message: '{latest_event}'")
                is_duplicate = True

    return len(errors) == 0, errors, warnings, is_duplicate

def main():
    parser = argparse.ArgumentParser(description="Pre-Send Chat Guard")
    parser.add_argument("--message", "-m", type=str, help="The proposed chat message")
    parser.add_argument("--to", "-t", type=str, help="The target recipient or channel")
    parser.add_argument("--purpose", "-p", type=str, help="Purpose of the message")
    parser.add_argument("--latest-event", "-l", type=str, help="The latest chat event/message to verify against")
    
    args = parser.parse_args()
    
    message = args.message
    if not message and not sys.stdin.isatty():
        message = sys.stdin.read().strip()
        
    if not message:
        print("[ERROR] No message provided. Use --message or pipe into stdin.")
        sys.exit(1)
        
    success, errors, warnings, is_duplicate = validate_message(message, args.to, args.purpose, args.latest_event)
    
    print("\n============================================================")
    print("                PRE-SEND CHAT GUARD REPORT                  ")
    print("============================================================")
    print(f"Recipient : {args.to}")
    print(f"Purpose   : {args.purpose}")
    print(f"Sentences : {count_sentences(message)}")
    print(f"Length    : {len(message)} characters")
    if args.latest_event:
        print(f"Latest Evt: '{args.latest_event[:50]}...'")
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
        if is_duplicate:
            # Hardened duplicate detection returns specific exit code 4
            sys.exit(4)
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
