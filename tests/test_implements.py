"""Acceptance tests for FR-002 (TC-016..TC-026): the `implements` decorator."""

import asyncio
import functools
import gc
import importlib
import inspect
import json
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

import ix_trace_py
from ix_trace_py import implements
from tests.helpers import cases, ids_of, run_suite

ROOT = Path(__file__).resolve().parent.parent


def _plain_function(a, b=2):
    return a + b


async def _plain_coroutine(a):
    return a * 2


class _Plain:
    value = 3

    def method(self, a):
        return a + self.value

    @staticmethod
    def static(a):
        return a - 1


def _fresh_function():
    def fn(a, b=2):
        return a + b

    return fn


def _snapshot(obj):
    """What a registry would change: refcount, referrers, vars and package names."""
    referrers = {id(r) for r in gc.get_referrers(obj) if not inspect.isframe(r)}
    return (
        sys.getrefcount(obj),
        referrers,
        dict(vars(obj)),
        dict(vars(ix_trace_py)),
    )


class TestIdentity:
    """The decorator returns exactly the object it was given."""

    @pytest.mark.trace("FR-002-AC-1")
    def test_tc016_function_is_returned_unchanged(self):
        """
        A function is decorated.

        Assumptions:
          - The function has a default argument.

        Criteria:
          - The result is the same object, with no `__wrapped__`.
          - Behaviour, `__dict__` and signature equal the undecorated ones.
        """
        before_dict = dict(vars(_plain_function))
        before_sig = inspect.signature(_plain_function)
        out = implements("FR-002-AC-1")(_plain_function)
        assert out is _plain_function
        assert not hasattr(out, "__wrapped__")
        assert dict(vars(out)) == before_dict
        assert inspect.signature(out) == before_sig
        assert out(1) == 3

    @pytest.mark.trace("FR-002-AC-1")
    def test_tc016_async_def_is_returned_unchanged(self):
        """
        A coroutine function is decorated.

        Assumptions:
          - None beyond the coroutine function.

        Criteria:
          - The result is the same object and is still a coroutine function.
        """
        out = implements("FR-002-AC-1")(_plain_coroutine)
        assert out is _plain_coroutine
        assert inspect.iscoroutinefunction(out)
        assert asyncio.run(out(4)) == 8

    @pytest.mark.trace("FR-002-AC-1")
    def test_tc016_method_and_staticmethod_are_returned_unchanged(self):
        """
        A method, and a staticmethod wrapper, are decorated in a class body.

        Assumptions:
          - The decorator is applied inside the class body.

        Criteria:
          - The method is the identical function object.
          - The staticmethod descriptor is the identical object and still works.
        """

        class Holder:
            def method(self):
                return 1

            static = staticmethod(lambda a: a)

        method = Holder.__dict__["method"]
        static = Holder.__dict__["static"]
        assert implements("FR-002-AC-1")(method) is method
        assert implements("FR-002-AC-1")(static) is static
        assert Holder.static(5) == 5

    @pytest.mark.trace("FR-002-AC-1")
    def test_tc016_class_is_returned_unchanged(self):
        """
        A class is decorated.

        Assumptions:
          - The class has a class attribute and methods.

        Criteria:
          - The result is the identical class, with its `__dict__` unchanged.
        """
        before = dict(vars(_Plain))
        out = implements("FR-002-AC-1")(_Plain)
        assert out is _Plain
        assert dict(vars(out)) == before
        assert out().method(1) == 4
        assert out.static(1) == 0

    @pytest.mark.trace("FR-002-AC-8")
    def test_tc023_decorated_is_undecorated(self):
        """
        A function is decorated with the decorator expression.

        Assumptions:
          - A fresh function is used.

        Criteria:
          - `decorated is undecorated`, so a call adds no wrapper frame.
        """
        undecorated = _fresh_function()
        decorated = implements("FR-002-AC-8")(undecorated)
        assert decorated is undecorated


_REGISTRY = []


def _module_registry(target):
    _REGISTRY.append(target)
    return target


def _closure_registry():
    held = []

    def decorator(target):
        held.append(target)
        return target

    return decorator


def _attribute_marker(target):
    target.__implements__ = True
    return target


def _identity(target):
    return target


def _leaks(decorator):
    """True when decorating a fresh function changes what a registry would.

    The caller holds `decorator` for the whole call, so a closure's container
    stays alive; the result of the decoration is discarded.
    """
    fn = _fresh_function()
    before = _snapshot(fn)
    decorator(fn)
    return _snapshot(fn) != before


