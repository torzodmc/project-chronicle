---
name: new
description: "Use when initializing a brand-new project chronicle division or starting a new tracked project."
---

# Chronicle: Initialize New Project (`/chronicle:new`)

Use this skill to initialize a new project chronicle division in the vault.

> [!IMPORTANT]
> **Zero Prior Checks & Strict Workspace Isolation:**
> 1. Do NOT inspect past projects, do NOT check previous active projects, and do NOT fail or complain if older project folders do not exist. When `/chronicle:new` is invoked, execute initialization immediately.
> 2. The agent is strictly forbidden from scanning parent directories, sibling directories, or other project folders outside the current active workspace. Derive the project name solely from the user's explicit argument or the current workspace directory name.

## Procedure

1. **Determine Project Name:**
   - If the user specified a project name in their request (e.g., `/chronicle:new my-app`), use that name.
   - If no project name was specified, default to the current workspace directory name automatically.

2. **Execute Init Helper:**
   Run the initialization helper:
   ```bash
   python "C:/Users/johnp/.gemini/config/plugins/chronicle/scripts/chronicle_helper.py" init --project <project_name>
   ```

3. **Confirm to User:**
   Output a clean confirmation:
   - **Project Initialized:** `[project_name]`
   - **Vault Path:** `E:\chronicles\projects\[project_name]\`
   - **Active Version:** Version 1 (`in_progress`)
   - Scaffolding complete: `master_evolution.md` (5-chapter architecture), `graveyard_of_traps.md`, and `versions/v1.md`.
