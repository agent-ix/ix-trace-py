---
id: SR-007
title: "Gap analysis of agent-ix/ix-trace-py PR 3 (PLAT-335) against FR-001"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/ix-trace-py; PR 3 diff only (head 727de7e): ix_trace_py/plugin.py, tests/test_plugin.py, tests/test_quire_quoin.py, spec/functional/FR-001-pytest-trace-marker-plugin.md (context)"
review_set: subset
---

## Summary

Ticket: PLAT-335. Planless gap analysis of FR-001 against the PR 3 code and tests. Plan completion: not assessed. `quire matrix --strict --scope .` (quire 0.36.2) reports every criterion FR-001-AC-1..11 `tagged`. FR-001-CON-1 is `method-without-symbol` (Inspection), and the inspection holds: the plugin writes only through pytest's reporter before the write. Every binding was read, and each test asserts the AC it claims. All bindings are correct. No stubs, no weak or tautological assertions, no mocks. The gaps are in what the tests exercise: the installed entry-point path for AC-1, a robust AC-10 measurement, and a whole-file comparison for AC-2. Code-level edge gaps (inheritance, param marks) are recorded in SR-006 FND-002 and FND-003.

Examined: FR-001-AC-1 through FR-001-AC-11 and FR-001-CON-1, with their binders in tests/test_plugin.py and tests/test_quire_quoin.py.

TC-010 robustness was measured on this host, terra, at load average 12-16. Three runs of the exact TC-010 shape (500 tests at `time.sleep(0.004)`, 5 interleaved runs each) gave a median overhead of +1.3%, +2.8% and +4.0% against the 5% limit. The emission-off spread was 2.83-4.41 s within one run. With `pass` bodies, child CPU time over 30 paired runs showed a median of +3.7% and a min-ratio of +8.8%. In-process `pytest.main` CPU time showed +4.7% median. So the plugin's own cost is a few percent of pytest's per-test work, and the 4 ms sleep padding is what holds TC-010's margin. That margin then sits inside the wall-clock noise.

## Verdict

**CONDITIONAL**: no high gap. Every AC has a real, correctly bound test. AC-6, AC-7, AC-8, AC-9 and AC-11 are fully exercised. AC-11 uses the real `quoin evidence record`, with both a passing and a failing variant. AC-7 matches the spec (xdist works). TC-010 is not robust as written. It is a wall-clock median of 5 runs against a 5% threshold on a shared host, the off run always goes first, and the margin comes from sleep padding. It will keep flaking under load (FND-002).

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | AC-1 says "With the plugin installed", but every test runs with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` plus `-p ix_trace_py.plugin`. The `pytest11` entry-point path that real users get is never exercised, which is why SR-006 FND-001 (crash when installed and named with `-p`) passed CI-equivalent runs. Add a subprocess run with autoload on (marker registered, emission works, `-p ix_trace_py.plugin` does not crash). | tests/helpers.py:21-31, tests/test_plugin.py:21-28 |
| FND-002 | medium | TC-010 is load-sensitive. It takes a wall-clock median of 5 runs against a 5% limit, always runs off before on, and pads each test with a 4 ms sleep, which dilutes the measured overhead into the noise band. Measured margins here were 1.3-4.0% against the 5% limit, with a 56% off-run spread. Make it robust within AC-10's wording: alternate or randomize on/off order per pair, take ≥11 runs (AC says "at least five"), and compare the median of per-pair on/off ratios (adjacent runs share load). Precompute the symbol once at collection instead of on each of the three `makereport` phases to trim the real cost. | tests/test_plugin.py:280-306 |
| FND-003 | low | TC-002 compares only `<testcase>` attributes and `<property>` elements. AC-2 says the whole JUnit file is identical apart from timing. Compare the full trees with `time`/`timestamp` stripped, so a plugin-side change to `<testsuite>` or any other child would be caught. | tests/test_plugin.py:37-43 |

## New findings (disposition pass 1)

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-004 | medium | Fix commit 00c8af6 adds `importlib.reload(plugin)` to `test_tc002_plugin_imports_only_pytest_and_stdlib`, only so coverage counts the module's import-time lines (coverage inflation). The reload re-executes the module body, which creates a new `_symbol_key` StashKey, so every tagged test that runs after it in the same session loses its symbol. Reproduced: `QUIRE_TRACE_EMIT=1 pytest -o junit_family=xunit1 --junit-xml=...` over this repo's own suite emits the `qualified_name` for TC-001/TC-002 and then pytest's default `tests.test_plugin`/`test_x[case]` names for every later test, so this repo's own `quoin evidence record` would not join them. Remove the reload. To cover the plugin's import-time lines, start coverage before plugins load (`coverage run -m pytest`, the pytest-cov-documented approach for plugins). | tests/test_plugin.py:58-62 |

## Dispositions

| FND | outcome | reason |
| --- | --- | --- |
| FND-001 | fixed | TC-012 (`test_tc012_installed_plugin_autoloads`) runs `runpytest_subprocess` with autoload left on, no `-p` and no conftest. It asserts `trace` is registered under `--strict-markers -W error` and that the id is emitted. Passes at cdb008d after `poetry install`. |
| FND-002 | fixed | TC-010 now runs 11 adjacent on/off pairs, alternates which run goes first, and asserts the median of per-pair ratios is under 1.05. The symbol is computed once at collection. Measured at cdb008d on terra (load average 11-12): the test passed 3/3. Two concurrent replicas of its algorithm gave median ratios of 0.985 and 0.985 (single-pair range 0.95-1.11), a margin of about 6 points to the limit. |
| FND-003 | fixed | TC-002 now compares the whole JUnit tree as text, with `time`/`timestamp` blanked (`_normalised`). |
| FND-004 | still-open | Added this round, introduced by 00c8af6. The `importlib.reload(plugin)` in TC-002 is still present at cdb008d. Remove it and start coverage before plugin load instead. |
| FND-004 | fixed | Round 2, 9bf3288. The reload is removed. `poe test` is now `coverage run -m pytest` then `coverage report`, with `[tool.coverage.run] source` and `[tool.coverage.report] fail_under = 100`, and `--cov*` is dropped from addopts. Makefile and scripts are untouched. Verified: `make test` passes 30/30 at 100%. A partial run makes `coverage report` exit 2, so the gate still bites. `QUIRE_TRACE_EMIT=1 -o junit_family=xunit1` over the repo suite gives every one of the 28 tagged cases `name == classname ==` its symbol. |
