"""Lesson 06 exercise: notes persistence.

Fill in the TODOs, then run:

    uv run python lessons/06_errors_files/exercise.py
"""

import csv
import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Note:                    # simplified model, provided
    id: int
    title: str
    body: str = ""
    tags: set[str] = field(default_factory=set)


# --- Exceptions -----------------------------------------------------------------
class NotesError(Exception):
    """Base class for every notes-app error."""


class NoteNotFoundError(NotesError):
    """Raised when a note id doesn't exist. Has a `note_id` attribute; message: 'note 42 not found'."""
    # TODO: __init__(self, note_id: int)


class CorruptStoreError(NotesError):
    """Raised when the notes file can't be parsed."""


# --- Serialization ----------------------------------------------------------------
def note_to_dict(note: Note) -> dict:
    """JSON-friendly dict. Tags become a SORTED list (sets aren't JSON-serializable)."""
    # TODO
    pass


def note_from_dict(data: dict) -> Note:
    """The reverse of note_to_dict. Tags become a set again."""
    # TODO
    pass


# --- Atomic writes ------------------------------------------------------------------
class AtomicWrite:
    """Context manager for crash-safe writes:

        with AtomicWrite(path) as f:
            f.write("...")

    - __enter__: create the parent dirs, open `<path>.tmp` (e.g. notes.json.tmp) for writing (utf-8),
      return the file object
    - __exit__ on success: close the file and move the temp file over `path` (Path.replace)
    - __exit__ on exception: close the file, delete the temp file, leave `path` untouched,
      and let the exception propagate
    """

    def __init__(self, path: Path) -> None:
        # TODO
        pass

    # TODO: __enter__, __exit__


# --- Repository ----------------------------------------------------------------------
def save_notes(path: Path, notes: list[Note]) -> None:
    """Write notes as a JSON list (indent=2) using AtomicWrite."""
    # TODO
    pass


def load_notes(path: Path) -> list[Note]:
    """Read notes. A missing file means no notes yet → []. Invalid JSON → raise CorruptStoreError,
    chained from the original JSONDecodeError (raise ... from e)."""
    # TODO
    pass


def get_note(notes: list[Note], note_id: int) -> Note:
    """Find a note by id, or raise NoteNotFoundError."""
    # TODO
    pass


def export_csv(path: Path, notes: list[Note]) -> None:
    """Write CSV with header id,title,tags. Tags are sorted and joined with ';'. Use csv.DictWriter."""
    # TODO
    pass


def main() -> None:
    notes = [
        Note(1, "RAG", "Retrieval augmented generation", {"llm", "ai"}),
        Note(2, "Pathlib", "Path objects, not strings"),
    ]
    assert note_to_dict(notes[0]) == {"id": 1, "title": "RAG", "body": "Retrieval augmented generation",
                                      "tags": ["ai", "llm"]}
    assert note_from_dict(note_to_dict(notes[0])) == notes[0]

    err = NoteNotFoundError(42)
    assert isinstance(err, NotesError) and err.note_id == 42 and str(err) == "note 42 not found"

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "store" / "notes.json"
        assert load_notes(path) == [], "missing file → empty list"

        save_notes(path, notes)
        assert json.loads(path.read_text(encoding="utf-8"))[0]["tags"] == ["ai", "llm"]
        assert load_notes(path) == notes
        assert not path.with_name("notes.json.tmp").exists(), "temp file should be gone"

        # A crash in the middle of a write must leave the old file intact
        try:
            with AtomicWrite(path) as f:
                f.write("half-written garb")
                raise RuntimeError("simulated crash")
        except RuntimeError:
            pass
        else:
            raise AssertionError("AtomicWrite must not swallow exceptions")
        assert load_notes(path) == notes, "original file must survive a failed write"
        assert not path.with_name("notes.json.tmp").exists(), "temp file must be cleaned up"

        path.write_text("{not json", encoding="utf-8")
        try:
            load_notes(path)
            raise AssertionError("expected CorruptStoreError")
        except CorruptStoreError as e:
            assert isinstance(e.__cause__, json.JSONDecodeError), "use `raise ... from e`"

        assert get_note(notes, 2).title == "Pathlib"
        try:
            get_note(notes, 99)
            raise AssertionError("expected NoteNotFoundError")
        except NotesError as e:              # catching the base class works too
            assert e.note_id == 99

        csv_path = Path(tmp) / "notes.csv"
        export_csv(csv_path, notes)
        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert rows == [{"id": "1", "title": "RAG", "tags": "ai;llm"},
                        {"id": "2", "title": "Pathlib", "tags": ""}]
    print("All checks passed ✅")


if __name__ == "__main__":
    main()
