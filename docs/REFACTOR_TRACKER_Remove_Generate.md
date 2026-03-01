# ZENO Refactor Tracker – Remove Generate Phase
Status: LOCKED SCOPE
Intent: Simplification (Not Upgrade)

------------------------------------------------------------
PRIMARY GOAL
------------------------------------------------------------

Make it harder for users to commit a mistake.

We are collapsing the lifecycle from:

Edit → Write → Generate → Export

to:

Edit → Live Validate → Commit Valid → Save

There is no Preview tab.
There is no Generate phase.
There is no Generated state.

IR must never contain invalid state.

------------------------------------------------------------
ARCHITECTURAL INVARIANTS (DO NOT CHANGE)
------------------------------------------------------------

- IR remains format-agnostic and schema-agnostic.
- UI remains schema-driven.
- No raw YAML editing.
- No transformation layer.
- No multi-format export.
- No schema redesign.
- No mode system.

------------------------------------------------------------
NEW OPERATIONAL MODEL
------------------------------------------------------------

1. Editing occurs in buffer.
2. Field-level validation runs per keystroke.
3. IR updates only when field becomes valid.
4. IR must never contain invalid state.
5. Save serializes IR directly.
6. Save disabled if any validation error exists.

There is no Generate step.
There is no Preview surface.

------------------------------------------------------------
DOCUMENTATION TASK GROUPS
------------------------------------------------------------

### GROUP A – Operation Model Specification

Files:
- OPERATION_MODEL_v2.0.md

Required Changes:
- Remove Generate phase.
- Remove Generated state.
- Remove Generate lifecycle section.
- Define IR as always-valid.
- Define Save as direct serialization.
- Collapse lifecycle to single-phase validation.

Rules:
- Full-file rewrite.
- No new conceptual features.
- Preserve deterministic philosophy.

Status:
[ ] Not Started
[ ] In Progress
[ ] Done


### GROUP B – UI Architecture

Files:
- ZENO_UI_Architecture_v2.3.md

Required Changes:
- Remove Preview tab.
- Remove Generate button references.
- Update tab contract to:
  - Model
  - Docs
- Define Model as structured projection surface.
- Remove Generate location clarification section.

Rules:
- Full-file rewrite.
- No UI upgrades beyond scope.
- No new tab additions.

Status:
[ ] Not Started
[ ] In Progress
[ ] Done


### GROUP C – Validation Engine Specification

Files:
- VALIDATION_ENGINE.md

Required Changes:
- Remove Generate-phase validation.
- Clarify that all validation occurs before IR mutation.
- Define IR as incapable of holding invalid state.
- Remove references to Preview blocking.

Rules:
- Preserve structured error model.
- No UI coupling.
- No new validator types.

Status:
[ ] Not Started
[ ] In Progress
[ ] Done


### GROUP D – UI Behavior Specification

Files:
- UI_BEHAVIOR_v2.3.md

Required Changes:
- Remove Preview behavior.
- Remove Generate behavior.
- Define:
  - Live validation per keystroke.
  - Inline floating hint behavior.
  - Save disabled on error.
  - No explicit Write button (if removed).

Rules:
- Must remain schema-driven.
- No raw text editing allowed.
- No implicit structural mutation.

Status:
[ ] Not Started
[ ] In Progress
[ ] Done


### GROUP E – File Menu Specification

Files:
- FILE_MENU_SPEC.md

Required Changes:
- Remove Generate dependencies.
- Ensure Save does not require prior Generate.
- Ensure Save disabled if validation errors exist.

Rules:
- Do not add new menu items.
- Preserve minimalism.

Status:
[ ] Not Started
[ ] In Progress
[ ] Done

------------------------------------------------------------
EXECUTION ORDER
------------------------------------------------------------

1. Complete Group A (Operation Model) first.
2. Then Groups B–E may proceed in parallel.
3. No code changes until all documentation groups are Done.
4. Architecture must remain internally consistent before code refactor begins.

------------------------------------------------------------
STRICT PROHIBITIONS
------------------------------------------------------------

- Do not reintroduce Generate implicitly.
- Do not invent transformation layer.
- Do not add multi-format abstraction.
- Do not modify IR model.
- Do not exceed file size rules.

End of Tracker.

------------------------------------------------------------
