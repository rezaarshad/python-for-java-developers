# Lesson 16: Code Quality & Shipping (+ the capstone)

## 1. The modern quality toolchain

| Tool        | Job                                          | Java equivalent                       |
|-------------|----------------------------------------------|---------------------------------------|
| `ruff check`| linter (hundreds of rules, very fast)        | Checkstyle + PMD + SpotBugs (partly)  |
| `ruff format` | formatter (Black-compatible)               | Spotless / google-java-format         |
| `mypy` (or `pyright`) | static type checker for your type hints | `javac`'s type checking          |
| `pytest` + `pytest-cov` | tests + coverage                   | JUnit + JaCoCo                        |
| `pre-commit`| run all of the above on `git commit`         | git hooks / Maven enforcer            |

```bash
uv run ruff check .            # lint
uv run ruff check --fix .      # auto-fix what's safe (import sorting, pyupgrade, ...)
uv run ruff format .           # format everything
uv run mypy src/               # type-check
```

Configure them once in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "SIM"]   # pycodestyle, pyflakes, isort, pyupgrade, bugbear, simplify

[tool.mypy]
strict = true                                   # like turning on every javac warning, as errors
```

The rule families worth knowing: **F** (real bugs: unused/undefined names), **B** (bugbear: mutable defaults,
bare excepts), **UP** (use modern syntax: `list[str]` not `List[str]`, `X | None` not `Optional[X]`),
**I** (import order), **SIM** (simplifications).

In VS Code, install the **Ruff** extension and enable format-on-save. That's the Lesson 01 PEP 8 fixes, automated.

## 2. Logging (not print)

```python
import logging

logger = logging.getLogger(__name__)           # ≈ LoggerFactory.getLogger(MyClass.class)

logger.info("indexed %d notes", count)         # lazy %-formatting, like SLF4J's {}
logger.exception("failed to save")             # inside except: logs the stack trace

# once, at the program entry point:
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
```

## 3. Configuration & secrets

Read config from environment variables (12-factor). `pydantic-settings` gives you a typed `Settings` class
that reads env vars and `.env` files (≈ `@ConfigurationProperties`). Put `.env` in `.gitignore`.

## 4. Packaging & distribution

```toml
[project]
name = "notes"
version = "0.1.0"
dependencies = ["typer", "pydantic", "anthropic", "numpy"]

[project.scripts]
notes = "notes.cli:app"        # creates the `notes` command

[build-system]
requires = ["uv_build>=0.12,<0.13"]
build-backend = "uv_build"
```

```bash
uv sync                     # installs your package (editable) + dependencies into .venv
uv run notes --help     # the entry point works
uv build                    # → dist/notes-0.1.0-py3-none-any.whl  (≈ a JAR) + .tar.gz (source)
uv publish                  # upload to PyPI (needs an account + token)
uv tool install .           # install the CLI globally for yourself, in its own isolated env
```

A **wheel** (`.whl`) is a zip of your package plus metadata, the Python equivalent of a JAR.
For services, ship a Docker image instead: `FROM python:3.13-slim`, copy the code, `uv sync --frozen`, then run `uvicorn`.

## 5. Exercise A: clean up `messy.py`

`exercise/messy.py` works (mostly), but it fails every quality gate and has one real bug that ruff's **B**
rules will point you to. Fix it until all tests pass:

```bash
uv run ruff check --select E,F,W,I,UP,B,SIM --line-length 120 lessons/16_shipping/exercise/messy.py
uv run ruff format --line-length 120 lessons/16_shipping/exercise/messy.py
uv run mypy --strict lessons/16_shipping/exercise/messy.py
uv run pytest lessons/16_shipping/exercise -v
```

## 6. Exercise B: the capstone, a real `notes` app 🧠

Assemble everything into the installable package at `src/notes/`, with a `notes` command. The
spec and acceptance tests are in [`capstone/`](capstone/README.md). This is the project you'll keep
extending: add a FastAPI server (Lesson 11), real embeddings, a web UI...
