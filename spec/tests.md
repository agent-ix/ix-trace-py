---
id: TM-001
title: "ix-trace-py Test Matrix"
type: TestMatrix
---

# Test Matrix

## Overview

This matrix maps every acceptance criterion in `ix-trace-py/spec/` to the test
that verifies it. Test cases use the `TC-XXX` prefix, and the `Type` column says
what kind of evidence each row is. The package marks its own tests with its own
marker wherever it can.

## Matrix Rules

1. **Coverage Rule** — every acceptance criterion has at least one trace, or an
   explicit row saying why it has none.
2. **One id, one symbol** — no trace id appears on two different tests.
3. **Real runs** — emission is observed by running pytest in a subprocess over a
   fixture suite and reading the JUnit file it wrote, not by calling plugin
   internals.

## Functional Requirement Coverage

| Functional Req | Acceptance Criteria | Test Cases | Status |
|----|----|----|--------|
| FR-001 pytest trace-marker plugin | AC-1..11; CON-1 | TC-001..TC-011 | 🚧 Planned — not run |
| FR-002 implements decorator | AC-1..11; CON-1..4 | TC-012..TC-022 | 🚧 Planned — not run |

## Test Case Summary

| Test ID | Title | Type | Priority | Traces To | Status |
|----|----|----|----|----|----|
| TC-001 | Plugin registers `trace`: a marked test collects warning-free and passes `--strict-markers`, emission on and off | Integration | P1 | FR-001-AC-1 | 🚧 Planned — not run |
| TC-002 | Emission off: JUnit equals the no-plugin run apart from timing, no `trace` property, no non-stdlib import | Integration | P1 | FR-001-AC-2 | 🚧 Planned — not run |
| TC-003 | Emission on: a function's markers give one `trace` property with each id once; class and module markers add nothing | Integration | P1 | FR-001-AC-3 | 🚧 Planned — not run |
| TC-004 | Emission on: ids are only marker arguments, none inferred from names; a non-`str` argument fails the run naming the test | Integration | P1 | FR-001-AC-4 | 🚧 Planned — not run |
| TC-005 | Symbols: module-level bare name, `Class.method`, nested-class `Outer.Inner.method`, parametrized `[case]` stripped to two cases; `name`==`classname`, `file` set, equal to `quire coverage --json` | Integration | P1 | FR-001-AC-5 | 🚧 Planned — not run |
| TC-006 | Outcomes: fail, setup error, skip and xfail keep pytest's own outcome and their ids | Integration | P1 | FR-001-AC-6 | 🚧 Planned — not run |
| TC-007 | xdist with two workers: each marked test once with its own ids | Integration | P1 | FR-001-AC-7 | 🚧 Planned — not run |
| TC-008 | Result file written by pytest's own writer, no sidecar or post-run step | Integration | P1 | FR-001-AC-8 | 🚧 Planned — not run |
| TC-009 | Any family other than `xunit1`/`legacy` (`xunit2`, the default) fails the enabled run naming the family and `-o junit_family=xunit1`; `xunit1` and `legacy` carry `trace`, `name`, `classname`, `file` | Integration | P1 | FR-001-AC-9 | 🚧 Planned — not run |
| TC-010 | Cost: 500-test marked suite under 5% median overhead with emission on | Integration | P1 | FR-001-AC-10 | 🚧 Planned — not run |
| TC-011 | End to end: real pytest suite -> `quoin evidence record` binds; failing variant binds nothing | E2E | P1 | FR-001-AC-11 | 🚧 Planned — not run |
| TC-012 | Identity: `@implements` on a function, `async def`, method, staticmethod-wrapped method and class returns the identical object with unchanged behaviour and signature | Unit | P1 | FR-002-AC-1 | 🚧 Planned — not run |
| TC-013 | No retained reference: `sys.getrefcount` and `gc.get_referrers` of the decorated object unchanged across decoration, with `vars()` and the package namespace equal; a fixture registry in a module, a closure and an in-place list each fail it | Unit | P1 | FR-002-AC-2 | 🚧 Planned — not run |
| TC-014 | Several ids and a repeated id are accepted | Unit | P1 | FR-002-AC-3 | 🚧 Planned — not run |
| TC-015 | `implements()` raises `ValueError` showing a well-formed call; a non-`str` argument raises `TypeError` naming its type and position; each at decoration | Unit | P1 | FR-002-AC-4 | 🚧 Planned — not run |
| TC-016 | `import ix_trace_py` with `pytest` unimportable succeeds, `implements` works, and `pytest` is absent from `sys.modules` | Integration | P1 | FR-002-AC-5 | 🚧 Planned — not run |
| TC-017 | Stacking above and below another decorator `D` and above `@pytest.mark.trace(...)` yields `D` alone's result and gives `D` the unchanged object | Unit | P1 | FR-002-AC-6 | 🚧 Planned — not run |
| TC-018 | Valid on module-level, method, nested function, nested class and test function; a test keeps its collection and `trace` property | Integration | P1 | FR-002-AC-7 | 🚧 Planned — not run |
| TC-019 | Decorated function `is` the undecorated function | Unit | P1 | FR-002-AC-8 | 🚧 Planned — not run |
| TC-020 | A fixture package decorated with `@implements(...)` and `@ix_trace_py.implements(...)` yields one `implements` per id and no `verifies` through `quire coverage --json`; a renamed import and single-quoted, raw and triple-quoted literals run and bind nothing | E2E | P1 | FR-002-AC-9 | 🚧 Planned — not run |
| TC-021 | Shape rule: `""`, `"FR 2"`, `"A-1, A-2"`, `"FR-XXX"` and `"1-A"` raise `ValueError` naming the argument; `ZZ-001`, `MADEUP-042-AC-9` and `interface_004-AC-1` are accepted; no kind list exists in the package | Unit | P1 | FR-002-AC-10 | 🚧 Planned — not run |
| TC-022 | A nested decorated definition checks its ids on each call of the enclosing function, a module-level one once at import, and both return the unchanged object | Unit | P1 | FR-002-AC-11 | 🚧 Planned — not run |

## Constraint Coverage

| Constraint | Covering evidence |
|----|----|
| FR-001-CON-1 | Inspection — no post-write rewrite step in the plugin; not performed |
| FR-002-CON-1 | Inspection — no flag on `trace`; not performed |
| FR-002-CON-2 | Inspection — the package parses no source; not performed |
| FR-002-CON-3 | Inspection — no production `trace` export; not performed |
| FR-002-CON-4 | TC-021 — no kind list in the package, `ZZ-001` accepted |

## Stakeholder Validation

| ID | Traces To | Validation | Status |
|----|----|----|----|
| StR-001-VC-1 | US-001; FR-001 | Demonstration — covered by TC-011 | 🚧 |
| StR-001-VC-2 | FR-001 | Demonstration — covered by TC-011 failing variant | 🚧 |
| StR-001-VC-3 | FR-001 | Demonstration — covered by TC-009 | 🚧 |
| StR-002-VC-1 | US-002; FR-002 | Demonstration — covered by TC-020 | 🚧 |
| StR-002-VC-2 | FR-002 | Demonstration — covered by TC-012 and TC-016 | 🚧 |

## Verification Status

Planned: no test exists yet and none has been run. The extractor-side equality of
the plugin's symbols (TC-005) is cross-checked by quire-rs FR-051-AC-47 and
FR-051-AC-48.
