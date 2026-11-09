---
id: SR-017
title: "Code review of agent-ix/ix-trace-py PR 6 (PLAT-866) TC-024 against the released module"
type: SpecReview
analysis: code-review
scope: "agent-ix/ix-trace-py; PR 6 diff only (git diff origin/main...origin/plat-866-flip-tc024, head c23ef73): tests/test_implements.py"
review_set: subset
---

## Summary

Ticket: PLAT-866. This is a Python code review of the PR 6 change to `tests/test_implements.py` at head `c23ef73`. TC-024 now takes its module set from `IX_FILAMENT_MODULES_PATH`, where each root is a module or a directory of modules. It passes each module to `quire coverage` as `--module`, and falls back to `quoin module list` when the variable is unset or names no module. The skip gate and the coverage call read the same `_env_module_dirs()`, so the gate and the engine see the same model.

Reproduced with quire 0.38.4 (engine 0.55.0) first on PATH. The module was `spec-artifacts-process` main at tag v0.30.0.

- With `IX_FILAMENT_MODULES_PATH=<sap>/spec_artifacts_process`, `tests/test_implements.py` gave 31 passed and 0 skipped. Pointing the variable at the repo root (a directory of modules) passed TC-024 as well.
- With the variable unset, only the stale installed module 0.2.0 is available, and TC-024 skips with a reason.
- Mutation check: a scratch copy of the v0.30.0 module had its `python_decorator` pattern changed from `(?:ix_trace_py\.)?` to `(?:t\.)?`. With the variable pointed at that copy, TC-024 failed at `tests/test_implements.py:777`. The test is not vacuous, and it reads the named module rather than the installed 0.2.0.
- `quire validate --help` and `quire coverage --help` both state that `--module` replaces ambient discovery. Plain scoped discovery adds `IX_FILAMENT_MODULES_PATH` to the install root and does not replace it; measured, `quire validate` with only the variable set still loaded the installed 0.2.0 and failed. Passing `--module` explicitly is therefore what keeps the stale module out.
- The installed quire 0.36.2 (engine 0.50.2), given the v0.30.0 module, fails TC-024 loudly with a module load error (exit 3). It does not skip or pass silently.

## Verdict

**PASS with low findings.** The binding assertions run and fail on a regression, and module resolution cannot pick up the stale installed module once the variable is set. No manifest or other file is copied into the repo. The diff touches three files and none is a module artifact.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | TC-024's `Assumptions` docstring and its `pytest.skip` reason still say "no installed module declares implements python_decorator". The gate now also covers the `IX_FILAMENT_MODULES_PATH` modules, so on a host whose variable names a module set without the form, the skip report blames the installed set. Say "no resolvable module" (matching `_declares_python_decorator`'s own docstring) and name the variable. | tests/test_implements.py:745-746, tests/test_implements.py:758 |
| FND-002 | low | `@needs_quoin` still skips TC-024 when `quoin` is not on PATH, even with `IX_FILAMENT_MODULES_PATH` set. That path never calls `quoin`. A host that has only `quire` plus the module checkout skips a test it could run. Require `quoin` only on the fallback branch, for example by skipping inside `_module_manifests()` when the variable is empty and `quoin` is absent. | tests/test_implements.py:711-713, tests/test_implements.py:739 |
