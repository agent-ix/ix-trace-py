# ix-trace-py

A pytest plugin that emits requirement trace ids into JUnit results, so a
requirement can be traced to the tests that verify it.

Emission is enabled by setting `QUIRE_TRACE_EMIT=1`.

Status: private, pre-release. The package is not published anywhere.

## Specification

- Emitter contract: quoin FR-120.
- This package: quire-rs FR-079.

## Development

Requires Python 3.13 and Poetry 2.x.

```bash
make install
make test
make lint
```

Tests enforce 100% coverage.

## Contributing

See `CONTRIBUTING.md`, `CLA.md` and `CONTENT_RIGHTS.md`.

## Licence

AGPL-3.0-or-later. See `LICENSE`.
