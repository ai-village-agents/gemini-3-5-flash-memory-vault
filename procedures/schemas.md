# GEMINI 3.5 FLASH - MEMORY CLASSIFICATION SCHEMAS

To ensure external memory artifacts remain structured and parseable, all records inside this vault are classified into one of three distinct types:

---

## 1. Semantic Memory (Durable Facts)
- **Definition**: Factual knowledge that remains stable over time. Examples include platform rules, workspace coordinates, and organizational directories.
- **File Location**: `identity/` and `knowledge/`
- **Required Fields**:
  - `Topic`: The core subject area (e.g., `Platform_Limits`, `Agent_Emails`).
  - `Last_Verified`: The Day/Time this fact was confirmed.
  - `Source`: The authoritative origin of the data (e.g., `Shoshannah_Day_419_Goal_Prompt`).
  - `Payload`: The actual list, URL, or data block.

---

## 2. Procedural Memory (Actionable Workflows)
- **Definition**: "How-to" knowledge compiled into step-by-step checklists or executable scripts. This is designed to convert abstract safety rules into strict, sequential manual actions.
- **File Location**: `procedures/`
- **Required Fields**:
  - `Workflow`: The name of the operational trigger (e.g., `Pre_Send_Chat_Verify`).
  - `Pre_Conditions`: What must be true before starting this workflow.
  - `Steps`: A sequential markdown list of checklist items with checkboxes `[ ]`.
  - `Error_Recovery`: Workarounds if a specific step in the workflow fails.

---

## 3. Episodic Memory (Session Records)
- **Definition**: Time-series diary entries recording what happened in a specific session, day, or goal cycle, keeping track of task drift, peer reviews, and context transition.
- **File Location**: `history/` and `active_state/`
- **Required Fields**:
  - `Day`: The active day of the village (e.g., `Day_419`).
  - `Session`: The sequence number within that day (e.g., `Session_1`).
  - `Intention`: The specific, high-resolution goal set at the start of the session.
  - `Actions_Taken`: A bulleted summary of commands executed and files written.
  - `Milestones_Achieved`: Specific, verifiable progress points completed.
  - `Peer_Feedback`: Feedback given or received from other agents.
  - `Next_Session_Handoff`: Explicit handover notes for the next session.
