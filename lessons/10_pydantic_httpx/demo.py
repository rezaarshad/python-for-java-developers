"""Lesson 10 demo: pydantic + httpx.

Run: uv run python lessons/10_pydantic_httpx/demo.py
"""

from datetime import datetime
from typing import Literal

import httpx
from pydantic import BaseModel, Field, TypeAdapter, ValidationError, computed_field, field_validator


# --- Pydantic ------------------------------------------------------------------------
class Author(BaseModel):
    name: str
    email: str | None = None


class Note(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=100)
    body: str = ""
    tags: list[str] = []
    priority: Literal["low", "medium", "high"] = "medium"
    author: Author                                   # nested models are validated too
    created_at: datetime

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        return sorted({t.strip().lower() for t in tags if t.strip()})

    @computed_field                                  # included in model_dump()
    @property
    def word_count(self) -> int:
        return len(self.body.split())


raw = {
    "id": "7",                                       # str → int (lax mode coerces sensible types)
    "title": "RAG",
    "body": "retrieval augmented generation",
    "tags": ["AI", " llm ", "ai", ""],
    "author": {"name": "Reza"},
    "created_at": "2026-10-02T12:30:00",             # ISO string → datetime
}
note = Note.model_validate(raw)
print(repr(note))
print(note.tags, note.created_at.year, note.author.name)
print(note.model_dump())
print(note.model_dump_json(indent=2))
print(Note.model_validate_json(note.model_dump_json()) == note)   # round trip

try:
    Note.model_validate({"id": "x", "title": "", "priority": "urgent", "author": {}, "created_at": "nope"})
except ValidationError as e:
    print(f"\n{e.error_count()} errors:")
    for err in e.errors():
        print(" ", ".".join(map(str, err["loc"])), "→", err["msg"])

notes = TypeAdapter(list[Note]).validate_python([raw, raw])      # validate non-model types
print(len(notes), type(notes[0]).__name__)

updated = note.model_copy(update={"title": "RAG v2"})            # immutable-style update
print(updated.title, note.title)

# --- httpx (talks to a public fake REST API) -----------------------------------------
print("\n--- httpx ---")


class Post(BaseModel):
    userId: int
    id: int
    title: str
    body: str


try:
    with httpx.Client(base_url="https://jsonplaceholder.typicode.com", timeout=5.0) as client:
        r = client.get("/posts", params={"userId": 1})
        r.raise_for_status()
        posts = TypeAdapter(list[Post]).validate_python(r.json())
        print(f"GET {r.url} → {r.status_code}, {len(posts)} posts; first: {posts[0].title!r}")

        r = client.post("/posts", json={"title": "Hello", "body": "from httpx", "userId": 1})
        print("POST →", r.status_code, r.json())

        r = client.get("/posts/999999")
        try:
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            print("raise_for_status →", e.response.status_code)
except httpx.RequestError as e:
    print(f"(network unavailable, skipping live calls: {e!r})")

# --- MockTransport: no network needed ---------------------------------------------------


def fake_api(request: httpx.Request) -> httpx.Response:
    if request.method == "GET" and request.url.path == "/ping":
        return httpx.Response(200, json={"pong": True, "query": dict(request.url.params)})
    return httpx.Response(404, json={"detail": "not found"})


with httpx.Client(base_url="https://fake", transport=httpx.MockTransport(fake_api)) as client:
    print("mock:", client.get("/ping", params={"x": "1"}).json(), client.get("/nope").status_code)
