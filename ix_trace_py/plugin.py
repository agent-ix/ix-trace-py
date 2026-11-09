"""pytest plugin: register the ``trace`` marker and emit it into JUnit output.

Binds Quoin FR-120 (Emitter contract) for pytest. Emission is enabled by
``QUIRE_TRACE_EMIT=1`` only.
"""

import os

import pytest
from _pytest.junitxml import xml_key

ENABLE_ENV = "QUIRE_TRACE_EMIT"
MARKER_NAME = "trace"
PROPERTY_NAME = "trace"
ALLOWED_FAMILIES = ("xunit1", "legacy")
_SYMBOL_ATTR = "ix_trace_symbol"


def emission_enabled() -> bool:
    return os.environ.get(ENABLE_ENV) == "1"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "trace(*ids): requirement ids this test verifies; emitted into JUnit "
        f"output as a '{PROPERTY_NAME}' property while {ENABLE_ENV}=1",
    )
    if not emission_enabled():
        return
    try:
        family = config.getini("junit_family")
    except ValueError:
        return
    if family not in ALLOWED_FAMILIES:
        raise pytest.UsageError(
            f"{ENABLE_ENV}=1 needs junit_family xunit1 (or legacy) so the JUnit "
            f"'file' attribute is kept, but junit_family is '{family}'; "
            "run with -o junit_family=xunit1"
        )
    config.pluginmanager.register(_Emitter(config), "ix_trace_py_emitter")


def _function_ids(item: pytest.Item) -> list[str]:
    """Ids of the markers on the test function itself, each once, in order."""
    ids: list[str] = []
    for mark in item.own_markers:
        if mark.name != MARKER_NAME:
            continue
        for arg in mark.args:
            if not isinstance(arg, str):
                raise pytest.UsageError(
                    f"{item.nodeid}: trace marker argument {arg!r} is "
                    f"{type(arg).__name__}, not str"
                )
            if arg not in ids:
                ids.append(arg)
    return ids


def _symbol(item: pytest.Function) -> str:
    classes = [n.name for n in item.listchain() if isinstance(n, pytest.Class)]
    return ".".join([*classes, item.originalname])


class _Emitter:
    """Hooks that exist only while emission is enabled."""

    def __init__(self, config: pytest.Config) -> None:
        self._config = config

    def pytest_collection_modifyitems(self, items: list[pytest.Item]) -> None:
        for item in items:
            if not isinstance(item, pytest.Function):
                continue
            ids = _function_ids(item)
            if ids:
                item.user_properties.append((PROPERTY_NAME, ",".join(ids)))

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item: pytest.Item):
        outcome = yield
        if isinstance(item, pytest.Function) and any(
            name == PROPERTY_NAME for name, _ in item.user_properties
        ):
            # A plain attribute travels with the report across xdist workers.
            setattr(outcome.get_result(), _SYMBOL_ATTR, _symbol(item))

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        symbol = getattr(report, _SYMBOL_ATTR, None)
        if symbol is None:
            return
        xml = self._config.stash.get(xml_key, None)
        if xml is None:
            return
        reporter = xml.node_reporter(report)
        reporter.add_attribute("name", symbol)
        reporter.add_attribute("classname", symbol)
