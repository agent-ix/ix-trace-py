---
id: SR-016
title: "Gap analysis of agent-ix/ix-trace-py PR 5 (PLAT-866) implements decorator"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/ix-trace-py; PR 5 diff only (git diff origin/main...HEAD, head 778395e) against spec/functional/FR-002-implements-decorator.md (AC-1..11, CON-1..4), spec/stakeholder/StR-002, spec/tests.md TC-016..TC-026; binder spellings from quire-rs FR-062 and spec-artifacts-process FR-004 (origin/main)"
review_set: subset
---

## Summary

Ticket: PLAT-866. This is a planless gap analysis of FR-002 against the PR's tests and the status columns in `spec/tests.md`. Plan completion was not assessed. The method was manual, AC to test to code. The computed matrix was read from `quire coverage --json` (quire 0.36.2). It reports FR-002 acceptance criteria as 11/11 backed, where AC-9 counts as backed through the tagged but skipped TC-024.

Every AC has a test tagged with its id (`@pytest.mark.trace("FR-002-AC-n")`). The code has no symbol without an owning requirement. `hello()` is pre-existing scaffold and is covered in SR-015 FND-007.

Statuses that are correct:

- FR-002 row: 🚧, passing except TC-024.
- TC-024 and StR-002-VC-1: 🚧. The upstream `python_decorator` form is still planned in spec-artifacts-process FR-004-AC-31/AC-33, and it is absent from the installed manifest.
- StR-002-VC-2: ✅. TC-016 and TC-020 pass.
- CON-1..3: inspection holds. CON-4 is backed by TC-025 and the source scan.

Two ✅ rows overclaim, because their tests do not show what the row says they show.

## Verdict

**FAIL (medium)**: two status overclaims in `spec/tests.md` (FND-001, FND-002), plus one low spec-text inconsistency (FND-003).

The binder-side spellings `@implements(...)` and `@ix_trace_py.implements(...)`, and the decision to accept but not statically bind renamed-import and non-double-quoted spellings, agree with quire-rs FR-062 and spec-artifacts-process FR-004.

A skip for TC-024 is acceptable under the spec as written. FR-002-AC-9's oracle is "the module of spec-artifacts-process", and FR-002 says the form is "planned there, not yet declared", so the test cannot pass yet and must not be faked. It does not need to be specified differently. Its assertion target is wrong, though (SR-015 FND-001).

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | TC-017 is marked ✅ and says "a fixture registry in a module, a closure and an in-place list each fail it". No module-level registry is tested. The closure and list controls fail only through the test's own `keep` reference, and an identity decorator fails the same harness (SR-015 FND-002). So the row overclaims its FR-002-AC-2 negative-control evidence. Keep the ✅ only after the controls really fail for the stated reason. | spec/tests.md:52, tests/test_implements.py:204-227 |
| FND-002 | medium | TC-021 is marked ✅ and says it "gives `D` the unchanged object". No assertion in TC-021 can fail for a wrapping `implements` (SR-015 FND-003, measured by mutation). The AC-6 clause "passes `D` the unchanged object" is therefore not backed by TC-021, although TC-016 and TC-023 back identity separately. | spec/tests.md:56, tests/test_implements.py:424-481 |
| FND-003 | low | FR-002 calls its rule "the shape rule of `ix-trace-rs` FR-003", then states a wider one: a KIND of letters, digits and underscores. ix-trace-rs FR-003 defines KIND as "one or more ASCII letters", which rejects `interface_004-AC-1`, an id that FR-002-AC-10 and spec-artifacts-process FR-004-AC-31 require to be accepted. The code correctly follows FR-002. Only the attribution is wrong. Reword it as "the ix-trace-rs FR-003 rule, widened to a KIND of letters, digits and underscores" (or file the widening against ix-trace-rs FR-003). | spec/functional/FR-002-implements-decorator.md:57-62 |

## Dispositions

| FND | outcome | reason |
| --- | --- | --- |
| FND-001 | fixed | 0db2f3d: the TC-017 row text is unchanged, but the tests now back it. The module-level registry (an in-place list), closure and attribute controls each fail the `_leaks` check, and an identity decorator passes it. |
| FND-002 | fixed | 0db2f3d: the TC-021 row is unchanged, and TC-021 now asserts that `D` receives the defined object (`received[0] is raw`) and that `implements` returns `D`'s result and the marked function themselves. A wrapping mutation fails both tests. |
| FND-003 | fixed | 0db2f3d: FR-002 Arguments now states the rule directly and says it is deliberately wider than ix-trace-rs FR-003 (letters-only KIND), citing FR-004-AC-31 and FR-002-AC-10. |
