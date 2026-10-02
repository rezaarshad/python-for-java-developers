"""Provided tests. Run: uv run pytest lessons/11_fastapi_sqlalchemy/exercise -v"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from api_app import Base, app, get_session


@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)

    def test_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = test_session      # swap the real DB for a fresh in-memory one
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def seeded(client):
    for payload in [
        {"title": "RAG", "body": "Retrieval augmented generation", "tags": ["AI", "llm"]},
        {"title": "FastAPI", "body": "Type hints become an API", "tags": ["python"]},
        {"title": "Pandas", "body": "DataFrames for python", "tags": ["python", "data"]},
    ]:
        assert client.post("/notes", json=payload).status_code == 201
    return client


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create(client):
    r = client.post("/notes", json={"title": "  RAG  ", "tags": ["AI", "ai", " llm "]})
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 1 and body["title"] == "RAG" and body["body"] == ""
    assert body["tags"] == ["ai", "llm"]
    assert "created_at" in body


@pytest.mark.parametrize("payload", [{}, {"title": ""}, {"title": "x" * 101}, {"title": "ok", "tags": "notalist"}])
def test_create_invalid_is_422(client, payload):
    assert client.post("/notes", json=payload).status_code == 422


def test_list(seeded):
    r = seeded.get("/notes")
    assert r.status_code == 200
    assert [n["title"] for n in r.json()] == ["RAG", "FastAPI", "Pandas"]


def test_list_by_tag(seeded):
    assert [n["id"] for n in seeded.get("/notes", params={"tag": "python"}).json()] == [2, 3]


def test_list_search(seeded):
    assert [n["id"] for n in seeded.get("/notes", params={"q": "PYTHON"}).json()] == [3]
    assert [n["id"] for n in seeded.get("/notes", params={"q": "a"}).json()] == [1, 2, 3]


def test_list_tag_and_search(seeded):
    assert [n["id"] for n in seeded.get("/notes", params={"tag": "python", "q": "type"}).json()] == [2]


def test_get(seeded):
    r = seeded.get("/notes/2")
    assert r.status_code == 200 and r.json()["title"] == "FastAPI"


def test_get_missing(seeded):
    r = seeded.get("/notes/99")
    assert r.status_code == 404
    assert r.json() == {"detail": "Note 99 not found"}


def test_get_non_int_id_is_422(seeded):
    assert seeded.get("/notes/abc").status_code == 422


def test_patch_only_changes_sent_fields(seeded):
    r = seeded.patch("/notes/1", json={"body": "updated"})
    assert r.status_code == 200
    assert r.json()["body"] == "updated" and r.json()["title"] == "RAG" and r.json()["tags"] == ["ai", "llm"]
    assert seeded.get("/notes/1").json()["body"] == "updated", "changes must be persisted"


def test_patch_tags_are_normalized(seeded):
    r = seeded.patch("/notes/1", json={"tags": ["NEW", "new"]})
    assert r.json()["tags"] == ["new"]


def test_patch_missing(seeded):
    assert seeded.patch("/notes/99", json={"body": "x"}).status_code == 404


def test_patch_invalid(seeded):
    assert seeded.patch("/notes/1", json={"title": ""}).status_code == 422


def test_delete(seeded):
    r = seeded.delete("/notes/1")
    assert r.status_code == 204 and r.content == b""
    assert seeded.get("/notes/1").status_code == 404
    assert seeded.delete("/notes/1").status_code == 404


def test_openapi_lists_endpoints(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert {"/notes", "/notes/{note_id}"} <= set(paths)