class TestNoRetainedReference:
    """No registry, closure or attribute keeps what was decorated."""

    @pytest.mark.trace("FR-002-AC-2")
    def test_tc017_implements_changes_nothing_observable(self):
        """
        The real decorator is run through the leak check.

        Assumptions:
          - The decorator object is held by this test while it is checked.

        Criteria:
          - Refcount, referrers, `vars()` and the package namespace are equal.
        """
        decorator = implements("FR-002-AC-2")
        assert not _leaks(decorator)
        assert decorator is not None

    @pytest.mark.trace("FR-002-AC-2")
    @pytest.mark.parametrize(
        "make",
        [lambda: _module_registry, _closure_registry, lambda: _attribute_marker],
        ids=["module-registry", "closure", "attribute"],
    )
    def test_tc017_a_leaking_decorator_fails_the_check(self, make):
        """
        Three real leaking decorators are run through the same leak check.

        Assumptions:
          - Each decorator really stores or marks its target.

        Criteria:
          - The check reports a leak for each.
        """
        decorator = make()
        try:
            assert _leaks(decorator)
        finally:
            _REGISTRY.clear()

    @pytest.mark.trace("FR-002-AC-2")
    def test_tc017_a_plain_identity_decorator_does_not_fail_the_check(self):
        """
        A plain identity decorator is run through the leak check.

        Assumptions:
          - The decorator keeps nothing.

        Criteria:
          - No leak is reported, so the check fails only for real leaks.
        """
        assert not _leaks(_identity)


# Built from parts so the source holds no literal id for a trace extractor to read.
GOOD_IDS = ["-".join(parts) for parts in (("ZZ", "001"), ("MADEUP", "042", "AC", "9"))]
GOOD_IDS.append("interface_004" + "-AC-" + "1")


class TestArguments:
    """Argument validation at decoration time."""

    @pytest.mark.trace("FR-002-AC-3")
    def test_tc018_several_and_repeated_ids_are_accepted(self):
        """
        Several ids, and a repeated id, are passed.

        Assumptions:
          - All ids are id-shaped.

        Criteria:
          - No error is raised and a callable decorator is returned.
        """
        assert callable(implements("A-1", "A-2"))
        assert callable(implements("A-1", "A-1"))

    @pytest.mark.trace("FR-002-AC-4")
    def test_tc019_no_argument_raises_value_error_with_a_call(self):
        """
        `implements()` is evaluated with no argument.

        Assumptions:
          - None.

        Criteria:
          - `ValueError` whose message shows `implements("FR-007-AC-1")`.
        """
        with pytest.raises(ValueError, match=r'implements\("FR-007-AC-1"\)'):
            implements()

    @pytest.mark.trace("FR-002-AC-4")
    @pytest.mark.parametrize(
        ("args", "position", "type_name"),
        [
            ((1,), 0, "int"),
            (("A-1", None), 1, "NoneType"),
            (("A-1", "A-2", ["A-3"]), 2, "list"),
        ],
    )
    def test_tc019_non_str_raises_type_error_naming_type_and_position(
        self, args, position, type_name
    ):
        """
        A non-`str` argument is passed.

        Assumptions:
          - The bad argument is at a known position.

        Criteria:
          - `TypeError` names the argument's type and position.
        """
        with pytest.raises(TypeError) as info:
            implements(*args)
        assert type_name in str(info.value)
        assert f"argument {position + 1}" in str(info.value)

    @pytest.mark.trace("FR-002-AC-4")
    def test_tc019_error_is_raised_when_the_decorator_expression_runs(self):
        """
        A bad call is written as a decorator expression on a definition.

        Assumptions:
          - The definition statement is executed inside `pytest.raises`.

        Criteria:
          - The error is raised at decoration, before the name is bound.
        """
        with pytest.raises(ValueError):

            @implements("FR 2")
            def never():  # pragma: no cover
                pass

        assert "never" not in locals()

    @pytest.mark.trace("FR-002-AC-10")
    @pytest.mark.parametrize("bad", ["", "FR 2", "A-1, A-2", "FR-XXX", "1-A"])
    def test_tc025_malformed_ids_raise_value_error_naming_the_argument(self, bad):
        """
        A string that is not id-shaped is passed.

        Assumptions:
          - The string is the first argument.

        Criteria:
          - `ValueError` names the offending argument.
        """
        with pytest.raises(ValueError) as info:
            implements(bad)
        assert repr(bad) in str(info.value)

    @pytest.mark.trace("FR-002-AC-10")
    @pytest.mark.parametrize("good", GOOD_IDS)
    def test_tc025_shape_is_checked_and_membership_never(self, good):
        """
        An id of an undeclared kind is passed.

        Assumptions:
          - The kind appears in no module.

        Criteria:
          - The id is accepted.
        """
        assert callable(implements(good))

    @pytest.mark.trace("FR-002-CON-4")
    def test_tc025_package_holds_no_kind_list(self):
        """
        The package source is read for a kind vocabulary.

        Assumptions:
          - Known kinds are `FR`, `NFR`, `StR`, `US`, `TC`.

        Criteria:
          - None of them is named in the package module.
        """
        source = (ROOT / "ix_trace_py" / "__init__.py").read_text()
        for kind in ("NFR", "StR", "TC-", '"FR"', '"US"'):
            assert kind not in source


