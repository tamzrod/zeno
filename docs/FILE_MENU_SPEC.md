# ZENO -- File Menu Specification

Version: 2.0
Status: LOCKED (Single-Phase Lifecycle)

------------------------------------------------------------------------

## 1. Scope

This document defines the authoritative behavior of the **File** menu in
ZENO.

The File menu controls document lifecycle and schema context
transitions.

It must remain minimal, deterministic, and consistent with:
- Document-centric architecture
- Single-phase live validation lifecycle
- Invalid buffer and validation error protection rules

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

There is NO:
- Close
- Unload Schema
- Mode switch
- Export Config

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

Precondition:
- May be executed at any time.

If a document is open:

-   If invalid buffers exist → show: Save (disabled) / Discard / Cancel
-   If Clean → show: Continue / Cancel

On success:
- Active document cleared
- Undo history cleared
- Title updated
- Schema path persisted

There is NO Unload Schema operation.

Schema persists across sessions.

------------------------------------------------------------------------

## 5. Document Lifecycle

### 5.1 New Config...

Precondition:
- Schema must be loaded.

If document open:
- Intercept invalid buffers and validation state.

Behavior:
- Create new deterministic config based on schema expansion rules.
- Arrays empty.
- Scalars null.
- Title updated to include document name.

------------------------------------------------------------------------

### 5.2 Open Config...

Precondition:
- Schema must be loaded.

If no schema:
- Operation blocked.

If document open:
- Intercept invalid buffers and validation state.

On success:
- Parse via adapter
- Load IR
- Run structural validation
- Highlight errors if present

------------------------------------------------------------------------

### 5.3 Save

Enabled only when:
- A document is active
- No invalid buffers exist
- No validation errors exist

If first save:
- Redirect to Save As.

Save serializes IR directly via adapter.

------------------------------------------------------------------------

### 5.4 Save As...

Enabled only when:
- A document is active
- No invalid buffers exist
- No validation errors exist

Save serializes IR directly via adapter.

------------------------------------------------------------------------

## 6. Config Wizard...

Precondition:
- Schema must be loaded.

If document open:
- Intercept invalid buffers and validation state.

Behavior:
- Guided configuration creation
- Final commit must pass live validation
- Ends in valid state

Wizard must NOT bypass:
- OperationProcessor
- Live validation
- IR valid-only rule

------------------------------------------------------------------------

## 7. Exit

If invalid buffers exist:
- Show Save (disabled) / Discard / Cancel

If Clean:
- Exit immediately

Schema path persisted automatically.

------------------------------------------------------------------------

## 8. Disabled States

When no document is active:
- Save → disabled (greyed out)
- Save As → disabled (greyed out)

When invalid buffers or validation errors exist:
- Save → disabled (greyed out)
- Save As → disabled (greyed out)

Preventive disabling is preferred over runtime errors.

------------------------------------------------------------------------

## 9. Design Principles

-   No silent state loss
-   No implicit mutation
-   Schema defines editing universe
-   Document transitions are explicit
-   Invalid buffers and validation errors always block Save
-   IR must never contain invalid state

The File menu is minimal by design.

It reflects ZENO's philosophy:

Make it hard for the user to make a mistake.

