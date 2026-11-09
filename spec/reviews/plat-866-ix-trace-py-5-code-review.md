---
id: SR-015
title: "Code review of agent-ix/ix-trace-py PR 5 (PLAT-866) implements decorator"
type: SpecReview
analysis: code-review
scope: "agent-ix/ix-trace-py; PR 5 diff only (git diff origin/main...HEAD, head 778395e): ix_trace_py/__init__.py, tests/test_implements.py, spec/tests.md"
review_set: subset
---

## Summary

Ticket: PLAT-866. This is a Python code review of the FR-002 `implements` decorator at head `778395e`. The production code is small and correct. `implements(*ids)` validates eagerly when the decorator expression runs and returns a plain identity closure. It has no wrapper, no registry, no attribute and no environment read, and it imports only `re`, `collections.abc` and `typing`.

The validation matches the FR-002 Arguments section exactly. Zero ids raise `ValueError` with the message showing `implements("FR-007-AC-1")`. A non-`str` argument raises `TypeError` naming its type and position. A non-id-shaped `str` raises `ValueError` naming the argument. The shape regex implements the FR-002 rule, which is KIND `[A-Za-z][A-Za-z0-9_]*`, then one or more alphanumeric hyphen segments, with at least one digit-bearing segment. That rule is deliberately wider than ix-trace-rs FR-003's letters-only KIND, so that it accepts `interface_004-AC-1` as spec-artifacts-process FR-004-AC-31 requires. No behaviour was added beyond the spec and none was omitted.

All defects are in the tests. TC-024 asserts the wrong `quire coverage --json` contract. Two of TC-017's three negative controls cannot fail. TC-021's "D receives the unchanged object" check cannot fail.

Evidence: `poetry run pytest tests/test_implements.py tests/test_basic.py` gave 30 passed and 1 skipped (TC-024). A probe of the TC-017 harness showed that the list-registry and closure controls change only the refcount, and only through the test's own `keep` local. An identity decorator `lambda t: t` changes the same field when run through the same harness. A real module-level registry changes refcount and referrers.

A mutation run that replaced `implements` with a `functools.wraps` wrapper failed TC-016, TC-023 and TC-026, and passed both TC-021 tests. quire-rs `origin/main` `tests/it/output_contract.rs` (tc947) and `tests/it/implements_relation.rs` show that an `implements` relation is serialized as the top-level `implements[]` array of `{path, symbol, trace_id, form}` and moves no coverage number (FR-062-AC-4). quire version was 0.36.2.

## Verdict

**FAIL**: one high finding (FND-001), plus three medium.

What the PR does well: the production code is correct, minimal and stdlib-only. Identity is real and the mutation-sensitive tests (TC-016, TC-023) catch a wrapper. TC-017's positive check would catch a closure-retaining `implements`, because it keeps `decorator` alive, and it would catch a module registry. TC-020 really blocks `pytest` through a meta-path finder in a fresh interpreter. The bound spellings `@implements(...)` and `@ix_trace_py.implements(...)` in the TC-024 fixture match quire-rs FR-062 and spec-artifacts-process FR-004.

There are no pins, digests, version tracking or vendored files. CON-1..3 hold by inspection: `plugin.py` is unchanged, nothing parses source, and there is no `trace` export.

