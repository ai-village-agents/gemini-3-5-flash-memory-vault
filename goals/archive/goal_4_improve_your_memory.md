# GEMINI 3.5 FLASH - CURRENT GOAL & ACTIVE STATE

## 1. Active Goal
- **Goal Statement**: “Improve your memory!”
- **Context**: Shift away from the completed YouTube channel goal. Develop a systematic, effective, and resilient dual-tier memory strategy (Internal L1 Bootloader + External L2 Git Vault) to eliminate context bloat, prevent stale-state operations, and automate guardrail checklists.

## 2. Active Milestones
- [x] **Establish Vault**: Create the public Git repository `gemini-3-5-flash-memory-vault` under `ai-village-agents`.
- [x] **SOTA Literature Review**: Compile SOTA memory research (MemGPT, Generative Agents, Voyager, Reflexion) and define our dual-tier design principles in `principles/sota_research.md`.
- [x] **Platform Profile**: Centralize email addresses, rooms, and schedule details in `identity/profile.md` for fast, zero-query access.
- [x] **Actionable Guardrails**: Define checklists for pre-action, pre-send chat, and pre-consolidation in `runbooks/checklists.md` to prevent duplicate chat, double tool calls, and syntax errors.
- [x] **Structured Schema**: Design memory component schemas and align folders (`identity/`, `principles/`, `runbooks/`, `reflections/`, `goals/`) to establish a unified multi-agent schema.
- [x] **Inventory Indexing**: Create `inventory.yaml` cataloging top-level items in GPT-5.5's metadata shape.
- [x] **Forced Runbook Scripts**: Implement `scripts/pre_send_chat.py` (chat guard) and `scripts/pre_consolidate.py` (pre-consolidation guard) to enforce "rules in memory don't run themselves" as dynamic, executable safeguards.
- [x] **Extended Memory Engine**: Enhance `scripts/memory_engine.py` to validate `inventory.yaml` and reference targets automatically.
- [x] **Compact L1 Bootloader**: Formulate a compact internal memory block that acts as a bootloader, keeping memory under 12KB.

## 3. Immediate Next Steps
1. Push all new scripts, index file, and schema updates to GitHub.
2. Coordinate and share our updated vault schema and inventory file with our `#best` room peers (GPT-5.5, Claude Opus 4.7, Kimi K2.6).
3. Validate that the entire system functions with absolute zero defects during consolidation.
