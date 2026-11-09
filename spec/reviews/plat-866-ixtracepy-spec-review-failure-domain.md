---
id: SR-013
title: "Failure-domain review of ix-trace-py PR 4: implements decorator FR-002 (PLAT-866)"
type: SpecReview
analysis: failure-domain
scope: "agent-ix/ix-trace-py; spec/ (PR 4 diff only, head 81e8e85)"
review_set: subset
---

## Summary

Ticket: PLAT-866. Spec-only PR, head `81e8e85`, scoped to `git diff origin/main...HEAD` (spec/functional/FR-002-implements-decorator.md, spec/stakeholder/StR-002-*.md, spec/usecase/US-002-*.md, spec/spec.md, spec/tests.md). Review set: base plus ears-conformance, integrity, scope-boundary, failure-domain and evidence; criterion-strength skipped (no Jev client installed, and the skill marks itself not runnable). No AssuranceProfile exists in this repository; this is a direct review, not an enforced ix-flow run. Sibling PRs read for consistency: quire-rs PR 628 (FR-062, head 8407145), spec-artifacts-process PR 133 (FR-004, head 0ee78cb), ix-trace-ts PR 8 (FR-002). `quire validate` on the changed docs exits 0 (quire 0.36.2).

Unstated failure modes of the run-time construct, and consistency of its id check with the other ix-trace specs. ix-trace-rs FR-002-AC-3 applies the FR-003 argument grammar to `#[implements]`: it rejects an empty list, a non-literal, an empty string and a literal that is not id-shaped, at compile time. ix-trace-py FR-001 and ix-trace-ts FR-002 (PR 8) check type only. FR-002 calls itself the Python counterpart of ix-trace-rs FR-002 but adopts the type-only rule.

Examined: FR-002-ARGS, FR-002-DECO, FR-002-AC-4, FR-002-AC-7. Context only: FR-002.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | The one import-time id check is type-only, so `@implements("")`, `@implements("FR 2")` and `@implements("FR-002-AC-1, FR-002-AC-2")` all import cleanly; the structural pattern (FR-004-AC-31 captures id-shaped quoted ids and requires a full match) then binds nothing, with at most a partial-implements-syntax-match warning and no finding at all where the pattern does not match. That is exactly the silent failure the paragraph claims to prevent ('a mistyped marker fails when the module is imported and not silently'), and it diverges from ix-trace-rs FR-002/FR-003, which reject an empty and a non-id-shaped literal. Either adopt the ix-trace-rs FR-003 shape rule (shape, never membership) with a ValueError naming the argument, plus an AC and TC and a matching change to the spec.md Out of Scope bullet, or drop the 'not silently' claim and state the divergence from ix-trace-rs explicitly. ix-trace-ts PR 8 has the same gap and should move with it. | spec/functional/FR-002-implements-decorator.md:54-58 |
| FND-002 | low | 'The only work is one call at import time' and 'fails when the module is imported' are false for a decorated nested function or class, which AC-7 makes valid: there the factory call and its check run every time the enclosing function runs, and an error surfaces at that call, not at import. AC-4 already words this correctly ('when the decorator expression is evaluated'); make the Description say once per evaluation of the decorated definition. | spec/functional/FR-002-implements-decorator.md:40-42, 55-57 |

## Verdict

Changes requested: 1 medium finding(s) must be fixed or dispositioned before merge.

## Dispositions

Round 1, verified against head 34188b5 (fix commits 7739746 and 34188b5).

| FND | Outcome | Reason |
| --- | --- | --- |
| FND-001 | fixed | Fixed in 7739746/34188b5: the ix-trace-rs FR-003 shape rule (as on ix-trace-rs main, underscored KIND included) is adopted with AC-10/TC-021 and CON-4 (shape, never membership); spec.md Out of Scope updated. Consistent with ix-trace-ts PR 8 at a10bb7d. |
| FND-002 | fixed | Fixed in 7739746: the Description says the decorator runs when its definition executes, and AC-11/TC-022 test the nested case. |
