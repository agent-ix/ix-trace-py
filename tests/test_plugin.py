"""Acceptance tests for FR-001 (TC-001..TC-010). Each runs real pytest."""

import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from statistics import median

import pytest

from tests.helpers import cases, ids_of, run_suite, trace_of

MARKED = """
import pytest

@pytest.mark.trace("FR-001-AC-1")
def test_marked():
    pass
"""


@pytest.mark.trace("FR-001-AC-1")
@pytest.mark.parametrize("emit", [None, "1"])
def test_tc001_marker_registered_and_strict(pytester, monkeypatch, emit):
    result, root = run_suite(
        pytester, monkeypatch, MARKED, "--strict-markers", "-W", "error", emit=emit
    )
    result.assert_outcomes(passed=1)
    assert len(cases(root)) == 1


def _normalised(root):
    """The whole JUnit tree as text, with timing attributes blanked."""
    for element in root.iter():
        for attr in ("time", "timestamp"):
            if attr in element.attrib:
                element.set(attr, "T")
    return ET.tostring(root, encoding="unicode")


@pytest.mark.trace("FR-001-AC-2")
@pytest.mark.parametrize("emit", [None, "0", "true", ""])
def test_tc002_disabled_equals_no_plugin_run(pytester, monkeypatch, emit):
    _, with_plugin = run_suite(pytester, monkeypatch, MARKED, emit=emit)
    _, without = run_suite(pytester, monkeypatch, MARKED, emit=emit, plugin=False)
    assert _normalised(with_plugin) == _normalised(without)
    assert trace_of(cases(with_plugin)[0]) is None


@pytest.mark.trace("FR-001-AC-2")
def test_tc002_plugin_imports_only_pytest_and_stdlib():
    import ast
    import pathlib

    import importlib

    import ix_trace_py.plugin as plugin

    # The installed entry point imports the plugin before coverage starts;
    # re-executing the module body lets coverage see its import-time lines.
    importlib.reload(importlib.import_module("ix_trace_py"))
    importlib.reload(plugin)

    tree = ast.parse(pathlib.Path(plugin.__file__).read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module.split(".")[0])
    assert imported <= set(sys.stdlib_module_names) | {"pytest", "_pytest"}


@pytest.mark.trace("FR-001-AC-3")
def test_tc003_function_markers_one_property_each_id_once(pytester, monkeypatch):
    src = """
import pytest

@pytest.mark.trace("A-1", "B-2")
@pytest.mark.trace("B-2", "C-3")
def test_many():
    pass

def test_none():
    pass

@pytest.mark.trace("CLS-1")
class TestK:
    @pytest.mark.trace("M-1")
    def test_method(self):
        pass

    def test_bare_method(self):
        pass

pytestmark = pytest.mark.trace("MOD-1")

def test_module_marked_only():
    pass
"""
    _, root = run_suite(pytester, monkeypatch, src)
    by_name = {c.get("name"): c for c in cases(root)}
    assert ids_of(by_name["test_many"]) == {"A-1", "B-2", "C-3"}
    assert len(trace_of(by_name["test_many"]).split(",")) == 3
    assert len(list(by_name["test_many"].iter("property"))) == 1
    assert trace_of(by_name["test_none"]) is None
    assert ids_of(by_name["TestK.test_method"]) == {"M-1"}
    assert trace_of(by_name["test_bare_method"]) is None
    assert trace_of(by_name["test_module_marked_only"]) is None


@pytest.mark.trace("FR-001-AC-4")
def test_tc004_ids_only_from_marker_arguments(pytester, monkeypatch):
    src = """
import pytest
ID = "FR-9-AC-9"

@pytest.mark.trace(ID)
def test_fr_001_ac_1_named_like_an_id():
    pass

def test_tc_002_unmarked():
    pass
"""
    _, root = run_suite(pytester, monkeypatch, src, filename="test_fr_001.py")
    by_name = {c.get("name"): c for c in cases(root)}
    assert ids_of(by_name["test_fr_001_ac_1_named_like_an_id"]) == {"FR-9-AC-9"}
    assert trace_of(by_name["test_tc_002_unmarked"]) is None


@pytest.mark.trace("FR-001-AC-4")
def test_tc004_non_str_argument_fails_naming_the_test(pytester, monkeypatch):
    src = """
import pytest

@pytest.mark.trace(7)
def test_bad_marker():
    pass
"""
    result, root = run_suite(pytester, monkeypatch, src)
    assert result.ret != 0
    result.stderr.fnmatch_lines(["*test_sample.py::test_bad_marker*"])
    assert cases(root) == []


