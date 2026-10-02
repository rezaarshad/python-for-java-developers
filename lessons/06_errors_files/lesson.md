# Lesson 06: Errors, Files & Context Managers

## 1. Exceptions: like Java, minus checked exceptions

```python
try:
    value = int(user_input)
except ValueError as e:              # catch (NumberFormatException e)
    print(f"not a number: {e}")
except (TypeError, KeyError):        # multi-catch
    ...
else:                                # runs only if NO exception happened (no Java equivalent)
    print("parsed", value)
finally:                             # always runs
    cleanup()
```

- **No checked exceptions.** Nothing forces you to declare or catch. Document raises in docstrings.
- `raise ValueError("msg")` (no `new`). Re-raise the current exception with a bare `raise`.
- Never write a bare `except:` or `except Exception: pass`, the same as an empty `catch (Exception e) {}`.

### Common built-ins

| Python               | Java                              | When                          |
|----------------------|-----------------------------------|-------------------------------|
| `ValueError`         | `IllegalArgumentException`        | right type, bad value         |
| `TypeError`          | `ClassCastException`-ish          | wrong type                    |
| `KeyError`           | (`map.get` returns null instead)  | missing dict key              |
| `IndexError`         | `IndexOutOfBoundsException`       | bad list index                |
| `AttributeError`     | `NullPointerException` (often)    | `None.foo`                    |
| `FileNotFoundError`  | `FileNotFoundException`           |                               |
| `NotImplementedError`| `UnsupportedOperationException`   |                               |
| `RuntimeError`       | `IllegalStateException`           |                               |

### Custom exceptions and chaining

```python
class NotesError(Exception):            # base for your library: callers can catch just this
    """Base class for all notes-app errors."""

class NoteNotFoundError(NotesError):
    def __init__(self, note_id: int) -> None:
        super().__init__(f"note {note_id} not found")
        self.note_id = note_id

try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    raise CorruptStoreError("bad notes file") from e   # ≈ new X("...", cause); sets __cause__
```

### EAFP vs LBYL

Python culture prefers **EAFP**: "Easier to Ask Forgiveness than Permission":

```python
try:                         # EAFP: Pythonic
    note = notes[note_id]
except KeyError:
    ...

if note_id in notes:         # LBYL: "Look Before You Leap", fine too, but racy for files
    note = notes[note_id]
```

## 2. Context managers: `with` ≈ try-with-resources

```java
try (var reader = Files.newBufferedReader(path)) { ... }
```

```python
with open(path, encoding="utf-8") as f:     # file is closed even if an exception is raised
    content = f.read()
```

Any object with `__enter__`/`__exit__` works with `with`: files, locks, DB transactions,
HTTP clients. You can write your own:

```python
class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self                          # bound to the `as` target
    def __exit__(self, exc_type, exc, tb):   # exception info, or None × 3 on success
        self.elapsed = time.perf_counter() - self.start
        return False                         # False/None = don't swallow exceptions

with Timer() as t:
    work()
print(t.elapsed)
```

(Lesson 07 shows a shorter way to write these with `@contextmanager`.)

## 3. Files with `pathlib` (≈ `java.nio.file.Path` + `Files`)

```python
from pathlib import Path

data_dir = Path.home() / "notes"          # `/` joins paths
file = data_dir / "notes.json"
file.parent.mkdir(parents=True, exist_ok=True) # mkdir -p
file.write_text("hello", encoding="utf-8")     # one-shot read/write
text = file.read_text(encoding="utf-8")
file.exists(), file.is_file(), file.suffix, file.stem, file.name
for p in data_dir.glob("*.json"): ...
file.unlink(missing_ok=True)                   # delete
```

Always pass `encoding="utf-8"` for text files.

## 4. JSON & CSV

```python
import json
json.dumps({"a": [1, 2]}, indent=2)           # dict → str   (≈ Jackson writeValueAsString)
json.loads('{"a": 1}')                        # str → dict
json.dump(obj, f) / json.load(f)              # to/from a file object
```

JSON maps to `dict`, `list`, `str`, `int`/`float`, `bool`, `None`. **Sets and dataclasses aren't
JSON-serializable**: convert them (`list(tags)`, `dataclasses.asdict(note)`) or use pydantic (Lesson 10).

```python
import csv
with open("out.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "title"])
    writer.writeheader()
    writer.writerow({"id": 1, "title": "RAG"})
with open("out.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))            # values come back as strings
```

## 5. Run the example

```bash
uv run python lessons/06_errors_files/errors_files_demo.py
```

## 6. Exercise: notes persistence

`exercise.py`: save and load notes to JSON safely, with your own exception hierarchy, an atomic
write context manager (no half-written files if the program crashes mid-write), and CSV export.
