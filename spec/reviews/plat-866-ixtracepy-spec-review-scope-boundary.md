---
id: SR-012
title: "Scope-boundary review of ix-trace-py PR 4: implements decorator FR-002 (PLAT-866)"
type: SpecReview
analysis: scope-boundary
scope: "agent-ix/ix-trace-py; spec/ (PR 4 diff only, head 81e8e85)"
review_set: subset
---

## Summary

Ticket: PLAT-866. Spec-only PR, head `81e8e85`, scoped to `git diff origin/main...HEAD` (spec/functional/FR-002-implements-decorator.md, spec/stakeholder/StR-002-*.md, spec/usecase/US-002-*.md, spec/spec.md, spec/tests.md). Review set: base plus ears-conformance, integrity, scope-boundary, failure-domain and evidence; criterion-strength skipped (no Jev client installed, and the skill marks itself not runnable). No AssuranceProfile exists in this repository; this is a direct review, not an enforced ix-flow run. Sibling PRs read for consistency: quire-rs PR 628 (FR-062, head 8407145), spec-artifacts-process PR 133 (FR-004, head 0ee78cb), ix-trace-ts PR 8 (FR-002). `quire validate` on the changed docs exits 0 (quire 0.36.2).

Cross-repo boundary against quire-rs PR 628 (FR-062, head 8407145) and spec-artifacts-process PR 133 (FR-004, head 0ee78cb). The statically bound spellings agree: FR-002 names `@implements(...)` and `@ix_trace_py.implements(...)`; quire-rs FR-062 'Spellings' says the shipped patterns accept the unqualified and the package-qualified `ix_trace_py.implements` spelling and resolve no import; spec-artifacts-process FR-004 'Spellings' says exactly `implements(...)` and `ix_trace_py.implements(...)`, renamed imports bind nothing, and FR-004-AC-31 tests both plus a renamed import. FR-002-AC-9 tests both spellings and the renamed-import case. The allocation is clean: this package owns only the runtime object (CON-2 forbids parsing source), the binding is quire-rs FR-062, the declared form is spec-artifacts-process FR-004, and the TypeScript construct is ix-trace-ts FR-002.

Examined: FR-002-SPELL, FR-002-AC-9, FR-002-CON-2. Context only: FR-002, FR-002-ARGS.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | The spelling contract covers the callee but not the id literal. FR-002 says the static side binds 'quoted string literals', yet the module's existing Python marker pattern matches only double-quoted ids (`"[^"]*"`) and spec-artifacts-process FR-004-AC-31 says only 'every quoted id'. `@implements('FR-1')`, a raw or triple-quoted literal, and an implicitly concatenated literal are all valid Python that pass the run-time check and, under a double-quote pattern, bind nothing with no finding. Pin which literal spellings bind (in FR-002 and with spec-artifacts-process FR-004) and add a single-quoted case to FR-002-AC-9 so the run-time and static sides cannot silently disagree. | spec/functional/FR-002-implements-decorator.md:60-61, 71-78 |
| FND-002 | low | FR-002 says spec-artifacts-process FR-004 'declares' the python_decorator form and 'pins' the spellings in the present tense, but FR-004 (PR 133) states the structural forms are 'planned, not declared' until the engine release that accepts the syntax value. Say the form is declared by FR-004 once that engine release lands, so a reader does not take FR-002-AC-9 as runnable today. | spec/functional/FR-002-implements-decorator.md:27-33, 71-75 |

## Verdict

Changes requested: 1 medium finding(s) must be fixed or dispositioned before merge.

## Dispositions

Round 1, verified against head 34188b5 (fix commits 7739746 and 34188b5).

| FND | Outcome | Reason |
| --- | --- | --- |
| FND-001 | fixed | Fixed in 7739746: only double-quoted literals bind, matching merged spec-artifacts-process FR-004 (9fc6a8b) and quire-rs FR-062 at c7eadc1; AC-9/TC-020 add single-quoted, raw and triple-quoted cases. |
| FND-002 | fixed | Fixed in 7739746: FR-002 says FR-004 will declare the form and that it is planned, matching merged FR-004. |