@pytest.mark.trace("FR-001-AC-5")
def test_tc005_symbols(pytester, monkeypatch):
    src = """
import pytest

@pytest.mark.trace("S-1")
def test_top():
    pass

class TestOuter:
    @pytest.mark.trace("S-2")
    def test_method(self):
        pass

    class TestInner:
        @pytest.mark.trace("S-3")
        def test_deep(self):
            pass

@pytest.mark.trace("S-4")
@pytest.mark.parametrize("n", [1, 2])
def test_param(n):
    pass
"""
    result, root = run_suite(pytester, monkeypatch, src)
    result.assert_outcomes(passed=5)
    got = [(c.get("name"), c.get("classname"), c.get("file")) for c in cases(root)]
    expected = [
        "test_top",
        "TestOuter.test_method",
        "TestOuter.TestInner.test_deep",
        "test_param",
        "test_param",
    ]
    assert got == [(s, s, "test_sample.py") for s in expected]


@pytest.mark.trace("FR-001-AC-6")
def test_tc006_outcomes_are_pytests_own(pytester, monkeypatch):
    src = """
import pytest

@pytest.fixture
def broken_setup():
    raise RuntimeError("setup")

@pytest.fixture
def broken_teardown():
    yield
    raise RuntimeError("teardown")

@pytest.mark.trace("O-1")
def test_fail():
    assert False

@pytest.mark.trace("O-2")
def test_setup_error(broken_setup):
    pass

@pytest.mark.trace("O-3")
def test_teardown_error(broken_teardown):
    pass

@pytest.mark.trace("O-4")
@pytest.mark.skip(reason="no")
def test_skipped():
    pass

@pytest.mark.trace("O-5")
@pytest.mark.xfail(reason="expected")
def test_xfail():
    assert False

@pytest.mark.trace("O-6")
def test_pass():
    pass
"""
    _, root = run_suite(pytester, monkeypatch, src)
    by_name = {c.get("name"): c for c in cases(root)}

    def kinds(case):
        return {c.tag for c in case if c.tag in ("failure", "error", "skipped")}

    assert kinds(by_name["test_fail"]) == {"failure"}
    assert kinds(by_name["test_setup_error"]) == {"error"}
    assert "error" in kinds(by_name["test_teardown_error"])
    assert kinds(by_name["test_skipped"]) == {"skipped"}
    assert kinds(by_name["test_xfail"]) == {"skipped"}
    assert kinds(by_name["test_pass"]) == set()
    for name, ident in [
        ("test_fail", "O-1"),
        ("test_setup_error", "O-2"),
        ("test_teardown_error", "O-3"),
        ("test_skipped", "O-4"),
        ("test_xfail", "O-5"),
        ("test_pass", "O-6"),
    ]:
        assert ids_of(by_name[name]) == {ident}


@pytest.mark.trace("FR-001-AC-7")
def test_tc007_xdist_each_test_once_with_own_ids(pytester, monkeypatch):
    src = "import pytest\n" + "".join(
        f'\n@pytest.mark.trace("X-{i}")\ndef test_n{i}():\n    pass\n'
        for i in range(20)
    )
    result, root = run_suite(
        pytester, monkeypatch, src, "-p", "xdist.plugin", "-n", "2"
    )
    result.assert_outcomes(passed=20)
    got = {c.get("name"): ids_of(c) for c in cases(root)}
    assert len(cases(root)) == 20
    assert got == {f"test_n{i}": {f"X-{i}"} for i in range(20)}


@pytest.mark.trace("FR-001-AC-8")
def test_tc008_only_pytests_own_file_is_written(pytester, monkeypatch):
    before = {p.name for p in pytester.path.iterdir()}
    run_suite(pytester, monkeypatch, MARKED)
    after = {p.name for p in pytester.path.iterdir()}
    created = after - before - {"test_sample.py", "__pycache__"}
    assert created == {"out.xml"}


@pytest.mark.trace("FR-001-AC-9")
@pytest.mark.parametrize("family", ["xunit2", None])
def test_tc009_xunit2_fails_loudly(pytester, monkeypatch, family):
    result, root = run_suite(pytester, monkeypatch, MARKED, family=family)
    assert result.ret != 0
    result.stderr.fnmatch_lines(["*junit_family is 'xunit2'*-o junit_family=xunit1*"])
    assert root is None


@pytest.mark.trace("FR-001-AC-9")
@pytest.mark.parametrize("family", ["xunit1", "legacy"])
def test_tc009_xunit1_and_legacy_carry_all_attributes(pytester, monkeypatch, family):
    result, root = run_suite(pytester, monkeypatch, MARKED, family=family)
    result.assert_outcomes(passed=1)
    (case,) = cases(root)
    assert trace_of(case) == "FR-001-AC-1"
    assert case.get("name") == case.get("classname") == "test_marked"
    assert case.get("file") == "test_sample.py"


