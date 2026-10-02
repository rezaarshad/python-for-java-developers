"""Notes service layer. This code is finished, but it has ONE bug. Write tests to find it."""

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


class NotesError(Exception):
    pass


class NoteNotFoundError(NotesError):
    pass


class DuplicateNoteError(NotesError):
    pass


@dataclass
class Note:
    slug: str
    title: str
    body: str
    tags: list[str]
    created_at: datetime
    summary: str | None = None


def slugify(title: str) -> str:
    """'Hello, World!' → 'hello-world'. Lowercase; runs of non-alphanumerics become a single '-';
    no leading/trailing '-'. Raises ValueError if nothing is left."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).lstrip("-")
    if not slug:
        raise ValueError(f"cannot slugify {title!r}")
    return slug


def parse_tags(raw: str) -> list[str]:
    """'AI, llm,  ai ,' → ['ai', 'llm']. Lowercase, trimmed, empty entries dropped,
    duplicates removed keeping first occurrence order."""
    tags = (t.strip().lower() for t in raw.split(","))
    return list(dict.fromkeys(t for t in tags if t))   # dict keeps insertion order → ordered dedupe


class NoteRepository(Protocol):
    def save(self, note: Note) -> None: ...
    def get(self, slug: str) -> Note | None: ...
    def all(self) -> list[Note]: ...


class InMemoryNoteRepository:
    def __init__(self) -> None:
        self._notes: dict[str, Note] = {}

    def save(self, note: Note) -> None:
        self._notes[note.slug] = note

    def get(self, slug: str) -> Note | None:
        return self._notes.get(slug)

    def all(self) -> list[Note]:
        return list(self._notes.values())


class Summarizer(Protocol):
    def summarize(self, text: str) -> str: ...


class NoteService:
    def __init__(self, repo: NoteRepository, clock: Callable[[], datetime] = datetime.now) -> None:
        self._repo = repo
        self._clock = clock

    def create(self, title: str, body: str = "", tags: str = "") -> Note:
        """Create and save a note. Raises DuplicateNoteError if the slug already exists."""
        slug = slugify(title)
        if self._repo.get(slug) is not None:
            raise DuplicateNoteError(slug)
        note = Note(slug, title.strip(), body, parse_tags(tags), self._clock())
        self._repo.save(note)
        return note

    def get(self, slug: str) -> Note:
        note = self._repo.get(slug)
        if note is None:
            raise NoteNotFoundError(slug)
        return note

    def search(self, text: str) -> list[str]:
        """Slugs of notes whose title or body contains text (case-insensitive), oldest first."""
        text = text.lower()
        hits = [n for n in self._repo.all() if text in n.title.lower() or text in n.body.lower()]
        return [n.slug for n in sorted(hits, key=lambda n: n.created_at)]

    def summarize(self, slug: str, summarizer: Summarizer) -> str:
        """Summarize a note's body with `summarizer` (in Lesson 14 that's Claude), cache it on the note,
        and return it. If a summary is already cached, return it WITHOUT calling the summarizer again."""
        note = self.get(slug)
        if note.summary is None:
            note.summary = summarizer.summarize(note.body)
            self._repo.save(note)
        return note.summary
