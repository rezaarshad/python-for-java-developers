"""Lesson 06: exceptions, context managers, pathlib, json, csv.

Run: uv run python lessons/06_errors_files/errors_files_demo.py
"""

import csv
import json
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path


# --- try / except / else / finally -------------------------------------------
def parse_age(text: str) -> int | None:
    try:
        age = int(text)
    except ValueError as e:
        print(f"  bad input {text!r}: {e}")
        return None
    else:                                    # only runs when no exception happened
        print(f"  parsed {age}")
        return age
    finally:                                 # always runs, even after return
        print("  (finally)")


parse_age("42")
parse_age("forty-two")


# --- Custom exceptions & chaining --------------------------------------------
class ConfigError(Exception):
    """Base error for config problems."""


class MissingKeyError(ConfigError):
    def __init__(self, key: str) -> None:
        super().__init__(f"missing config key: {key}")
        self.key = key


def load_config(text: str) -> dict:
    try:
        config = json.loads(text)
    except json.JSONDecodeError as e:
        raise ConfigError("config is not valid JSON") from e     # keeps the original as __cause__
    if "model" not in config:
        raise MissingKeyError("model")
    return config


for raw in ['{"model": "claude-sonnet-5-5"}', "{oops", "{}"]:
    try:
        print(load_config(raw))
    except MissingKeyError as e:
        print("missing:", e.key)
    except ConfigError as e:                 # catches the base class: order matters, specific first
        print("config error:", e, "| caused by:", repr(e.__cause__))


# --- EAFP ------------------------------------------------------------------------
prices = {"apple": 1.2}
try:
    print(prices["banana"])
except KeyError as e:
    print("no price for", e)


# --- Context managers ---------------------------------------------------------------
class Timer:
    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.elapsed = time.perf_counter() - self.start
        status = "failed" if exc_type else "ok"
        print(f"  block {status} in {self.elapsed * 1000:.2f} ms")
        return False                         # don't swallow exceptions


with Timer():
    sum(range(1_000_000))

try:
    with Timer():
        raise RuntimeError("boom")
except RuntimeError:
    print("  exception still propagated")


# --- pathlib + text files --------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:  # the directory is deleted when the block exits
    root = Path(tmp)
    notes_dir = root / "data" / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)

    hello = notes_dir / "hello.txt"
    hello.write_text("line one\nline two\n", encoding="utf-8")
    print(hello.name, hello.stem, hello.suffix, hello.parent.name, hello.exists())

    with open(hello, encoding="utf-8") as f:   # stream line by line (memory friendly)
        for number, line in enumerate(f, start=1):
            print(number, line.rstrip("\n"))

    with open(hello, "a", encoding="utf-8") as f:   # modes: r, w, a, x (create, fail if exists), b (binary)
        f.write("line three\n")
    print(hello.read_text(encoding="utf-8").splitlines())

    # --- JSON -------------------------------------------------------------------------
    @dataclass
    class Note:
        id: int
        title: str
        tags: list[str]

    notes = [Note(1, "RAG", ["ai"]), Note(2, "Pathlib", ["python", "io"])]
    json_file = root / "notes.json"
    json_file.write_text(json.dumps([asdict(n) for n in notes], indent=2), encoding="utf-8")
    print(json_file.read_text(encoding="utf-8"))
    loaded = [Note(**d) for d in json.loads(json_file.read_text(encoding="utf-8"))]
    print(loaded == notes)

    # --- CSV --------------------------------------------------------------------------
    csv_file = root / "notes.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "title", "tags"])
        writer.writeheader()
        for n in notes:
            writer.writerow({"id": n.id, "title": n.title, "tags": ";".join(n.tags)})
    print(csv_file.read_text(encoding="utf-8"))
    with open(csv_file, newline="", encoding="utf-8") as f:
        print(list(csv.DictReader(f)))      # everything comes back as str

    print(sorted(p.name for p in root.rglob("*") if p.is_file()))
