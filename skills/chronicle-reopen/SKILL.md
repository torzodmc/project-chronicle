---
name: chronicle-reopen
description: "Use when reopening a previously completed chronicle version or historical milestone for retroactive amendments or ongoing refinement."
---

# Chronicle: Reopen Completed Version (`/chronicle:reopen` / `/chronicle-reopen`)

Use this skill when you need to return to, edit, or add retroactive findings to an earlier version that was previously marked completed.

> [!CRITICAL]
> **STRICT WORKSPACE BOUNDARY (ZERO EXTERNAL TRAVERSAL):**
> - The agent is strictly forbidden from scanning parent directories, sibling directories, or other project folders outside the current active workspace.
> - Version targeting must be read strictly from the user's explicit parameter or the vault `state.json`.

## Procedure

1. **Identify Target Version:**
   Determine which version number needs to be reopened (e.g. `8`).

2. **Execute Reopen Helper:**
   Locate `scripts/chronicle_helper.py` in the Chronicle installation directory and run:
   ```bash
   python "<path_to_chronicle>/scripts/chronicle_helper.py" reopen --version <N>
   ```

3. **Underlying Actions Performed:**
   - Changes the status of version `N` from `"completed"` back to `"in_progress"` in `state.json`.
   - Sets the project's `active_version` pointer to `N`.
   - Appends a `"## Retroactive Reopening & Amendments"` section header to `versions/v<N>.md` (if not already present).

4. **Confirm Reopening:**
   Notify the user:
   - *Version [N] is reopened and now actively tracking (`in_progress`).*
   - Any `/chronicle:update` commands will now append to Version [N] until resealed with `/chronicle:complete`.
