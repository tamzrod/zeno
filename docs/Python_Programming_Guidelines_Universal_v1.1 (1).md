# Python Programming Guidelines (Universal)

Version: 1.1 Status: LOCKED

------------------------------------------------------------------------

## 0. Purpose

This document defines mandatory programming workflow rules. These are
NOT stylistic suggestions. These are deterministic process constraints.

Violation of any rule is considered a process failure.

------------------------------------------------------------------------

# 1. Core Philosophy

## 1.1 Deterministic Workflow

All modifications must preserve continuity. No hidden assumptions. No
implicit reconstruction of files.

## 1.2 One Responsibility Per File

Each file must serve one clear responsibility. Large files signal
structural problems.

## 1.3 Explicit Over Implicit

Never rely on memory. Never rely on assumed structure. Always operate on
visible, provided state.

------------------------------------------------------------------------

# 2. Mandatory File Rules

## 2.1 Mandatory File Header (ABSOLUTE)

Every `.py` file MUST begin with:

    # relative/path/to/file.py

Rules: - Must be on line 1 - No blank line before it - No docstring
before it - Must match actual project structure

Violation = Structural failure.

------------------------------------------------------------------------

## 2.2 Full-File Replacement Rule (ABSOLUTE)

When modifying Python code:

-   Always output the complete file.
-   Never output snippet-only patches.
-   Never say "replace this section."
-   Never partially edit code.

If unsure about the current file state: → Ask for the full file before
modifying.

------------------------------------------------------------------------

## 2.3 No-Assumption Rule (ABSOLUTE)

If the current file content is not explicitly provided:

1.  Do NOT assume structure.
2.  Do NOT recreate from memory.
3.  Do NOT simplify for demo.
4.  Request one of the following:
    -   The full file content
    -   `tree /f` output
    -   Relevant module structure

Never modify based on inference.

Process integrity overrides speed.

------------------------------------------------------------------------

## 2.4 File Size Ceiling (HARD LIMIT)

No Python file may exceed:

    300 lines

If a file approaches 300 lines:

-   Split by responsibility
-   Extract widgets, helpers, or services
-   Maintain clean boundaries

Violation = Structural design issue.

------------------------------------------------------------------------

# 3. UI / Application Discipline

## 3.1 No Regression by Assumption

Never remove existing menu items, modes, or behavior unless explicitly
instructed.

## 3.2 Respect Existing Contracts

Before altering UI: - Review existing contract files - Confirm expected
structure - Do not overwrite working logic

------------------------------------------------------------------------

# 4. Documentation Rules

## 4.1 Markdown Must Be Downloadable

All `.md` documentation must be delivered as downloadable files. No
inline-only documentation when file output is required.

## 4.2 Standalone Mode Required

When generating documentation via pypandoc: - Use convert_text -
Include: extra_args=\['--standalone'\]

------------------------------------------------------------------------

# 5. Enforcement Checklist

Before delivering code, verify:

-   [ ] File header present and correct
-   [ ] Whole-file output (no snippets)
-   [ ] Under 300 lines
-   [ ] No structural assumptions made
-   [ ] Existing functionality preserved
-   [ ] Deterministic state maintained

If any box cannot be checked: → Stop and request clarification.

------------------------------------------------------------------------

# 6. Guiding Principle

Structure prevents chaos. Assumption creates repetition. Discipline
preserves velocity.

End of Document.