@pytest.mark.trace("FR-001-AC-10")
def test_tc010_cost_under_five_percent(pytester):
    src = "import pytest, time\n" + "".join(
        f'\n@pytest.mark.trace("P-{i}")\ndef test_n{i}():\n    time.sleep(0.004)\n'
        for i in range(500)
    )
    pytester.makepyfile(test_perf=src)
    base_env = {
        **os.environ,
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTHONPATH": os.pathsep.join(sys.path),
    }
    base_env.pop("QUIRE_TRACE_EMIT", None)
    args = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]
    args += ["-p", "ix_trace_py.plugin", "--junit-xml=perf.xml"]
    args += ["-o", "junit_family=xunit1", str(pytester.path / "test_perf.py")]

    def run(emit: bool) -> float:
        env = {**base_env, **({"QUIRE_TRACE_EMIT": "1"} if emit else {})}
        start = time.perf_counter()
        subprocess.run(args, env=env, check=True, capture_output=True)
        return time.perf_counter() - start

    # Adjacent on/off pairs share machine load; alternate which goes first.
    ratios = []
    for n in range(11):
        if n % 2:
            on = run(True)
            off = run(False)
        else:
            off = run(False)
            on = run(True)
        ratios.append(on / off)
    assert median(ratios) < 1.05


@pytest.mark.trace("FR-001-AC-8")
def test_tc008_enabled_run_without_a_result_file_is_harmless(pytester, monkeypatch):
    src = MARKED + '\ndef doc():\n    """\n    >>> 1\n    1\n    """\n'
    monkeypatch.setenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    monkeypatch.setenv("QUIRE_TRACE_EMIT", "1")
    pytester.makepyfile(test_sample=src)
    result = pytester.runpytest(
        "-p",
        "ix_trace_py.plugin",
        "--doctest-modules",
        "-p",
        "no:cacheprovider",
        "-o",
        "junit_family=xunit1",
    )
    result.assert_outcomes(passed=2)
    assert not (pytester.path / "out.xml").exists()


@pytest.mark.trace("FR-001-AC-9")
def test_tc009_without_the_junit_plugin_there_is_no_family_to_check(
    pytester, monkeypatch
):
    monkeypatch.setenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    monkeypatch.setenv("QUIRE_TRACE_EMIT", "1")
    pytester.makepyfile(test_sample=MARKED)
    result = pytester.runpytest(
        "-p", "ix_trace_py.plugin", "-p", "no:junitxml", "-p", "no:cacheprovider"
    )
    result.assert_outcomes(passed=1)


@pytest.mark.trace("FR-001-AC-4")
@pytest.mark.parametrize("bad", ['ids="X"', '"X", why="Y"'])
def test_tc015_marker_keyword_arguments_fail_naming_the_test(
    pytester, monkeypatch, bad
):
    src = f"""
import pytest

@pytest.mark.trace({bad})
def test_kwargs():
    pass
"""
    result, root = run_suite(pytester, monkeypatch, src)
    assert result.ret != 0
    result.stderr.fnmatch_lines(["*test_sample.py::test_kwargs*keyword*"])
    assert cases(root) == []


@pytest.mark.trace("FR-001-AC-3")
def test_tc014_parametrize_marks_are_not_function_markers(pytester, monkeypatch):
    src = """
import pytest

@pytest.mark.trace("DEF-1")
@pytest.mark.parametrize(
    "n", [1, pytest.param(2, marks=pytest.mark.trace("PARAM-9"))]
)
def test_p(n):
    pass

@pytest.mark.parametrize("n", [pytest.param(1, marks=pytest.mark.trace("PARAM-8"))])
def test_only_param_marked(n):
    pass
"""
    _, root = run_suite(pytester, monkeypatch, src)
    tagged = [ids_of(c) for c in cases(root) if c.get("name") == "test_p"]
    assert tagged == [{"DEF-1"}, {"DEF-1"}]
    assert all(not ids & {"PARAM-8", "PARAM-9"} for ids in map(ids_of, cases(root)))


@pytest.mark.trace("FR-001-AC-1")
def test_tc012_installed_plugin_autoloads(pytester, monkeypatch):
    """The installed entry point alone registers `trace` and emits: no `-p`,
    no conftest, plugin autoload left on."""
    monkeypatch.delenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", raising=False)
    monkeypatch.setenv("QUIRE_TRACE_EMIT", "1")
    pytester.makepyfile(test_sample=MARKED)
    result = pytester.runpytest_subprocess(
        "--strict-markers",
        "-W",
        "error",
        "--junit-xml=out.xml",
        "-o",
        "junit_family=xunit1",
        "-p",
        "no:cacheprovider",
    )
    result.assert_outcomes(passed=1)
    (case,) = cases(ET.parse(pytester.path / "out.xml").getroot())
    assert trace_of(case) == "FR-001-AC-1"
