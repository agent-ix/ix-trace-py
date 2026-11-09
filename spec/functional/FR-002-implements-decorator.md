---
id: FR-002
title: "implements decorator declares the ids a production symbol implements"
type: FR
relationships:
  - target: "ix://agent-ix/ix-trace-py/StR-002"
    type: "implements"
    cardinality: "1:1"
  - target: "ix://agent-ix/ix-trace-py/US-002"
    type: "implements"
    cardinality: "1:1"
  - target: "ix://agent-ix/quire-rs/FR-062"
    type: "consumes"
    cardinality: "1:1"
---

# FR-002: implements decorator declares the ids a production symbol implements

## Description

The package SHALL export a decorator factory `implements(*ids: str)` from the
top-level module `ix_trace_py`, so that a production function, method or class
declares the specification ids it **implements** — its scope — as
`@implements("FR-007-AC-1", "FR-007-AC-2")`. This requirement is the Python
counterpart of the `#[implements]` attribute of `ix-trace-rs`
(`ix-trace-rs` FR-002).

The static side is [quire-rs FR-062](ix://agent-ix/quire-rs/FR-062): it binds the
decorator from the syntax tree with no code executed, through the
`python_decorator` form that
[spec-artifacts-process FR-004](ix://agent-ix/spec-artifacts-process/FR-004)
declares. This requirement adds only the run-time object the written form names, so
that the form is an importable, type-checked symbol and not an undefined name.

### The decorator

`implements(*ids)` returns a decorator. Applied to a function, method or class, the
decorator returns that same object. It does not wrap it, replace it, add an
attribute to it, record it in a registry or read the environment, so a decorated
object is identical to the undecorated one and a call to it costs nothing the
undecorated call did not. The only work is one call at import time, which checks
the ids.

`implements` is a separate name from the `trace` marker and not an option of it.
`trace` declares evidence and may back an acceptance criterion; `implements`
declares scope and never may, and the module contract keeps the two apart so that a
mis-declared form binds nothing rather than the wrong thing
(quire-rs FR-062-CON-3). There is no `@trace` decorator for production code, and
this package does not add one: a test is marked with
`@pytest.mark.trace(...)`, which quire-rs FR-051 already binds.

### Arguments

Each argument is a `str`. At least one is required. An argument that is not a
`str`, and a call with no argument, raise at the decoration site with an error that
names the argument, so a mistyped marker fails when the module is imported and not
silently. The package checks the type of an id and not its shape or membership:
which ids exist is declared by the module, as for the pytest marker.

A string held in a variable is a `str` at run time and is accepted. The static side
binds only quoted string literals, so such an id is accepted and not bound.

### Import posture

`import ix_trace_py` imports nothing beyond the standard library. In particular it
does not import `pytest`, so production code that uses `implements` runs in an
environment where pytest is not installed. The pytest plugin of
[FR-001](./FR-001-pytest-trace-marker-plugin.md) lives in its own module, and only
the `pytest11` entry point loads it.

### Statically bound spellings

The static side resolves no import. The spellings it binds are `@implements(...)`
and `@ix_trace_py.implements(...)`, as the module declaration pins them
([spec-artifacts-process FR-004](ix://agent-ix/spec-artifacts-process/FR-004)).
A renamed import (`import ix_trace_py as t`, `from ix_trace_py import implements as
impl`) works at run time and is not bound statically and raises no finding, because the
shipped patterns are anchored at the start of the candidate; write one of the two
spellings for a decorator that is to be read.

### Stacking and placement

The decorator composes with any other decorator in any order and returns what it
was given, so it neither hides nor alters a decorator beneath it. It is valid on
`def`, `async def` and `class`, at module level, in a class body and nested. Used on
a test function it is accepted and, statically, binds nothing, because `implements`
binds only production symbols (quire-rs FR-062-AC-2).

## Rationale

Production scope in Python is declared today by an `Implements:` comment matched as
text. A comment is not a construct the language checks, so a changed separator, a
wrapped line or an example in prose binds the wrong thing or nothing, and the
extractor cannot tell. A decorator is a node the parser hands over with its name and
arguments already separated. Making it the identity function keeps the construct
free at run time, which is the constraint that matters because a Python decorator,
unlike the compile-time Rust attribute, executes at import.

## Acceptance Criteria

| ID | Criteria | Verification |
| --- | --- | --- |
| FR-002-AC-1 | `from ix_trace_py import implements` succeeds, and `@implements("FR-002-AC-1")` applied to a function, an `async def`, a method, a staticmethod-wrapped method and a class returns the identical object (`is`), whose behaviour, `__dict__`, `__wrapped__` absence and signature equal those of the undecorated definition. | Test |
| FR-002-AC-2 | The decorator adds no attribute to the decorated object and no entry to any module-level registry: the decorated object's `vars()` and the package's module namespace are equal before and after decoration. | Test |
| FR-002-AC-3 | `implements("A-1", "A-2")` accepts several ids, and a repeated id is accepted and not an error. | Test |
| FR-002-AC-4 | `implements()` raises `ValueError`, and an argument that is not a `str` (an `int`, `None`, a `list`) raises `TypeError`, each when the decorator expression is evaluated and each with a message that names the offending argument. | Test |
| FR-002-AC-5 | `import ix_trace_py` in an interpreter in which `pytest` cannot be imported succeeds, `implements` works there, and `sys.modules` holds no `pytest` entry afterwards. | Test |
| FR-002-AC-6 | `@implements(...)` stacked above and below another decorator, and above `@pytest.mark.trace(...)` on one definition, each leaves the other decorator's effect unchanged and the result identical to applying that decorator alone. | Test |
| FR-002-AC-7 | The decorator is valid on a module-level definition, a method, a nested function and a nested class, and on a test function, where it changes neither the test's collection nor its `trace` property under `QUIRE_TRACE_EMIT=1`. | Test |
| FR-002-AC-8 | Calling a function decorated with `implements` 100,000 times adds no measurable per-call time over the undecorated function: the decorated and undecorated callables are the same object, asserted by identity, and the median call time over at least five runs differs by under 5%. | Test |
| FR-002-AC-9 | A fixture package whose production definitions carry `@implements(...)` yields, through `quire coverage --json` under the module of `spec-artifacts-process`, one `implements` relation per declared id on the decorated symbol and no `verifies` relation, for both `@implements(...)` and `@ix_trace_py.implements(...)`, while a decorator written through a renamed import binds nothing. | Test |

## Constraints

| ID | Constraint | Type | Validation |
| --- | --- | --- | --- |
| FR-002-CON-1 | `implements` SHALL NOT be an argument or flag of `trace`. | Design | Inspection |
| FR-002-CON-3 | The package SHALL NOT export a production `trace` decorator. | Design | Inspection |
| FR-002-CON-2 | The package SHALL NOT parse source or import the extractor to bind a decorator; static binding is quire-rs. | Design | Inspection |

## Dependencies

- **Upstream**: [quire-rs FR-062](ix://agent-ix/quire-rs/FR-062) (the `implements` relation and the `python_decorator` syntax position); [spec-artifacts-process FR-004](ix://agent-ix/spec-artifacts-process/FR-004) (the declared form); `ix-trace-rs` FR-002 (the Rust counterpart).
- **Upstream**: [US-002](../usecase/US-002-declare-the-ids-a-production-symbol-implements.md), which traces to [StR-002](../stakeholder/StR-002-python-production-code-declares-the-ids-it-implements.md).
- **Sibling**: [FR-001](./FR-001-pytest-trace-marker-plugin.md), the evidence side; `ix-trace-ts` FR-002, the TypeScript construct.
