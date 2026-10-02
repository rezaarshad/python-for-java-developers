"""Provided tests for the notes CLI. Run: uv run pytest lessons/09_cli/exercise -v"""

import json

import pytest
from typer.testing import CliRunner

from cli_app import app

runner = CliRunner()


@pytest.fixture
def notes_file(tmp_path):
    return tmp_path / "notes.json"


def run(notes_file, *args, input=None):
    return runner.invoke(app, ["--file", str(notes_file), *args], input=input)


@pytest.fixture
def populated(notes_file):
    run(notes_file, "add", "Python CLIs", "-b", "typer and rich", "-t", "Python", "-t", "cli")
    run(notes_file, "add", "Claude API", "-b", "messages in python", "-t", "ai")
    run(notes_file, "add", "Groceries", "-t", "python")
    return notes_file


def test_add_creates_file_and_prints(notes_file):
    result = run(notes_file, "add", "RAG", "--body", "retrieval", "--tag", "AI", "--tag", "llm")
    assert result.exit_code == 0, result.output
    assert "Added note 1: RAG" in result.output
    assert json.loads(notes_file.read_text()) == [
        {"id": 1, "title": "RAG", "body": "retrieval", "tags": ["ai", "llm"]}
    ]


def test_add_increments_ids(populated):
    assert [n["id"] for n in json.loads(populated.read_text())] == [1, 2, 3]


def test_list_empty(notes_file):
    result = run(notes_file, "list")
    assert result.exit_code == 0
    assert "No notes yet." in result.output


def test_list_shows_table(populated):
    result = run(populated, "list")
    assert result.exit_code == 0
    for text in ["ID", "Title", "Tags", "Python CLIs", "Claude API", "python, cli"]:
        assert text in result.output


def test_list_filter_by_tag(populated):
    result = run(populated, "list", "--tag", "ai")
    assert "Claude API" in result.output
    assert "Groceries" not in result.output


def test_search(populated):
    result = run(populated, "search", "PYTHON")
    assert result.exit_code == 0
    assert result.output.splitlines() == ["1: Python CLIs", "2: Claude API"]


def test_search_no_match_exits_1(populated):
    result = run(populated, "search", "kotlin")
    assert result.exit_code == 1
    assert "No matches for 'kotlin'" in result.output


def test_delete_with_yes(populated):
    result = run(populated, "delete", "2", "--yes")
    assert result.exit_code == 0
    assert "Deleted note 2" in result.output
    assert [n["id"] for n in json.loads(populated.read_text())] == [1, 3]


def test_delete_confirm_declined(populated):
    result = run(populated, "delete", "1", input="n\n")
    assert result.exit_code == 0
    assert "Delete 'Python CLIs'?" in result.output
    assert "Cancelled." in result.output
    assert len(json.loads(populated.read_text())) == 3


def test_delete_confirm_accepted(populated):
    result = run(populated, "delete", "1", input="y\n")
    assert "Deleted note 1" in result.output


def test_delete_missing(populated):
    result = run(populated, "delete", "99", "-y")
    assert result.exit_code == 1
    assert "Note 99 not found" in result.output


def test_stats(populated):
    result = run(populated, "stats")
    assert result.exit_code == 0
    assert "3 notes" in result.output
    assert "Top tags: python (2), cli (1), ai (1)" in result.output


def test_envvar(notes_file, monkeypatch):
    monkeypatch.setenv("NOTES_FILE", str(notes_file))
    runner.invoke(app, ["add", "From env"])
    assert json.loads(notes_file.read_text())[0]["title"] == "From env"
