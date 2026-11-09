---
id: SR-011
title: "Integrity review of ix-trace-py PR 4: implements decorator FR-002 (PLAT-866)"
type: SpecReview
analysis: integrity
scope: "agent-ix/ix-trace-py; spec/ (PR 4 diff only, head 81e8e85)"
review_set: subset
---

## Summary

Ticket: PLAT-866. Spec-only PR, head `81e8e85`, scoped to `git diff origin/main...HEAD` (spec/functional/FR-002-implements-decorator.md, spec/stakeholder/StR-002-*.md, spec/usecase/US-002-*.md, spec/spec.md, spec/tests.md). Review set: base plus ears-conformance, integrity, scope-boundary, failure-domain and evidence; criterion-strength skipped (no Jev client installed, and the skill marks itself not runnable). No AssuranceProfile exists in this repository; this is a direct review, not an enforced ix-flow run. Sibling PRs read for consistency: quire-rs PR 628 (FR-062, head 8407145), spec-artifacts-process PR 133 (FR-004, head 0ee78cb), ix-trace-ts PR 8 (FR-002). `quire validate` on the changed docs exits 0 (quire 0.36.2).

Atomicity and consistency of the nine ACs and three constraints. No AC contradicts another or FR-001; AC numbering is contiguous; every AC has one TC.

Examined: FR-002-AC-1, FR-002-AC-2, FR-002-AC-3, FR-002-AC-4, FR-002-AC-5, FR-002-AC-6, FR-002-AC-7, FR-002-AC-8, FR-002-AC-9, FR-002-CON-1, FR-002-CON-2, FR-002-CON-3. Context only: FR-002-ARGS.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | AC-4 requires 'each with a message that names the offending argument', but `implements()` has no argument to name, so the empty-call half has no checkable message content. It also picks ValueError for the empty call where the TypeScript sibling (ix-trace-ts PR 8 FR-002-AC-6) and Python's own missing-argument convention use TypeError. State the empty-call message content (e.g. names `implements` and a well-formed example) and either align the exception type with the sibling or say why it differs. | spec/functional/FR-002-implements-decorator.md:105 |
| FND-002 | low | AC-6 requires 'the result identical to applying that decorator alone'. For a wrapping decorator (functools.wraps) two separate applications produce two distinct objects, so 'identical' cannot mean `is` and two implementers will read it differently. Say what is compared: e.g. `implements(...)(d(f)) is d(f)`-shaped identity on the same application, and equal behaviour/signature/`__wrapped__` for `d(implements(...)(f))` versus `d(f)`. | spec/functional/FR-002-implements-decorator.md:107 |

## Verdict

No blocking findings; the low findings should be fixed in the same PR.

## Dispositions

Round 1, verified against head 34188b5 (fix commits 7739746 and 34188b5).

| FND | Outcome | Reason |
| --- | --- | --- |
| FND-001 | fixed | Fixed in 7739746: the empty-call message content is pinned (shows a well-formed call). Python keeps ValueError for a wrong value and TypeError for a wrong type, where ix-trace-ts uses TypeError throughout by JS convention; each follows its language's convention, so the split is not a defect. |
| FND-002 | fixed | Fixed in 7739746: AC-6 now states the comparison (D alone's result; D receives the unchanged object). |
