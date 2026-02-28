# ZENO -- UI Architecture

Version: 2.3\
Status: LOCKED (Supersedes v2.2)

------------------------------------------------------------------------

# 0. Scope

This document defines the authoritative UI surface contract for ZENO.

It supersedes all prior UI-related definitions including: - Any
Mode-based UI model - Any definition including Close or Unload Schema in
File menu - Ambiguous Generate location - Implicit Export behavior -
Unlocked title bar behavior

Core architecture layers (Schema, IR, Store, Validators,
OperationProcessor) remain unchanged.

------------------------------------------------------------------------

# 1. Document-Centric Architecture (LOCKED)

ZENO is document-centric.

There is no manual Mode switch.

The UI state is defined by:

-   Active Schema
-   Active Document (optional)

Important:

-   A Schema is also a structured document.
-   ZENO may edit schemas via a meta-schema.
-   Behavior is governed entirely by the Active Schema.
-   No UI behavior may depend on file extension.

Definitions:

Active Schema: The schema currently loaded and used for rendering and
validation.

Active Document: The structured document currently being edited
(configuration file or schema file).

------------------------------------------------------------------------

# 2. Right Workspace Layout (LOCKED)

The right workspace SHALL contain exactly three tabs:

1.  Model
2.  Docs
3.  Preview

No additional tabs are permitted unless formally documented.

------------------------------------------------------------------------

# 3. Tab Responsibilities

## 3.1 Model Tab

Purpose: Schema-governed editing of the Active Document model (IR).

Rules:

-   Editing allowed only where Active Schema permits.
-   Write is the ONLY operation that mutates IR.
-   Dirty state MUST be tracked.
-   Generate MUST be disabled while Dirty is true.
-   No free-text editing of full document.

Required Control: - Write

Optional: - Node-level read-only preview (must not replace full Preview
tab).

------------------------------------------------------------------------

## 3.2 Docs Tab

Purpose: Display documentation and field help from the Active Schema.

Rules:

-   Read-only.
-   Derived strictly from schema metadata.
-   Must not mutate IR.

------------------------------------------------------------------------

## 3.3 Preview Tab

Purpose: Display full generated output (whole-document projection).

Required Controls:

-   Generate
-   Export Config

Rules:

-   Preview is read-only.
-   Generate must NOT mutate IR.
-   If Generate fails, preview remains unchanged.
-   Export must NOT implicitly call Generate.
-   Export exports last successfully generated output only.
-   Export must be disabled until at least one successful Generate.
-   Generate and Export must be disabled while Dirty = true.

------------------------------------------------------------------------

# 4. Operation Lifecycle (LOCKED)

Canonical lifecycle:

Edit → Write → Generate → Export

Edit: User modifies fields in Model tab (Dirty = true).

Write: - Runs Write-phase validation. - On success: commits to IR and
clears Dirty. - On failure: IR unchanged.

Generate: - Runs Generate-phase validation. - On success: updates
Preview. - On failure: Preview unchanged.

Export: - Writes currently displayed Preview output to disk. - Does not
mutate IR. - Does not trigger Generate.

------------------------------------------------------------------------

# 5. Dirty State Rules (ABSOLUTE)

If Dirty = true:

-   Generate is disabled.
-   Export is disabled.
-   Loading another schema or document must not silently discard
    changes.

Dirty clears only after successful Write.

------------------------------------------------------------------------

# 6. Menu Bar Structure (LOCKED)

Top-level menus SHALL be:

1.  File
2.  Edit
3.  Help

A Mode menu SHALL NOT exist.

------------------------------------------------------------------------

## 6.1 File Menu (Authoritative)

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

There is NO:

-   Close
-   Unload Schema
-   Mode switch

All transitions must respect Dirty state interception rules.

------------------------------------------------------------------------

## 6.2 Edit Menu

-   Undo
-   Redo

Undo/Redo applies to Model tab field edits only. It must not trigger
Write or Generate implicitly.

------------------------------------------------------------------------

## 6.3 Help Menu

-   About
-   Documentation (optional local links)

No runtime dependency on internet required.

------------------------------------------------------------------------

# 7. Title Bar Contract (LOCKED)

The title bar SHALL reflect the Active Schema.

Primary format:

ZENO -- `<ActiveSchemaName>`{=html}

Extended format (if document loaded):

ZENO -- `<ActiveSchemaName>`{=html} -- `<ActiveDocumentName>`{=html}

Rules:

-   Title changes when schema loads.
-   Title changes when document opens.
-   Title does NOT change during Edit, Write, Generate, or Export.
-   Schema name should come from schema metadata (application field).
-   If metadata not available, fallback to schema filename.
-   No mode indicator appended.

------------------------------------------------------------------------

# 8. Generate Location Clarification (LOCKED)

Full-document Generate belongs exclusively to the Preview tab.

Model tab may include node-level read-only preview, but full projection
must occur only in Preview tab.

------------------------------------------------------------------------

# 9. Enforcement Checklist

Before implementation:

-   Tabs match: Model / Docs / Preview
-   No Mode menu exists
-   File/Edit/Help menus present
-   File menu matches authoritative structure exactly
-   Dirty gating rules enforced
-   Generate and Export separation enforced
-   Title bar follows contract
-   No IR mutation during Generate or Export

------------------------------------------------------------------------

End of Document.
