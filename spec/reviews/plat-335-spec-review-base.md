---
id: SR-001
title: "Base spec review of agent-ix/ix-trace-py PR 2 (PLAT-335)"
type: SpecReview
analysis: base
scope: "agent-ix/ix-trace-py; spec/ (PR 2 diff only, head d4f1db0)"
review_set: subset
---

## Summary

Ticket: PLAT-335. Spec-only PR, head `d4f1db0`, scoped to `git diff origin/main...HEAD`. The PR relocates quire-rs FR-079 (merged in quire-rs PR 613) into this repository as FR-001, with StR-001, US-001, spec.md and a Test Matrix (TC-001..TC-011). Contract: Quoin FR-120 (E-1..E-10, amended E-4/AC-5) and ADR-100 on quoin main. Prior quire-rs reviews (spec/reviews/plat-334-335-spec-review-*.md) were read so fixed issues are not re-raised. `quire validate --scope . "spec/**/*.md"` exits 0 (quire 0.36.2). Carry-over check: after renaming FR-079 to FR-001, the Description, every section and all eleven AC texts and CON-1 are byte-identical to quire-rs main FR-079; no AC is weakened and no constraint lost. Every fix the prior rounds asked for is present: xunit2 fails loudly with remedy `-o junit_family=xunit1` (AC-9), function-level markers only (AC-3), a non-`str` argument fails naming the test (AC-4), no staleness clause in AC-11, and `QUIRE_TRACE_EMIT=1` scoped to the pytest and TypeScript emitters. Ids FR-001, AC-1..11, CON-1, TC-001..TC-011, StR-001 (VC-1..3) and US-001 are unique and sequential. No hash, pin, digest, tally or tracking record, no vendored or copied schema, no compatibility layer.

Examined: FR-001, FR-001-AC-1, FR-001-AC-2, FR-001-AC-3, FR-001-AC-4, FR-001-AC-5, FR-001-AC-6, FR-001-AC-7, FR-001-AC-8, FR-001-AC-9, FR-001-AC-10, FR-001-AC-11, FR-001-CON-1, StR-001, US-001, spec/spec.md, TM-001. Context only: none.

No assurance profile exists in this repository; this is a direct review, not an enforced ix-flow run.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | Every AC Verification cell reads `Test (TC-NNN)`. The quoin checklist says a Verification cell names a method only, with no `TC-` id. The relocation added these ids; quire-rs FR-079 had `Test`. The AC-to-TC mapping already lives in the Test Matrix `Traces To` column, so this is a second copy that can drift (the prior quire-rs round found stale off-by-one audit rows of exactly this kind). Fix: make each cell `Test`. ix-trace-rs uses the same form, outside this diff. | spec/functional/FR-001-pytest-trace-marker-plugin.md:97-107 |

## Verdict

Faithful relocation, with nothing weakened or lost. One low finding. No high finding. The base checklist does not block merge.
