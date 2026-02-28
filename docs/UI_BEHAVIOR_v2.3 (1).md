# ZENO -- UI Behavior Specification

**Status: Updated (Aligned with Architecture Lock and UI Architecture
v2.3)**

------------------------------------------------------------------------

## 1. Purpose

This document defines the behavior of the Zeno user interface.

Zeno is a controlled configuration instrument.

Zeno is document-centric.

There are no manual modes.

UI behavior is determined entirely by:

-   Active Schema
-   Active Document (optional)

------------------------------------------------------------------------

## 2. Top-Level Layout

    File   Edit   Help

    +--------------------+--------------------------------------+
    | Tree               | Tabs: [ Model | Docs | Preview ]     |
    | (Structure)        |                                      |
    |                    | Right Workspace                      |
    |                    |                                      |
    +-----------------------------------------------------------+
    | Status: ✔ Ready                                          |
    +-----------------------------------------------------------+

------------------------------------------------------------------------

## 3. Document-Centric Model

ZENO operates without manual mode switching.

Definitions:

-   Active Schema: The schema currently governing structure and
    validation.
-   Active Document: The structured document currently being edited
    (optional).

Rules:

-   Behavior is governed entirely by the Active Schema.
-   A schema itself is also a structured document.
-   No UI layout or logic may depend on file extension.
-   There is no Schema Mode or Config Mode.

------------------------------------------------------------------------

## 4. Left Panel -- Structure Tree

The tree is authoritative.

Rules:

-   Fully derived from IR.
-   Structure allowed strictly by Active Schema.
-   No arbitrary key insertion.
-   Context menu is schema-driven.
-   Add / Remove / Reorder allowed only if schema permits.
-   Root cannot be removed.
-   Invalid nodes highlighted in red.
-   Parent nodes indicate child errors.

The tree prevents structural mistakes.

------------------------------------------------------------------------

## 5. Right Panel Tabs

Exactly three tabs:

1.  Model
2.  Docs
3.  Preview

No additional tabs permitted.

------------------------------------------------------------------------

### 5.1 Model Tab

Purpose: Safely mutate the Active Document model (IR).

Contains:

-   Field editor controls
-   Write button

Rules:

-   Editing does not auto-apply.
-   Write is the ONLY operation that mutates IR.
-   Dirty state must be tracked.
-   Generate and Export are disabled while Dirty is true.

On Write:

-   Runs Write-phase validation.
-   On success:
    -   IR updated
    -   Dirty cleared
    -   Status: ✔ Write successful
-   On failure:
    -   IR unchanged
    -   Errors highlighted
    -   Status updated

Undo/Redo operates on field edits only. Undo does not implicitly trigger
Write or Generate.

------------------------------------------------------------------------

### 5.2 Docs Tab

Purpose: Provide contextual help.

Rules:

-   Read-only.
-   Displays schema-derived documentation.
-   May include:
    -   Field description
    -   Intent notes
    -   Constraints
    -   Export notes

Docs tab never mutates state.

------------------------------------------------------------------------

### 5.3 Preview Tab

Purpose: Display full generated projection of the Active Document.

Contains:

-   Generate button
-   Export Config button
-   Read-only preview view

Rules:

-   Generate must be explicit.
-   Generate must NOT mutate IR.
-   Export must NOT call Generate.
-   Export exports last successfully generated output only.
-   Export disabled until at least one successful Generate.
-   Generate and Export disabled while Dirty = true.

On Generate:

-   Runs Generate-phase validation.
-   On success:
    -   Preview updated
    -   Status: ✔ Preview generated
-   On failure:
    -   Preview unchanged
    -   Errors highlighted
    -   Status updated

------------------------------------------------------------------------

## 6. File Menu

The File menu SHALL contain exactly:

    File
     ├── New Config...
     ├── Open Config...
     ├── Save
     ├── Save As...
     ├── ----------------
     ├── Config Wizard...
     ├── Load Schema...
     └── Exit

Rules:

-   No Close operation.
-   No Unload Schema operation.
-   No Mode switch.
-   No additional items unless formally documented.
-   Dirty state must be intercepted before destructive transitions.

------------------------------------------------------------------------

## 7. Edit Menu

    Edit
     ├── Undo
     └── Redo

Rules:

-   Applies only to Model tab edits.
-   Must not trigger Write.
-   Must not trigger Generate.

------------------------------------------------------------------------

## 8. Help Menu

    Help
     ├── Documentation
     ├── Validation Rules
     └── About

Rules:

-   All help content local.
-   No tutorial overlays.
-   No runtime dependency on internet.

------------------------------------------------------------------------

## 9. Status Line

Single-line feedback mechanism.

Examples:

✔ Ready\
✔ Write successful\
❌ Duplicate port 502\
Generating preview...

Rules:

-   No popup validation dialogs.
-   Persistent until next state change.
-   Clear and concise only.

------------------------------------------------------------------------

## 10. Error Visualization

When validation fails:

-   Field highlighted in red.
-   Tree node marked with error indicator.
-   Parent nodes indicate child error.
-   Status line displays summary.

Errors persist until corrected.

------------------------------------------------------------------------

## 11. Drag and Drop (Optional)

If implemented:

-   Must respect schema constraints.
-   Must validate before committing reorder.
-   Must not violate uniqueness or structural rules.

------------------------------------------------------------------------

## 12. Alignment Statement

This UI behavior is fully aligned with:

-   Architecture Lock
-   UI Architecture v2.3
-   File Menu Specification
-   Two-phase Validation Model

ZENO is document-centric.

Structure is schema-governed.

Mutation and projection are strictly separated.
