---
type: master-requirements
name: ix-trace-py
org: agent-ix
component_type: python-pytest-plugin
implementation_language: python
tags:
  - traceability
  - pytest
  - evidence
depends_on: []
standards_alignment:
  - iso-iec-ieee-29148
relationships:
  - target: "ix://agent-ix/quoin/FR-120"
    type: "depends_on"
    cardinality: "1:1"
  - target: "ix://agent-ix/quire-rs/FR-051"
    type: "depends_on"
    cardinality: "1:1"
  - target: "ix://agent-ix/quire-rs/FR-062"
    type: "depends_on"
    cardinality: "1:1"
security_critical: false
---

# Master Requirements Specification

## Purpose

This document specifies `ix-trace-py`, a pytest plugin and the Python construct
for production scope. It registers the `trace`
marker that Python tests use to name the specification ids they verify, and,
when asked, writes those ids into the JUnit XML that pytest itself writes, so
that `quoin evidence record` can bind the same ids to a result.

The static side already exists: `quire-rs` FR-051 binds
`@pytest.mark.trace("FR-001-AC-1")` from the syntax tree with no code executed.
What is missing is the execution side. The JUnit reader in the evidence adapter
reads a `trace` property, and nothing in the Python ecosystem writes one. The
contract a writer must meet is the Emitter contract (E-1..E-10) of
[Quoin FR-120](ix://agent-ix/quoin/FR-120); this package is its pytest binding.

## Scope

### In Scope

- Registration of the `trace` marker, so a marked test raises no
  `PytestUnknownMarkWarning` and passes under `--strict-markers`.
- Emission of the marker's ids as a `trace` property on each tagged
  `<testcase>` of pytest's own JUnit output, enabled by `QUIRE_TRACE_EMIT=1`.
- The symbol the plugin reports for each case (`name`, `classname`, `file`), so
  the execution view joins the static view.
- Loud failure where a result file would otherwise silently lack a mark or a
  `file`.

- The `implements` decorator, which a production function, method or class
  carries to declare the ids it implements, as an identity function that imports
  nothing beyond the standard library.

### Out of Scope

- **Which ids exist.** The kind vocabulary is declared by the module; this
  package checks neither shape nor membership of an id beyond requiring a `str`.
- **Static binding.** Reading the marker from the syntax tree is `quire-rs`
  FR-051, and the plugin imports nothing of it.
- **Binding the decorator.** Reading `@implements(...)` from the syntax tree is
  `quire-rs` FR-062, and its declared form is `spec-artifacts-process` FR-004.
- **A production `trace` decorator.** Evidence is declared by the pytest marker
  only; scope and evidence stay separate constructs.
- **Class and module markers.** A marker on a class or a module-level
  `pytestmark` is not emitted, because the static side binds a decorator only to
  the `def` it decorates.
- **Writing a result file.** pytest's own `--junit-xml` writer does that; the
  plugin writes no sidecar file and runs no step after pytest exits.
- **Other languages.** The Rust and TypeScript emitters are `ix-trace-rs` and
  `ix-trace-ts`. `QUIRE_TRACE_EMIT` is the enable name for the pytest and
  TypeScript emitters only; the Rust emitter is enabled by a cargo feature.

## System Overview

### System Description

A pytest plugin loaded through the `pytest11` entry point. It registers the
`trace` marker unconditionally. While `QUIRE_TRACE_EMIT=1`, it reads the `trace`
markers on each collected test function, adds one `trace` user property per
tagged item, and renames the item's reported `name` and `classname` to the
extractor's `qualified_name`, so pytest's own JUnit writer emits them. It
imports nothing beyond pytest and the standard library.

### Interfaces

The public surface is the `trace` marker, the environment variable
`QUIRE_TRACE_EMIT`, and the decorator factory `implements` exported by
`ix_trace_py`.

## Requirements Architecture

### Requirement Groups

- **Functional** — the marker registration and its emission
  ([FR-001](./functional/FR-001-pytest-trace-marker-plugin.md)).
- **Functional (scope)** — the production `implements` decorator
  ([FR-002](./functional/FR-002-implements-decorator.md)).
- **Stakeholder** — the need the plugin answers
  ([StR-001](./stakeholder/StR-001-python-tests-bind-ids-at-run-time.md)),
  reached through
  [US-001](./usecase/US-001-run-a-marked-suite-and-record-its-evidence.md); and
  [StR-002](./stakeholder/StR-002-python-production-code-declares-the-ids-it-implements.md),
  reached through
  [US-002](./usecase/US-002-declare-the-ids-a-production-symbol-implements.md).

### Traceability Approach

Every acceptance criterion is traced from the Test Matrix (`spec/tests.md`) to a
test carrying the id. The package marks its own tests with its own marker.

## References

- [Quoin FR-120](ix://agent-ix/quoin/FR-120) — the `trace` mark and the Emitter
  contract (E-1..E-10) this package binds for pytest.
- [quire-rs FR-051](ix://agent-ix/quire-rs/FR-051) — the marker form and the
  `qualified_name` the plugin must equal (FR-051-AC-47), and the end-to-end
  demonstration of the emitter chain (FR-051-AC-48).
- [quire-rs FR-062](ix://agent-ix/quire-rs/FR-062) — the `implements` relation and
  the `python_decorator` syntax position that binds the decorator.
- ISO/IEC/IEEE 29148:2018 — requirements engineering, the shape these artifacts
  follow.
