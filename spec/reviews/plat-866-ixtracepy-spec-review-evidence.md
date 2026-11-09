---
id: SR-014
title: "Evidence review of ix-trace-py PR 4: implements decorator FR-002 (PLAT-866)"
type: SpecReview
analysis: evidence
scope: "agent-ix/ix-trace-py; spec/ (PR 4 diff only, head 81e8e85)"
review_set: subset
---

## Summary

Ticket: PLAT-866. Spec-only PR, head `81e8e85`, scoped to `git diff origin/main...HEAD` (spec/functional/FR-002-implements-decorator.md, spec/stakeholder/StR-002-*.md, spec/usecase/US-002-*.md, spec/spec.md, spec/tests.md). Review set: base plus ears-conformance, integrity, scope-boundary, failure-domain and evidence; criterion-strength skipped (no Jev client installed, and the skill marks itself not runnable). No AssuranceProfile exists in this repository; this is a direct review, not an enforced ix-flow run. Sibling PRs read for consistency: quire-rs PR 628 (FR-062, head 8407145), spec-artifacts-process PR 133 (FR-004, head 0ee78cb), ix-trace-ts PR 8 (FR-002). `quire validate` on the changed docs exits 0 (quire 0.36.2).

Verification method per obligation and whether each criterion can fail. Test is the right method for AC-1..AC-9 and Inspection for CON-1..CON-3; the StR VCs are Demonstrations backed by TC-020 and TC-016. The identity-decorator properties the ticket asks for are each testable: identity (AC-1, `is`), no attribute (AC-2 `vars()`), no pytest import (AC-5 `sys.modules`), no per-call cost (AC-8 identity). The registry half of AC-2 and the timing half of AC-8 are weak, below. spec-criterion-strength-analysis was not run: no Jev client is installed and the skill marks itself not runnable; its can-this-fail judgement was done manually and is recorded here.

Examined: FR-002-AC-1, FR-002-AC-2, FR-002-AC-3, FR-002-AC-4, FR-002-AC-5, FR-002-AC-6, FR-002-AC-7, FR-002-AC-8, FR-002-AC-9, FR-002-CON-1, FR-002-CON-2, FR-002-CON-3, StR-002-VC-1, StR-002-VC-2. Context only: FR-002-DECO.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | The registry half of AC-2 cannot fail for the usual registry shapes. Comparing the package namespace before and after decoration (a shallow snapshot) does not see an in-place append to an existing module-level list, dict or WeakSet, since the binding is the same object; nor a registry held in `ix_trace_py.plugin`, in the factory's closure or default argument, or in another module. Replace it with a check that sees any retained reference, e.g. `sys.getrefcount(obj)` (or `gc.get_referrers(obj)`) unchanged across decoration, or a deep snapshot of every `ix_trace_py*` module. | spec/functional/FR-002-implements-decorator.md:103 |
| FND-002 | low | The timing half of AC-8 can only fail through noise. Once the decorated and undecorated callables are asserted to be the same object, the 5% median comparison times one function against itself; and if identity fails, the identity clause (and AC-1) already fail. The clause adds a flaky benchmark that guards nothing. Drop the timing clause and keep the identity assertion (or fold AC-8 into AC-1). | spec/functional/FR-002-implements-decorator.md:109 |

## Verdict

Changes requested: 1 medium finding(s) must be fixed or dispositioned before merge.
