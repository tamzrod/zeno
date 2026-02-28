# ZENO -- File Menu Specification

Version: 1.0\
Status: LOCKED

------------------------------------------------------------------------

## 1. Scope

This document defines the authoritative behavior of the **File** menu in
ZENO.

The File menu controls document lifecycle and schema context
transitions.

It must remain minimal, deterministic, and consistent with: -
Document-centric architecture - Explicit Write/Generate lifecycle -
Dirty state protection rules

------------------------------------------------------------------------

## 2. Menu Structure

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

No additional items are permitted unless formally documented.

There is NO: - Close - Unload Schema - Mode switch

------------------------------------------------------------------------

## 3. Startup State

On application launch:

-   No schema loaded
-   No document loaded
-   Save disabled
-   Save As disabled
-   Config operations blocked until schema is loaded

Title: `ZENO -- No Schema`

------------------------------------------------------------------------

## 4. Schema Handling

### 4.1 Load Schema...

Precondition: - May be executed at any time.

If a document is open:

-   If Dirty → show: Save / Discard / Cancel
-   If Clean → show: Continue / Cancel

On success: - Active document cleared - Undo history cleared - Preview
cleared - Dirty reset - Title updated - Schema path persisted

There is NO Unload Schema operation.

Schema persists across sessions.

------------------------------------------------------------------------

## 5. Document Lifecycle

### 5.1 New Config...

Precondition: - Schema must be loaded.

If document open: - Intercept Dirty state.

Behavior: - Create new deterministic config based on schema expansion
rules. - Arrays empty. - Scalars null. - Dirty = false. - Title updated
to include document name.

------------------------------------------------------------------------

### 5.2 Open Config...

Precondition: - Schema must be loaded.

If no schema: - Operation blocked.

If document open: - Intercept Dirty state.

On success: - Parse via adapter - Load IR - Run structural validation -
Highlight errors if present - Dirty = false

------------------------------------------------------------------------

### 5.3 Save

Enabled only when a document is active.

If first save: - Redirect to Save As.

Save does NOT trigger Generate.

------------------------------------------------------------------------

### 5.4 Save As...

Enabled only when a document is active.

Does not mutate schema. Does not trigger Generate.

------------------------------------------------------------------------

## 6. Config Wizard...

Precondition: - Schema must be loaded.

If document open: - Intercept Dirty state.

Behavior: - Guided configuration creation - Final commit must pass Write
validation - Ends in Clean state

Wizard must NOT bypass: - OperationProcessor - Write validation - Dirty
rules

------------------------------------------------------------------------

## 7. Exit

If Dirty: - Show Save / Discard / Cancel

If Clean: - Exit immediately

Schema path persisted automatically.

------------------------------------------------------------------------

## 8. Disabled States

When no document is active: - Save → disabled (greyed out) - Save As →
disabled (greyed out)

Preventive disabling is preferred over runtime errors.

------------------------------------------------------------------------

## 9. Design Principles

-   No silent state loss
-   No implicit mutation
-   Schema defines editing universe
-   Document transitions are explicit
-   Dirty state always protected

The File menu is minimal by design.

It reflects ZENO's philosophy:

Make it hard for the user to make a mistake.
