---
id: SR-005
title: "Failure-domain review of agent-ix/ix-trace-py PR 2 (PLAT-335)"
type: SpecReview
analysis: failure-domain
scope: "agent-ix/ix-trace-py; spec/ (PR 2 diff only, head d4f1db0)"
review_set: subset
---

## Summary

Ticket: PLAT-335. Spec-only PR, head `d4f1db0`, scoped to `git diff origin/main...HEAD`. The PR relocates quire-rs FR-079 (merged in quire-rs PR 613) into this repository as FR-001, with StR-001, US-001, spec.md and a Test Matrix (TC-001..TC-011). Contract: Quoin FR-120 (E-1..E-10, amended E-4/AC-5) and ADR-100 on quoin main. Prior quire-rs reviews (spec/reviews/plat-334-335-spec-review-*.md) were read so fixed issues are not re-raised. `quire validate --scope . "spec/**/*.md"` exits 0 (quire 0.36.2). Checked unstated failure modes against pytest 9.0.2 `_pytest/junitxml.py` installed locally. Already settled and present: xunit2 drops `file`, so the run fails loudly with the remedy; class and module markers are excluded; a non-`str` argument fails; outcomes are pytest's own, so E-4 holds (a raising test is `<failure>`/`<error>` with its ids, per AC-6); xdist renaming happens where LogXML runs (AC-7).

Examined: FR-001, FR-001-AC-4, FR-001-AC-6, FR-001-AC-7, FR-001-AC-9. Context only: US-001.

No assurance profile exists in this repository; this is a direct review, not an enforced ix-flow run.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | The FR fails an enabled run `under any family other than xunit1`. pytest accepts `junit_family` values `legacy`, `xunit1` and `xunit2`. `LogXML.__init__` maps `legacy` to `xunit1` (`_pytest/junitxml.py`:489-490), so `legacy` keeps `file`. A plugin that checks the ini value fails a valid `legacy` configuration; one that checks `LogXML.family` accepts it. The two readings differ. Fix: say `under any family that drops file (xunit2)`, or name `legacy` as accepted. | spec/functional/FR-001-pytest-trace-marker-plugin.md:80-84, spec/functional/FR-001-pytest-trace-marker-plugin.md:105 |

## Verdict

One low ambiguity. No unstated failure mode that blocks merge.
