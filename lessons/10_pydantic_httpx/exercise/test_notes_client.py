"""Provided tests. Run: uv run pytest lessons/10_pydantic_httpx/exercise -v"""

from datetime import datetime

import httpx
import pytest
from pydantic import ValidationError

from notes_client import Note, NoteIn, NoteNotFoundError, NotesClient


# --- A fake server, in-process ------------------------------------------------------------
class FakeNotesServer:
    def __init__(self) -> None:
        self.notes: dict[int, dict] = {
            1: {"id": 1, "title": "RAG", "body": "retrieval", "tags": ["ai", "llm"], "created_at": "2026-10-01T09:00:00"},
            2: {"id": 2, "title": "httpx", "body": "", "tags": ["python"], "created_at": "2026-10-02T10:30:00"},
        }
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        parts = request.url.path.strip("/").split("/")
        if parts == ["notes"] and request.method == "GET":
            tag = request.url.params.get("tag")
            return httpx.Response(200, json=[n for n in self.notes.values() if tag is None or tag in n["tags"]])
        if parts == ["notes"] and request.method == "POST":
            import json
            data = json.loads(request.content)
            if data["title"] == "forbidden":
                return httpx.Response(422, json={"detail": "nope"})
            note = {"id": max(self.notes) + 1, **data, "created_at": "2026-10-03T08:00:00"}
            self.notes[note["id"]] = note
            return httpx.Response(201, json=note)
        if len(parts) == 2 and parts[0] == "notes":
            note_id = int(parts[1])
            if note_id not in self.notes:
                return httpx.Response(404, json={"detail": "not found"})
            if request.method == "GET":
                return httpx.Response(200, json=self.notes[note_id])
            if request.method == "DELETE":
                del self.notes[note_id]
                return httpx.Response(204)
        return httpx.Response(500)


@pytest.fixture
def server():
    return FakeNotesServer()


@pytest.fixture
def api(server):
    with NotesClient("https://notes.test", transport=httpx.MockTransport(server)) as client:
        yield client


# --- Models --------------------------------------------------------------------------------
def test_note_in_normalizes():
    n = NoteIn(title="  RAG  ", tags=["AI", " llm ", "ai", ""])
    assert n.title == "RAG"
    assert n.tags == ["ai", "llm"]
    assert n.body == ""


@pytest.mark.parametrize("title", ["", "   ", "x" * 101])
def test_note_in_rejects_bad_titles(title):
    with pytest.raises(ValidationError):
        NoteIn(title=title)


def test_note_parses_server_json():
    n = Note.model_validate({"id": "3", "title": "T", "created_at": "2026-10-02T12:00:00"})
    assert n.id == 3 and n.created_at == datetime(2026, 10, 2, 12, 0)
    assert isinstance(n, NoteIn)


def test_default_tags_not_shared():
    a, b = NoteIn(title="a"), NoteIn(title="b")
    a.tags.append("x")
    assert b.tags == []


# --- Client -------------------------------------------------------------------------------
def test_list_notes(api):
    notes = api.list_notes()
    assert [n.id for n in notes] == [1, 2]
    assert all(isinstance(n, Note) for n in notes)
    assert notes[0].created_at == datetime(2026, 10, 1, 9, 0)


def test_list_notes_by_tag_sends_query_param(api, server):
    assert [n.title for n in api.list_notes(tag="python")] == ["httpx"]
    assert server.requests[-1].url.params["tag"] == "python"


def test_list_notes_without_tag_sends_no_param(api, server):
    api.list_notes()
    assert "tag" not in server.requests[-1].url.params


def test_get_note(api):
    assert api.get_note(1).tags == ["ai", "llm"]


def test_get_missing_note(api):
    with pytest.raises(NoteNotFoundError) as exc_info:
        api.get_note(42)
    assert exc_info.value.note_id == 42


def test_create_note(api, server):
    created = api.create_note(NoteIn(title=" Pydantic ", body="validation", tags=["Python"]))
    assert created.id == 3 and created.title == "Pydantic" and created.tags == ["python"]
    sent = server.requests[-1]
    assert sent.method == "POST"
    import json
    assert json.loads(sent.content) == {"title": "Pydantic", "body": "validation", "tags": ["python"]}


def test_create_note_server_rejects(api):
    with pytest.raises(httpx.HTTPStatusError):
        api.create_note(NoteIn(title="forbidden"))


def test_delete_note(api, server):
    api.delete_note(1)
    assert 1 not in server.notes
    with pytest.raises(NoteNotFoundError):
        api.delete_note(1)


def test_context_manager_closes(server):
    client = NotesClient("https://notes.test", transport=httpx.MockTransport(server))
    with client as same:
        assert same is client
    with pytest.raises(RuntimeError):     # httpx refuses to send on a closed client
        client.list_notes()
