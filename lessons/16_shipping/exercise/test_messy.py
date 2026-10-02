"""Lesson 16 exercise tests. Behaviour must be preserved AND the quality tools must pass.

Run: uv run pytest lessons/16_shipping/exercise -v
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from messy import average_words, find_note, load_config, parse_tags, slug

FILE = Path(__file__).parent / "messy.py"


# --- behaviour (all pass except the hidden-state one, which is a real bug to fix) -------------------------
def test_parse_tags():
    assert parse_tags("AI, llm, ai, ,Python") == ["ai", "llm", "python"]


def test_parse_tags_has_no_hidden_state():
    parse_tags("ai")
    assert parse_tags("ai") == ["ai"], "the mutable default argument leaks state between calls!"


def test_average_words():
    assert average_words([{"body": "one two"}, {"body": "one two three four"}]) == 3.0
    assert average_words([]) is None


def test_find_note():
    notes = [{"id": 1}, {"id": 2}]
    assert find_note(notes, 2) == {"id": 2}
    assert find_note(notes, 9) is None


def test_load_config(tmp_path):
    good = tmp_path / "c.json"
    good.write_text(json.dumps({"model": "claude-sonnet-5-5"}), encoding="utf-8")
    assert load_config(good)["model"] == "claude-sonnet-5-5"
    assert load_config(tmp_path / "missing.json") == {"model": "claude-opus-5-5"}
    bad = tmp_path / "bad.json"
    bad.write_text("{oops", encoding="utf-8")
    assert load_config(bad) == {"model": "claude-opus-5-5"}


def test_slug():
    assert slug("Hello, World!") == "hello-world"


# --- quality gates ------------------------------------------------------------------------------------------
def run(*cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", *cmd], capture_output=True, text=True)


def test_ruff_lint_passes():
    r = run("ruff", "check", "--select", "E,F,W,I,UP,B,SIM", "--line-length", "120", str(FILE))
    assert r.returncode == 0, r.stdout


def test_ruff_format_is_clean():
    r = run("ruff", "format", "--check", "--line-length", "120", str(FILE))
    assert r.returncode == 0, "run: uv run ruff format --line-length 120 " + str(FILE)


def test_mypy_strict_passes():
    r = run("mypy", "--strict", "--no-error-summary", str(FILE))
    assert r.returncode == 0, r.stdout


@pytest.mark.parametrize("forbidden", ["except:", "== None", "List[", "Optional[", "Dict["])
def test_no_legacy_patterns(forbidden):
    assert forbidden not in FILE.read_text(encoding="utf-8")
