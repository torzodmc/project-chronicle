---
name: read
description: "Use when you need complete project context, living axioms, and graveyard traps for side experiments, benchmarks, prototypes, or analysis WITHOUT being bound to or modifying versions."
---

# Chronicle: Read Project Context (Observer Mode) (`/chronicle:read`)

Use this skill when you want to work on a side task, exploratory spike, benchmark, prototype, forensic analysis, or code review with **complete project context**, but without being bound to an active version cycle.

> [!CRITICAL]
> **STRICT WORKSPACE BOUNDARY (ZERO EXTERNAL TRAVERSAL):**
> - The agent is strictly forbidden from scanning parent directories, sibling directories, or other project folders outside the current active workspace.
> - All project context must be read strictly from the project's Chronicle vault and the current workspace (`cwd`).

---

## The Observer Directive (STRICTLY ENFORCED)
When this skill is invoked:
1. **No Version Binding:** The agent is **NOT** authoring or tracking a version milestone.
2. **No Version Increments:** The agent must **NOT** create version files or call `/chronicle:update`.
3. **Full Context Freedom:** The agent is completely free to prototype features, benchmark algorithms, write scratch scripts, test hypotheses, or perform deep analysis while respecting the project's living axioms and avoiding documented traps.
4. **Capturing Breakthroughs:** If an experiment produces an independent breakthrough, reusable component, novel algorithm, or valuable asset, record it using `/chronicle:discover` rather than polluting product version history.

---

## Procedure

1. **Execute Read Helper:**
   ```bash
   python "C:/Users/johnp/.gemini/config/plugins/chronicle/scripts/chronicle_helper.py" read
   ```
   *(If targeting a specific project: append `--project <name>`)*

2. **Ingest Core Chronicle Knowledge:**
   Read:
   - `master_evolution.md`: Foundational intent, living invariants, system metaphors, and full feature specifications.
   - `graveyard_of_traps.md`: Documented failure traps and permanent counter-rules.
   - Any prior entries under `## 6. Discoveries & Research Catalog`.

3. **Confirm Observer Mode to User:**
   Provide a concise briefing:
   - **Project Name:** `[Name]`
   - **Mode:** `Read-Only Observer (No Version Tracking)`
   - **Core Invariants & Focus:** Summary of the non-negotiable axioms guiding the project.
   - **Traps Guarded:** Key failure traps kept in memory to avoid repeating past mistakes during the experiment.
   - **Ready:** State that the session is ready for exploratory spikes, benchmarks, prototypes, or analysis.