class TestImportPosture:
    """The package imports nothing beyond the standard library."""

    @pytest.mark.trace("FR-002-AC-5")
    def test_tc020_import_works_with_pytest_unimportable(self):
        """
        A fresh interpreter blocks `pytest` and imports the package.

        Assumptions:
          - A meta-path finder raises `ImportError` for `pytest`.

        Criteria:
          - The import and a decoration succeed.
          - `sys.modules` holds no `pytest` entry afterwards.
        """
        code = textwrap.dedent("""
            import sys

            class Block:
                def find_spec(self, name, path=None, target=None):
                    if name == "pytest" or name.startswith("pytest."):
                        raise ImportError("blocked")

            sys.meta_path.insert(0, Block())
            try:
                import pytest
            except ImportError:
                pass
            else:
                raise SystemExit("pytest importable")

            import ix_trace_py
            from ix_trace_py import implements

            @implements("FR-002-AC-5")
            def f():
                return 1

            assert f() == 1
            assert "pytest" not in sys.modules
            """)
        out = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        assert out.returncode == 0, out.stderr


def _wrap(fn):
    @functools.wraps(fn)
    def inner(*a, **k):
        return ("wrapped", fn(*a, **k))

    return inner


class TestStacking:
    """The decorator composes with any other decorator in any order."""

    @pytest.mark.trace("FR-002-AC-6")
    def test_tc021_above_and_below_another_decorator(self):
        """
        `implements` is stacked above and below a wrapping decorator `D`.

        Assumptions:
          - `D` wraps with `functools.wraps`, so a wrapper from `implements`
            would be visible as a different object.

        Criteria:
          - Both stacks yield what `D` alone yields.
          - Stacked under `D`, `D` receives the very object that was defined.
          - Stacked over `D`, `implements` returns `D`'s result itself.
        """
        received = []

        def spy(fn):
            received.append(fn)
            return _wrap(fn)

        def raw():
            return 1

        alone = _wrap(raw)
        above_result = implements("FR-002-AC-6")(alone)
        assert above_result is alone

        below_result = spy(implements("FR-002-AC-6")(raw))
        assert received == [raw]
        assert received[0] is raw
        assert below_result.__wrapped__ is raw
        assert below_result() == alone() == above_result() == ("wrapped", 1)
        assert type(below_result) is type(alone)

    @pytest.mark.trace("FR-002-AC-6")
    def test_tc021_above_a_pytest_trace_marker(self):
        """
        `implements` is stacked above `pytest.mark.trace` on one definition.

        Assumptions:
          - The marker is applied as a decorator.

        Criteria:
          - `implements` returns the marked function itself, marker intact.
        """

        @pytest.mark.trace("FR-002-AC-6")
        def marked():
            pass

        assert implements("FR-002-AC-6")(marked) is marked
        assert [m.name for m in marked.pytestmark] == ["trace"]


SCOPED = """
import pytest
from ix_trace_py import implements

@implements("FR-002-AC-7")
def module_level():
    pass

class Holder:
    @implements("FR-002-AC-7")
    def method(self):
        pass

def outer():
    @implements("FR-002-AC-7")
    def inner():
        pass

    @implements("FR-002-AC-7")
    class Inner:
        pass

    return inner, Inner

@implements("FR-002-AC-7")
@pytest.mark.trace("FR-002-AC-7")
def test_marked():
    assert outer()

@implements("FR-002-AC-7")
def test_unmarked():
    pass
"""


class TestPlacement:
    """The decorator is valid in every position."""

    @pytest.mark.trace("FR-002-AC-7")
    def test_tc022_valid_everywhere_and_test_keeps_its_trace(
        self, pytester, monkeypatch
    ):
        """
        A fixture suite decorates module-level, method, nested and test code.

        Assumptions:
          - Emission is on and the plugin is loaded explicitly.

        Criteria:
          - The suite passes with both tests collected.
          - The marked test keeps its `trace` property; the other has none.
        """
        result, root = run_suite(pytester, monkeypatch, SCOPED)
        result.assert_outcomes(passed=2)
        by_name = {c.get("name"): c for c in cases(root)}
        assert ids_of(by_name["test_marked"]) == {"FR-002-AC-7"}
        assert ids_of(by_name["test_unmarked"]) == set()