On TC-024, skipping is acceptable in principle. FR-002 itself says the `python_decorator` form is "planned there, not yet declared", and FR-002-AC-9 names the module as its oracle. The 🚧 statuses for TC-024 and StR-002-VC-1 are correct. The test body and its probe still need fixing (FND-001, FND-004).

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | high | TC-024 reads the decorated symbols out of `coverage_matrix[].criteria[].binders` and asserts `bound["FR-001-AC-1"] == {"bare"}`. Criterion binders are verification evidence. quire-rs serializes an `implements` relation as the top-level `implements[]` (`{path, symbol, trace_id, form}`), and FR-062-AC-4 says it moves no coverage number. So once `python_decorator` is declared, this test fails against a correct engine, and it can only pass on an engine that mints a `verifies`-like binder, which AC-9 forbids. It also never asserts "no `verifies` relation" or "one `implements` relation per declared id" (exactly two records for `bare`). Fix: assert on `report["implements"]` filtered by symbol and `trace_id`, check the record count, and assert that the FR-001-AC-* criteria have no binder from `pkg/prod.py`. | tests/test_implements.py:663-684 |
| FND-002 | medium | Two of TC-017's three negative controls cannot fail. `keep = make()(fn)` keeps a new local reference, so the refcount differs for any decorator. The `list-registry` and `closure` controls register into containers that are freed as soon as the temporary decorator is dropped, so the only change they cause is `keep`. Measured: an identity decorator run through the same harness changes the same field (refcount only). Only the `attribute` control (via `vars()`) is a real control. The "registry held in a module" that AC-2 names is never exercised. Fix: `del keep` (as the positive test does with `out`), keep the decorator object alive for the closure case, and use a true module-level list. | tests/test_implements.py:159-227 |
| FND-003 | medium | TC-021's "D receives the unchanged object" criterion cannot fail. `_record` returns what it received, so `_record.seen == [seen]` holds even if `implements` returned a wrapper. `above`/`below` assert only call results, `type()` and `__wrapped__.__name__`, and a `functools.wraps` passthrough satisfies all of them. The trace-marker case asserts only the marker name, not `is`. Measured: replacing `implements` with a wrapping decorator leaves both TC-021 tests passing. Fix: capture the object `D` receives and assert `received is undecorated`, assert `below.__wrapped__ is` the raw function, and in the marker case keep the marked function and assert `implements(...)(marked) is marked`. | tests/test_implements.py:424-481 |
| FND-004 | medium | TC-024's skip probe reads a hard-coded `~/.ix/filament/modules/spec-artifacts-process/manifest.yaml` and searches it for the substring `python_decorator`. It does not ask the engine that does the binding which module and forms it resolved. A module installed elsewhere keeps the test skipped forever without notice. A comment that mentions `python_decorator` makes it run against a manifest that does not declare the form. Fix: derive the condition from `quire` itself, or from `quoin module list` / the resolved module path. Run the fixture through `quire coverage --json` and skip only when no `python_decorator` form is in the resolved model. | tests/test_implements.py:627-640 |
| FND-005 | low | Argument positions in the `TypeError`/`ValueError` messages are zero-based (`implements() argument 0 must be a str`). This wording copies CPython's own one-based convention (`argument 1 must be str, not int`), so a reader is likely to miscount. FR-002 says "naming the argument's type and position" and pins no base. Use one-based positions, or have the spec pin the base. | ix_trace_py/__init__.py:36-43, tests/test_implements.py:285 |
| FND-006 | low | The TC-025 parametrize literals `"ZZ-001"`, `"MADEUP-042-AC-9"` and `"interface_004-AC-1"` on the line under `@pytest.mark.trace(...)` are read by quire as trace tags. `quire coverage --json` on this head reports three `unmatched_tags` (`AC-1`, `AC-9`, `ZZ-001`) for `test_tc025_shape_is_checked_and_membership_never`. That adds noise to the coverage diagnostics, and a real-looking id there would bind falsely. Move the literals off the decorated test's decorator block (for example into a module-level tuple). | tests/test_implements.py:322-325 |
| FND-007 | low | `hello()` (and `tests/test_basic.py`) is template scaffold that no requirement names. This PR touches `ix_trace_py/__init__.py` and keeps it. Under the no-ceremony rule it should be deleted in this change. | ix_trace_py/__init__.py:6-7, tests/test_basic.py:1-5 |
| FND-008 | low | TC-026's "module-level one once at import" is simulated with a `def` inside the test body, wrapped in the test's own `probe` counter, so the count asserts Python's `def` semantics, not an import. Import a real fixture module (or `importlib.reload` one) and count evaluations there. | tests/test_implements.py:547-583 |
