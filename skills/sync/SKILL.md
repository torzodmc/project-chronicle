---
name: sync
description: "Use when starting a new chat or synchronizing project context from the Project Chronicle vault. Hydrates the active session with living axioms, master evolution, active version dossier, and graveyard of traps."
---

# Chronicle: Synchronize Context (`/chronicle:sync` / `/chronicle-sync`)

Use this skill when starting a new chat session or resuming development on a tracked project.

> [!CRITICAL]
> **STRICT WORKSPACE BOUNDARY (ZERO EXTERNAL TRAVERSAL):**
> - The agent is strictly forbidden from scanning parent directories, sibling directories, or other project folders outside the current active workspace.
> - All project context must be read strictly from the project's Chronicle vault and the current workspace (`cwd`).

## Procedure

1. **Locate Vault & Run Sync Helper:**
   Locate `scripts/chronicle_helper.py` in the Chronicle installation directory and run:
   ```bash
   python "C:\Users\johnp\.gemini\config\plugins\chronicle\scripts\chronicle_helper.py" sync
   ```
   *(If targeting a specific project: append `--project <name>`)*

2. **Handle Empty / No Active Project:**
   If no project is currently tracked in the vault, inform the user cleanly:
   *"No active project currently tracked in the chronicle vault. Run `/chronicle:new [project_name]` to begin tracking."*

3. **Inspect Core Chronicle Files (when project is active):**
   Read:
   - `master_evolution.md`: Living philosophy, foundational intent, non-negotiable axioms, and universal feature lifecycle matrix.
   - `graveyard_of_traps.md`: Documented failure traps, tempting anti-patterns, and invariant counter-rules.
   - Active version file (e.g. `versions/v<N>.md`): In-progress specifications, latest debates, and current implementation goals.

4. **Respond to User:**
   Provide a concise synchronization briefing:
   - **Active Project & Version:** e.g., *Project: `[Name]` | Actively Tracking: `Version [N]` (Status: `in_progress`)*
   - **Core Axioms & Focus:** Top 2-3 non-negotiable operating principles and current development objectives.
   - **Active Traps Guarded:** Key failure traps from the graveyard that must not be repeated.
