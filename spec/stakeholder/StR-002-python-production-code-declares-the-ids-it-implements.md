---
id: StR-002
title: "Python authors need production code to declare the requirement ids it implements"
type: StR
relationships:
  - target: "ix://agent-ix/ix-trace-py/FR-002"
    type: "satisfied_by"
---

# StR-002: Python authors need production code to declare the requirement ids it implements

## Stakeholder Need

Authors of traced Python repositories shall state, on a production
function, method or class, the specification ids it implements, in a construct
the language itself checks and the extractor reads from the syntax tree, so that
the link from a requirement to its production code does not depend on how a
comment happens to be worded or wrapped.

## Rationale

Test evidence is already declared with a language construct, the pytest `trace`
marker. Production scope is not: Python code carries it only as an `Implements:`
comment matched as text, so a changed separator, a wrapped line or an example in
prose silently binds the wrong thing or nothing. Rust declares the same scope with
`#[implements]`. A requirement-to-code link that mutation scoping and impact
analysis depend on should be as hard to mistype as the test side is.

## Validation Criteria

| ID | Criteria | Validation |
|----|----------|------------|
| StR-002-VC-1 | A production function decorated with `@implements("FR-001-AC-1")` is read by `quire coverage` as an `implements` relation to that id and contributes no verification evidence | Demonstration |
| StR-002-VC-2 | Importing a module that uses the decorator in an environment without pytest succeeds and the decorated object behaves exactly as it did undecorated | Demonstration |

## Stakeholders

Authors and reviewers of traced Python repositories, and consumers of coverage and
mutation-scoping reports that need a requirement's production files.

## Context and Assumptions

The static binding of the decorator is `quire-rs` FR-062 and the declaration of
its form is `spec-artifacts-process` FR-004. This package supplies only the
decorator itself, so the written form is an importable symbol and not an
undefined name.

## Dependencies

**Upstream**: `ix://agent-ix/quire-rs/FR-062`. **Downstream**:
[FR-002](../functional/FR-002-implements-decorator.md).
