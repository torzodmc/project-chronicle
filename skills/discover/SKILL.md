---
name: discover
description: "Use when you have achieved an experimental breakthrough, designed an algorithm, validated a mathematical finding, or created a valuable asset that should be permanently cataloged without being bound to a product version milestone."
---

# Chronicle: Record Discovery & Research Asset (`/chronicle:discover` / `/chronicle-discover`)

Use this skill to permanently capture experimental breakthroughs, specialized algorithms, data structures, optimization techniques, mathematical proofs, standalone datasets, models, or research assets into the project's permanent knowledge base. Discoveries are decoupled from sequential product versioning, preserving valuable findings for all future iterations across any domain.

> [!CRITICAL]
> **STRICT WORKSPACE BOUNDARY (ZERO EXTERNAL TRAVERSAL):**
> - The agent is strictly forbidden from scanning parent directories, sibling directories, or other project folders outside the current active workspace.
> - All discoveries must be registered strictly in the project's Chronicle vault under `discoveries/` and reference code assets located within the active workspace (`cwd`) or designated artifact storage.

---

## When to Use Discoveries vs. Product Versions

| Dimension | Product Version Milestone (`/chronicle:update`, `/chronicle:complete`) | Discovery Catalog (`/chronicle:discover`) |
|---|---|---|
| **Purpose** | Sequential iteration of the core product or codebase | Preserving empirical breakthroughs, standalone algorithms, prototypes, or assets |
| **Tracking** | Strict chronological sequence ($V_1 \to V_2 \to \dots$) | Independent reference catalog accessible to any version |
| **Lifecycle** | In-progress, completed, skipped, reopened | Permanent reference asset with empirical verification |
| **Typical Content** | Core features, release milestones, refactors, bugfixes | Novel algorithms, optimization benchmarks, proofs, models, standalone scripts |

---

## Discovery Capture Protocol

### 1. Execute Discovery Registration
Run the helper to scaffold the discovery dossier and register it in `state.json` and `master_evolution.md`:

```bash
python "../../scripts/chronicle_helper.py" discover --title "<Discovery Title>" --asset-path "<primary_code_or_asset_path>" --summary "<one_line_summary>"
```
*(If targeting a specific project: append `--project <name>`)*

This command automatically:
1. Allocates a sequential ID (e.g. `001`, `002`).
2. Creates the dossier in the vault at `<vault>/projects/<project>/discoveries/<id>-<slug>.md`.
3. Appends a catalog entry into `master_evolution.md` under `## 6. Discoveries & Research Catalog`.
4. Updates `state.json`.

---

### 2. Populate the Discovery Dossier
Open and complete the generated discovery file in the vault. The dossier consists of 5 universal sections:

1. **Concrete Asset Locations:**
   - Absolute or workspace-relative path to the primary implementation or entrypoint.
   - Exact paths to any compiled binaries, artifacts, caches, serialized weights, or generated outputs (if applicable).
   - Concrete locations of benchmarks, test suites, or validation fixtures.

2. **Intuition, Philosophy & The "Why":**
   - The core bottleneck, problem, or exploratory curiosity that triggered this investigation.
   - The underlying hypothesis, mental model, or design principle.
   - Why this discovery is strategically or practically valuable to the project.

3. **Technical Anatomy & Mechanics:**
   - Deep explanation of the mechanism, algorithm, data structure, math, or architecture.
   - Critical constants, algorithmic parameters, flags, or environment dependencies.
   - Time/space complexity or performance characteristics.

4. **Empirical Proof & Validation:**
   - Tangible benchmark metrics, latency/throughput gains, error rates, or comparative results against a baseline.
   - Reproducible verification commands or test scripts with expected outputs.

5. **Architectural Integration Pathway:**
   - How a future production version could operationalize or merge this discovery into the core product.
   - Prerequisites, API contracts, or refactoring required before core adoption.

---

### 3. Verify Integrity
Run schema validation to verify that all dossiers and catalog entries remain structurally valid:

```bash
python "../../scripts/chronicle_helper.py" validate
```

---

## Output Confirmation Format

Upon recording a discovery, confirm to the user:
- **Discovery ID:** `DISCOVERY-XXX`
- **Title:** `[Title]`
- **Primary Asset Location:** `[Path]`
- **Breakthrough Summary:** `[Summary]`
- **Catalog Entry:** `master_evolution.md ## 6. Discoveries & Research Catalog updated`
- **Dossier:** `[Path to discoveries/XXX-slug.md]`
