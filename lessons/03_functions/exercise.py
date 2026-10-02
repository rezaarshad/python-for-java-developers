"""Lesson 03 exercise: notes query helpers.

Notes are dicts like in Lesson 02:  {"id": 1, "title": "...", "body": "...", "tags": {...}, "pinned": False}
Fill in the TODOs, then run:

    uv run python lessons/03_functions/exercise.py
"""

from collections.abc import Callable

type Note = dict
type Predicate = Callable[[Note], bool]


def make_id_generator(start: int = 1) -> Callable[[], int]:
    """Return a function that yields start, start+1, start+2, ... on each call (use a closure)."""
    # TODO
    pass


def make_note(next_id: Callable[[], int], title: str, *tags: str, body: str = "", pinned: bool = False) -> Note:
    """Build a note. `tags` are variadic, stored as a lowercase set. `body` and `pinned` are keyword-only.
    Example: make_note(gen, "RAG", "AI", "llm", body="...", pinned=True)"""
    # TODO
    pass


def has_tag(tag: str) -> Predicate:
    """Return a predicate: True if the note has `tag` (case-insensitive)."""
    # TODO
    pass


def contains(text: str) -> Predicate:
    """Return a predicate: True if `text` appears in the title or body (case-insensitive)."""
    # TODO
    pass


def is_pinned(note: Note) -> bool:
    """A plain predicate (not a factory)."""
    # TODO
    pass


def all_of(*predicates: Predicate) -> Predicate:
    """Combine predicates with AND. all_of() with no predicates matches everything."""
    # TODO
    pass


def any_of(*predicates: Predicate) -> Predicate:
    """Combine predicates with OR. any_of() with no predicates matches nothing."""
    # TODO
    pass


def negate(predicate: Predicate) -> Predicate:
    """Return the opposite predicate."""
    # TODO
    pass


def query(notes: list[Note], *predicates: Predicate, sort_by: str = "id", limit: int | None = None) -> list[int]:
    """Ids of notes matching ALL predicates, sorted by the `sort_by` field, at most `limit` results."""
    # TODO
    pass


def main() -> None:
    gen = make_id_generator()
    assert (gen(), gen(), gen()) == (1, 2, 3)
    other = make_id_generator(100)
    assert other() == 100 and gen() == 4, "each generator must have its own state"

    next_id = make_id_generator()
    notes = [
        make_note(next_id, "Python functions", "python", "Basics", body="def, lambda, closures"),
        make_note(next_id, "Claude API", "AI", "llm", body="Messages API in Python", pinned=True),
        make_note(next_id, "Embeddings", "ai", body="Vectors for semantic search"),
        make_note(next_id, "Java streams", "java", body="filter, map, collect"),
    ]
    assert notes[0] == {"id": 1, "title": "Python functions", "body": "def, lambda, closures",
                        "tags": {"python", "basics"}, "pinned": False}
    assert notes[1]["pinned"] is True

    assert query(notes, has_tag("AI")) == [2, 3]
    assert query(notes, contains("python")) == [1, 2]
    assert query(notes, is_pinned) == [2]
    assert query(notes, has_tag("ai"), negate(is_pinned)) == [3]
    assert query(notes, any_of(has_tag("java"), contains("vector"))) == [3, 4]
    assert query(notes, all_of(has_tag("ai"), contains("python"))) == [2]
    assert query(notes, all_of()) == [1, 2, 3, 4]
    assert query(notes, any_of()) == []
    assert query(notes) == [1, 2, 3, 4]
    assert query(notes, sort_by="title") == [2, 3, 4, 1]
    assert query(notes, sort_by="title", limit=2) == [2, 3]
    print("All checks passed ✅")


if __name__ == "__main__":
    main()
