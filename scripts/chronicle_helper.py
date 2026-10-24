#!/usr/bin/env python3
"""
Universal Project Chronicle Helper Script.
Deterministic CLI and library helper for managing project evolution state,
version progression, schema validation, discoveries, and markdown dossiers.
Zero external dependencies (Python 3 standard library only).
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path


def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _utc_now_date():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _slugify(text):
    if not text:
        return "project"
    slug = re.sub(r"[^\w\s-]", "", str(text)).strip().lower()
    return re.sub(r"[-\s]+", "-", slug) or "project"


DEFAULT_VAULT_NAME = ".chronicle"
PRIMARY_DEDICATED_VAULT = r"E:\chronicles"


def resolve_vault_path(vault_path=None):
    if vault_path:
        return os.path.abspath(vault_path)
    
    # 1. Environment variable CHRONICLE_VAULT
    if "CHRONICLE_VAULT" in os.environ and os.environ["CHRONICLE_VAULT"].strip():
        return os.path.abspath(os.environ["CHRONICLE_VAULT"].strip())

    # 2. Check local workspace or parents for .chronicle or chronicles folder
    try:
        curr = Path(os.getcwd()).resolve()
        for parent in [curr] + list(curr.parents):
            for name in [DEFAULT_VAULT_NAME, "chronicles"]:
                candidate = parent / name
                if candidate.is_dir():
                    return str(candidate)
    except Exception:
        pass

    # 3. Check if standard ~/.chronicles exists
    home_vault = Path.home() / ".chronicles"
    if home_vault.is_dir():
        return str(home_vault)

    # 4. Backward compatibility: if E:\chronicles already exists on disk, preserve it
    if os.path.exists(PRIMARY_DEDICATED_VAULT):
        return PRIMARY_DEDICATED_VAULT

    # 5. Default to centralized ~/.chronicles
    return str(home_vault)


def _load_state(vault):
    state_file = os.path.join(vault, "state.json")
    if not os.path.exists(state_file):
        return {
            "created_at": _utc_now_iso(),
            "last_updated": _utc_now_iso(),
            "active_project": None,
            "projects": {}
        }
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to parse state file at '{state_file}'. "
            f"The file may be corrupted or locked. Error: {exc}"
        )

    if not isinstance(state, dict):
        raise RuntimeError(f"Corrupt state file: root object must be a dictionary in '{state_file}'")

    if "projects" not in state or not isinstance(state["projects"], dict):
        state["projects"] = {}

    return state


def _save_state(vault, state):
    os.makedirs(vault, exist_ok=True)
    state["last_updated"] = _utc_now_iso()
    state_file = os.path.join(vault, "state.json")
    tmp_file = f"{state_file}.{os.getpid()}.tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_file, state_file)


def _resolve_project_name(project_name, state):
    """
    Deterministically resolves which project to target:
    1. Explicit project_name passed by user/caller.
    2. Match a registered project whose workspace_root equals or is an ancestor of CWD.
    3. Match a registered project whose name matches slugified CWD folder name.
    4. Fallback to state['active_project'].
    """
    if project_name and str(project_name).strip():
        return _slugify(str(project_name).strip())
        
    projects = state.get("projects", {})
    if not projects:
        return None

    try:
        cwd_resolved = str(Path.cwd().resolve())
        cwd_slug = _slugify(Path.cwd().name)

        # 2. Check workspace_root match
        best_match = None
        best_len = 0
        for pname, pdata in projects.items():
            w_root = pdata.get("workspace_root")
            if w_root:
                try:
                    rel = os.path.relpath(cwd_resolved, w_root)
                    if not rel.startswith("..") and not rel.startswith("/") and not rel.startswith("\\"):
                        if len(w_root) > best_len:
                            best_match = pname
                            best_len = len(w_root)
                except ValueError:
                    pass
        if best_match:
            return best_match

        # 3. Check if folder name matches a project
        if cwd_slug in projects:
            return cwd_slug
    except Exception:
        pass

    # 4. Fallback to active_project
    return state.get("active_project")


def _generate_v_template(version_num, title=None):
    date_str = _utc_now_date()
    v_title = title if title else f"Milestone / Iteration {version_num}"
    return f"""# Version {version_num}: {v_title}

**Status:** in_progress  
**Date Created:** {date_str} | **Last Updated:** {date_str}  

---

