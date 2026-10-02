# Lesson 09: Command-Line Apps with `typer` & `rich`

| Library  | What it is                                                    | Java analogue            |
|----------|---------------------------------------------------------------|--------------------------|
| `argparse` | stdlib argument parser: verbose but dependency-free       | Apache Commons CLI       |
| `typer`  | build CLIs from **type hints**: the function signature *is* the CLI | picocli          |
| `rich`   | colors, tables, progress bars, pretty tracebacks, markdown   | (nothing this nice)       |

Typer is built on `click`, from the same author as FastAPI, and uses the same type-hint-driven style.

## 1. Typer basics

```python
from typing import Annotated
import typer

app = typer.Typer(help="notes: your second brain")

@app.command()
def add(
    title: str,                                                    # positional argument
    body: Annotated[str, typer.Option("--body", "-b")] = "",       # --body / -b option
    tag: Annotated[list[str] | None, typer.Option("--tag", "-t")] = None,   # repeatable: -t ai -t llm
    pinned: bool = False,                                          # --pinned / --no-pinned flag
):
    """Add a note."""                                              # becomes the --help text
    typer.echo(f"Added {title}")

@app.command("list")                                               # explicit command name
def list_notes(): ...

if __name__ == "__main__":
    app()
```

```bash
uv run python app.py add "RAG" -b "retrieval" -t ai -t llm
uv run python app.py --help
uv run python app.py add --help
```

- Types are converted and validated: `int`, `float`, `Path`, `bool`, enums (which become choices), `datetime`.
- `typer.Option(envvar="NOTES_FILE")` falls back to an environment variable.
- `raise typer.Exit(code=1)` to exit with an error code; `typer.confirm("Sure?")`, `typer.prompt("Name")`.
- `@app.callback()` runs before every command, for global options like `--file`. Pass shared state through `ctx.obj`.

## 2. Rich

```python
from rich.console import Console
from rich.table import Table

console = Console()
console.print("[bold green]Saved![/] 3 notes")            # markup tags
table = Table("ID", "Title", "Tags", title="Notes")
table.add_row("1", "RAG", "ai, llm")
console.print(table)

from rich.progress import track
for item in track(items, description="Embedding..."): ...

from rich import print as rprint
rprint({"nested": {"dicts": [1, 2]}})                      # pretty-printed
```

## 3. Testing CLIs

```python
from typer.testing import CliRunner
runner = CliRunner()

def test_add(tmp_path):
    result = runner.invoke(app, ["--file", str(tmp_path / "n.json"), "add", "RAG"])
    assert result.exit_code == 0
    assert "Added" in result.output
```

`CliRunner` runs the app in-process and captures its output. It's fast, and needs no subprocess.

## 4. Making it a real command

In `pyproject.toml`:

```toml
[project.scripts]
notes = "notes.cli:app"
```

After `uv sync`, `uv run notes add "RAG"` works. In Lesson 16 we wire up the real package this way.

## 5. Run the example

```bash
uv run python lessons/09_cli/demo_cli.py --help
uv run python lessons/09_cli/demo_cli.py hello Reza --times 2 --shout
uv run python lessons/09_cli/demo_cli.py langs
uv run python lessons/09_cli/demo_cli.py work
```

## 6. Exercise: the notes CLI

Implement the commands in `exercise/cli_app.py` (`add`, `list`, `search`, `delete`, `stats`). The storage
helpers and the global `--file` option are provided.

```bash
uv run pytest lessons/09_cli/exercise -v                         # tests are provided
uv run python lessons/09_cli/exercise/cli_app.py --file /tmp/n.json add "Hello" -t demo
uv run python lessons/09_cli/exercise/cli_app.py --file /tmp/n.json list
```
