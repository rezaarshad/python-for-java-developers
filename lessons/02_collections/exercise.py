"""Lesson 02 exercise: notes app v0.1, an in-memory note store.

A note is a dict:  {"id": 1, "title": "...", "body": "...", "tags": {"python", "ai"}}
All notes live in a list. Fill in the TODOs, then run:

    uv run python lessons/02_collections/exercise.py

Try to use comprehensions, sorted(key=...), set operations, and Counter where they fit.
Most functions can be written in 1-3 lines.
"""

from collections import Counter

Note = dict  # a type alias, just for readability. We'll replace it with a real class in Lesson 04.


def add_note(notes: list[Note], title: str, body: str, tags: list[str]) -> Note:
    """Create a note, append it to `notes`, and return it.
    - id = 1 for the first note, otherwise (largest existing id) + 1
    - tags are stored as a set of lowercase strings (so ["AI", "ai"] → {"ai"})"""
    # TODO
    pass


def find_by_tag(notes: list[Note], tag: str) -> list[str]:
    """Titles of notes that have `tag` (case-insensitive), in insertion order."""
    # TODO
    pass


def search(notes: list[Note], text: str) -> list[int]:
    """Ids of notes whose title OR body contains `text` (case-insensitive)."""
    # TODO
    pass


def all_tags(notes: list[Note]) -> list[str]:
    """Every distinct tag across all notes, sorted alphabetically."""
    # TODO
    pass


def tag_counts(notes: list[Note]) -> list[tuple[str, int]]:
    """The 3 most used tags with their counts, most used first, e.g. [("python", 3), ...]."""
    # TODO (hint: Counter)
    pass


def common_tags(notes: list[Note], id_a: int, id_b: int) -> set[str]:
    """Tags shared by the notes with ids id_a and id_b."""
    # TODO (hint: first build a dict {id: note}, then set intersection)
    pass


def titles_by_length(notes: list[Note]) -> list[str]:
    """Titles sorted by length (longest first); ties broken alphabetically."""
    # TODO (hint: key can return a tuple; a negative number reverses one part)
    pass


def main() -> None:
    notes: list[Note] = []
    add_note(notes, "Lists", "Python lists are like ArrayList", ["Python", "basics"])
    add_note(notes, "Dicts", "Dicts are ordered hash maps", ["python", "BASICS"])
    add_note(notes, "LLM prompts", "Prompting Claude well", ["ai", "llm"])
    add_note(notes, "RAG", "Retrieval augmented generation with Python", ["ai", "python", "llm"])

    assert [n["id"] for n in notes] == [1, 2, 3, 4]
    assert notes[1]["tags"] == {"python", "basics"}
    assert find_by_tag(notes, "AI") == ["LLM prompts", "RAG"]
    assert search(notes, "python") == [1, 4]
    assert all_tags(notes) == ["ai", "basics", "llm", "python"]
    assert tag_counts(notes)[0] == ("python", 3)
    assert len(tag_counts(notes)) == 3
    assert common_tags(notes, 1, 4) == {"python"}
    assert titles_by_length(notes) == ["LLM prompts", "Dicts", "Lists", "RAG"]
    print("All checks passed ✅")


if __name__ == "__main__":
    main()
