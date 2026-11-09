---
id: US-002
title: "Declare the ids a production symbol implements"
type: US
relationships:
  - target: "ix://agent-ix/ix-trace-py/StR-002"
    type: "traces_to"
---

# US-002: Declare the ids a production symbol implements

## Story

**As a** developer whose production Python code realises specified requirements
**I want** to write the ids a function, method or class implements as a decorator
on it
**So that** the requirement-to-code link is read from the syntax tree and survives
reformatting, rather than depending on the wording of a comment.

## Context

The developer already marks tests with `@pytest.mark.trace(...)`. They want the
production side to read the same way, and they do not want production code to
import pytest or to run any extra code per call.

## Acceptance Examples (Illustrative)

```python
from ix_trace_py import implements


@implements("FR-007-AC-1", "FR-007-AC-2")
def lookup_first_heading(document): ...
```

`quire coverage` reports an `implements` relation from `lookup_first_heading` to
`FR-007-AC-1` and to `FR-007-AC-2`, and no coverage number moves.

## Constraints (Contextual)

The decorator marks scope, never evidence. A test is marked with
`@pytest.mark.trace(...)`; `@implements(...)` on a test binds nothing.

## Dependencies (Contextual)

`quire-rs` FR-062 for the static reading.

## Notes (Informative)

An id held in a variable is a `str` at run time and is accepted, but the static
side binds only quoted string literals.
