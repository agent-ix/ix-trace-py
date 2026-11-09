"""Helpers: run real pytest over a fixture suite and read the JUnit it wrote."""

import xml.etree.ElementTree as ET

import pytest

PLUGIN = "ix_trace_py.plugin"


def run_suite(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
    source: str,
    *args: str,
    emit: str | None = "1",
    plugin: bool = True,
    family: str | None = "xunit1",
    filename: str = "test_sample.py",
) -> tuple[pytest.RunResult, ET.Element | None]:
    """Run pytest over `source`; return the result and the parsed JUnit root."""
    monkeypatch.setenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    if emit is None:
        monkeypatch.delenv("QUIRE_TRACE_EMIT", raising=False)
    else:
        monkeypatch.setenv("QUIRE_TRACE_EMIT", emit)
    pytester.makepyfile(**{filename[:-3]: source})
    cmd = ["--junit-xml=out.xml", "-p", "no:cacheprovider", *args]
    if family is not None:
        cmd += ["-o", f"junit_family={family}"]
    if plugin:
        cmd = ["-p", PLUGIN, *cmd]
    result = pytester.runpytest(*cmd)
    path = pytester.path / "out.xml"
    return result, (ET.parse(path).getroot() if path.exists() else None)


def cases(root: ET.Element) -> list[ET.Element]:
    return list(root.iter("testcase"))


def trace_of(case: ET.Element) -> str | None:
    for prop in case.iter("property"):
        if prop.get("name") == "trace":
            return prop.get("value")
    return None


def ids_of(case: ET.Element) -> set[str]:
    value = trace_of(case)
    return set(value.split(",")) if value else set()
