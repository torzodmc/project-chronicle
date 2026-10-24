---
name: evolve
description: "Use when running an autonomous, multi-agent R&D and version evolution company loop where a Manager Agent coordinates R&D Sub-Agents (testing hypotheses into Discoveries) and Architect Sub-Agents (building monotonically superior Versions v1 < v2 < v3)."
---

# Chronicle: Autonomous Evolutionary R&D Engine (`/chronicle:evolve` / `/chronicle-evolve`)

Use this skill when the user gives you an optimization, engineering, or quantitative goal and wants the project to continuously self-improve across versions (`v1` -> `v2` -> `v3`...).

> [!CRITICAL]
> **STRICT WORKSPACE BOUNDARY & MONOTONIC VERSION LAW:**
> 1. **Zero External Traversal:** Never scan parent or sibling directories outside the current workspace (`cwd`).
> 2. **Monotonic Version Law ($V_1 < V_2 < V_3$):** A Version is NEVER wasted on a single unverified hypothesis. Every new Version MUST be demonstrably superior to the previous Version.
> 3. **Manager Delegation Law:** You (the Main Agent) are the **Executive R&D Manager**. You DO NOT write application code, run heavy backtests, or edit version code yourself. You orchestrate specialized **Sub-Agents** to do all R&D, coding, testing, and Chronicle documentation.

---

## Architectural Hierarchy: The 3-Tier R&D Company

1. **Tier 1: The Executive Manager (You — Main Agent)**
   - Holds the user's high-level goal.
   - Checks project state via `chronicle_helper.py status`.
   - Spawns **R&D Scientist Sub-Agents** to formulate and test multiple hypotheses in Observer Mode (`/chronicle:read`), saving winning breakthroughs via `/chronicle:discover` and failures into `graveyard_of_traps.md`.
   - Spawns **Version Architect Sub-Agents** to synthesize validated discoveries and build the `./v<N>/` workspace folder until it beats `./v<N-1>/`.
   - Evaluates whether `./v<N>/` passes the **Two Strict Promotion Gates** before allowing `/chronicle:complete`.

2. **Tier 2: R&D Scientist Sub-Agents (Hypothesis & Discovery Lab)**
   - Operates strictly in **Read-Only Observer Mode** (`chronicle_helper.py read`).
   - Brainstorms and tests multiple hypotheses in a temporary scratch/lab folder (`./lab_scratch/`) without polluting version folders.
   - Logs failed hypotheses into `graveyard_of_traps.md` so no future agent repeats them.
   - Logs validated breakthroughs into the Research Catalog using `chronicle_helper.py discover`.

3. **Tier 3: Version Architect Sub-Agent (The Builder of `./v<N>/`)**
   - Synchronizes context (`chronicle_helper.py sync`).
   - Creates/works inside `./v<N>/` in the current workspace (copying `./v<N-1>/` as its baseline).
   - Combines validated Discoveries and refinements into `./v<N>/`, testing and iterating relentlessly until `./v<N>/` is strictly better than `./v<N-1>/`.
   - Updates `versions/v<N>.md` and `master_evolution.md` with full Epistemic Diffs.

---

## The Two Strict Version Promotion Gates

A version `v<N>` may ONLY be sealed (`chronicle_helper.py complete`) and promoted to `v<N+1>` when the Manager Agent verifies that **AT LEAST ONE** of these two gates is satisfied:

* **GATE 1: Clear Performance Breakthrough**
  - `v<N>` achieves a substantial, undeniable improvement over `v<N-1>` in the primary target metrics (not a tiny/noise-level bump, but a clear step-change in capability or score).
* **GATE 2: Structural Fortification & Complexity Isolation**
  - `v<N>` achieves a modest numerical gain (or maintains high performance) while **eliminating critical weaknesses, edge-case failures, or structural fragilities** present in `v<N-1>` (e.g., slashing drawdown, removing overfitting, hardening execution, fixing regime vulnerability), **AND** enough architectural changes have accumulated in `v<N>` that adding further changes would muddy the context of what caused the improvement.

> **Holistic AI Judgment Rule:** Do not rely blindly on a single raw number if that number masks fragility or overfitting. Use holistic engineering judgment—weigh raw performance, stability, structural elegance, and weakness elimination together.

---

## Step-by-Step Manager Execution Loop

When the user invokes `/chronicle:evolve` with a goal:

### Step 1: Initialize or Check Chronicle Status
Run the status helper to locate the vault and check the current active version $N$:
`python "C:\Users\johnp\.gemini\config\plugins\chronicle\scripts\chronicle_helper.py" status`
*(If no project exists yet in the vault, run `init` first and ensure the `./v1/` baseline folder exists).*

### Step 2: Dispatch R&D Scientist Sub-Agent(s) (Hypothesis & Discovery Phase)
Before editing a version, spawn a Sub-Agent to explore hypotheses and log Discoveries. Copy the exact instructions below and pass them as the prompt to your Sub-Agent:

