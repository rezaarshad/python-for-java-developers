"""Capstone acceptance tests for the real notes package in src/notes/.

Run: uv run pytest lessons/16_shipping/capstone -v
"""

import json
from datetime import datetime
from types import SimpleNamespace as NS

import pytest
from typer.testing import CliRunner

cli = pytest.importorskip("notes.cli", reason="build src/notes/cli.py first (see README.md)")
llm = pytest.importorskip("notes.llm", reason="build src/notes/llm.py first (see README.md)")
app = cli.app

runner = CliRunner()


@pytest.fixture
def notes_file(tmp_path):
    return tmp_path / "notes.json"


def run(notes_file, *args, **kwargs):
    return runner.invoke(app, ["--file", str(notes_file), *args], **kwargs)


@pytest.fixture
def populated(notes_file):
    for args in [
        ["add", "RAG", "-b", "Retrieve relevant notes with embeddings then prompt Claude", "-t", "AI", "-t", "llm"],
        ["add", "pytest fixtures", "-b", "Fixtures replace BeforeEach and tmp_path gives temp files", "-t", "python"],
        ["add", "Groceries", "-b", "oat milk coffee bananas", "-t", "personal"],
    ]:
        assert run(notes_file, *args).exit_code == 0
    return notes_file


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0 and "notes 0.1.0" in result.output


def test_add_and_storage_format(notes_file):
    result = run(notes_file, "add", "RAG", "-b", "body", "-t", "AI", "-t", "ai")
    assert result.exit_code == 0 and "Added note 1: RAG" in result.output
    [stored] = json.loads(notes_file.read_text(encoding="utf-8"))
    assert {k: stored[k] for k in ["id", "title", "body", "tags"]} == {"id": 1, "title": "RAG", "body": "body", "tags": ["ai"]}
    datetime.fromisoformat(stored["created_at"])


def test_list(populated):
    out = run(populated, "list").output
    for text in ["ID", "Title", "Tags", "RAG", "pytest fixtures", "ai, llm"]:
        assert text in out
    assert "Groceries" not in run(populated, "list", "-t", "python").output


def test_list_empty(notes_file):
    assert "No notes yet." in run(notes_file, "list").output


def test_show(populated):
    result = run(populated, "show", "2")
    assert result.exit_code == 0
    for text in ["pytest fixtures", "python", "BeforeEach"]:
        assert text in result.output
    missing = run(populated, "show", "9")
    assert missing.exit_code == 1 and "Note 9 not found" in missing.output


def test_search_ranks_by_relevance(populated):
    result = run(populated, "search", "embeddings prompt")
    assert result.exit_code == 0
    assert result.output.splitlines()[0] == "1: RAG"


def test_search_no_match(populated):
    result = run(populated, "search", "kotlin coroutines")
    assert result.exit_code == 1 and "No matches for 'kotlin coroutines'" in result.output


def test_delete(populated):
    assert "Deleted note 3" in run(populated, "delete", "3", "-y").output
    assert [n["id"] for n in json.loads(populated.read_text(encoding="utf-8"))] == [1, 2]


class FakeClient:
    def __init__(self):
        self.calls = []
        self.beta = NS(messages=self)

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(content=[NS(type="text", text="Use embeddings, then prompt Claude [1].")],
                  stop_reason="end_turn", stop_details=None)


def test_ask_requires_api_key(populated, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = run(populated, "ask", "how does rag work?")
    assert result.exit_code == 1 and "Set ANTHROPIC_API_KEY to use 'ask'" in result.output


def test_ask_uses_retrieved_notes(populated, monkeypatch):
    fake = FakeClient()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(llm, "make_client", lambda: fake)
    result = run(populated, "ask", "How do embeddings help me prompt Claude?")
    assert result.exit_code == 0, result.output
    assert "Use embeddings, then prompt Claude [1]." in result.output
    assert "Sources: 1" in result.output
    [call] = fake.calls
    assert call["model"] == "claude-opus-5-5" and call["fallbacks"] == "default"
    assert "Retrieve relevant notes" in json.dumps(call["messages"])
    assert "oat milk" not in json.dumps(call["messages"]), "only send relevant notes"


def test_ask_nothing_relevant_skips_llm(populated, monkeypatch):
    fake = FakeClient()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(llm, "make_client", lambda: fake)
    result = run(populated, "ask", "xyzzy plugh")
    assert "I couldn't find anything relevant in your notes." in result.output
    assert fake.calls == []