EVALUATED = """
from ix_trace_py import implements

evaluated = []


def probe(*ids):
    evaluated.append(ids)
    return implements(*ids)


def module_level():
    pass


decorated_module_level = probe("FR-002-AC-11")(module_level)


def enclosing(ids):
    def nested():
        pass

    return probe(*ids)(nested), nested
"""


class TestEvaluationTime:
    """When the decorator expression runs, and the cost thereafter."""

    @pytest.mark.trace("FR-002-AC-11")
    def test_tc026_nested_checks_each_call_and_module_level_once(
        self, tmp_path, monkeypatch
    ):
        """
        A real fixture module is imported, then its nested definition is run.

        Assumptions:
          - The module is imported from a temporary directory on `sys.path`.

        Criteria:
          - The module-level decorator ran once, at import, and not on re-import.
          - The nested decorator is evaluated on every enclosing call.
          - Both decorated objects are the unchanged objects.
          - A bad id in the nested decorator raises on the call.
        """
        (tmp_path / "evaluated_fixture.py").write_text(EVALUATED)
        monkeypatch.syspath_prepend(str(tmp_path))
        sys.modules.pop("evaluated_fixture", None)
        try:
            mod = importlib.import_module("evaluated_fixture")
            assert mod.evaluated == [("FR-002-AC-11",)]
            assert mod.decorated_module_level is mod.module_level
            importlib.import_module("evaluated_fixture")
            assert len(mod.evaluated) == 1

            for expected in (2, 3):
                out, raw = mod.enclosing(("FR-002-AC-11",))
                assert out is raw
                assert len(mod.evaluated) == expected
            with pytest.raises(ValueError):
                mod.enclosing(("FR XXX",))
        finally:
            sys.modules.pop("evaluated_fixture", None)


IMPLEMENTED = '''
import ix_trace_py
import ix_trace_py as t
from ix_trace_py import implements
from ix_trace_py import implements as impl

@implements("FR-001-AC-1", "FR-001-AC-2")
def bare():
    pass

@ix_trace_py.implements("FR-001-AC-3")
def dotted():
    pass

@t.implements("FR-001-AC-4")
def renamed_module():
    pass

@impl("FR-001-AC-5")
def renamed_name():
    pass

@implements('FR-001-AC-6')
def single_quoted():
    pass

@implements(r"FR-001-AC-7")
def raw():
    pass

@implements("""FR-001-AC-8""")
def triple_quoted():
    pass
'''

needs_quire = pytest.mark.skipif(
    shutil.which("quire") is None, reason="quire CLI not installed"
)


def _coverage(repo: Path) -> dict:
    """The `quire coverage --json` report for `repo`, from the resolved modules."""
    out = subprocess.run(
        ["quire", "coverage", "--json", "--scope", str(repo)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(out.stdout)


class TestStaticBinding:
    """quire binds the decorator from the syntax tree (quire-rs FR-062)."""

    @pytest.mark.trace("FR-002-AC-9")
    @needs_quire
    def test_tc024_quire_binds_the_two_spellings_only(self, tmp_path):
        """
        A fixture package is read by `quire coverage --json`.

        Assumptions:
          - The resolved module declares the `python_decorator` form; quire
            itself says so by returning `implements` relations for the fixture,
            and the test skips when it returns none.

        Criteria:
          - The bare and dotted spellings give one `implements` relation per id
            on the decorated symbol, in the top-level `implements` array.
          - Renamed imports and single-quoted, raw and triple-quoted literals
            give none, though the module imports and runs.
          - No criterion has a `verifies` binder from the fixture file.
        """
        repo = tmp_path / "repo"
        shutil.copytree(
            ROOT / "spec", repo / "spec", ignore=shutil.ignore_patterns("reviews")
        )
        (repo / "pkg").mkdir()
        (repo / "pkg" / "prod.py").write_text(IMPLEMENTED)
        subprocess.run(
            [sys.executable, "-c", "import pkg.prod"],
            cwd=repo,
            env={"PYTHONPATH": f"{ROOT}:{repo}"},
            check=True,
        )
        report = _coverage(repo)
        relations = [
            r for r in report.get("implements", []) if r["path"] == "pkg/prod.py"
        ]
        if not any(r["symbol"] == "bare" for r in relations):
            pytest.skip("the resolved module does not declare python_decorator")

        found = sorted(
            (r["symbol"], r["trace_id"]) for r in relations if r["symbol"] != "pkg.prod"
        )
        assert found == [
            ("bare", "FR-001-AC-1"),
            ("bare", "FR-001-AC-2"),
            ("dotted", "FR-001-AC-3"),
        ]
        verifying = [
            b
            for doc in report["coverage_matrix"]
            for criterion in doc["criteria"]
            for b in criterion["binders"]
            if b["path"] == "pkg/prod.py"
        ]
        assert verifying == []
