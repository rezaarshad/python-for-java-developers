# Python for Java Developers → AI Engineer

**Learn Python the way a Java developer thinks: 16 hands-on lessons from Hello World to FastAPI, pandas,
and building an AI assistant with Claude & RAG.**

![Python 3.13](https://img.shields.io/badge/python-3.13-blue) ![uv](https://img.shields.io/badge/managed%20with-uv-purple) ![License: MIT](https://img.shields.io/badge/license-MIT-green)

## Who this is for

You already know how to program: Java, Spring, JUnit, Maven. You don't need another "what is a variable"
tutorial. You need to know **what's different**, **what the Python equivalent of X is**, and **which libraries
people actually use**. Every lesson maps Python onto concepts you already know:

| You know (Java)                          | You'll learn (Python)                           |
|------------------------------------------|-------------------------------------------------|
| `record`, Lombok `@Data`                 | `@dataclass`, pydantic models                   |
| `stream().filter().map().collect()`      | comprehensions, generators, `itertools`         |
| interfaces                               | `Protocol` (structural typing)                  |
| JUnit, Mockito                           | pytest fixtures, `parametrize`, `Mock`          |
| Spring `@RestController` + JPA           | FastAPI + SQLAlchemy                            |
| `CompletableFuture`, virtual threads     | `asyncio`, `async`/`await`                      |
| Maven + `pom.xml`                        | `uv` + `pyproject.toml`                         |

## What you'll build

One project grows with you, lesson by lesson: a personal notes assistant.
It starts as a script, then becomes a CLI, a REST API, a data pipeline, and finally an AI assistant
that answers questions about your notes using retrieval-augmented generation (RAG).

When you finish the capstone, it works like this:

```console
$ notes add "RAG" -b "Retrieve relevant notes with embeddings, then prompt Claude" -t ai
Added note 1: RAG
$ notes search "embeddings"
1: RAG
$ notes ask "How does RAG use my notes?"
<Claude's answer, grounded in your notes, citing [1]>
Sources: 1
```

## Roadmap

| #  | Lesson | Python concepts | Libraries | Exercise |
|----|--------|-----------------|-----------|----------|
| 01 | [Setup & Hello World](lessons/01_hello/lesson.md) | interpreter, REPL, dynamic typing, f-strings, `__main__` | — | warm-up functions |
| 02 | [Collections & comprehensions](lessons/02_collections/lesson.md) | list/dict/set/tuple, slicing, comprehensions, unpacking | `collections` | in-memory note store |
| 03 | [Functions](lessons/03_functions/lesson.md) | defaults, `*args/**kwargs`, type hints, closures | — | query predicates & combinators |
| 04 | [Classes the Pythonic way](lessons/04_classes/lesson.md) | `@dataclass`, dunders, properties, Protocols, Enum | `dataclasses` | `Note` model + `NoteStore` |
| 05 | [Modules & packages](lessons/05_packages/lesson.md) | imports, `__init__`, `__main__`, `pyproject.toml` | `uv` | package it as `notes_lite` |
| 06 | [Errors, files, context managers](lessons/06_errors_files/lesson.md) | exceptions, `with`, `pathlib`, JSON, CSV | `pathlib`, `json`, `csv` | persistence + atomic writes |
| 07 | [Iterators, generators, decorators](lessons/07_generators_decorators/lesson.md) | `yield`, `itertools`, `functools`, `@contextmanager` | `itertools` | streaming + `@timed`/`@retry` |
| 08 | [Testing](lessons/08_testing/lesson.md) | fixtures, parametrize, mocks, monkeypatch | `pytest` | write tests, find the bug 🐛 |
| 09 | [Command-line apps](lessons/09_cli/lesson.md) | type-hint-driven CLIs, `CliRunner` | `typer`, `rich` | the notes CLI |
| 10 | [Validation & HTTP](lessons/10_pydantic_httpx/lesson.md) | models, validators, `MockTransport` | `pydantic`, `httpx` | typed API client |
| 11 | [REST API + database](lessons/11_fastapi_sqlalchemy/lesson.md) | `Depends`, ORM, dependency overrides | `fastapi`, `sqlalchemy` | notes REST API |
| 12 | [Concurrency](lessons/12_asyncio/lesson.md) | `async/await`, gather, Semaphore, Queue, GIL | `asyncio` | concurrent fetching |
| 13 | [Data essentials](lessons/13_data/lesson.md) | vectorization, DataFrames, plotting | `numpy`, `pandas`, `matplotlib` | note analytics |
| 14 | [LLMs with Claude](lessons/14_llm_claude/lesson.md) | messages, streaming, structured output, tool use | `anthropic` | summaries, chat, agent loop |
| 15 | [Embeddings & RAG](lessons/15_rag/lesson.md) | TF-IDF, cosine search, grounding, recall@k | `numpy` + `anthropic` | "ask your notes" |
| 16 | [Code quality & shipping](lessons/16_shipping/lesson.md) | lint, types, logging, packaging | `ruff`, `mypy` | clean-up + **capstone** |

### Side lessons

Tools that aren't part of the main track but that you'll use throughout.

| Lesson | What |
|--------|------|
| [Jupyter](lessons/side_jupyter/lesson.md) | interactive notebooks for exploring data and AI |

## Getting started

Requires [uv](https://docs.astral.sh/uv/) (it installs Python 3.13 for you):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/rezaarshad/python-for-java-developers.git && cd python-for-java-developers
uv sync                                      # creates .venv with Python 3.13 and every library
uv run python lessons/01_hello/hello.py
```

## How each lesson works

Each lesson lives in `lessons/NN_name/` with:
- `lesson.md`: the concepts, with Java side-by-side comparisons
- demo `*.py` files: runnable examples (read them top to bottom)
- an exercise with TODOs:
  - **Lessons 01–07**: `exercise.py`, with `assert` checks in `main()` → `uv run python lessons/NN_.../exercise.py` until it prints `All checks passed ✅`
  - **Lessons 08–16**: a module plus provided pytest tests → `uv run pytest lessons/NN_... -v` until everything is green

Every exercise has been checked against a reference solution (not included), so if a test fails, the bug is in the exercise code, not the test.

```bash
uv run pytest lessons/09_cli -v        # test one lesson
uv run pytest                          # everything (unsolved exercises fail; that's expected)
```

Lesson 14 onward can call the real Claude API: set `ANTHROPIC_API_KEY` to run the demos. The exercise tests
use fake clients, so they need no key and cost nothing.

## License

[MIT](LICENSE): use it, fork it, teach with it.
