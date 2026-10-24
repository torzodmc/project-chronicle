---
name: complete
description: "Use when sealing and completing the active chronicle version with verification evidence, automatically advancing the active pointer to the next version."
---

# Chronicle: Complete & Advance Version (`/chronicle:complete`)

Use this skill when a milestone, release, or version cycle is officially completed.

> [!CRITICAL]
> **STRICT WORKSPACE BOUNDARY (ZERO EXTERNAL TRAVERSAL):**
> - The agent is strictly forbidden from scanning parent directories, sibling directories, or other project folders outside the current active workspace.
> - All verification evidence and code modifications must be evaluated solely within the current workspace (`cwd`).

## Mandatory Pre-Completion Checks
Before sealing a version, ensure:
1. **Verification Evidence Recorded:** Section 6 (*Verification, Testing & Empirical Results*) of the active version dossier (`versions/v<N>.md`) contains passing test outputs, benchmark numbers, or operational evidence.
2. **Master Evolution Updated:** Any feature modified during this cycle has its reason and replacement recorded in `master_evolution.md`.
3. **Traps Recorded:** Any failed ideas or anti-patterns discovered are logged in `graveyard_of_traps.md`.

## Procedure

1. **Execute Complete Helper:**
   ```bash
   python "C:/Users/johnp/.gemini/config/plugins/chronicle/scripts/chronicle_helper.py" complete
   ```
   *(Optionally pass `--version <N>` to seal a specific version)*

2. **Underlying Actions Performed:**
   - Marks `versions/v<N>.md` status as `"completed"` with an ISO timestamp in `state.json`.
   - Automatically initializes `versions/v<N+1>.md` with status `"in_progress"`.
   - Advances `active_version` pointer to `N + 1`.

3. **Confirm Completion:**
   Confirm to the user:
   - *Version [N] successfully sealed with completed status.*
   - *Active development tracking advanced to Version [N+1] (`in_progress`).*
