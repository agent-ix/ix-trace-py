---
id: SR-009
title: "Spec review (base) of ix-trace-py PR 4: implements decorator FR-002 (PLAT-866)"
type: SpecReview
analysis: base
scope: "agent-ix/ix-trace-py; spec/ (PR 4 diff only, head 81e8e85)"
review_set: subset
---

## Summary

Ticket: PLAT-866. Spec-only PR, head `81e8e85`, scoped to `git diff origin/main...HEAD` (spec/functional/FR-002-implements-decorator.md, spec/stakeholder/StR-002-*.md, spec/usecase/US-002-*.md, spec/spec.md, spec/tests.md). Review set: base plus ears-conformance, integrity, scope-boundary, failure-domain and evidence; criterion-strength skipped (no Jev client installed, and the skill marks itself not runnable). No AssuranceProfile exists in this repository; this is a direct review, not an enforced ix-flow run. Sibling PRs read for consistency: quire-rs PR 628 (FR-062, head 8407145), spec-artifacts-process PR 133 (FR-004, head 0ee78cb), ix-trace-ts PR 8 (FR-002). `quire validate` on the changed docs exits 0 (quire 0.36.2).

Checklist results. ID formats are well-formed and do not collide: main holds FR-001, StR-001, US-001, TC-001..TC-011 and SR-001..SR-008, this PR adds FR-002, StR-002, US-002, TC-012..TC-020, and PR 4 is the only open PR in the repository. Every one of the nine ACs has exactly one TC in the Test Case Summary (AC-1->TC-012 ... AC-9->TC-020) and the Requirement Coverage row reads AC-1..9; CON-1..3 -> TC-012..TC-020. Links: FR-002 implements StR-002 and US-002; StR-002 satisfied_by FR-002; US-002 traces_to StR-002; spec.md adds the quire-rs FR-062 depends_on edge. Public-repo check (the repository is PUBLIC): the diff carries no ticket ids, no delivery order, no roadmap, no quire-research reference and no private repository; every cross-repo citation (quire-rs, spec-artifacts-process, ix-trace-rs, ix-trace-ts, quoin) is to a public repository. The phrase 'mutation scoping and impact analysis' in StR-002's rationale names a capability already specified in public quoin/quire-rs text and is not a roadmap disclosure. Style: StR-002 and US-002 follow the StR-001/US-001 section layout, voice and length; one over-claim is recorded below. No hash, digest, pin or tracking record is introduced.

Examined: FR-002, StR-002, StR-002-VC-1, StR-002-VC-2, US-002, FR-002-AC-1, FR-002-AC-2, FR-002-AC-3, FR-002-AC-4, FR-002-AC-5, FR-002-AC-6, FR-002-AC-7, FR-002-AC-8, FR-002-AC-9, FR-002-CON-1, FR-002-CON-2, FR-002-CON-3. Context only: none.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | StR-002-VC-2 is mapped to TC-016 only, but its second half ('the decorated object behaves exactly as it did undecorated') is asserted by TC-012 (FR-002-AC-1), not by TC-016 (no pytest import). Add TC-012 to the covering evidence. | spec/tests.md:74 |
| FND-002 | low | tests.md gives FR-002-CON-1 the evidence 'no production trace export and no flag on trace', which folds in CON-3's subject; CON-1 is only 'no flag on trace'. In FR-002 the Constraints table also lists CON-3 before CON-2. Make CON-1's evidence its own and order the table CON-1, CON-2, CON-3. | spec/tests.md:62 |
| FND-003 | low | FR-002 names spec-artifacts-process FR-004 as an Upstream dependency (the declared form whose spellings it repeats) but its relationships carry only StR-002, US-002 and quire-rs FR-062; spec.md likewise adds only FR-062. Add an ix://agent-ix/spec-artifacts-process/FR-004 consumes edge so the spelling dependency is in the graph, not only in prose. | spec/functional/FR-002-implements-decorator.md:1-15 |
| FND-004 | low | spec.md System Description still describes the package as only 'A pytest plugin loaded through the pytest11 entry point ... It imports nothing beyond pytest and the standard library', which is now false for the package as a whole: FR-002 requires `import ix_trace_py` to import nothing beyond the standard library and the plugin to live in its own module. Describe both parts and their import postures. (The In Scope list also has a stray blank line splitting it into two lists.) | spec/spec.md:80-86 |
| FND-005 | low | StR-002 says the ids are stated 'in a construct the language itself checks'. Python checks only that the name `implements` resolves; the ids are checked by the package, and only for type (FR-002 Arguments). StR-001 makes no comparable claim. Reword to what holds, e.g. 'in a construct the interpreter resolves and the extractor reads from the syntax tree'. | spec/stakeholder/StR-002-python-production-code-declares-the-ids-it-implements.md:14-18 |

## Verdict

No blocking findings; the low findings should be fixed in the same PR.
