# Lesson 05: Modules, Packages & Project Layout

## 1. Vocabulary (Java → Python)

| Java                         | Python                                                      |
|------------------------------|-------------------------------------------------------------|
| `.java` file / class         | **module**: any `.py` file                                  |
| package (directory)          | **package**: a directory with an `__init__.py`              |
| JAR on Maven Central         | **distribution** on PyPI (pypi.org), installed with uv/pip  |
| `pom.xml` / `build.gradle`   | `pyproject.toml`                                            |
| Maven/Gradle                 | `uv` (or pip, poetry)                                       |
| `~/.m2` + classpath          | virtual environment (`.venv/`), one per project             |
| `mvn dependency:tree` lock   | `uv.lock` (commit it!)                                      |

One file can hold many classes and functions. Don't write one class per file. Group by topic.

## 2. Imports

```python
import math                       # use as math.sqrt(2)
from math import sqrt, pi         # use as sqrt(2)
from collections import Counter as C   # alias
import numpy as np                # conventional aliases: np, pd, plt
from mypkg.models import Note     # absolute import (preferred)
from .models import Note          # relative import, only inside a package
```

Avoid `from module import *`. It hides where names come from.

When you `import x`, Python searches `sys.path` (≈ the classpath): the script's directory, then
the standard library, then `.venv/.../site-packages`. **Modules run once, on first import**, and are then cached in `sys.modules`.
That's why the `if __name__ == "__main__":` guard matters.

## 3. A package

```
notes_lite/
├── __init__.py      # runs on `import notes_lite`; defines the public API
├── __main__.py      # runs on `python -m notes_lite`
├── models.py        # Note, Priority
├── store.py         # NoteStore (imports from .models)
└── exporters.py     # MarkdownExporter, CsvExporter
```

`__init__.py` usually re-exports the public API so users write `from notes_lite import Note`
instead of `from notes_lite.models import Note`:

```python
# notes_lite/__init__.py
from .models import Note, Priority
from .store import NoteStore

__all__ = ["Note", "Priority", "NoteStore"]   # what's "public" (and what `import *` takes)
__version__ = "0.1.0"
```

**Circular imports** (a imports b, b imports a) fail more easily than in Java. Keep dependencies
pointing one way: `models` ← `store` ← `exporters`/`cli`.

## 4. The `src/` layout

```
my-project/
├── pyproject.toml
├── uv.lock
├── src/notes/__init__.py        # the installable package (you build this in the Lesson 16 capstone)
├── tests/
└── .venv/
```

Putting the package under `src/` stops it from being imported by accident from the working directory.
You only import the *installed* version, which `uv` installs in editable mode (≈ `mvn install` with live reload).

## 5. `pyproject.toml` & `uv`

```toml
[project]
name = "notes"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = ["httpx>=0.28", "pydantic>=2.13"]     # ≈ <dependencies>

[project.scripts]
notes = "notes:main"             # creates a `notes` command → calls notes.main()

[dependency-groups]
dev = ["pytest", "ruff", "mypy"]   # ≈ <scope>test</scope>
```

| Task                         | Command                          |
|------------------------------|----------------------------------|
| add a dependency             | `uv add httpx`                   |
| add a dev-only dependency    | `uv add --dev pytest`            |
| remove                       | `uv remove httpx`                |
| install everything from lock | `uv sync`                        |
| run in the venv              | `uv run python app.py`, `uv run pytest` |
| run a tool without installing| `uvx ruff check .` (≈ `npx`)     |
| upgrade                      | `uv lock --upgrade`              |

You'll see `pip install -r requirements.txt` in older projects. It's the same idea with less tooling.

## 6. Standard library highlights ("batteries included")

`pathlib`, `json`, `csv`, `datetime`, `re`, `logging`, `argparse`, `subprocess`, `itertools`,
`functools`, `collections`, `dataclasses`, `typing`, `unittest`, `sqlite3`, `urllib`, `zipfile`,
`random`, `statistics`, `uuid`, `hashlib`. Check the stdlib before adding a dependency.

## 7. Run the example

```bash
cd lessons/05_packages/demo
uv run python app.py
uv run python -m geometry
```

## 8. Exercise: package the notes app

Turn your Lesson 04 solution into a package. Work in `lessons/05_packages/exercise/`:

1. Fill in the files in `notes_lite/`. Each file has TODO instructions. Copy your Lesson 04 code into them.
2. Use relative imports between modules (`from .models import Note`).
3. Re-export the public API from `__init__.py`, and set `__all__` and `__version__ = "0.1.0"`.
4. Make `python -m notes_lite` print `notes_lite 0.1.0: 3 notes`.

Check your work:

```bash
cd lessons/05_packages/exercise
uv run python check.py
```
