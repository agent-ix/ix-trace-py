"""TC-005 (extractor equality) and TC-011 (end to end), against the real
`quire` and `quoin` CLIs. Skipped where those tools are not installed."""

import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
needs_quire = pytest.mark.skipif(
    shutil.which("quire") is None, reason="quire CLI not installed"
)
needs_quoin = pytest.mark.skipif(
    shutil.which("quoin") is None, reason="quoin CLI not installed"
)

SUITES = """---
id: SR-001
type: SuiteRegistry
title: "suite registry"
---

# SR-001: suite registry

## Suites

| ID | Name | Command | Tool | Evidence Kind |
|----|------|---------|------|---------------|
| SUITE-001 | pytest | `pytest` | pytest | Unit |
"""

SHAPES = """
import pytest

@pytest.mark.trace("FR-001-AC-1")
def test_top():
    pass

class TestOuter:
    @pytest.mark.trace("FR-001-AC-2")
    def test_method(self):
        pass

    class TestInner:
        @pytest.mark.trace("FR-001-AC-3")
        def test_deep(self):
            pass

@pytest.mark.trace("FR-001-AC-4")
@pytest.mark.parametrize("n", [1, 2])
def test_param(n):
    pass
"""

TAGGED = """
import pytest

@pytest.mark.trace("FR-001-AC-1")
def test_tagged():
    assert {outcome}
"""


def make_repo(tmp_path: Path, tests: str) -> Path:
    """A throwaway git repo holding this repo's spec and one test file."""
    repo = tmp_path / "repo"
    shutil.copytree(
        ROOT / "spec", repo / "spec", ignore=shutil.ignore_patterns("reviews")
    )
    (repo / "spec" / "evidence").mkdir()
    (repo / "spec" / "evidence" / "suites.md").write_text(SUITES)
    (repo / "tests").mkdir()
    (repo / "tests" / "test_sample.py").write_text(tests)
    return repo


def git(repo: Path, *args: str) -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@example.com",
    }
    out = subprocess.run(
        ["git", *args], cwd=repo, env=env, check=True, capture_output=True, text=True
    )
    return out.stdout.strip()


def run_pytest(repo: Path) -> ET.Element:
    """Run real pytest in a subprocess with emission on; return the JUnit."""
    env = {
        **os.environ,
        "QUIRE_TRACE_EMIT": "1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTHONPATH": str(ROOT),
    }
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "ix_trace_py.plugin",
            "-p",
            "no:cacheprovider",
            "-o",
            "junit_family=xunit1",
            "--junit-xml=results.xml",
            "tests",
        ],
        cwd=repo,
        env=env,
        capture_output=True,
    )
    return ET.parse(repo / "results.xml").getroot()


@pytest.mark.trace("FR-001-AC-5")
@needs_quire
def test_tc005_symbols_equal_quire_coverage(tmp_path):
    repo = make_repo(tmp_path, SHAPES)
    root = run_pytest(repo)
    report = json.loads(
        subprocess.run(
            ["quire", "coverage", "--json", "--scope", str(repo)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    binders = {
        (b["qualified_name"], b["path"])
        for doc in report["coverage_matrix"]
        for criterion in doc["criteria"]
        for b in criterion["binders"]
    }
    emitted = {
        (c.get("name"), c.get("file"))
        for c in root.iter("testcase")
        if c.get("classname") == c.get("name")
    }
    assert len(list(root.iter("testcase"))) == 5
    assert (
        emitted
        == binders
        == {
            ("test_top", "tests/test_sample.py"),
            ("TestOuter.test_method", "tests/test_sample.py"),
            ("TestOuter.TestInner.test_deep", "tests/test_sample.py"),
            ("test_param", "tests/test_sample.py"),
        }
    )


def record(repo: Path) -> dict:
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "fixture")
    out = subprocess.run(
        [
            "quoin",
            "evidence",
            "record",
            "--suite",
            "SUITE-001",
            "--commit",
            git(repo, "rev-parse", "HEAD"),
            "--tool",
            "pytest",
            "--adapter",
            "junit",
            "--results",
            "results.xml",
            "--json",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return json.loads(out)


@pytest.mark.trace("FR-001-AC-11")
@needs_quoin
def test_tc011_passing_suite_binds_its_obligation(tmp_path):
    repo = make_repo(tmp_path, TAGGED.format(outcome="True"))
    run_pytest(repo)
    assert record(repo)["bound"] == ["FR-001-AC-1"]


@pytest.mark.trace("FR-001-AC-11")
@needs_quoin
def test_tc011_failing_suite_binds_nothing(tmp_path):
    repo = make_repo(tmp_path, TAGGED.format(outcome="False"))
    root = run_pytest(repo)
    assert [c.tag for c in root.iter("failure")] == ["failure"]
    assert record(repo)["bound"] == []
