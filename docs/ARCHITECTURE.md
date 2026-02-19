# ZENO -- Architecture Document

Version: v0.1 (Pre-Implementation Lock)

------------------------------------------------------------------------

# 1. Purpose

Zeno is a schema-driven structured text editor.

It is a desktop engineering tool used to: - Edit structured
configuration files - Enforce schema rules - Prevent invalid
configurations by design

Zeno is NOT: - A runtime engine - A config executor - A format-specific
editor - A domain-specific MMA tool

------------------------------------------------------------------------

# 2. Core Philosophy

Core is dumb\
Schema is smart\
Adapters translate formats\
UI renders based on schema

Strict separation of concerns is mandatory.

------------------------------------------------------------------------

# 3. High-Level Architecture

UI Layer\
↓\
Schema Layer\
↓\
Core Engine (IR + Validation)\
↓\
Adapters\
↓\
Text Formats (YAML, JSON, INI, etc.)

Each layer has fixed responsibilities and may not leak into others.

------------------------------------------------------------------------

# 4. Layer Responsibilities

## 4.1 UI Layer

Responsible for: - Rendering tree view - Rendering inspector view -
Triggering user operations - Displaying validation feedback

UI must NEVER: - Interpret YAML/JSON - Contain domain logic - Contain
hardcoded business rules - Modify IR directly

All edits must pass through schema-validated operations.

------------------------------------------------------------------------

## 4.2 Schema Layer

Responsible for: - Defining structure - Defining node types - Defining
constraints - Defining cardinality rules - Defining conditional
visibility - Defining validation rules - Defining editor behavior

Schema drives: - Tree rendering - Inspector rendering - Add/remove
permissions - Required rules - Validation outcomes

Schema must be declarative.

------------------------------------------------------------------------

## 4.3 Core Engine

Contains: - Intermediate Representation (IR) - Validation Engine -
Operation Processor

Core responsibilities: - Store document state in IR - Apply validated
operations - Maintain revision state - Trigger validation - Provide
change events

Core must be: - Format-agnostic - Domain-agnostic

Core must not know YAML or MMA.

------------------------------------------------------------------------

## 4.4 Adapters

Adapters translate:

Text format ⇄ IR

Initial adapter: - YAML

Future adapters: - JSON - INI - NGINX - Other structured formats

Adapters must: - Parse text into IR - Serialize IR into text - Preserve
data fidelity - Avoid validation logic

Adapters must never inject schema rules.

------------------------------------------------------------------------

## 4.5 Plugins (Future)

Plugins may extend: - Custom validators - Domain-specific validation
rules

Plugins operate at validation level only. They must not bypass core
contracts.

------------------------------------------------------------------------

# 5. Core Principle

Zeno does NOT understand YAML.

Zeno understands only:

Intermediate Representation (IR)

Everything must pass through IR. No layer may bypass IR.

------------------------------------------------------------------------

# 6. Data Flow

## Open File

Text\
→ Adapter parses\
→ IR created\
→ Validation executed\
→ UI rendered

## Edit Document

User action\
→ Operation proposed\
→ Schema validation\
→ Operation applied to IR\
→ Validation re-run\
→ UI updated

## Save File

IR\
→ Validation check\
→ Adapter serializes\
→ Text output

------------------------------------------------------------------------

# 7. Strict Invariants

1.  UI never modifies IR directly.
2.  Schema defines behavior.
3.  Core does not know file format.
4.  Adapters do not validate.
5.  Validation blocks illegal state.
6.  Domain logic must exist only inside schema.
7.  Zeno remains generic.

------------------------------------------------------------------------

# 8. Extensibility Model

Zeno must allow: - New schemas - New adapters - New validators - New
schema-driven UI behaviors

Without modifying core logic.

------------------------------------------------------------------------

# 9. Pre-Implementation Discipline

Before coding begins: - Architecture must be locked. - IR must be
formally defined. - Schema specification must be defined.

No implementation starts without contract lock.

------------------------------------------------------------------------

END OF ARCHITECTURE.md v0.1
