"""Lesson 09 exercise: the notes CLI.

Run:   uv run python lessons/09_cli/exercise/cli_app.py --help
Test:  uv run pytest lessons/09_cli/exercise -v

Notes are stored as a JSON list of dicts: {"id": 1, "title": "...", "body": "...", "tags": ["ai"]}
"""

import json
from collections import Counter
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="notes: your second brain, in the terminal.")
console = Console()

DEFAULT_FILE = Path.home() / ".notes.json"


# --- Provided: storage helpers -------------------------------------------------
def load_notes(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_notes(path: Path, notes: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notes, indent=2), encoding="utf-8")


# --- Provided: global --file option ---------------------------------------------
@app.callback()
def main(
    ctx: typer.Context,
    file: Annotated[Path, typer.Option("--file", "-f", envvar="NOTES_FILE",
                                       help="Notes file")] = DEFAULT_FILE,
):
    """Runs before every command; stores the notes path in ctx.obj."""
    ctx.obj = file


# --- TODO: commands -------------------------------------------------------------------
# Every command takes `ctx: typer.Context` as its first parameter. The notes file is `ctx.obj`.


# TODO: `add TITLE [--body/-b TEXT] [--tag/-t TAG ...]`
#   - id = max existing id + 1 (1 for the first note); tags lowercased
#   - print: Added note 3: <title>


# TODO: `list [--tag/-t TAG]`   (name the function list_notes and use @app.command("list"))
#   - no notes (after filtering) → print: No notes yet.
#   - otherwise print a rich Table with columns ID, Title, Tags (tags joined with ", ")


# TODO: `search TEXT`
#   - case-insensitive match on title or body; print one line per hit: "<id>: <title>"
#   - no hits → print: No matches for '<text>'   and exit with code 1


# TODO: `delete NOTE_ID [--yes/-y]`
#   - unknown id → print: Note <id> not found   and exit with code 1
#   - without --yes, ask typer.confirm(f"Delete '<title>'?"); if declined, print Cancelled. (exit code 0)
#   - print: Deleted note <id>


# TODO: `stats`
#   - print: <n> notes
#   - then, if any tags exist, the 3 most common:  Top tags: python (2), ai (1)


if __name__ == "__main__":
    app()
