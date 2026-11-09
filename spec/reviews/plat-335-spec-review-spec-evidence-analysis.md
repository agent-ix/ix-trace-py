---
id: SR-004
title: "Evidence review of agent-ix/ix-trace-py PR 2 (PLAT-335)"
type: SpecReview
analysis: evidence
scope: "agent-ix/ix-trace-py; spec/ (PR 2 diff only, head d4f1db0)"
review_set: subset
---

## Summary

Ticket: PLAT-335. Spec-only PR, head `d4f1db0`, scoped to `git diff origin/main...HEAD`. The PR relocates quire-rs FR-079 (merged in quire-rs PR 613) into this repository as FR-001, with StR-001, US-001, spec.md and a Test Matrix (TC-001..TC-011). Contract: Quoin FR-120 (E-1..E-10, amended E-4/AC-5) and ADR-100 on quoin main. Prior quire-rs reviews (spec/reviews/plat-334-335-spec-review-*.md) were read so fixed issues are not re-raised. `quire validate --scope . "spec/**/*.md"` exits 0 (quire 0.36.2). Checked that each AC can fail and that its method fits. AC-1..AC-11 each state an observable result with a negative control: warning-free collection under `--strict-markers`, byte-equality apart from timing, an exact id set, a named error, an exact `<testcase>` count, pytest's own outcome child, no sidecar file, a 5% median over five or more runs, and a bound/unbound obligation. `Test` is the right method for every AC, and `Inspection` is right for CON-1. Matrix rule 3 (subprocess over a fixture suite) is sound evidence for an emitter.

Examined: FR-001-AC-1, FR-001-AC-2, FR-001-AC-3, FR-001-AC-4, FR-001-AC-5, FR-001-AC-6, FR-001-AC-7, FR-001-AC-8, FR-001-AC-9, FR-001-AC-10, FR-001-AC-11, FR-001-CON-1, TM-001. Context only: none.

No assurance profile exists in this repository; this is a direct review, not an enforced ix-flow run.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | The symbol table says a method reports `Class.method` with nested classes dot-joined, and Quoin FR-120 E-2 requires equality `including a top-level, a nested and a parametrized test`. AC-5 tests a module-level function, one method and a parametrized function, but no method of a nested class. pytest's nodeid spells that case `TestOuter::TestInner::test_m`, so it is the rename branch most likely to be wrong (`TestInner.test_m` instead of `TestOuter.TestInner.test_m`), and no criterion would catch it. Fix: add `a method of a nested class reports Outer.Inner.method` to AC-5 and to TC-005. | spec/functional/FR-001-pytest-trace-marker-plugin.md:68, spec/functional/FR-001-pytest-trace-marker-plugin.md:101 |

## Verdict

Every AC can fail as written. One medium coverage gap (FND-001), to fix in this PR.

## Dispositions

| FND | outcome | reason |
| --- | --- | --- |
| FND-001 | fixed | Fix commit b423570: AC-5 and TC-005 now include a method of a nested class reporting `Outer.Inner.method`, and the symbol table shows the example. |
