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
  - target: "ix://agent-ix/spec-artifacts-process/FR-004"
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
decorator from the syntax tree, through the `python_decorator` form that
[spec-artifacts-process FR-004](ix://agent-ix/spec-artifacts-process/FR-004) will
declare (planned there, not yet declared in the manifest). This requirement adds
only the run-time object the written form names, so that the form is an importable
symbol and not an undefined name.

### The decorator

`implements(*ids)` returns a decorator. Applied to a function, method or class, the
decorator returns that same object. It does not wrap it, replace it, add an
attribute to it, record it in a registry or read the environment, so a decorated
object is identical to the undecorated one and a call to it costs nothing the
undecorated call did not. The only work is one call when the decoration executes,
which checks the ids.

`implements` is a separate name from the `trace` marker and not an option of it.
`trace` declares evidence and may back an acceptance criterion; `implements`
declares scope and never may, and the module contract keeps the two apart so that a
mis-declared form binds nothing rather than the wrong thing
(quire-rs FR-062-CON-3). There is no `@trace` decorator for production code, and
this package does not add one: a test is marked with
`@pytest.mark.trace(...)`, which quire-rs FR-051 already binds.

### Arguments

Each argument is a `str` and **id-shaped**, the shape rule of `ix-trace-rs`
FR-003: a KIND that begins with an ASCII letter, followed by any mix of ASCII
letters, digits and underscores, then one or more hyphen-separated segments that
are each non-empty and alphanumeric, at least one of which contains an ASCII
digit. The package checks shape and never membership: `ZZ-001` is accepted
although no module declares that kind, and the kind vocabulary stays in the module.
At least one argument is required.

- If a call has no argument, then the package SHALL raise `ValueError` whose
  message shows a well-formed call, `implements("FR-007-AC-1")`.
- If an argument is not a `str`, then the package SHALL raise `TypeError` naming
  the argument's type and position.
- If an argument is a `str` that is not id-shaped, including the empty string,
  `"FR 2"` and `"A-1, A-2"`, then the package SHALL raise `ValueError` naming that
  argument.

Each error is raised when the decorator expression is evaluated, so a mistyped
marker fails when the decoration executes and not silently.

The pytest marker of [FR-001](./FR-001-pytest-trace-marker-plugin.md) requires a
`str` only and is unchanged; the shape check belongs to this construct, whose only
effect is the static relation, so an id that binds nothing is a defect worth failing
on.

### Statically bound spellings

The static side resolves no import. The spellings it binds are `@implements(...)`
and `@ix_trace_py.implements(...)`, as the module declaration pins them
([spec-artifacts-process FR-004](ix://agent-ix/spec-artifacts-process/FR-004)).
A renamed import (`import ix_trace_py as t`, `from ix_trace_py import implements as
impl`) works at run time and is not bound statically and raises no finding, because
the shipped patterns are anchored at the start of the candidate; write one of the
two spellings for a decorator that is to be read.

Only **double-quoted** string literals bind statically, because the module's
patterns read double quotes. A single-quoted, raw (`r"..."`), triple-quoted,
f-string or implicitly concatenated literal, and an id held in a variable, is a
`str` at run time and is accepted, but binds nothing statically. Write each id as a
double-quoted literal for a decorator that is to be read.

### Import posture

`import ix_trace_py` imports nothing beyond the standard library. In particular it
does not import `pytest`, so production code that uses `implements` runs in an
environment where pytest is not installed. The pytest plugin of
[FR-001](./FR-001-pytest-trace-marker-plugin.md) lives in its own module, and only
the `pytest11` entry point loads it.

### Stacking, placement and when it runs

The decorator composes with any other decorator in any order and returns what it
was given, so it neither hides nor alters a decorator beneath it. Stacked over
another decorator `D`, the result of the stack is exactly the result `D` alone
produces, and stacked under one, `D` receives the unchanged object. It is valid on
`def`, `async def` and `class`, at module level, in a class body and nested. Used on
a test function it is accepted and, statically, binds nothing, because `implements`
binds only production symbols (quire-rs FR-062-AC-2).

The decorator expression runs when its definition statement executes. For a module
level definition that is once at import. For a nested definition it is each call of
the enclosing function, so the ids are checked, and a new factory result is made,
on every such call; the decorated nested object is still the unchanged object, and
the cost is that enclosing call's one check and nothing per call of the nested
object.

## Rationale

Production scope in Python is declared today by an `Implements:` comment matched as
text. A comment is not a construct the language checks, so a changed separator, a
wrapped line or an example in prose binds the wrong thing or nothing, and the
extractor cannot tell. A decorator is a node the parser hands over with its name and
arguments already separated. Making it the identity function keeps the construct
free at run time, which is the constraint that matters because a Python decorator,
unlike the compile-time Rust attribute, executes when its definition does.

## Acceptance Criteria

| ID | Criteria | Verification |
| --- | --- | --- |
| FR-002-AC-1 | `from ix_trace_py import implements` succeeds, and `@implements("FR-002-AC-1")` applied to a function, an `async def`, a method, a staticmethod-wrapped method and a class returns the identical object (`is`), whose behaviour, `__dict__`, `__wrapped__` absence and signature equal those of the undecorated definition. | Test |
| FR-002-AC-2 | The decorator retains no reference to what it decorates: across decoration the decorated object's `sys.getrefcount` and its `gc.get_referrers` set are unchanged, and its `vars()` and the package's module namespace are equal before and after, so a registry held in a module, a closure or an in-place container would fail it. | Test |
| FR-002-AC-3 | `implements("A-1", "A-2")` accepts several ids, and a repeated id is accepted and not an error. | Test |
| FR-002-AC-4 | `implements()` raises `ValueError` whose message shows a well-formed call; an argument that is not a `str` (an `int`, `None`, a `list`) raises `TypeError` naming its type and position; each is raised when the decorator expression is evaluated. | Test |
| FR-002-AC-5 | `import ix_trace_py` in an interpreter in which `pytest` cannot be imported succeeds, `implements` works there, and `sys.modules` holds no `pytest` entry afterwards. | Test |
| FR-002-AC-6 | `@implements(...)` stacked above and below another decorator `D`, and above `@pytest.mark.trace(...)` on one definition, yields the result `D` alone yields and passes `D` the unchanged object. | Test |
| FR-002-AC-7 | The decorator is valid on a module-level definition, a method, a nested function and a nested class, and on a test function, where it changes neither the test's collection nor its `trace` property under `QUIRE_TRACE_EMIT=1`. | Test |
| FR-002-AC-8 | The decorated callable is the undecorated callable: `decorated is undecorated` holds for a function, so a call to it adds no work. | Test |
| FR-002-AC-9 | A fixture package whose production definitions carry `@implements(...)` yields, through `quire coverage --json` under the module of `spec-artifacts-process`, one `implements` relation per declared id on the decorated symbol and no `verifies` relation, for both `@implements(...)` and `@ix_trace_py.implements(...)`, while a decorator written through a renamed import, and one written with a single-quoted, raw or triple-quoted literal, runs and binds nothing. | Test |
| FR-002-AC-10 | `implements("")`, `implements("FR 2")`, `implements("A-1, A-2")`, `implements("FR-XXX")` and `implements("1-A")` each raise `ValueError` naming the argument, while `implements("ZZ-001")`, `implements("MADEUP-042-AC-9")` and `implements("interface_004-AC-1")` are accepted, since shape is checked and membership never is. | Test |
| FR-002-AC-11 | A decorator on a nested definition is evaluated on each call of the enclosing function and checks its ids each time, a module-level one once at import, and in both the decorated object is the unchanged object. | Test |

## Constraints

| ID | Constraint | Type | Validation |
| --- | --- | --- | --- |
| FR-002-CON-1 | `implements` SHALL NOT be an argument or flag of `trace`. | Design | Inspection |
| FR-002-CON-2 | The package SHALL NOT parse source or import the extractor to bind a decorator; static binding is quire-rs. | Design | Inspection |
| FR-002-CON-3 | The package SHALL NOT export a production `trace` decorator. | Design | Inspection |
| FR-002-CON-4 | The package SHALL NOT encode which kinds exist; shape is checked and membership never is. | Design | Test (TC-021) |

## Dependencies

- **Upstream**: [quire-rs FR-062](ix://agent-ix/quire-rs/FR-062) (the `implements` relation and the `python_decorator` syntax position); [spec-artifacts-process FR-004](ix://agent-ix/spec-artifacts-process/FR-004) (the form it will declare); `ix-trace-rs` FR-002 and FR-003 (the Rust counterpart and the shape rule).
- **Upstream**: [US-002](../usecase/US-002-declare-the-ids-a-production-symbol-implements.md), which traces to [StR-002](../stakeholder/StR-002-python-production-code-declares-the-ids-it-implements.md).
- **Sibling**: [FR-001](./FR-001-pytest-trace-marker-plugin.md), the evidence side; `ix-trace-ts` FR-002, the TypeScript construct.
