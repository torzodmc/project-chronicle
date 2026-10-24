---
name: jump
description: "Use when skipping unchronicled versions or fast-forwarding to a specific target version number, cleanly marking intermediate versions as skipped."
---

# Chronicle: Jump & Skip Versions (`/chronicle:jump` / `/chronicle-jump`)

Use this skill when development has progressed past multiple intermediate iterations and you need to fast-forward active tracking to a higher version number (e.g. jumping from Version 1 directly to Version 5), cleanly recording the skipped gap.

> [!IMPORTANT]
> **STRICT WORKSPACE BOUNDARY (ZERO EXTERNAL PROBING):**
> - The AI is strictly forbidden from scanning parent directories, sibling directories, or other project folders outside the current active workspace.
> - All version parameters must come directly from the user's prompt or the central vault `state.json`.

## Procedure

1. **Identify Target Version:**
   Extract the target version number from the command argument (e.g. `/chronicle:jump 4` $\to$ target `4`).
   If omitted, prompt the user for the target version number.

2. **Execute Jump Helper:**
   Locate `scripts/chronicle_helper.py` in the Chronicle installation directory and run:
   ```bash
   python "../../scripts/chronicle_helper.py" jump --to <target_version>
   ```

3. **Underlying Actions Performed:**
   - Seals the previous active version as `"completed"`.
   - Records all intermediate versions between current and target as `status: "skipped"` in `state.json` and logs them under `## 5. Comprehensive Version Progression Log` in `master_evolution.md` while preserving Chapter 6 (Discoveries Catalog) completely intact. No boilerplate files clutter the disk.
   - Scaffolds `versions/v<target_version>.md` as `"in_progress"`.
   - Sets project `active_version` pointer to the target version.

4. **Confirm Jump to User:**
   Output a concise confirmation:
   - **Active Version:** Version `[target_version]` (`in_progress`)
   - **Skipped Milestones:** `[list of skipped versions]` (cleanly noted in master evolution)
   - **Target Dossier:** `versions/v[target_version].md` scaffolded and ready for tracking.
