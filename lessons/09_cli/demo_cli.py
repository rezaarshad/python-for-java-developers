"""Lesson 09 demo: typer + rich.

Run: uv run python lessons/09_cli/demo_cli.py --help
"""

import time
from enum import Enum
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import track
from rich.table import Table

app = typer.Typer(help="A demo CLI built with typer and rich.")
console = Console()


class Style(str, Enum):          # an enum becomes a validated choice: --style [plain|fancy]
    plain = "plain"
    fancy = "fancy"


@app.command()
def hello(
    name: str,
    times: Annotated[int, typer.Option("--times", "-n", min=1, help="How many greetings")] = 1,
    shout: bool = False,
    style: Style = Style.plain,
):
    """Greet someone."""
    message = f"Hello, {name}!"
    if shout:
        message = message.upper()
    for _ in range(times):
        if style is Style.fancy:
            console.print(f"[bold magenta]✨ {message} ✨[/]")
        else:
            typer.echo(message)


@app.command()
def langs():
    """Show a rich table."""
    table = Table("Language", "Typing", "Use it for", title="Languages you know")
    table.add_row("Java", "static", "[cyan]backends[/]")
    table.add_row("Python", "dynamic + hints", "[green]AI, data, scripting[/]")
    console.print(table)


@app.command()
def work(steps: int = 20):
    """Show a progress bar."""
    for _ in track(range(steps), description="Working..."):
        time.sleep(0.05)
    console.print("[bold green]Done![/]")


@app.command()
def fail():
    """Exit with an error code."""
    console.print("[red]Something went wrong[/]")
    raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
