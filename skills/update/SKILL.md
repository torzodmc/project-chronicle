---
name: update
description: "Use when capturing conversation debates, epistemic diffs, feature modifications, philosophy evolution, and new failure traps into the active version dossier and master evolution."
---

# Chronicle: Update Version & Evolution (`/chronicle:update`)

Use this skill when recording session progress, conversational debates, architectural pivots, code modifications, or failure post-mortems into the Project Chronicle.

> [!CRITICAL]
> **STRICT WORKSPACE & CHAT BOUNDARY (ZERO EXTERNAL TRAVERSAL):**
> 1. The agent is **strictly forbidden** from scanning parent directories, sibling directories, or other project folders outside the current active workspace.
> 2. Chronicle updates must be sourced **strictly and exclusively** from:
>    - The current chat session's conversation history.
>    - The current active workspace (`cwd`) only.
> 3. Under no circumstances may an agent probe external directories to "discover" other projects or versions. State must be read strictly from the vault's `state.json`.

---

## Extraction Protocols (STRICTLY ENFORCED)

### 1. The Epistemic Diff (Banning Bland Summaries)
Never write generic bullet points like *"Discussed architecture and modified code."*
The agent **MUST** document:
- **Old Assumption:** What did the team or prior version assume before this milestone?
- **The Collision Event:** What specific bug, test failure, empirical benchmark, or user pushback shattered that assumption?
- **New Reality & Philosophy:** What is the new mental model, using the creator's exact words and metaphors?

### 2. The Clarification Checkpoint
If a major architectural pivot or philosophical shift occurred during the chat but the rationale was left ambiguous, **pause and ask the user a single focused clarifying question before saving**:
> *"We pivoted from X to Y mid-session—was that driven by test data or an intentional architectural preference?"*

### 3. Exhaustive Master Evolution Architecture (Forbidding Truncated Bullets)
The file `master_evolution.md` is the project's living manifesto and intellectual compass—unbounded by length. It must **never** be condensed into sterile bullet points. The agent must maintain and expand all 5 comprehensive chapters:

1. **Chapter 1: Foundational Intent & Origin Thesis**
   - *Core Problem & Origin Story:* Exhaustively explain the original problem that gave birth to the project, prior manual or prototype attempts, human emotional/operational frustrations, and the reason for inception.
   - *The Creator's Mission:* What success looks like, what catastrophic failure looks like, and why this system must exist.
   - *Human vs. Machine Boundaries:* Exactly what decisions are delegated to automation/AI versus what must remain human discretion.

2. **Chapter 2: Core System Philosophy, Metaphors & Living Invariants**
   - *Core Mental Models & Metaphors:* The vivid analogies and intuitive models used to conceptualize the system's mechanics.
   - *Non-Negotiable Living Axioms:* Permanent invariant laws that must hold true across every single version.
   - *Boundary Guarantees:* Causal data protections, safety boundaries, and operational integrity laws.

3. **Chapter 3: The Epistemic History of Beliefs (Mental Model Progression)**
   - Chronological, narrative record tracking how the creator's philosophy and understanding transformed over time.
   - For every version: document the Initial Belief $\to$ Real-World Encounter/Bug $\to$ Philosophical Adaptation.

4. **Chapter 4: Universal Feature Lifecycle Matrix & Full Specifications**
   - Exhaustive technical specifications for every component introduced from Day 1 onward.
   - Components must be tracked as `[ACTIVE]`, `[MODIFIED in VN]`, or `[RETIRED in VN]`.
   - **Never delete past components.** Every modification or retirement must include the verbatim rationale for why it was changed and what replaced it.

5. **Chapter 5: Comprehensive Version Progression Log**
   - Deterministic chronological milestone timeline of all completed, active, and skipped versions.

### 4. Trap Mechanism Protocol
If an idea, design pattern, or optimization failed or proved harmful, log it immediately into `graveyard_of_traps.md` answering:
- **Anti-Pattern / Trap:** Exact name and description of the failed approach.
- **What Made It Tempting:** Why did it sound good initially?
- **Hidden Failure Mechanism:** What exact bug, edge case, or secondary effect broke it?
- **Why Future AIs Will Re-Suggest It:** Why would an agent without context propose this trap again?
- **Permanent Invariant Counter-Rule:** Non-negotiable architectural invariant to prevent this trap forever.

---

## Procedure

1. **Verify Current Status:**
   Run the status helper to confirm the active project and version:
   ```bash
   python "C:/Users/johnp/.gemini/config/plugins/chronicle/scripts/chronicle_helper.py" status
   ```

2. **Clarify Ambiguities (if any):**
   If any strategic decision lacks a clear "why", ask the user for clarification before editing files.

3. **Update Active Version Dossier (`versions/v<N>.md`):**
   - Update Section 1: *Human Philosophy, Vision & Mental Models* (Epistemic Diff).
   - Update Section 2: *Conversational Debates & Decisions* (Key user quotes, debates).
   - Update Section 3: *Exhaustive Feature & Architecture Anatomy* (Technical specs).
   - Update Section 4: *What Changed vs. Previous Version & Why* (Modified/retired components).
   - Update Section 5: *Post-Mortems, Failure Modes & Traps Discovered*.
   - Update Section 6: *Verification, Testing & Empirical Results* (Commands run, test evidence).

4. **Update Cumulative Master Ledger (`master_evolution.md`):**
   - Expand and enrich all 5 chapters with complete narrative depth.
   - Update the Universal Feature Lifecycle Matrix with all `[ACTIVE]`, `[MODIFIED in VN]`, and `[RETIRED in VN]` entries.
   - Update Chapter 5 Progression Log with the latest milestone.

5. **Update Graveyard of Traps (`graveyard_of_traps.md`):**
   - Append any new failure mechanisms to the Trap Mechanism Table.

6. **Validate State & Dossiers:**
   ```bash
   python "C:/Users/johnp/.gemini/config/plugins/chronicle/scripts/chronicle_helper.py" validate
   ```

7. **Present Summary:**
   Provide a concise confirmation of changes made to the chronicle files for user review.
