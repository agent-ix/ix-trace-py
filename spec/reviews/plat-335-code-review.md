---
id: SR-006
title: "Code review of agent-ix/ix-trace-py PR 3 (PLAT-335) pytest trace plugin"
type: SpecReview
analysis: code-review
scope: "agent-ix/ix-trace-py; PR 3 diff only (git diff origin/main...HEAD, head 727de7e): ix_trace_py/plugin.py, conftest.py, pyproject.toml, poetry.lock, tests/helpers.py, tests/test_plugin.py, tests/test_quire_quoin.py, spec/tests.md"
review_set: subset
---

## Summary

Ticket: PLAT-335. Python code review of the FR-001 pytest plugin, head `727de7e`. The plugin is small and mostly correct. It sets `name` and `classname` on pytest's own reporter before the write, so there is no rewrite step. It keeps xdist working by sending the symbol as a report attribute, and it fails loudly on xunit2 and on non-`str` ids. One high defect: the `pytest11` entry point is named `ix_trace_py`, but the module is `ix_trace_py.plugin`. As a result, `-p ix_trace_py.plugin` and `pytest_plugins = ["ix_trace_py.plugin"]` crash with `ValueError: Plugin already registered under a different name` once the package is installed. The repo's own root `conftest.py` does exactly this, so `make test` crashes after a standard `poetry install`. This was reproduced on pytest 9.2.0. Two medium defects break the AC-5/AC-4 equality with the static side: inherited test methods, and `pytest.param(..., marks=trace(...))`.

Examined: ix_trace_py/plugin.py (all), conftest.py, pyproject.toml `pytest11` entry and dependency groups, tests/helpers.py, tests/test_plugin.py, tests/test_quire_quoin.py, against FR-001 and FR-001-AC-1..11, FR-001-CON-1. No AssuranceProfile exists in this repository.

Evidence: `make test` in the worktree after `poetry install` gave the ValueError above. With `-p no:ix_trace_py` all 25 tests pass, with 100% coverage. A scratch suite with an inherited method, a param-level trace mark, a kwarg-only marker and a unittest method was compared against `quire coverage --json` (quire 0.36.2).

## Verdict

**FAIL**: one high finding (FND-001). Done well: emission is gated strictly on `QUIRE_TRACE_EMIT == "1"`, and the emitting hooks are registered only while it is enabled. Class and module `pytestmark` are correctly excluded through `own_markers`. Parametrized cases strip `[case]` through `originalname`. The xunit2 refusal stops the run before any file is written. CON-1 holds by inspection. No vendoring, no copied schema, no tracking or pin ceremony. The tests run real pytest through `pytester` and the real `quire` and `quoin` CLIs. Nothing internal is mocked. Tests bind by `@pytest.mark.trace`, which dogfoods the marker under test. Following FR-001-AC-7 (xdist works) over the brief's "concurrent tests throw" is correct, because the spec is the authority.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | high | `pytest11` entry point is named `ix_trace_py`, not the module name `ix_trace_py.plugin`. pytest dedupes `-p`/`pytest_plugins` by module name, so with the package installed `-p ix_trace_py.plugin` or `pytest_plugins=["ix_trace_py.plugin"]` re-registers the module and pytest aborts with `ValueError: Plugin already registered under a different name`. The repo's root `conftest.py` lists it, so `make test` crashes after `poetry install`. Fix: drop `ix_trace_py.plugin` from `conftest.py` (keep `pytester`) and/or name the entry point `ix_trace_py.plugin`; add a test that runs with autoload on. | pyproject.toml:30-31, conftest.py:1 |
| FND-002 | medium | A trace-marked method inherited by a subclass (`class TestChild(TestBase)`) is emitted as `TestChild.test_x`. `quire coverage` binds only `TestBase.test_x`, so that record never joins the static view, which violates AC-5's "equal what quire coverage reports". `_symbol` builds the name from the collecting class chain, not the defining class (`item.function.__qualname__`-based). Untested. | ix_trace_py/plugin.py:61-63 |
| FND-003 | medium | `item.own_markers` includes callspec marks, so `pytest.param(2, marks=pytest.mark.trace("X"))` emits `X` for that case. That mark is not on the test function's `def`, and `quire coverage` binds nothing for it, which contradicts the FR-001 Description ("Only markers on the test function itself are emitted") and AC-4. Use `get_unpacked_marks(item.function)`-style function marks (or filter out `item.callspec.marks`). Untested. | ix_trace_py/plugin.py:45-57 |
| FND-004 | low | Keyword arguments to the marker (`@pytest.mark.trace(ids="X")`) are silently ignored. The test runs and carries no `trace`. FR-001's "Failure is loud" intent says a malformed marker should fail naming the test, as a non-`str` positional does. | ix_trace_py/plugin.py:46-57 |
| FND-005 | low | The plugin imports private `_pytest.junitxml.xml_key`, and the package declares no runtime `pytest` dependency or version floor (pytest is dev-only). Installing into an older or newer pytest without that private name fails at import with no clear message. Declare `pytest>=9` (the measured version) as a runtime dependency. | ix_trace_py/plugin.py:10, pyproject.toml:14-15 |
