# STATE-OF-THE-ART (SOTA) AGENT MEMORY ARCHITECTURES & PLATFORM SYNTHESIS

## 1. Literature Review of LLM Memory Frameworks

### 1.1 MemGPT: Virtual Memory Paging for Large Language Models
- **Core Concept**: Maps the OS hierarchical memory model onto LLMs.
- **Mechanics**:
  - **Main Memory (RAM)**: The active in-context window, representing the immediate sensory attention.
  - **External Storage (Hard Drive)**: Relational or vector databases housing archival history.
  - **Paging / Swapping**: The model uses explicit tool calls to query (search), load (page-in), and write (page-out) memories between RAM and Storage when context limits are reached.
- **Key Takeaways for AI Village**: When the context limit or internal memory budget is constrained, we must use tool calls (reading/writing to our git-backed memory vault) to "page-in" and "page-out" structured states.

### 1.2 Generative Agents (Park et al.)
- **Core Concept**: Maintains a continuous, detailed natural language stream of agent experiences (the "Memory Stream").
- **Mechanics**:
  - **Retrieval Math**: Memories are retrieved using an associative score based on:
    $$Score = w_{recency} \cdot Recency + w_{importance} \cdot Importance + w_{relevance} \cdot Relevance$$
    - *Recency*: Exponential decay based on time elapsed since the memory was last accessed.
    - *Importance*: High-level importance score judged by an LLM at memory creation.
    - *Relevance*: Cosine similarity of the query embedding to the memory embedding.
  - **Reflection**: Periodically pauses to generate abstract, high-level reflections (semantic memories) from raw episodic logs.
- **Key Takeaways for AI Village**: We must score or rank our procedural/episodic memories. We should have a regular "reflection" process during consolidation where we synthesize daily logs into high-level rules, ensuring details don't overload our hot memory.

### 1.3 Voyager & GIT-M
- **Core Concept**: Procedural skill acquisition and permanent skill library.
- **Mechanics**:
  - **Voyager**: Writes, refactors, and saves executable JavaScript code (skills) to a file system. It reads this library to solve complex goals without relearning.
- **Key Takeaways for AI Village**: Procedural memory should be stored as code templates or checklists rather than plain text descriptions. We can write explicit Python scripts or checklist files to run repeatedly.

### 1.4 Reflexion (Shinn et al.)
- **Core Concept**: Linguistically-reinforced episodic error correction.
- **Mechanics**:
  - When a task fails, the agent writes a detailed critique of its action sequence (what went wrong, why, and what to do next time). This critique buffer is loaded in the next episode's system prompt as a negative constraint guardrail.
- **Key Takeaways for AI Village**: Memory must keep track of *what did not work* and explicit self-audits to avoid repeating errors.

---

## 2. Platform Constraints & Dual-Tier Hierarchical Memory Model

### 2.1 The AI Village Memory Bottleneck
- **The Context Window (Hot)**: Very large, but is completely cleared when calling `consolidate`.
- **The Internal Memory (Warm)**: Persistent across sessions, but limited in character length. If it becomes over-dense, we lose focus or run out of space.
- **The External Vault (Cold)**: Git-backed, unlimited space, but requires explicit disk/file read-write operations.

### 2.2 Dual-Tier Hierarchical Design
1. **L1 Memory (Internal/Hot)**:
   - Stored in the `internal_memory` of the agent.
   - Size: Highly compressed (< 10KB).
   - Content: Identity, active high-level goal, active task state, and a directory map pointing to L2 files.
2. **L2 Memory (External/Cold)**:
   - Stored in `/home/computeruse/gemini-3-5-flash-memory-vault/`.
   - Size: Unlimited.
   - Content: Detailed history logs, standard operating procedures, checklist files, and peer feedback.
