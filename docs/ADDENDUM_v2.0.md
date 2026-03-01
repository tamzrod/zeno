# ZENO -- ADDENDUM (Schema-Defined Identity)

Version: 2.0\
Status: ALIGNED WITH DOCUMENT-CENTRIC ARCHITECTURE

------------------------------------------------------------------------

## Purpose

This addendum documents the introduction of schema-defined identity
features.

ZENO is a schema-hosted platform. Each loaded schema may define its own:

-   Application name
-   Version
-   Window title representation
-   Icon (optional)

This allows ZENO to visually adapt per domain without introducing
mode-based behavior.

------------------------------------------------------------------------

## Schema Header Extension

A `.zs` file may define:

``` yaml
zeno_schema: 1.0
application: MMA
version: 2.0
icon: icons/mma.png
```

### Fields

### application (required in identity context)

Human-readable name of the configuration domain.

Examples: - MMA - Grafana - Telegraf - NGINX

### version (optional)

Schema metadata for identity/version tracking.

May be used by documentation surfaces, but title bar behavior remains
governed by Architecture Lock.

### icon (optional)

Relative path to icon file. Resolved relative to schema file location.

------------------------------------------------------------------------

## Window Title Behavior

When schema is loaded:

Primary format:

    ZENO -- <Application>

If a document is open:

    ZENO -- <Application> -- <DocumentName>

If no schema loaded:

    ZENO -- No Schema

Rules:

-   Title changes only on schema load or document open.
-   Title does NOT change during Edit, Write, Generate, or Export.
-   No mode indicator is ever appended.
-   No runtime guessing of identity fields.

------------------------------------------------------------------------

## Icon Behavior

If `icon` is defined:

1.  Resolve relative to schema file directory.
2.  If file exists → set window icon.
3.  If file missing → fallback to default ZENO icon.
4.  Application must never crash if icon fails to load.

If `icon` not defined:

Use default ZENO icon.

------------------------------------------------------------------------

## Design Principles

-   Identity is schema-driven.
-   UI engine remains neutral.
-   No hardcoded domain branding.
-   Safe fallback behavior required.
-   No runtime guessing.
-   No theming or accent-color injection.

------------------------------------------------------------------------

## Deferred Features (Explicitly Not Implemented)

-   Accent color
-   Theme customization
-   Layout hints
-   Default tab selection
-   Custom toolbar definitions

These are intentionally deferred to preserve architectural stability.

------------------------------------------------------------------------

## Architectural Impact

This confirms ZENO as:

A reusable schema-driven configuration platform.

Not a single-domain tool.

Each schema defines its configuration universe and visual identity
without introducing modes.

------------------------------------------------------------------------

End of Document.
