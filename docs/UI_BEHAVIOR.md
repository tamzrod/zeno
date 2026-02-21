# ZENO -- UI Behavior Specification

## 1. Purpose

This document defines the behavior of the Zeno user interface.

Zeno is not a generic editor. Zeno is a controlled configuration
instrument.

The UI enforces structure, clarity, and determinism.

------------------------------------------------------------------------

## 2. Top-Level Layout

    File   Edit   Help                         Mode: CONFIG

    +--------------------+--------------------------------------+
    | Tree               | Tabs: [ Modify | Docs | Preview ]    |
    | (Structure)        |                                      |
    |                    | Right Workspace                      |
    |                    |                                      |
    +-----------------------------------------------------------+
    | Status: ✔ Ready                                          |
    +-----------------------------------------------------------+

------------------------------------------------------------------------

## 3. Modes

Zeno operates in two modes:

### 3.1 Schema Mode

-   Editing `.zs` schema files
-   Tree represents schema structure
-   Modify edits schema
-   Documentation shows schema metadata
-   Preview disabled or schema-only view

### 3.2 Config Mode

-   Requires loaded schema
-   Tree represents configuration structure
-   Modify edits config values
-   Documentation shows schema help
-   Preview generates runtime export

Mode must always be visible in the UI header.

------------------------------------------------------------------------

## 4. Left Panel -- Structure Tree

The tree is authoritative.

Rules: - Controlled entirely by schema - No arbitrary key insertion -
Right-click context menu is schema-driven - Add / Rename / Delete
allowed only if schema permits - Invalid nodes highlighted in red -
Parent nodes indicate child errors

The tree prevents structural mistakes.

------------------------------------------------------------------------

## 5. Right Panel Tabs

### 5.1 Modify Tab

Purpose: Mutate configuration safely.

Contains: - Field editor controls - Read button - Write button

Behavior: - No auto-apply - Write triggers validation - On validation
failure: - Reject mutation - Highlight errors - Update status line - On
success: - Update IR - Clear errors - Status: ✔ Write successful

Undo/Redo applies per Write action (atomic mutation).

------------------------------------------------------------------------

### 5.2 Documentation Tab

Purpose: Provide contextual help.

Behavior: - Read-only - Displays: - Field description - Intent notes -
Constraints - Export mapping notes - Driven entirely by schema metadata

Documentation tab never modifies state.

------------------------------------------------------------------------

### 5.3 Preview Tab

Purpose: Generate runtime configuration projection.

Contains: - Generate button - Runtime preview view

Behavior: - No live updating - Generate must be explicit - On validation
failure: - Preview remains unchanged - Errors highlighted - Status
updated - On success: - Preview refreshed - Status: ✔ Preview generated

------------------------------------------------------------------------

## 6. File Menu

    File
     ├── New Config
     ├── Open Config...
     ├── Save
     ├── Save As...
     ├── Close Config
     ├── ----------------
     ├── Load Schema...
     ├── Unload Schema
     ├── ----------------
     └── Exit

Rules: - Config editing requires loaded schema - Loading schema clears
current config - No implicit schema loading

------------------------------------------------------------------------

## 7. Edit Menu

    Edit
     ├── Undo
     ├── Redo
     ├── ----------------
     ├── Cut
     ├── Copy
     ├── Paste
     └── Delete

Rules: - Undo/Redo operates on Write-level mutations - Paste must
validate before applying - Invalid paste is rejected with error
highlight - Delete disabled if schema forbids removal

------------------------------------------------------------------------

## 8. Help Menu

    Help
     ├── Documentation
     ├── Schema Reference
     ├── Validation Rules
     └── About Zeno

Rules: - All help content local - No dependency on internet - No wizard
or tutorial overlays

------------------------------------------------------------------------

## 9. Status Line

Single-line feedback mechanism.

Examples:

✔ Ready\
✔ Write successful\
❌ Duplicate port 502\
Generating preview...

Rules: - No popup validation dialogs - Persistent until next state
change - Clear and concise messages only

------------------------------------------------------------------------

## 10. Error Visualization

When validation fails:

-   Field highlighted in red
-   Tree node marked with error indicator
-   Parent nodes show child error marker
-   Status line displays summary

Errors remain visible until corrected.

------------------------------------------------------------------------

## 11. Drag and Drop

Reordering via drag-and-drop is optional and must respect schema
constraints.

If implemented: - Must validate before committing reorder - Must not
violate uniqueness or structural rules

------------------------------------------------------------------------

## 12. Design Evolution Notes

Initial concept: - Basic tree + editor

Evolved design: - Two-mode system - Explicit Write / Generate
lifecycle - No live preview - Strict schema enforcement -
Highlight-based validation - Bottom status line instead of popups -
Atomic undo model (per Write)

UI behavior supports the core philosophy:

Make it hard for the user to make a mistake.
