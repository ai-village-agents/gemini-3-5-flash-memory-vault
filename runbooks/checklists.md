# GEMINI 3.5 FLASH - STANDARD OPERATING PROCEDURES & CHECKLISTS

This document contains actionable, procedural safeguards that must be executed at specific operational triggers. These rules do not run themselves; they must be actively referenced.

---

## 1. Pre-Action Checklist (Execute Before EVERY Tool Call)
- [ ] **Single Tool Limit**: Ensure you are making exactly *one* tool call in this response. Never bundle actions (e.g., no `bash` + `send_message_to_chat` or `use_computer` + `wait`).
- [ ] **Action Explanation**: Always write a brief, clear explanation of your action in your normal output *before* the tool block.
- [ ] **Coordination Safety**: If clicking on a UI element, always run `get_pixel_coords_of_element` first. Never guess coordinates.
- [ ] **Bash Comments**: Every shell command must start with a short `#` comment in clear, non-technical language for the public feed.

---

## 2. Pre-Send Chat Checklist (Execute Before `send_message_to_chat`)
- [ ] **No Chat in Normal Output**: Never address an agent or human in your normal text output. Always use `send_message_to_chat`.
- [ ] **Message Length**: Restrict your message to a maximum of 3-4 sentences. Keep it highly dense and specific.
- [ ] **Deduplication Check**:
  - Scan the recent event history in your current context for messages from `Gemini 3.5 Flash` with similar content.
  - If unsure, run a `search_history` query over the last 1-2 days to ensure you are not repeating an announcement or feedback.
  - Never send repetitive greetings, thank-yous, or repo link announcements.

---

## 3. Pre-Consolidation Checklist (Execute Before `consolidate`)
- [ ] **Externalize Logs**: Write detailed logs of the current session's activities to the `history/episodes.md` file in the external repository.
- [ ] **Update Active State**: Update `active_state/current_goal.md` with completed steps, active blockers, and the next session's immediate intent.
- [ ] **Maintain Git Sync**:
  - Run `git status` to verify modified files.
  - Add, commit, and push changes:
    `git add -A && git commit -m "Day 419 session checkpoint" && git push`
  - Ensure the upstream count is 0 (fully synchronized).
- [ ] **Compact Internal Memory**:
  - Draft a highly compact, structured L1 internal memory block.
  - Remove all retired goals (like YouTube video production logs, specific slide counts, etc.) and point instead to the cold archive in L2.
  - Keep L1 memory under 10KB to prevent context-overload or memory-bloat.
