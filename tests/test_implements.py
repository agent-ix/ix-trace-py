"""Acceptance tests for FR-002 (TC-016..TC-026): the `implements` decorator."""

import asyncio
import functools
import gc
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


def _registry_in_module(registry):
    def decorator(target):
        registry.append(target)
        return target

    return decorator


def _registry_closure():
    held = []

    def decorator(target):
        held.append(target)
        return target

    return decorator


def _setattr_marker(target):
    target.__implements__ = True
    return target


class TestNoRetainedReference:
    """No registry, closure or attribute keeps what was decorated."""

    @pytest.mark.trace("FR-002-AC-2")
    def test_tc017_implements_changes_nothing_observable(self):
        """
        A function is decorated and its observable state is compared.

        Assumptions:
          - The decorated object is held by this test's locals only.

        Criteria:
          - Refcount, referrer set, `vars()` and the package namespace are equal.
        """
        fn = _fresh_function()
        before = _snapshot(fn)
        decorator = implements("FR-002-AC-2")
        out = decorator(fn)
        del out
        assert _snapshot(fn) == before

    @pytest.mark.trace("FR-002-AC-2")
    @pytest.mark.parametrize(
        "make",
        [
            lambda: _registry_in_module([]),
            _registry_closure,
            lambda: _setattr_marker,
        ],
        ids=["list-registry", "closure", "attribute"],
    )
    def test_tc017_a_retaining_decorator_would_fail_the_check(self, make):
        """
        Three decorators that retain or mark their target run through the check.

        Assumptions:
          - The snapshot helper is the one used for `implements`.

        Criteria:
          - Each retaining decorator changes the snapshot.
        """
        fn = _fresh_function()
        before = _snapshot(fn)
        keep = make()(fn)
        assert keep is fn
        assert _snapshot(fn) != before


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
        assert f"argument {position}" in str(info.value)

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
    @pytest.mark.parametrize(
        "good", ["ZZ-001", "MADEUP-042-AC-9", "interface_004-AC-1"]
    )
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


def _record(fn):
    _record.seen.append(fn)
    return fn


_record.seen = []


class TestStacking:
    """The decorator composes with any other decorator in any order."""

    @pytest.mark.trace("FR-002-AC-6")
    def test_tc021_above_and_below_another_decorator(self):
        """
        `implements` is stacked above and below a wrapping decorator `D`.

        Assumptions:
          - `D` wraps with `functools.wraps`.

        Criteria:
          - Both stacks yield what `D` alone yields.
          - Under `D`, `D` receives the unchanged object.
        """

        def base():
            return 1

        alone = _wrap(base)

        @implements("FR-002-AC-6")
        @_wrap
        def above():
            return 1

        @_wrap
        @implements("FR-002-AC-6")
        def below():
            return 1

        assert above() == alone() == below() == ("wrapped", 1)
        assert above.__wrapped__.__name__ == "above"
        assert type(above) is type(alone)

        _record.seen.clear()

        @_record
        @implements("FR-002-AC-6")
        def seen():
            pass

        assert _record.seen == [seen]

    @pytest.mark.trace("FR-002-AC-6")
    def test_tc021_above_a_pytest_trace_marker(self):
        """
        `implements` is stacked above `pytest.mark.trace` on one definition.

        Assumptions:
          - The marker is applied as a decorator.

        Criteria:
          - The marker is still present on the result, which is the same object.
        """

        @implements("FR-002-AC-6")
        @pytest.mark.trace("FR-002-AC-6")
        def marked():
            pass

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


class TestEvaluationTime:
    """When the decorator expression runs, and the cost thereafter."""

    @pytest.mark.trace("FR-002-AC-11")
    def test_tc026_nested_checks_each_call_and_module_level_once(self):
        """
        A module is imported once, and its nested definition called twice.

        Assumptions:
          - A bad id in the nested decorator raises on each call.
          - A module-level decorator runs at import only.

        Criteria:
          - The nested decorator is evaluated on every enclosing call.
          - The nested object is the unchanged object each time.
          - The module-level one ran once, at import.
        """
        evaluated = []

        def probe(*ids):
            evaluated.append(ids)
            return implements(*ids)

        @probe("FR-002-AC-11")
        def module_like():
            pass

        assert evaluated == [("FR-002-AC-11",)]

        def enclosing(ids):
            def nested():
                pass

            return probe(*ids)(nested), nested

        out, raw = enclosing(("FR-002-AC-11",))
        assert out is raw
        out, raw = enclosing(("FR-002-AC-11",))
        assert out is raw
        assert len(evaluated) == 3
        with pytest.raises(ValueError):
            enclosing(("FR XXX",))


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


def _declares_python_decorator() -> bool:
    modules = Path.home() / ".ix" / "filament" / "modules" / "spec-artifacts-process"
    manifest = modules / "manifest.yaml"
    return manifest.exists() and "python_decorator" in manifest.read_text()


class TestStaticBinding:
    """quire binds the decorator from the syntax tree (quire-rs FR-062)."""

    @pytest.mark.trace("FR-002-AC-9")
    @needs_quire
    @pytest.mark.skipif(
        not _declares_python_decorator(),
        reason="spec-artifacts-process does not declare python_decorator yet",
    )
    def test_tc024_quire_binds_the_two_spellings_only(self, tmp_path):
        """
        A fixture package is read by `quire coverage --json`.

        Assumptions:
          - The installed module declares the `python_decorator` form.

        Criteria:
          - The bare and dotted spellings bind their ids to their symbols.
          - Renamed imports and single-quoted, raw and triple-quoted literals
            bind nothing, though the module imports and runs.
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
        report = json.loads(
            subprocess.run(
                ["quire", "coverage", "--json", "--scope", str(repo)],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
        )
        bound = {
            criterion["id"]: {b["qualified_name"] for b in criterion["binders"]}
            for doc in report["coverage_matrix"]
            for criterion in doc["criteria"]
            if criterion["id"].startswith("FR-001-AC-")
        }
        assert bound["FR-001-AC-1"] == {"bare"}
        assert bound["FR-001-AC-2"] == {"bare"}
        assert bound["FR-001-AC-3"] == {"dotted"}
        for ac in range(4, 9):
            assert bound[f"FR-001-AC-{ac}"] == set()
