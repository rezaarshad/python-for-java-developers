# Capstone: `notes`, your second brain in the terminal

Build the real package in **`src/notes/`** by reusing your solutions from the earlier lessons. There's no
skeleton this time: you design the modules. Done = the acceptance tests pass and `uv run notes` works.

```bash
uv run pytest lessons/16_shipping/capstone -v
```

## Suggested layout

```
src/notes/
├── __init__.py     # __version__ = "0.1.0"
├── models.py       # pydantic Note / NoteIn                          (Lesson 10)
├── storage.py      # JSON file repository, atomic writes, errors     (Lessons 06, 07)
├── search.py       # TF-IDF embedder + vector index                  (Lessons 13, 15)
├── llm.py          # Claude client factory + RAG answer              (Lessons 14, 15)
└── cli.py          # typer app                                       (Lesson 09)
```

Then turn the repo into an installable package. In `pyproject.toml`, delete the `[tool.uv]` / `package = false`
lines and add:

```toml
[project.scripts]
notes = "notes.cli:app"       # creates the `notes` command

[build-system]
requires = ["uv_build>=0.12,<0.13"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-name = "notes"         # the package lives in src/notes/ (the project name is different)
```

Run `uv sync`: uv installs your package in editable mode, and `uv run notes --help` works.

## Spec (what the acceptance tests check)

The global option `--file/-f PATH` (env var `NOTES_FILE`, default `~/.notes.json`) works as in Lesson 09.

| Command | Behaviour |
|---------|-----------|
| `notes --version` | prints `notes 0.1.0`, exits 0 (hint: an eager `typer.Option` callback on the app callback) |
| `add TITLE [-b BODY] [-t TAG]...` | prints `Added note <id>: <title>`. Tags are lowercased and deduped. The note gets a `created_at` timestamp |
| `list [-t TAG]` | a table of ID, Title, Tags; `No notes yet.` if there are none |
| `show ID` | prints the title, tags, and body; unknown id → `Note <id> not found`, exit 1 |
| `search QUERY [-k N]` | TF-IDF search over title + body; one line per hit, `<id>: <title>`, best first; nothing relevant → `No matches for '<query>'`, exit 1 |
| `delete ID [-y]` | as in Lesson 09 |
| `ask QUESTION` | RAG: retrieve the top notes, ask Claude, print the answer, then a `Sources: 1, 3` line (note ids). Without `ANTHROPIC_API_KEY` → `Set ANTHROPIC_API_KEY to use 'ask'`, exit 1. Nothing relevant → `I couldn't find anything relevant in your notes.` with **no** LLM call |

Storage format: a JSON list of notes, each `{"id", "title", "body", "tags", "created_at"}` (ISO datetime string).

### Testability contract for `ask`

`notes.llm` must expose `make_client()`, which returns `anthropic.Anthropic()`. The CLI must call it as
`llm.make_client()` (look it up on the module at call time), so tests can monkeypatch it with a fake client
that has `.beta.messages.create(**kwargs)`. Use the Lesson 14 `LLM_OPTIONS` (model + refusal fallback).

## Quality bar

```bash
uv run ruff check src/ && uv run ruff format --check src/ && uv run mypy --strict src/
```

## Stretch goals

- `notes serve`: start a FastAPI server (Lesson 11) over the same storage
- `notes summarize ID` and `notes tag ID` (Lesson 14 functions)
- Swap TF-IDF for real embeddings (Voyage AI), behind the same `Embedder` protocol
- `uv build`, then `uv tool install dist/*.whl` and use `notes` from anywhere
