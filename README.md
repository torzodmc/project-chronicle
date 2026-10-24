# Project Chronicle

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Compatible With: Antigravity & Claude Code](https://img.shields.io/badge/AI%20Assistants-Antigravity%20%7C%20Claude%20Code-purple.svg)](https://github.com/torzodmc/project-chronicle)

> *"A dedicated knowledge engine for software that evolves through version iterations (V1, V2, V3...). It permanently captures what AI models cannot observe from raw code alone: human intent, architectural philosophy, epistemic pivots, discarded failure modes, and reusable research breakthroughs."*

---

**Project Chronicle** is a universal evolutionary knowledge engine and skill suite for AI pair programming. It bridges the gap between ephemeral conversational AI context and long-term project reality across iterative software lifecycles.

Instead of losing human intent, conversational debates, architectural pivots, and discarded failure modes across chats, Project Chronicle permanently captures:
1. **Living Axioms & Philosophy:** The creator's foundational intent, mental models, and non-negotiable architectural boundaries.
2. **Universal Feature Lifecycle Matrix:** Exhaustive tracking of every feature from inception, evolution, refactoring, or retirement with exact reasons.
3. **Graveyard of Discarded Traps:** Permanent anti-patterns and failure traps so future AI agents never mistakenly re-suggest flawed ideas.
4. **Independent Discoveries & Research Catalog:** Permanent storage for experimental breakthroughs, standalone algorithms, mathematical proofs, or benchmarked assets without polluting sequential version milestones.
5. **Read-Only Observer Mode:** Instant hydration of deep architectural and risk context for side spikes, benchmarks, and prototypes without version authoring duties.

---

## The Chronicle Skill Suite

Project Chronicle exposes 9 modular, namespaced agent skills compatible with **Antigravity**, **Claude Code**, and agentic coding platforms:

| Skill / Command | Trigger Alias | Description |
|---|---|---|
| `/chronicle:new` | `/chronicle-new` | Initializes a brand-new project chronicle division in the vault with foundational templates. |
| `/chronicle:sync` | `/chronicle-sync` | Hydrates a new chat session with living axioms, master evolution, active version dossier, and graveyard traps. |
| `/chronicle:read` | `/chronicle-read` | Read-only observer mode: loads complete project context for side tasks and prototypes without version authoring duties. |
| `/chronicle:discover` | `/chronicle-discover` | Records an experimental breakthrough, algorithm, proof, model, or benchmarked asset into the permanent research catalog. |
| `/chronicle:update` | `/chronicle-update` | Captures epistemic diffs, conversational debates, user pushbacks, and architectural pivots into the active version and master evolution. |
| `/chronicle:complete` | `/chronicle-complete` | Seals the active version with empirical verification evidence and advances active tracking to $V_{N+1}$. |
| `/chronicle:jump` | `/chronicle-jump` | Fast-forwards tracking across multiple unchronicled iterations (e.g. $V_1 \to V_5$), cleanly recording skipped gaps. |
| `/chronicle:reopen` | `/chronicle-reopen` | Reopens a historical completed milestone for retroactive amendments or ongoing refinement. |
| `/chronicle:status` | `/chronicle-status` | Displays project health, active version pointer, total versions, and historical progression timeline. |

---

## Architectural Principles

- **Zero External Dependencies:** Built with 100% pure Python standard library (`os`, `json`, `sys`, `re`, `argparse`, `datetime`). Runs immediately on Windows, macOS, and Linux without `pip install` or virtual environments.
- **Atomic State Persistence:** All `state.json` modifications are written atomically via temporary swap files (`.tmp` $\to$ `os.replace`), preventing 0-byte state corruption during interrupted executions.
- **Strict Workspace Isolation:** Projects are automatically bound to their root workspace directories to prevent state bleed across different repositories on the same machine.
- **Epistemic Diff Protocol:** Banning bland, sterile bullet points. Agents document the *Old Assumption*, the *Collision Event* that shattered it, and the *New Reality*.
- **The Graveyard Mechanism:** Captures not just what failed, but *why it was tempting* and *why future AIs will mistakenly re-propose it*, accompanied by permanent invariant counter-rules.

---

## Installation & Setup

### 1. Antigravity / Gemini CLI
Clone or copy this repository into your plugins directory:
```bash
git clone https://github.com/torzodmc/project-chronicle.git ~/.gemini/config/plugins/chronicle
```
Restart your Antigravity session. The slash commands (`/chronicle:sync`, `/chronicle:discover`, etc.) will automatically appear in your autocomplete menu.

### 2. Claude Code
Copy the `skills/` directory into your global or workspace Claude skills folder:
```bash
# Global installation
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/

# Ensure chronicle_helper.py is accessible in PATH or ~/.claude/scripts
cp scripts/chronicle_helper.py ~/.claude/scripts/
```

### 3. Standalone CLI Usage
The helper script can be executed directly from any terminal:
```bash
python scripts/chronicle_helper.py --help

# Initialize a project
python scripts/chronicle_helper.py init --project my-project

# Check status
python scripts/chronicle_helper.py status

# Complete active version and advance to N+1
python scripts/chronicle_helper.py complete

# Record a breakthrough discovery
python scripts/chronicle_helper.py discover --title "Lock-Free Ring Buffer" --asset-path "core/ring_buffer.py" --summary "Zero-allocation atomic queue"

# Validate vault integrity
python scripts/chronicle_helper.py validate
```

---

## Vault Hierarchy

By default, Project Chronicle stores project evolutions in a centralized vault at `~/.chronicles/` (configurable via `CHRONICLE_VAULT` environment variable, project-local `.chronicle` directory, or `--vault` flag):

```text
chronicles/
├── state.json                     # Atomic registry of active projects, workspace bindings, versions, and discoveries
└── projects/
    └── <project_name>/
        ├── master_evolution.md    # 6-Chapter living manifesto, invariants, lifecycle matrix, and research catalog
        ├── graveyard_of_traps.md  # Comprehensive catalog of discarded anti-patterns
        ├── versions/
        │   ├── v1.md              # Milestone 1 dossier with epistemic diffs and verification
        │   └── v2.md              # Milestone 2 dossier
        └── discoveries/
            ├── 001-lock-free-ring-buffer.md
            └── 002-zero-copy-parser.md
```

---

## Testing & Quality Assurance

Project Chronicle includes a comprehensive unit test suite covering initialization, status tracking, version completion, jumping without markdown corruption, reopening, atomic persistence, observer mode, and discovery cataloging:

```bash
python -m unittest discover -s tests
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
