"""Lesson 10 exercise: a typed client for a remote notes API.

The remote API (simulated in the tests with httpx.MockTransport):

    GET    /notes?tag=ai     → 200 [ {note}, ... ]     (tag query param is optional)
    GET    /notes/{id}       → 200 {note}  | 404
    POST   /notes  {noteIn}  → 201 {note}  | 422 if the server rejects it
    DELETE /notes/{id}       → 204         | 404

    note JSON: {"id": 1, "title": "...", "body": "...", "tags": ["ai"], "created_at": "2026-10-02T12:00:00"}

Run the tests: uv run pytest lessons/10_pydantic_httpx/exercise -v
"""

from datetime import datetime

import httpx
from pydantic import BaseModel, Field, field_validator


class NoteNotFoundError(Exception):
    def __init__(self, note_id: int) -> None:
        super().__init__(f"note {note_id} not found")
        self.note_id = note_id


class NoteIn(BaseModel):
    """What the client SENDS.
    TODO:
    - title: str, 1..100 characters, with surrounding whitespace stripped
      (hint: a field_validator with mode="before", or Field + str_strip_whitespace in model_config)
    - body: str, default ""
    - tags: list[str], default empty; lowercased, stripped, empty strings dropped,
      duplicates removed (keep first-seen order)
    """


class Note(NoteIn):
    """What the client RECEIVES: NoteIn plus server-assigned fields.
    TODO: id: int, created_at: datetime
    """


class NotesClient:
    """Wraps httpx.Client. Usable as a context manager:

        with NotesClient("https://api.example.com") as api:
            api.list_notes()
    """

    def __init__(self, base_url: str, *, transport: httpx.BaseTransport | None = None,
                 timeout: float = 5.0) -> None:
        # TODO: create self._client = httpx.Client(base_url=..., transport=..., timeout=...)
        pass

    def list_notes(self, tag: str | None = None) -> list[Note]:
        """GET /notes, sending ?tag=... only if tag is given."""
        # TODO
        pass

    def get_note(self, note_id: int) -> Note:
        """GET /notes/{id}. 404 → NoteNotFoundError. Other errors → httpx.HTTPStatusError (raise_for_status)."""
        # TODO
        pass

    def create_note(self, note: NoteIn) -> Note:
        """POST /notes with the note as JSON. Returns the created Note."""
        # TODO
        pass

    def delete_note(self, note_id: int) -> None:
        """DELETE /notes/{id}. 404 → NoteNotFoundError."""
        # TODO
        pass

    def close(self) -> None:
        # TODO
        pass

    # TODO: __enter__ (return self) and __exit__ (close)
