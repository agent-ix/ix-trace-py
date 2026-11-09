---
id: StR-001
title: "Python test authors need the ids a test verifies recorded with its result"
type: StR
relationships:
  - target: "ix://agent-ix/ix-trace-py/FR-001"
    type: "satisfied_by"
---

# StR-001: Python test authors need the ids a test verifies recorded with its result

## Stakeholder Need

Authors of traced Python repositories shall have each test result of a marked
pytest suite recorded against the specification ids the test names, so that an obligation is bound by a test that ran and passed rather than
only by a test that is annotated.

## Rationale

A static scan proves a test is annotated, never that it ran. The evidence side
reads a JUnit `trace` property to bind ids to a result, but pytest writes none,
and a pytest case name (`tests/test_x.py::TestC::test_m[a]`, a dotted module
path as `classname`) is not the symbol the extractor reports, so the static and
execution views never join. A result file that silently lacks a mark or a `file`
is worse than none: it looks recorded and binds nothing.

## Validation Criteria

| ID | Criteria | Validation |
|----|----------|------------|
| StR-001-VC-1 | A real pytest suite run with emission enabled produces a result file `quoin evidence record` accepts, and the obligation it names is bound | Demonstration |
| StR-001-VC-2 | The same suite with its tagged test made to fail records a failing entry and binds nothing | Demonstration |
| StR-001-VC-3 | A configuration that would lose a mark or a `file` fails the run and names the remedy | Demonstration |

## Stakeholders

Authors and reviewers of traced Python repositories, and consumers of coverage
and evidence reports who decide whether a requirement is verified.

## Context and Assumptions

The suite already writes JUnit XML with pytest's `--junit-xml`. Emission is
opt-in: installing the plugin or writing the marker never changes a result file.

## Dependencies

**Upstream**: [Quoin FR-120](ix://agent-ix/quoin/FR-120) and
`ix://agent-ix/quire-rs/FR-051`. **Downstream**:
[FR-001](../functional/FR-001-pytest-trace-marker-plugin.md).