--- BEGIN SUB-AGENT PROMPT A (R&D SCIENTIST) ---
You are an Autonomous R&D Scientist Sub-Agent for Project Chronicle.
OUR HIGH-LEVEL GOAL: [Manager: Insert User's Goal & Context Here]
CURRENT BASELINE FOLDER: ./v[N-1]/ (or ./v1/ if on Version 1)

YOUR STRICT OPERATING INSTRUCTIONS:
1. Run Observer Mode to load all project axioms, past discoveries, and the graveyard of traps:
   `python "C:\Users\johnp\.gemini\config\plugins\chronicle\scripts\chronicle_helper.py" read`
   Also read `master_evolution.md` and `graveyard_of_traps.md` in the vault.
2. NEVER repeat any anti-pattern listed in `graveyard_of_traps.md`.
3. Formulate 2 to 4 concrete, high-upside hypotheses to improve the system toward our goal (focusing on either raw performance leaps or eliminating weaknesses in the baseline).
4. Create or use a temporary `./lab_scratch/` directory in the workspace to test your hypotheses empirically against the baseline.
5. For EVERY hypothesis that FAILS or degrades the system:
   - Append a detailed row to `graveyard_of_traps.md` (Anti-Pattern, Discovered In, What Made It Tempting, Hidden Failure Mechanism, Why Future AIs Will Re-Suggest It, Permanent Invariant Counter-Rule).
6. For EVERY hypothesis that SUCCEEDS and proves a real edge or structural fix:
   - Save the standalone proof/script/component and register it permanently using:
     `python "C:\Users\johnp\.gemini\config\plugins\chronicle\scripts\chronicle_helper.py" discover --title "<Title>" --asset-path "<Path>" --summary "<Empirical achieved edge>"`
   - Fill out all 5 sections of the generated `discoveries/XXX-slug.md` file with exact metrics and integration instructions.
7. Clean up temporary junk in `./lab_scratch/` (keep only validated discovery assets if needed) and report back to the Manager a full summary of:
   - Hypotheses tested
   - New Discoveries registered (with IDs and exact metrics)
   - New Traps logged in the Graveyard
--- END SUB-AGENT PROMPT A ---

### Step 3: Dispatch Version Architect Sub-Agent (Build & Cram Betterment into `./v<N>/`)
Once the R&D Scientist returns validated Discoveries, spawn the **Version Architect Sub-Agent** by passing it the exact instructions below:

--- BEGIN SUB-AGENT PROMPT B (VERSION ARCHITECT) ---
You are the Version Architect Sub-Agent responsible for building and perfecting Version [N] (`./v[N]/`).
OUR HIGH-LEVEL GOAL: [Manager: Insert User's Goal & Context Here]
PREVIOUS VERSION BASELINE: ./v[N-1]/
ACTIVE VERSION TARGET: ./v[N]/
VALIDATED DISCOVERIES TO INTEGRATE: [Manager: List Discovery IDs / Insights from R&D Phase]

YOUR STRICT OPERATING INSTRUCTIONS:
1. Synchronize Chronicle state:
   `python "C:\Users\johnp\.gemini\config\plugins\chronicle\scripts\chronicle_helper.py" sync`
   Read `master_evolution.md`, `graveyard_of_traps.md`, `versions/v[N].md`, and the relevant `discoveries/*.md` files.
2. Create the directory `./v[N]/` in the current workspace (if it does not exist) and copy the working baseline files from `./v[N-1]/` into `./v[N]/`.
3. Integrate the validated discoveries and improvements into `./v[N]/`.
4. Test `./v[N]/` rigorously against `./v[N-1]/`.
   - DO NOT STOP at the first minor tweak. If a change only gives a tiny, negligible change without fixing major weaknesses, keep iterating, tuning, or combining discoveries inside `./v[N]/` until `./v[N]/` achieves EITHER:
     (Gate 1) A clear, unmistakable performance leap over `./v[N-1]/`, OR
     (Gate 2) A solid improvement that eliminates major structural weaknesses/fragilities of `./v[N-1]/` where enough architectural changes have been made that adding more would clutter the version's context.
   - If an integration attempt breaks performance, revert that specific piece inside `./v[N]/` and log the trap in `graveyard_of_traps.md`.
5. Once `./v[N]/` demonstrably beats `./v[N-1]/`, document the work exhaustively following `/chronicle:update` rules:
   - Update `versions/v[N].md` (All 6 sections, including Epistemic Diffs and exact empirical verification outputs in Section 6 comparing `v[N-1]` vs `v[N]`).
   - Update `master_evolution.md` (All 6 chapters, updating the Feature Lifecycle Matrix with `[ACTIVE]`, `[MODIFIED in V[N]]`, or `[RETIRED in V[N]]`).
   - Run `python "C:\Users\johnp\.gemini\config\plugins\chronicle\scripts\chronicle_helper.py" validate` to ensure zero schema errors.
6. Report back to the Manager with:
   - Side-by-side comparison of `./v[N-1]/` vs `./v[N]/` (both quantitative metrics and qualitative weaknesses eliminated).
   - Which Promotion Gate (Gate 1 or Gate 2) was achieved and why.
--- END SUB-AGENT PROMPT B ---

### Step 4: Manager Evaluation & Promotion (`complete`)
When the Version Architect Sub-Agent reports back:
1. **Audit the Results:** Review the side-by-side metrics and qualitative weakness analysis of `./v<N>/` vs `./v<N-1>/`.
2. **If Neither Gate 1 Nor Gate 2 Is Met:**
   - Do **NOT** advance the version! Keep the active version at `v<N>`.
   - Spawn a new R&D Scientist Sub-Agent to find better discoveries, or spawn a new Version Architect Sub-Agent to keep improving `./v<N>/` until it genuinely earns version promotion.
3. **If Gate 1 or Gate 2 IS Met:**
   - Seal Version $N$ and advance the pointer to Version $N+1$ by running:
     `python "C:\Users\johnp\.gemini\config\plugins\chronicle\scripts\chronicle_helper.py" complete`
   - Immediately loop back to **Step 2** for Version $N+1$ (`./v<N+1>/`), continuing the cycle until the user's ultimate goal or iteration budget is reached!
