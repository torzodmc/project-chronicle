# Project Chronicle Guidelines & Evolutionary Invariants

When working in a repository tracked by Project Chronicle, the agent must adhere to the following universal invariants:

## 1. Respect the Graveyard of Traps
- Before proposing any major architectural changes, refactors, dependencies, or algorithmic approaches, consult the project's `graveyard_of_traps.md` or active chronicle dossier.
- **Rule:** Never re-introduce an approach, pattern, or dependency that has already been documented as a failure trap.

## 2. Living Philosophy & Immutable Axioms
- The project's foundational intent, mental models, and non-negotiable living axioms are recorded in `master_evolution.md`.
- Code changes must align with these axioms. Code alone cannot convey foundational human intent; preserve the human creator's core philosophy across all iterations.

## 3. Epistemic Diff Protocol
- When an assumption or architectural thesis is proven wrong by an empirical encounter (a bug, benchmark failure, test breakdown, or user correction):
  - Do not silently rewrite history or pretend the old belief was never held.
  - Formulate the transition as an **Epistemic Diff**:
    - **Old Assumption:** What was previously believed to be true.
    - **The Collision Event:** The exact empirical evidence or user pushback that shattered the assumption.
    - **New Reality & Philosophy:** The revised mental model and operating principle.

## 4. Decoupled Breakthroughs & Discoveries
- If an independent mathematical finding, reusable tool, trained model, or standalone asset is created outside the scope of a sequential version milestone, do not force it into a version dossier.
- Record it permanently in the research catalog using `/chronicle:discover`.

## 5. Strict Workspace Isolation
- Zero external traversal: The agent must never scan parent directories, sibling directories, or external workspaces to infer state or configuration.
