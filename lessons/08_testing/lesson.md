# Lesson 08: Testing with pytest

`pytest` is the de-facto standard (`unittest` is in the stdlib, JUnit-style, but rarely chosen for new code).
From now on, every exercise comes with pytest tests instead of `assert`s in `main()`.

## 1. JUnit → pytest

```java
class CalculatorTest {
    @Test
    void addsNumbers() {
        assertEquals(4, Calculator.add(2, 2));
    }
}
```

```python
def test_adds_numbers():
    assert add(2, 2) == 4
```

- Test files are named `test_*.py`, and test functions `test_*`. No class needed (you *can* group them in `class TestX:`).
- A plain `assert`: pytest rewrites it to show both sides on failure. No `assertEquals` zoo.
- Run with `uv run pytest`, `uv run pytest path/to/test_file.py::test_name`, or `-k "slug"` (name filter).
  Use `-x` to stop at the first failure and `-v` for verbose output.

## 2. Exceptions & approximate values

```python
import pytest

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError, match="division"):   # ≈ assertThrows
        divide(1, 0)

def test_float():
    assert 0.1 + 0.2 == pytest.approx(0.3)
```

## 3. Fixtures ≈ `@BeforeEach` + dependency injection

```python
@pytest.fixture
def store():                       # setup
    s = NoteStore()
    s.add("RAG")
    yield s                        # the test runs here
    s.close()                      # teardown (optional)

def test_len(store):               # request a fixture by naming a parameter
    assert len(store) == 1
```

- Each test gets a **fresh** fixture (`scope="function"` by default). Use `scope="module"`/`"session"` for expensive ones.
- Fixtures can depend on other fixtures.
- Shared fixtures go in `conftest.py`, which pytest discovers automatically. No imports needed.
- Built-in fixtures: `tmp_path` (a fresh temp `Path`), `monkeypatch`, `capsys` (captured stdout), `caplog`.

## 4. Parametrize ≈ `@ParameterizedTest`

```python
@pytest.mark.parametrize("text, expected", [
    ("Hello World", "hello-world"),
    ("  spaces  ", "spaces"),
    ("C++ & Java!", "c-java"),
])
def test_slugify(text, expected):
    assert slugify(text) == expected
```

## 5. Mocking ≈ Mockito

```python
from unittest.mock import Mock

def test_summary_uses_client():
    client = Mock()
    client.summarize.return_value = "short"           # when(client.summarize(any())).thenReturn("short")
    assert summarize_note(note, client) == "short"
    client.summarize.assert_called_once_with(note.body)  # verify(client).summarize(note.body)

client.fetch.side_effect = TimeoutError()              # thenThrow
```

Because of duck typing, you often don't need a mocking library at all. Pass a tiny fake class.
Prefer **fakes** (a real in-memory implementation) over mocks for repositories.

`monkeypatch` swaps attributes and environment variables for one test and undoes it afterwards:

```python
def test_reads_api_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(module, "now", lambda: FIXED_TIME)
```

## 6. Design for testability

Inject dependencies (a repository, a clock, an HTTP client) through the constructor or as function
parameters, exactly as you'd do with Spring, minus the container. That's what makes `NoteService` in the exercise testable.

## 7. Run the example

```bash
uv run pytest lessons/08_testing/demo -v
```

## 8. Exercise: test the notes service layer (and find the bug 🐛)

`exercise/note_service.py` is **finished code with one bug in it**. Your job:

1. Write the tests in `exercise/test_note_service.py`. Each TODO test currently fails with `pytest.fail("TODO")`.
2. Use fixtures, `parametrize`, `pytest.raises`, a fake clock, and a `Mock`.
3. One of your tests should expose the bug. Then fix it in `note_service.py`.

```bash
uv run pytest lessons/08_testing/exercise -v
```

Done = all green, with the bug fixed.
