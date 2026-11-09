---
id: US-001
title: "Run a marked suite and record its evidence"
type: US
relationships:
  - target: "ix://agent-ix/ix-trace-py/StR-001"
    type: "traces_to"
---

# US-001: Run a marked suite and record its evidence

## Story

**As a** developer with a pytest suite whose tests carry `@pytest.mark.trace(...)`
**I want** one run of the suite to produce a result file naming the ids each test
verifies
**So that** `quoin evidence record` binds those ids to the outcome the run
actually produced.

## Context

The developer already marks tests and already writes JUnit XML. They want the ids
to travel with the result without changing how the suite is run beyond a flag and
an environment variable.

## Acceptance Examples (Illustrative)

```python
@pytest.mark.trace("FR-001-AC-1", "TC-041")
def test_lookup_returns_first_heading(): ...
```

```text
QUIRE_TRACE_EMIT=1 pytest -o junit_family=xunit1 --junit-xml=results.xml
```

The `<testcase>` for `test_lookup_returns_first_heading` carries
`<property name="trace" value="FR-001-AC-1,TC-041"/>` and reports the same name
the extractor reports for it.

## Constraints (Contextual)

A marker on a class or a module-level `pytestmark` is not emitted; the marker
goes on the test function.

## Dependencies (Contextual)

pytest, and `quoin evidence record` to consume the file.

## Notes (Informative)

Under pytest's default `junit_family` (`xunit2`) the run fails loudly with the
remedy, rather than writing a file without `file`.
