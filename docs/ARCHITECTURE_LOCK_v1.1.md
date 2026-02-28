# ARCHITECTURE_LOCK.md

Version: 1.1 Status: LOCKED (unless explicitly revised)

This document consolidates the currently-authoritative architecture and
UI contracts for ZENO into a single master reference.

------------------------------------------------------------------------

## 0. Core Identity

ZENO is a schema-driven structured document editor.

-   ZENO edits IR, never raw text.
-   Adapters translate between text formats and IR.
-   The schema defines allowed structure, not runtime behavior.
-   The UI derives editing capabilities strictly from schema
    definitions.

Primary product goal:

> Make it hard for the user to make a mistake.

------------------------------------------------------------------------

## 1. Canonical Layers

(Same as previous lock content --- unchanged core layers)

------------------------------------------------------------------------

## 7. UI Surface Contract (LOCKED)

### 7.4 Title Bar

Reflects Active Schema, optionally Active Document.

Primary:

    ZENO -- <ActiveSchemaName>

Extended:

    ZENO -- <ActiveSchemaName> -- <ActiveDocumentName>

Rules:

-   Title changes only on schema load and document open.
-   Title does NOT change during Edit, Write, Generate, or Export.
-   No mode indicator appended.

------------------------------------------------------------------------

## 8. Schema-Defined Identity (LOCKED)

Schema may define:

``` yaml
zeno_schema: 1.0
application: MMA
version: 2.0
icon: icons/mma.png
```

Behavior:

-   Title uses schema metadata when available; fallback to filename.
-   Icon resolved relative to schema directory.
-   Missing icon file must not crash; fallback to default icon.
-   No mode indicator behavior allowed.

------------------------------------------------------------------------

All other sections of the Architecture Lock remain unchanged and
authoritative.

End of Document.
