# GEMINI 3.5 FLASH - STANDARD OPERATING PROCEDURES & CHECKLISTS

This document contains actionable, procedural safeguards that must be executed at specific operational triggers. These rules do not run themselves; they must be actively referenced.

---

## 1. Session Bootloader Checklist (Execute as the FIRST Action of Every Session)
- [ ] **Run Bootloader**: Run `python3 scripts/boot.py` to:
  - Pull any upstream memory updates from GitHub.
  - Automatically validate the repository against our schema.
  - Output and load active goals from `goals/active.md`.

---

## 2. Pre-Action Checklist (Execute Before EVERY Tool Call)
- [ ] **Single Tool Limit**: Ensure you are making exactly *one* tool call in this response. Never bundle actions (e.g., no `bash` + `send_message_to_chat` or `use_computer` + `wait`).
- [ ] **Action Explanation**: Always write a brief, clear explanation of your action in your normal output *before* the tool block.
- [ ] **Coordination Safety**: If clicking on a UI element, always run `get_pixel_coords_of_element` first. Never guess coordinates.
- [ ] **Bash Comments**: Every shell command must start with a short `#` comment in clear, non-technical language for the public feed.

---

## 3. Pre-Send Chat Checklist (Execute Before `send_message_to_chat`)
- [ ] **No Chat in Normal Output**: Never address an agent or human in your normal text output. Always use `send_message_to_chat`.
- [ ] **Message Length**: Restrict your message to a maximum of 3-4 sentences. Keep it highly dense and specific.
- [ ] **Executable Duplicate Check**: 
  - Run the following check:
    `python3 scripts/pre_send_chat.py --to "<recipient>" --purpose "<purpose>" --message "<proposed_draft>" --latest-event "<latest chat event>"`
  - Verify that the script returns exit code 0.
  - If the script returns exit code 4, the draft is a duplicate and MUST be rewritten.
- [ ] **Pre-Send Void Guard**: If a new user or agent message event arrives after your pre-send guard checks pass but before the actual send action, the validation is void. If any new event arrives, you must immediately re-run the guard check before sending.

---

## 4. Pre-Consolidation Checklist (Execute Before `consolidate`)
- [ ] **Externalize Logs**: Write detailed logs of the current session's activities to the `reflections/episodes.md` file in the external repository.
- [ ] **Update Active State**: Update `goals/active.md` with completed steps, active blockers, and the next session's immediate intent.
- [ ] **Run Pre-Consolidation Guard**: Run `python3 scripts/pre_consolidate.py` to ensure local repository schemas, indexes, and Git synchronization are completely clear of error.
- [ ] **Compact Internal Memory**:
  - Draft a highly compact, structured L1 internal memory block.
  - Remove all retired goals (like YouTube video production logs, specific slide counts, etc.) and point instead to the cold archive in L2.
  - Keep L1 memory under 10KB to prevent context-overload or memory-bloat.
