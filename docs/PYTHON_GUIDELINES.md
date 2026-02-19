# Python Programming Guidelines --- Universal & Reusable Edition

**Status:** Authoritative\
**Target Version:** Python 3.11+

This document defines mandatory engineering rules for writing clean,
durable, architecture-safe Python systems.

These rules are:

-   Project-agnostic\
-   Framework-neutral\
-   AI-safe\
-   Architecture-preserving\
-   Reusable across desktop apps, services, CLI tools, embedded systems,
    and libraries

If code violates this document, it is considered incorrect --- even if
it runs.

------------------------------------------------------------------------

# 1. Core Philosophy

## 1.1 Boring Is Correct

Correct Python code is:

-   Explicit\
-   Predictable\
-   Readable\
-   Easy to delete\
-   Easy to replace

If code looks clever, magical, dynamic, or overly abstract --- it is
probably wrong.

Prefer:

-   Clear control flow\
-   Direct data structures\
-   Simple classes\
-   Obvious naming

Avoid:

-   Hidden side effects\
-   Implicit behavior\
-   Metaprogramming unless strictly necessary\
-   "Smart" shortcuts that reduce clarity

------------------------------------------------------------------------

## 1.2 One Responsibility per Unit

-   One file → One responsibility\
-   One module → One domain\
-   One class → One role\
-   One function → One clear action

If a function requires heavy explanation, it must be split.

Large files signal design problems.

------------------------------------------------------------------------

## 1.3 Explicit Over Implicit

Python supports dynamic behavior. That does not mean you should use it.

Avoid:

-   Runtime attribute injection\
-   Dynamic mutation of class definitions\
-   Implicit state changes\
-   Side-effect-based APIs

Prefer:

-   Clear arguments\
-   Clear return values\
-   Immutable data when possible

------------------------------------------------------------------------

# 2. Structural Rules

## 2.1 Mandatory File Header

Every `.py` file must begin with its full relative path:

    # internal/core/store.py

Rules:

-   No blank lines before this line\
-   No banner comments\
-   No docstring before the path comment

This enforces clarity of ownership and location.

------------------------------------------------------------------------

## 2.2 Full-File Replacement Rule

When modifying files (especially in collaborative or AI-assisted
workflows):

-   Always replace the entire file\
-   Never apply partial patches\
-   Never provide snippet-only changes

Workflow:

1.  Open file\
2.  Select all\
3.  Replace\
4.  Save

Partial edits cause architectural drift.

------------------------------------------------------------------------

## 2.3 No Empty Files

Empty modules are invalid.

If a file has no responsibility, delete it.

------------------------------------------------------------------------

# 3. Dependency Discipline

## 3.1 No Circular Imports

Circular imports indicate broken boundaries.

Refactor the design --- do not workaround with local imports.

------------------------------------------------------------------------

## 3.2 No Hidden Global State

Avoid:

-   Mutable module-level variables\
-   Cross-module state mutation\
-   Hidden singletons

If shared state is necessary:

-   Make it explicit\
-   Inject it\
-   Control its lifecycle

------------------------------------------------------------------------

## 3.3 Layer Boundaries Must Be Clear

Core logic must not depend on:

-   Frameworks (FastAPI, Flask, PySide, etc.)\
-   Databases\
-   YAML/JSON libraries\
-   Network layers

Adapters translate.\
Core executes.\
Policy decides.

Never mix responsibilities.

------------------------------------------------------------------------

# 4. Function & Class Rules

## 4.1 Type Hints Are Mandatory

All public functions must use type hints.

    def apply_operation(op: Operation) -> None:
        ...

Untyped public interfaces are not allowed.

------------------------------------------------------------------------

## 4.2 Small Functions Win

A function should:

-   Do one thing\
-   Be understandable in one read\
-   Avoid deep nesting

If nesting exceeds 2--3 levels, refactor.

------------------------------------------------------------------------

## 4.3 No Silent Failure

Never write:

    except Exception:
        pass

Errors must be:

-   Intentional\
-   Typed\
-   Explicit

If an error is ignored, document why.

------------------------------------------------------------------------

## 4.4 No Magic Behavior

Avoid:

-   Overusing **getattr**\
-   Overriding dunder methods unnecessarily\
-   Reflection-based routing\
-   Hidden control flow

Clarity beats cleverness.

------------------------------------------------------------------------

# 5. Debug & Logging Discipline

## 5.1 Debug Code Must Be Isolated

Wrap temporary debug logic:

    # debug
    logger.debug("state: %s", state)
    # debug ends

Debug code must be removable without refactoring.

------------------------------------------------------------------------

## 5.2 Logging Over Print

Never use print() in production systems.

Use structured logging.

------------------------------------------------------------------------

# 6. Assumption Control

## 6.1 Declare Assumptions

Before implementing behavior that affects:

-   Protocol rules\
-   Authorization\
-   State transitions\
-   Memory handling\
-   Concurrency\
-   External interfaces

You must explicitly declare assumptions.

Undeclared assumptions are architectural violations.

------------------------------------------------------------------------

## 6.2 Classify Assumptions

All assumptions must be labeled:

**HARD Assumption** - Affects correctness or safety\
- If wrong → system breaks

**SOFT Assumption** - Affects ergonomics or style\
- If wrong → system still works

------------------------------------------------------------------------

## 6.3 HARD Assumptions Require Evidence

Every HARD assumption must reference:

-   Exact file\
-   Exact class/function\
-   Verifiable behavior

If it cannot be verified:

STOP implementation.

------------------------------------------------------------------------

# 7. Concurrency Discipline

If using:

-   Threads\
-   AsyncIO\
-   Multiprocessing

Rules:

-   Avoid shared mutable state\
-   Use clear synchronization\
-   Document lifecycle\
-   No hidden background workers

Concurrency must be visible in architecture --- never implicit.

------------------------------------------------------------------------

# 8. Error Handling Principles

-   Raise meaningful exceptions\
-   Use specific exception types\
-   Never swallow unexpected errors\
-   Fail loudly during development

Silent corruption is worse than loud failure.

------------------------------------------------------------------------

# Final Principle

If the code becomes hard to delete, it was written wrong.

Durable Python systems shrink as they mature.
