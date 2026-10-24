---
name: chronicle-status
description: "Use when checking current Project Chronicle state, active project, active version status, total versions, and historical timeline across all versions."
---

# Chronicle: Status & Timeline (`/chronicle:status` / `/chronicle-status`)

Use this skill to view the active project chronicle, current tracked version, completion statuses, and overall version progression.

> [!CRITICAL]
> **STRICT WORKSPACE BOUNDARY (ZERO EXTERNAL TRAVERSAL):**
> - The agent is strictly forbidden from scanning parent directories, sibling directories, or other project folders outside the current active workspace.
> - Chronicle state must be read strictly from the vault's `state.json`.

## Procedure

1. **Execute Status Helper:**
   Locate `scripts/chronicle_helper.py` in the Chronicle installation directory and run:
   ```bash
   python "<path_to_chronicle>/scripts/chronicle_helper.py" status
   ```

2. **Display Chronicle Health & Timeline:**
   - If no project is currently active:
     Display: *"No active project in chronicle vault. Run `/chronicle:new [project_name]` to initialize a project."*
   - If an active project exists:
     Output formatted table with:
     - **Active Project:** Name of the tracked project
     - **Vault Path:** Resolved vault directory
     - **Active Version:** Version number and status (`in_progress` or `completed`)
     - **Timeline Table:** All recorded versions, statuses, and dates (including skipped milestones).
