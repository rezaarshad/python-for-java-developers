"""Checks your notes_lite package. Run from this folder:

    uv run python check.py
"""

import subprocess
import sys

import notes_lite
from notes_lite import CsvExporter, MarkdownExporter, Note, NoteStore, Priority, export_all
from notes_lite import exporters, models, store


def main() -> None:
    assert notes_lite.__version__ == "0.1.0"
    assert sorted(notes_lite.__all__) == sorted(
        ["Note", "Priority", "NoteStore", "MarkdownExporter", "CsvExporter", "export_all"]
    )
    assert models.Note is Note and models.Priority is Priority, "Note/Priority belong in models.py"
    assert store.NoteStore is NoteStore, "NoteStore belongs in store.py"
    assert exporters.MarkdownExporter is MarkdownExporter, "exporters belong in exporters.py"
    assert "from .models" in open(store.__file__).read(), "store.py should use a relative import"

    s = NoteStore()
    s.add("RAG", "retrieval", {"AI"}, Priority.HIGH)
    s.add("Groceries")
    assert len(s) == 2 and s[1].tags == {"ai"}
    assert export_all(s, CsvExporter()) == ["1,RAG,HIGH", "2,Groceries,MEDIUM"]
    assert MarkdownExporter().export(s[1]).startswith("# RAG")

    out = subprocess.run([sys.executable, "-m", "notes_lite"], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "notes_lite 0.1.0: 3 notes", f"got: {out.stdout!r}"
    print("All checks passed ✅")


if __name__ == "__main__":
    main()
