"""Lesson 04 exercise: notes models. Notes become real types instead of dicts.

Fill in the TODOs, then run:

    uv run python lessons/04_classes/exercise.py
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class Priority(Enum):
    # TODO: LOW = 1, MEDIUM = 2, HIGH = 3
    pass


@dataclass
class Note:
    """Fields: id (int), title (str), body (str, default ""), tags (set[str], default empty),
    priority (Priority, default MEDIUM).

    Use __post_init__ to strip whitespace from the title, lowercase all tags, and raise
    ValueError if the title is empty after stripping."""

    # TODO: fields

    # TODO: __post_init__

    @property
    def word_count(self) -> int:
        """Number of words in the body."""
        # TODO
        pass

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        """Build a Note from a dict like Lesson 02's. tags may be any iterable,
        and priority may be missing or given as a name like "HIGH"."""
        # TODO (hint: Priority["HIGH"] looks up an enum member by name)
        pass


class NoteStore:
    """Holds notes and assigns ids. Should support:
        len(store), note_id in store, store[note_id] (KeyError if missing), for note in store
    """

    def __init__(self) -> None:
        # TODO: a dict {id: Note} and the next id
        pass

    def add(self, title: str, body: str = "", tags: set[str] | None = None,
            priority: "Priority | None" = None) -> Note:
        """Create, store, and return a Note with the next id (1, 2, 3, ...)."""
        # TODO
        pass

    def remove(self, note_id: int) -> None:
        # TODO
        pass

    # TODO: __len__, __contains__, __getitem__, __iter__

    def by_priority(self) -> list[Note]:
        """Notes sorted by priority, HIGH first; ties keep insertion order."""
        # TODO
        pass


class Exporter(Protocol):
    def export(self, note: Note) -> str: ...


class MarkdownExporter:
    def export(self, note: Note) -> str:
        """'# Title\\n\\nbody\\n\\ntags: a, b' with tags sorted. Omit the tags line if there are no tags."""
        # TODO
        pass


class CsvExporter:
    def export(self, note: Note) -> str:
        """'id,title,priority_name', e.g. '1,RAG,HIGH'"""
        # TODO
        pass


def export_all(store: NoteStore, exporter: Exporter) -> list[str]:
    # TODO
    pass


def main() -> None:
    assert [p.value for p in Priority] == [1, 2, 3]

    n = Note(1, "  RAG  ", "Retrieval augmented generation", {"AI", "LLM"})
    assert n.title == "RAG" and n.tags == {"ai", "llm"} and n.priority is Priority.MEDIUM
    assert n.word_count == 3
    assert n == Note(1, "RAG", "Retrieval augmented generation", {"ai", "llm"})   # dataclass __eq__
    try:
        Note(2, "   ")
        raise AssertionError("empty title should raise ValueError")
    except ValueError:
        pass
    assert Note.from_dict({"id": 7, "title": "X", "tags": ["A"], "priority": "HIGH"}) == \
        Note(7, "X", "", {"a"}, Priority.HIGH)
    assert Note.from_dict({"id": 8, "title": "Y"}).priority is Priority.MEDIUM

    store = NoteStore()
    store.add("Python classes", "dataclass and protocols", {"python"})
    store.add("Claude API", "Messages", {"ai"}, Priority.HIGH)
    store.add("Groceries", priority=Priority.LOW)
    store.add("Embeddings", "vectors", {"ai"}, Priority.HIGH)
    assert len(store) == 4
    assert 2 in store and 99 not in store
    assert store[2].title == "Claude API"
    assert [note.id for note in store] == [1, 2, 3, 4]
    assert [note.id for note in store.by_priority()] == [2, 4, 1, 3]
    store.remove(3)
    assert len(store) == 3 and 3 not in store
    assert store.add("Next").id == 5, "ids are never reused"
    try:
        store[3]
        raise AssertionError("missing id should raise KeyError")
    except KeyError:
        pass

    assert MarkdownExporter().export(n) == "# RAG\n\nRetrieval augmented generation\n\ntags: ai, llm"
    assert MarkdownExporter().export(store[5]) == "# Next\n\n"
    assert export_all(store, CsvExporter()) == [
        "1,Python classes,MEDIUM", "2,Claude API,HIGH", "4,Embeddings,HIGH", "5,Next,MEDIUM",
    ]
    print("All checks passed ✅")


if __name__ == "__main__":
    main()