### 1. Human Philosophy, Vision & Mental Models
- **The Core Intuition:** [What is the human creator trying to achieve in this version?]
- **Mental Metaphors & Analogies:** [Key mental models used to frame the problem]
- **The Epistemic Diff (Old Belief vs. Collision Event vs. New Reality):**
  - *Old Assumption:* [What did we believe before this version?]
  - *The Collision Event:* [What specific bug, test result, or user correction shattered that assumption?]
  - *New Reality & Philosophy:* [What is the new mental model, in the user's exact words?]
- **The "Why":** [Underlying rationale that code alone cannot convey]

### 2. Conversational Debates & Decisions (The Chat Record)
- **Key Debates:** [What architectural alternatives were discussed in chat?]
- **User Corrections & Pushback:** [Where did the user correct the AI or reject a proposal?]
- **Clarification Checkpoints:** [Specific clarifications confirmed with the user during update]
- **Agreed Compromises:** [Why this specific path was chosen over alternatives]

### 3. Exhaustive Feature & Architecture Anatomy
- **Feature Name & Purpose:** [Description]
- **Detailed Mechanics:** [Internal behavior, edge cases handled, dependencies]
- **Interactions:** [Cross-component impacts]
- **Code Reference:** [Specific modules or files modified]

### 4. What Changed vs. Previous Version & Why
- **Modified Features:** [What it used to do, what it does now, and why]
- **Retired Features:** [What was removed and why]
- **Preserved Invariants:** [What was intentionally kept untouched and why]

### 5. Post-Mortems, Failure Modes & Traps Discovered
- **Bugs / Failure Scenarios:** [What broke during development or testing?]
- **Root Cause Analysis:** [Why did it fail?]
- **Permanent Lessons:** [Actionable rules to prevent recurrence]

### 6. Verification, Testing & Empirical Results
- [Commands run, test outputs, benchmark/backtest data, and tangible proof of correctness]
"""


def _generate_master_template(project_name):
    date_str = _utc_now_date()
    return f"""# {project_name} — Master Evolutionary Ledger

**Project:** {project_name}  
**Date Initialized:** {date_str} | **Last Updated:** {date_str}  

---

## 1. Foundational Intent & Origin Thesis
- **The Core Problem & Origin Story:** [Document the foundational human intent, pain with manual/prototype iterations, operational/emotional friction points, and the reason for inception]
- **The Creator's Mission:** [What success looks like, what failure looks like, and why this system must exist]
- **Human vs. Machine Boundaries:** [What decisions are delegated to automation/AI vs. preserved for human oversight]

---

## 2. Core System Philosophy, Metaphors & Living Invariants
- **Core Mental Models & Metaphors:** [Foundational mental models and analogies used to reason about the system]
- **Non-Negotiable Living Axioms:** [Universal invariants and rules that persist across all versions]
- **Boundary Guarantees:** [Fundamental safety rules, causal data protections, and operational integrity laws]

---

## 3. The Epistemic History of Beliefs (Mental Model Progression)
- **Version 1 Foundation:**
  - *Initial Belief:* [What was originally assumed to be true at inception]
  - *Real-World Encounter:* [What empirical evidence, bug, benchmark, or user pushback challenged that belief]
  - *Philosophical Shift:* [The resulting adaptation in mental models and core philosophy]

---

## 4. Universal Feature Lifecycle Matrix & Full Specifications
| Feature / Subsystem | Introduced | Current Status | Current Specification | Evolution History & Replacement Rationale |
|---|---|---|---|---|
| Core Subsystem | V1 | ACTIVE | Baseline Architecture | Initial implementation details |

---

## 5. Comprehensive Version Progression Log
- **Version 1**: Foundation & initial baseline established.

---

## 6. Discoveries & Research Catalog
| Discovery | Date | Primary Asset Location | Breakthrough Edge & Summary |
|---|---|---|---|
| (No discoveries logged yet. Run /chronicle:discover to record findings) | - | - | - |
"""


def _generate_discovery_template(title, discovery_id, project_name, asset_path=None):
    date_str = _utc_now_date()
    asset_str = f"`{asset_path}`" if asset_path else "[Path to primary implementation, script, notebook, or source asset]"
    return f"""# Discovery {discovery_id:03d}: {title}

**Project:** {project_name}  
**Discovery ID:** DISCOVERY-{discovery_id:03d} | **Date:** {date_str}  
**Status:** Validated Research / Experimental  

---

### 1. Concrete Asset Locations
- **Primary Implementation / Script:** {asset_str}
- **Artifacts / Binaries / Outputs:** [Paths to saved artifacts, compiled binaries, models/weights, or generated outputs (if any)]
- **Fixtures / Test Harness / Inputs:** [Paths to input data, benchmarks, or verification fixtures]

---

### 2. Intuition, Philosophy & The "Why"
- **The Core Problem / Bottleneck / Curiosity:** [What question, limitation, or exploratory idea triggered this investigation?]
- **Hypothesis & Mental Model:** [What did we expect to find or prove, and what principle motivated this approach?]
- **Why It Matters:** [The philosophical, practical, or architectural significance of this breakthrough]

---

### 3. Technical Anatomy & Mechanics
- **How It Works:** [Deep technical explanation of the mechanism, algorithm, data structure, mathematical relationship, or pattern]
- **Key Parameters & Configuration:** [Critical constants, flags, inputs, or environment setup]
- **Complexity & Characteristics:** [Time/space complexity, resource consumption, or performance trade-offs]

---

### 4. Empirical Proof & Validation
- **Observed Metrics / Benchmarks:** [Tangible test results, benchmarks, latency/throughput gains, or error metrics versus baseline]
- **Validation Evidence:** [Exact commands executed, test outputs, or reproducible verification steps]

---

### 5. Architectural Integration Pathway
- **Potential Production Role:** [How a future production version could operationalize or merge this discovery]
- **Integration Prerequisites:** [Prerequisites, API contracts, or refactoring required before core adoption]
"""


def _generate_graveyard_template(project_name):
    date_str = _utc_now_date()
    return f"""# {project_name} — Graveyard of Discarded Ideas & Traps

**Project:** {project_name}  
**Last Updated:** {date_str}  

| Anti-Pattern / Trap | Discovered In | What Made It Tempting | Hidden Failure Mechanism | Why Future AIs Will Mistakenly Re-Suggest It | Permanent Invariant Counter-Rule |
|---|---|---|---|---|---|
| Sample Anti-Pattern | V0 | Apparent simplicity | Fragile edge cases | Overfitting to simple examples | Always enforce strict boundary checks |
"""


def _ensure_6_chapter_master(master_file, project_name):
    """Upgrades a legacy master_evolution.md to the rich 6-chapter format non-destructively."""
    if not os.path.exists(master_file):
        return
    with open(master_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    if "## 1. Foundational Intent & Origin Thesis" in content:
        if "## 6. Discoveries & Research Catalog" not in content:
            content = content.rstrip() + "\n\n---\n\n## 6. Discoveries & Research Catalog\n| Discovery | Date | Primary Asset Location | Breakthrough Edge & Summary |\n|---|---|---|---|\n| (No discoveries logged yet. Run /chronicle:discover to record findings) | - | - | - |\n"
            with open(master_file, "w", encoding="utf-8") as f:
                f.write(content)
        return

    has_old_1 = "## 1. Core Philosophy & Living Invariant Principles" in content
    has_old_2 = "## 2. Universal Feature Lifecycle Matrix" in content
    
    if has_old_1 and has_old_2:
        header_part = content.split("## 1. Core Philosophy & Living Invariant Principles")[0]
        rest1 = content.split("## 1. Core Philosophy & Living Invariant Principles")[1]
        old_philosophy = rest1.split("## 2. Universal Feature Lifecycle Matrix")[0].strip()
        rest2 = rest1.split("## 2. Universal Feature Lifecycle Matrix")[1]
        
        if "## 3. Comprehensive Version Progression Log" in rest2:
            old_matrix = rest2.split("## 3. Comprehensive Version Progression Log")[0].strip()
            old_log = rest2.split("## 3. Comprehensive Version Progression Log")[1].strip()
        else:
            old_matrix = rest2.strip()
            old_log = "- **Version 1**: Baseline established."
            
        new_content = f"""{header_part.strip()}

---

## 1. Foundational Intent & Origin Thesis
- **The Core Problem & Origin Story:** [Document the foundational human intent, pain with manual/prototype iterations, operational/emotional friction points, and the reason for inception]
- **The Creator's Mission:** [What success looks like, what failure looks like, and why this system must exist]
- **Human vs. Machine Boundaries:** [What decisions are delegated to automation/AI vs. preserved for human oversight]

---

## 2. Core System Philosophy, Metaphors & Living Invariants
{old_philosophy.strip()}

---

## 3. The Epistemic History of Beliefs (Mental Model Progression)
- **Version 1 Foundation:**
  - *Initial Belief:* [What was originally assumed to be true at inception]
  - *Real-World Encounter:* [What empirical evidence, bug, benchmark, or user pushback challenged that belief]
  - *Philosophical Shift:* [The resulting adaptation in mental models and core philosophy]

---

## 4. Universal Feature Lifecycle Matrix & Full Specifications
{old_matrix.strip()}

---

## 5. Comprehensive Version Progression Log
{old_log.strip()}

---

## 6. Discoveries & Research Catalog
| Discovery | Date | Primary Asset Location | Breakthrough Edge & Summary |
|---|---|---|---|
| (No discoveries logged yet. Run /chronicle:discover to record findings) | - | - | - |
"""
        new_content = re.sub(r'(?:---\s*\n\s*){2,}', '---\n\n', new_content)
        with open(master_file, "w", encoding="utf-8") as f:
            f.write(new_content.strip() + "\n")


def init_project(project_name=None, vault_path=None):
    if not project_name or not str(project_name).strip():
        project_name = _slugify(Path.cwd().name)
    project_name = _slugify(str(project_name))

    vault = resolve_vault_path(vault_path)
    state = _load_state(vault)
    
    project_dir = os.path.join(vault, "projects", project_name)
    versions_dir = os.path.join(project_dir, "versions")
    discoveries_dir = os.path.join(project_dir, "discoveries")
    os.makedirs(versions_dir, exist_ok=True)
    os.makedirs(discoveries_dir, exist_ok=True)
    
    master_file = os.path.join(project_dir, "master_evolution.md")
    if not os.path.exists(master_file):
        with open(master_file, "w", encoding="utf-8") as f:
            f.write(_generate_master_template(project_name))
            
    graveyard_file = os.path.join(project_dir, "graveyard_of_traps.md")
    if not os.path.exists(graveyard_file):
        with open(graveyard_file, "w", encoding="utf-8") as f:
            f.write(_generate_graveyard_template(project_name))
            
    v1_file = os.path.join(versions_dir, "v1.md")
    if not os.path.exists(v1_file):
        with open(v1_file, "w", encoding="utf-8") as f:
            f.write(_generate_v_template(1, "Foundation & Initial Architecture"))

    cwd_root = str(Path.cwd().resolve())
    if project_name not in state["projects"]:
        state["projects"][project_name] = {
            "created_at": _utc_now_iso(),
            "workspace_root": cwd_root,
            "active_version": 1,
            "versions": [
                {
                    "version": 1,
                    "title": "Foundation & Initial Architecture",
                    "file": "versions/v1.md",
                    "status": "in_progress",
                    "created_at": _utc_now_iso()
                }
            ],
            "discoveries": []
        }
    else:
        state["projects"][project_name]["workspace_root"] = cwd_root
    
    state["active_project"] = project_name
    _save_state(vault, state)
    
    return {
        "success": True,
        "vault": vault,
        "project": project_name,
        "project_dir": project_dir,
        "active_version": 1,
        "status": "in_progress"
    }


def get_status(project_name=None, vault_path=None):
    vault = resolve_vault_path(vault_path)
    state = _load_state(vault)
    pname = _resolve_project_name(project_name, state)
    if not pname or pname not in state.get("projects", {}):
        return {
            "success": True,
            "project_name": None,
            "vault_path": vault,
            "active_version": None,
            "version_status": None,
            "total_versions": 0,
            "versions": [],
            "total_discoveries": 0,
            "discoveries": [],
            "message": "No active project currently tracked in vault. Run /chronicle:new to initialize one."
        }
        
    pdata = state["projects"][pname]
    active_v = pdata.get("active_version", 1)
    v_entry = next((v for v in pdata.get("versions", []) if v["version"] == active_v), None)
    v_status = v_entry["status"] if v_entry else "unknown"
    discoveries = pdata.get("discoveries", [])
    
    return {
        "success": True,
        "project_name": pname,
        "vault_path": vault,
        "active_version": active_v,
        "version_status": v_status,
        "total_versions": len(pdata.get("versions", [])),
        "versions": pdata.get("versions", []),
        "total_discoveries": len(discoveries),
        "discoveries": discoveries
    }


def sync_project(project_name=None, version=None, vault_path=None):
    vault = resolve_vault_path(vault_path)
    state = _load_state(vault)
    pname = _resolve_project_name(project_name, state)
    if not pname or pname not in state.get("projects", {}):
        return {
            "success": False,
            "error": "No active project in vault. Run /chronicle:new to start tracking."
        }
        
    state["active_project"] = pname
    if version is not None:
        v_num = int(version)
        known_versions = [v["version"] for v in state["projects"][pname].get("versions", [])]
        if v_num not in known_versions:
            return {
                "success": False,
                "error": f"Version {v_num} does not exist in project '{pname}'. Known versions: {known_versions}. Use /chronicle:jump to fast-forward."
            }
        state["projects"][pname]["active_version"] = v_num
        
    _save_state(vault, state)

    project_dir = os.path.join(vault, "projects", pname)
    master_file = os.path.join(project_dir, "master_evolution.md")
    _ensure_6_chapter_master(master_file, pname)

    return get_status(pname, vault_path=vault)


def read_project(project_name=None, vault_path=None, include_content=True):
    vault = resolve_vault_path(vault_path)
    state = _load_state(vault)
    pname = _resolve_project_name(project_name, state)
    if not pname or pname not in state.get("projects", {}):
        return {
            "success": False,
            "error": "No active project in vault. Run /chronicle:new to initialize one."
        }
        
    project_dir = os.path.join(vault, "projects", pname)
    master_file = os.path.join(project_dir, "master_evolution.md")
    graveyard_file = os.path.join(project_dir, "graveyard_of_traps.md")
    _ensure_6_chapter_master(master_file, pname)
    
    master_content = ""
    graveyard_content = ""
    if include_content:
        if os.path.exists(master_file):
            with open(master_file, "r", encoding="utf-8") as f:
                master_content = f.read()
        if os.path.exists(graveyard_file):
            with open(graveyard_file, "r", encoding="utf-8") as f:
                graveyard_content = f.read()
            
    pdata = state["projects"][pname]
    active_v = pdata.get("active_version", 1)
    discoveries = pdata.get("discoveries", [])
    
    res = {
        "success": True,
        "mode": "read_only_observer",
        "project_name": pname,
        "vault_path": vault,
        "active_version": active_v,
        "total_versions": len(pdata.get("versions", [])),
        "total_discoveries": len(discoveries),
        "discoveries": discoveries,
        "master_evolution_path": master_file,
        "graveyard_path": graveyard_file,
        "observer_directive": f"You are in Read-Only Observer Mode for project '{pname}'. You have complete architectural, philosophical, and risk context in memory to assist with side tasks, experiments, benchmarks, prototypes, or analysis. You are NOT authoring a version milestone and must NOT increment versions or run /chronicle:update. If an independent breakthrough or reusable asset is created, catalog it using /chronicle:discover."
    }
    if include_content:
        res["master_evolution_content"] = master_content
        res["graveyard_content"] = graveyard_content
    return res


def discover_item(title, asset_path=None, summary=None, project_name=None, vault_path=None):
    vault = resolve_vault_path(vault_path)
    state = _load_state(vault)
    pname = _resolve_project_name(project_name, state)
    if not pname or pname not in state.get("projects", {}):
        return {
            "success": False,
            "error": "No active project found in vault. Run /chronicle:new first."
        }
        
    pdata = state["projects"][pname]
    if "discoveries" not in pdata:
        pdata["discoveries"] = []
        
    disc_list = pdata["discoveries"]
    next_id = len(disc_list) + 1
    
    slug = _slugify(title)
    filename = f"{next_id:03d}-{slug}.md"
    
    project_dir = os.path.join(vault, "projects", pname)
    disc_dir = os.path.join(project_dir, "discoveries")
    os.makedirs(disc_dir, exist_ok=True)
    
    disc_file = os.path.join(disc_dir, filename)
    rel_file = f"discoveries/{filename}"
    
    if not os.path.exists(disc_file):
        with open(disc_file, "w", encoding="utf-8") as f:
            f.write(_generate_discovery_template(title, next_id, pname, asset_path))
            
    disc_entry = {
        "id": next_id,
        "title": title,
        "file": rel_file,
        "asset_path": asset_path,
        "created_at": _utc_now_iso()
    }
    pdata["discoveries"].append(disc_entry)
    _save_state(vault, state)
    
    # Append to master_evolution.md
    master_file = os.path.join(project_dir, "master_evolution.md")
    if os.path.exists(master_file):
        with open(master_file, "r", encoding="utf-8") as f:
            m_content = f.read()
            
        summary_str = summary if summary else "Breakthrough asset / experimental finding"
        asset_str = f"`{asset_path}`" if asset_path else "See discovery dossier"
        row = f"| [{title}]({rel_file}) | {_utc_now_date()} | {asset_str} | {summary_str} |\n"
        
        cat_header = "## 6. Discoveries & Research Catalog"
        if cat_header in m_content:
            parts = m_content.split(cat_header)
            # Replace placeholder row if present (robust against CRLF and whitespace)
            post_header = re.sub(r'\|\s*\(No discoveries logged yet[^\r\n]*\|\s*-\s*\|\s*-\s*\|\s*-\s*\|\r?\n', '', parts[1])
            m_content = parts[0] + cat_header + post_header.rstrip() + "\n" + row
        else:
            m_content = m_content.rstrip() + f"\n\n---\n\n{cat_header}\n\n| Discovery | Date | Primary Asset Location | Breakthrough Edge & Summary |\n|---|---|---|---|\n{row}\n"
            
        with open(master_file, "w", encoding="utf-8") as f:
            f.write(m_content)
            
    return {
        "success": True,
        "project": pname,
        "discovery_id": next_id,
        "title": title,
        "file": rel_file,
        "absolute_path": disc_file
    }


def complete_version(version=None, project_name=None, vault_path=None):
    vault = resolve_vault_path(vault_path)
    state = _load_state(vault)
    pname = _resolve_project_name(project_name, state)
    if not pname or pname not in state.get("projects", {}):
        return {"success": False, "error": f"Project '{pname}' not found"}
        
    pdata = state["projects"][pname]
    if version is None:
        v_num = pdata.get("active_version", 1)
    else:
        v_num = int(version)
    
    # Mark target version as completed
    v_entry = next((v for v in pdata.get("versions", []) if v["version"] == v_num), None)
    if v_entry:
        v_entry["status"] = "completed"
        v_entry["completed_at"] = _utc_now_iso()
    else:
        pdata["versions"].append({
            "version": v_num,
            "title": f"Milestone {v_num}",
            "file": f"versions/v{v_num}.md",
            "status": "completed",
            "completed_at": _utc_now_iso()
        })
        
    # Update file header on disk if present using safe targeted regex
    v_file = os.path.join(vault, "projects", pname, "versions", f"v{v_num}.md")
    if os.path.exists(v_file):
        with open(v_file, "r", encoding="utf-8") as f:
            content = f.read()
        content = re.sub(r'(?mi)^(\*\*Status:\*\*|\*\*Status\*\*:)\s*(?:in_progress|in[ -]progress)\s*$', r'**Status:** completed  ', content)
        with open(v_file, "w", encoding="utf-8") as f:
            f.write(content)

    recorded_versions = pdata.get("versions", [])
    max_v = max((v["version"] for v in recorded_versions), default=v_num)

    if v_num < max_v:
        # Completing a reopened historical version (e.g. V2 while project is at V5)
        highest_in_prog = next((v["version"] for v in reversed(recorded_versions) if v.get("status") == "in_progress"), max_v)
        pdata["active_version"] = highest_in_prog
        next_v = highest_in_prog
    else:
        # Normal sequential progression: V_N completed, advance to V_{N+1}
        next_v = v_num + 1
        next_entry = next((v for v in recorded_versions if v["version"] == next_v), None)
        if not next_entry:
            pdata["versions"].append({
                "version": next_v,
                "title": f"Milestone {next_v}",
                "file": f"versions/v{next_v}.md",
                "status": "in_progress",
                "created_at": _utc_now_iso()
            })
        else:
            next_entry["status"] = "in_progress"
            next_entry["file"] = f"versions/v{next_v}.md"

        pdata["active_version"] = next_v

        # Scaffold v{next_v}.md if missing
        next_file = os.path.join(vault, "projects", pname, "versions", f"v{next_v}.md")
        if not os.path.exists(next_file):
            with open(next_file, "w", encoding="utf-8") as f:
                f.write(_generate_v_template(next_v))

    _save_state(vault, state)

    return {
        "success": True,
        "completed_version": v_num,
        "next_active_version": next_v
    }


def jump_version(target_version, project_name=None, vault_path=None):
    vault = resolve_vault_path(vault_path)
    state = _load_state(vault)
    pname = _resolve_project_name(project_name, state)
    if not pname or pname not in state.get("projects", {}):
        return {"success": False, "error": "No active project found in vault. Run /chronicle:new first."}
        
    pdata = state["projects"][pname]
    current_v = pdata.get("active_version", 1)
    target_v = int(target_version)
    
    recorded_versions = [v["version"] for v in pdata.get("versions", [])]
    max_v = max(recorded_versions) if recorded_versions else current_v
    
    if target_v <= current_v:
        return {
            "success": False,
            "error": f"Target version {target_v} must be greater than current active version {current_v}. Use /chronicle:reopen --version {target_v} to return to an earlier version."
        }
        
    if target_v <= max_v:
        return {
            "success": False,
            "error": f"Target version {target_v} already exists in project history (highest version is {max_v}). Use /chronicle:reopen --version {target_v} to reopen existing versions."
        }
        
    # 1. Seal current active version if in_progress
    curr_entry = next((v for v in pdata.get("versions", []) if v["version"] == current_v), None)
    if curr_entry and curr_entry.get("status") == "in_progress":
        curr_entry["status"] = "completed"
        curr_entry["completed_at"] = _utc_now_iso()
        curr_file = os.path.join(vault, "projects", pname, "versions", f"v{current_v}.md")
        if os.path.exists(curr_file):
            with open(curr_file, "r", encoding="utf-8") as f:
                content = f.read()
            content = re.sub(r'(?mi)^(\*\*Status:\*\*|\*\*Status\*\*:)\s*(?:in_progress|in[ -]progress)\s*$', r'**Status:** completed  ', content)
            with open(curr_file, "w", encoding="utf-8") as f:
                f.write(content)
                
    # 2. Record skipped versions in state.json
    skipped_versions = []
    for v in range(current_v + 1, target_v):
        v_entry = next((entry for entry in pdata.get("versions", []) if entry["version"] == v), None)
        if not v_entry:
            pdata["versions"].append({
                "version": v,
                "title": "Skipped Milestone",
                "status": "skipped",
                "skipped_at": _utc_now_iso()
            })
            skipped_versions.append(v)
        else:
            v_entry["status"] = "skipped"
            v_entry["skipped_at"] = _utc_now_iso()
            skipped_versions.append(v)
            
    # 3. Add target version to state.json
    target_entry = next((entry for entry in pdata.get("versions", []) if entry["version"] == target_v), None)
    if not target_entry:
        pdata["versions"].append({
            "version": target_v,
            "title": f"Milestone / Iteration {target_v}",
            "file": f"versions/v{target_v}.md",
            "status": "in_progress",
            "created_at": _utc_now_iso()
        })
    else:
        target_entry["status"] = "in_progress"
        target_entry["file"] = f"versions/v{target_v}.md"
        
    pdata["active_version"] = target_v
    _save_state(vault, state)
    
    # 4. Scaffold target version file
    target_file = os.path.join(vault, "projects", pname, "versions", f"v{target_v}.md")
    if not os.path.exists(target_file):
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(_generate_v_template(target_v))
            
    # 5. Append skipped milestones and target milestone to master_evolution.md
    master_file = os.path.join(vault, "projects", pname, "master_evolution.md")
    if os.path.exists(master_file):
        _ensure_6_chapter_master(master_file, pname)
        
        with open(master_file, "r", encoding="utf-8") as f:
            m_content = f.read()
            
        log_entries = []
        for sv in skipped_versions:
            log_entries.append(f"- **Version {sv}**: Skipped / Unchronicled milestone (Fast-forwarded to Version {target_v}).")
        log_entries.append(f"- **Version {target_v}** ({_utc_now_date()}): In progress.")
        
        log_text = "\n".join(log_entries) + "\n"
        
        if "## 5. Comprehensive Version Progression Log" in m_content:
            parts = m_content.split("## 5. Comprehensive Version Progression Log", 1)
            prefix = parts[0] + "## 5. Comprehensive Version Progression Log\n"
            suffix = parts[1]
            if "## 6. Discoveries & Research Catalog" in suffix:
                ch5_body, ch6_body = suffix.split("## 6. Discoveries & Research Catalog", 1)
                clean_ch5 = re.sub(r'(?:\r?\n)*---\s*$', '', ch5_body.rstrip())
                m_content = prefix + clean_ch5.rstrip() + "\n" + log_text + "\n---\n\n## 6. Discoveries & Research Catalog" + ch6_body
            else:
                clean_ch5 = re.sub(r'(?:\r?\n)*---\s*$', '', suffix.rstrip())
                m_content = prefix + clean_ch5.rstrip() + "\n" + log_text
        elif "## 3. Comprehensive Version Progression Log" in m_content:
            parts = m_content.split("## 3. Comprehensive Version Progression Log", 1)
            clean_ch3 = re.sub(r'(?:\r?\n)*---\s*$', '', parts[1].rstrip())
            m_content = parts[0] + "## 3. Comprehensive Version Progression Log\n" + clean_ch3.rstrip() + "\n" + log_text
        else:
            m_content += f"\n\n---\n\n## 5. Comprehensive Version Progression Log\n{log_text}\n"
            
        with open(master_file, "w", encoding="utf-8") as f:
            f.write(m_content)
            
    return {
        "success": True,
        "project": pname,
        "previous_version": current_v,
        "active_version": target_v,
        "skipped_versions": skipped_versions,
        "target_file": target_file
    }


def reopen_version(version, project_name=None, vault_path=None):
    vault = resolve_vault_path(vault_path)
    state = _load_state(vault)
    pname = _resolve_project_name(project_name, state)
    if not pname or pname not in state.get("projects", {}):
        return {"success": False, "error": f"Project '{pname}' not found"}
        
    pdata = state["projects"][pname]
    v_num = int(version)
    
    v_entry = next((v for v in pdata.get("versions", []) if v["version"] == v_num), None)
    if not v_entry:
        return {"success": False, "error": f"Version {v_num} does not exist in project '{pname}'"}
        
    v_entry["status"] = "in_progress"
    v_entry["file"] = f"versions/v{v_num}.md"
    pdata["active_version"] = v_num
    _save_state(vault, state)
    
    v_file = os.path.join(vault, "projects", pname, "versions", f"v{v_num}.md")
    if not os.path.exists(v_file):
        with open(v_file, "w", encoding="utf-8") as f:
            f.write(_generate_v_template(v_num))
    else:
        with open(v_file, "r", encoding="utf-8") as f:
            content = f.read()
        content = re.sub(r'(?mi)^(\*\*Status:\*\*|\*\*Status\*\*:)\s*(?:completed|skipped|in_progress|in[ -]progress)\s*$', r'**Status:** in_progress  ', content)
        if "## Retroactive Reopening & Amendments" not in content:
            content += f"\n\n---\n\n## Retroactive Reopening & Amendments ({_utc_now_date()})\n"
        with open(v_file, "w", encoding="utf-8") as f:
            f.write(content)
            
    return {
        "success": True,
        "reopened_version": v_num,
        "active_version": v_num,
        "status": "in_progress"
    }


def validate_vault(project_name=None, vault_path=None):
    vault = resolve_vault_path(vault_path)
    state_file = os.path.join(vault, "state.json")
    if not os.path.exists(state_file):
        return {
            "valid": False,
            "errors": [f"Missing state file: {state_file}"]
        }

    try:
        state = _load_state(vault)
    except Exception as exc:
        return {
            "valid": False,
            "errors": [f"Corrupt state file: {exc}"]
        }

    errors = []
    pname = _resolve_project_name(project_name, state)
    if not pname:
        return {
            "valid": True,
            "errors": [],
            "message": "Vault is clean. No active projects currently tracked."
        }
        
    if pname not in state.get("projects", {}):
        errors.append(f"Project '{pname}' declared active but missing from projects registry")
        return {"valid": False, "errors": errors}
        
    project_dir = os.path.join(vault, "projects", pname)
    if not os.path.isdir(project_dir):
        errors.append(f"Missing project directory: {project_dir}")
        return {"valid": False, "errors": errors}
        
    master_file = os.path.join(project_dir, "master_evolution.md")
    if not os.path.exists(master_file):
        errors.append(f"Missing master_evolution.md in {project_dir}")
        
    graveyard_file = os.path.join(project_dir, "graveyard_of_traps.md")
    if not os.path.exists(graveyard_file):
        errors.append(f"Missing graveyard_of_traps.md in {project_dir}")
        
    versions_dir = os.path.join(project_dir, "versions")
    if not os.path.isdir(versions_dir):
        errors.append(f"Missing versions directory in {project_dir}")
    else:
        for ventry in state["projects"][pname].get("versions", []):
            if ventry.get("status") == "skipped":
                continue  # Skipped versions do not require dossier files
            vnum = ventry["version"]
            vfile = os.path.join(versions_dir, f"v{vnum}.md")
            if not os.path.exists(vfile):
                errors.append(f"Missing version dossier {vfile}")

    # Validate discoveries if present
    for dentry in state["projects"][pname].get("discoveries", []):
        dfile = os.path.join(vault, "projects", pname, dentry.get("file", ""))
        if not os.path.exists(dfile):
            errors.append(f"Missing discovery dossier {dfile}")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


# Alias for backward compatibility
validate_schemas = validate_vault


def main():
    parser = argparse.ArgumentParser(description="Universal Project Chronicle CLI Helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Initialize a project chronicle division")
    p_init.add_argument("--project", default=None, help="Project name (defaults to current folder name)")
    p_init.add_argument("--vault", help="Custom vault path")

    # status
    p_status = subparsers.add_parser("status", help="Get chronicle status")
    p_status.add_argument("--project", help="Project name (defaults to active)")
    p_status.add_argument("--vault", help="Custom vault path")

    # sync
    p_sync = subparsers.add_parser("sync", help="Synchronize active project/version")
    p_sync.add_argument("--project", help="Project name")
    p_sync.add_argument("--version", type=int, help="Version to anchor")
    p_sync.add_argument("--vault", help="Custom vault path")

    # read
    p_read = subparsers.add_parser("read", help="Hydrate complete project context in read-only observer mode without version binding")
    p_read.add_argument("--project", help="Project name (defaults to active project)")
    p_read.add_argument("--vault", help="Custom vault path")

    # discover
    p_discover = subparsers.add_parser("discover", help="Record an experimental discovery or breakthrough")
    p_discover.add_argument("--title", required=True, help="Title of the discovery")
    p_discover.add_argument("--asset-path", help="Path to primary script, model, or dataset")
    p_discover.add_argument("--summary", help="Brief one-line summary of breakthrough")
    p_discover.add_argument("--project", help="Project name (defaults to active project)")
    p_discover.add_argument("--vault", help="Custom vault path")

    # complete
    p_complete = subparsers.add_parser("complete", help="Complete a version and advance to N+1")
    p_complete.add_argument("--version", type=int, default=None, help="Version to complete (defaults to active_version)")
    p_complete.add_argument("--project", help="Project name")
    p_complete.add_argument("--vault", help="Custom vault path")

    # jump
    p_jump = subparsers.add_parser("jump", help="Jump forward to a target version and mark intermediate as skipped")
    p_jump.add_argument("--to", type=int, required=True, help="Target version number to jump to")
    p_jump.add_argument("--project", help="Project name")
    p_jump.add_argument("--vault", help="Custom vault path")

    # reopen
    p_reopen = subparsers.add_parser("reopen", help="Reopen a completed version for editing")
    p_reopen.add_argument("--version", type=int, required=True, help="Version to reopen")
    p_reopen.add_argument("--project", help="Project name")
    p_reopen.add_argument("--vault", help="Custom vault path")

    # validate
    p_validate = subparsers.add_parser("validate", help="Validate schemas and state integrity")
    p_validate.add_argument("--project", help="Project name")
    p_validate.add_argument("--vault", help="Custom vault path")

    args = parser.parse_args()

    if args.command == "init":
        res = init_project(args.project, args.vault)
        print(json.dumps(res, indent=2))
    elif args.command == "status":
        res = get_status(args.project, args.vault)
        print(json.dumps(res, indent=2))
    elif args.command == "sync":
        res = sync_project(args.project, args.version, args.vault)
        print(json.dumps(res, indent=2))
    elif args.command == "read":
        res = read_project(args.project, args.vault, include_content=False)
        print(json.dumps(res, indent=2))
    elif args.command == "discover":
        res = discover_item(args.title, args.asset_path, args.summary, args.project, args.vault)
        print(json.dumps(res, indent=2))
    elif args.command == "complete":
        res = complete_version(args.version, args.project, args.vault)
        print(json.dumps(res, indent=2))
    elif args.command == "jump":
        res = jump_version(args.to, args.project, args.vault)
        print(json.dumps(res, indent=2))
    elif args.command == "reopen":
        res = reopen_version(args.version, args.project, args.vault)
        print(json.dumps(res, indent=2))
    elif args.command == "validate":
        res = validate_vault(args.project, args.vault)
        print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
