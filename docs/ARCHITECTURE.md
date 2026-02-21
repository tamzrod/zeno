# ZENO -- Architecture Document

## 1. Purpose

Zeno is a schema-driven configuration instrument.

Its purpose is:

> Make it hard for the user to make a mistake.

Zeno is not a text editor.\
Zeno is not a YAML playground.\
Zeno is a controlled configuration environment.

------------------------------------------------------------------------

## 2. Core Philosophy

1.  Structure is authoritative.
2.  Schema defines what is allowed.
3.  Core engine is dumb.
4.  Schema is smart.
5.  UI never enforces domain rules directly.
6.  No live magic processing.
7.  No hidden defaults.
8.  Explicit actions only.
9.  Deterministic validation.
10. Errors are highlighted, not shouted.

------------------------------------------------------------------------

## 3. High-Level Architecture

    +--------------------+
    |        UI          |
    |  (Desktop / Web)   |
    +--------------------+
               |
               v
    +--------------------+
    |        Core        |
    |  IR + Schema +     |
    |  Validator +       |
    |  Exporter          |
    +--------------------+

Core is UI-agnostic.

Future: - Desktop UI (PySide6) - Web UI (separate frontend)

Both must call the same core logic.

------------------------------------------------------------------------

## 4. Two Operating Modes

### 4.1 Schema Mode

Purpose: Edit `.zs` schema files.

Characteristics: - Tree represents schema structure. - Modify tab edits
schema. - Documentation tab describes schema meta. - Preview is disabled
or schema preview only.

------------------------------------------------------------------------

### 4.2 Config Mode

Purpose: Edit configuration constrained by a loaded schema.

Characteristics: - Schema must be loaded first. - Tree represents
configuration structure. - Modify tab edits config values. -
Documentation tab shows schema-based help. - Preview tab generates
runtime export.

Schema is mandatory in Config Mode.

------------------------------------------------------------------------

## 5. UI Layout

    File   Edit   Help                          Mode: CONFIG

    +--------------------+--------------------------------------+
    | Tree               | Tabs: [ Modify | Docs | Preview ]    |
    | (Structure)        |                                      |
    |                    | Right Workspace                      |
    |                    |                                      |
    +-----------------------------------------------------------+
    | Status: ✔ Ready                                          |
    +-----------------------------------------------------------+

------------------------------------------------------------------------

## 6. Left Panel -- Structure Authority

-   Schema-controlled tree.
-   No arbitrary key creation.
-   Right-click context menu depends on node type.
-   Add / Rename / Delete only if allowed by schema.
-   Errors visually highlighted on nodes.

Tree enforces structure.

------------------------------------------------------------------------

## 7. Right Panel -- Context Tabs

### 7.1 Modify Tab

Purpose: Mutate IR safely.

Contains: - Editable fields - Read button - Write button

Rules: - No auto-apply. - Write performs validation. - Reject invalid
state mutation.

------------------------------------------------------------------------

### 7.2 Documentation Tab

Purpose: Knowledge layer.

Displays: - Field description - Intent notes - Export mapping notes -
Constraints

Read-only. Schema-driven.

------------------------------------------------------------------------

### 7.3 Preview Tab

Purpose: Runtime projection.

Contains: - Generate button - Export preview

Rules: - No live updating. - Generate must be explicit. - Generate
performs full validation. - Preview updates only on success.

------------------------------------------------------------------------

## 8. Status Line

Single-line status at bottom.

Examples:

✔ Ready\
✔ Write successful\
❌ Duplicate port 502\
Generating preview...

No validation popups. No modal interruptions.

------------------------------------------------------------------------

## 9. Validation Layers

### 9.1 Write Phase Validation

Triggered by Modify → Write.

Validates: - Structural integrity - Required presence - Type
correctness - `unique_by` rules (array-local)

Purpose: Protect IR integrity.

------------------------------------------------------------------------

### 9.2 Generate Phase Validation

Triggered by Preview → Generate.

Validates: - Structural integrity (re-check) - Semantic rules -
Cross-field constraints - Runtime export constraints

Purpose: Protect runtime correctness.

------------------------------------------------------------------------

## 10. Schema Design Principles

Schema is strict.

-   Unknown keywords → error.
-   `unique_by` allowed only on arrays.
-   `unique_by` applies within array scope.
-   Absence of `state_sealing` = disabled.
-   Export mappings documented in comments only.
-   No hidden behavior in schema grammar.

Schema describes intent. Exporter maps intent to runtime structure.

------------------------------------------------------------------------

## 11. Error Handling Model

-   Errors return path + message.
-   UI highlights nodes.
-   Status line displays summary.
-   No popup validation errors.
-   Preview remains unchanged on failure.

------------------------------------------------------------------------

## 12. Operation Lifecycle

User Flow:

    Edit → Write → (validate structure + uniqueness)
    → Generate → (validate semantic + export)

Mutation and projection are separated.

Write protects the model.\
Generate protects deployment.

------------------------------------------------------------------------

## 13. Design Evolution Notes

Initial Direction: - Structural schema loader - Basic validator

Evolved To: - Strict schema grammar - unique_by enforcement - Two-phase
validation - No live preview - Explicit Read / Write / Generate -
Status-line based feedback - Two-mode system (Schema / Config)

Core philosophy remained constant: Make it hard for the user to make a
mistake.
