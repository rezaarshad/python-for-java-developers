"""Lesson 07 exercise: notes streaming & cross-cutting concerns.

Fill in the TODOs, then run:

    uv run python lessons/07_generators_decorators/exercise.py
"""

import functools
import json
import tempfile
import time
from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path


# --- Generators ----------------------------------------------------------------------
def read_jsonl(path: Path) -> Iterator[dict]:
    """Yield one dict per line of a JSON-Lines file (one JSON object per line).
    Skip blank lines. Read lazily: never call f.read() or f.readlines()."""
    # TODO
    pass


def with_tag(notes: Iterable[dict], tag: str) -> Iterator[dict]:
    """Lazily yield only notes whose "tags" list contains `tag`."""
    # TODO (one line: a generator expression)
    pass


def chunked(items: Iterable, size: int) -> Iterator[list]:
    """Yield lists of up to `size` items: chunked(range(5), 2) → [0, 1], [2, 3], [4].
    Write it yourself with a loop and yield (itertools.batched exists, but don't use it here)."""
    # TODO
    pass


class IdSequence:
    """An ITERATOR CLASS (implement __iter__ and __next__, no yield) over ids start, start+step, ...
    that stops before reaching `stop`. Like range(start, stop, step)."""

    def __init__(self, start: int, stop: int, step: int = 1) -> None:
        # TODO
        pass

    # TODO: __iter__, __next__


# --- Decorators ------------------------------------------------------------------------
def timed(fn: Callable) -> Callable:
    """Decorator: after each call, append the elapsed seconds (float) to `wrapper.timings`,
    a list attribute on the wrapper function. Preserve the name/docstring with functools.wraps.
    Record the timing even if fn raises (try/finally)."""
    # TODO
    pass


def retry(times: int, exceptions: tuple[type[Exception], ...] = (Exception,)) -> Callable:
    """Decorator factory: call fn up to `times` times while it raises one of `exceptions`.
    Re-raise the last exception if every attempt fails. Exceptions not in `exceptions`
    propagate immediately, without retrying."""
    # TODO
    pass


# --- Context manager ----------------------------------------------------------------------
@contextmanager
def temporary_tags(note: dict, *tags: str):
    """Add tags to note["tags"] for the duration of the with-block, then restore the
    ORIGINAL tag list, even if the block raises. Yield the note."""
    # TODO
    pass


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "notes.jsonl"
        lines = [json.dumps({"id": i, "title": f"Note {i}", "tags": ["ai"] if i % 2 else ["python"]})
                 for i in range(1, 8)]
        path.write_text("\n".join(lines[:3]) + "\n\n" + "\n".join(lines[3:]) + "\n", encoding="utf-8")

        gen = read_jsonl(path)
        assert isinstance(gen, Iterator), "read_jsonl must be a generator"
        assert next(gen) == {"id": 1, "title": "Note 1", "tags": ["ai"]}
        assert [n["id"] for n in read_jsonl(path)] == [1, 2, 3, 4, 5, 6, 7], "skip blank lines"
        assert [n["id"] for n in with_tag(read_jsonl(path), "ai")] == [1, 3, 5, 7]
        assert isinstance(with_tag([], "x"), Iterator)

    assert list(chunked(range(5), 2)) == [[0, 1], [2, 3], [4]]
    assert list(chunked([], 3)) == []
    assert isinstance(chunked([1], 1), Iterator)

    seq = IdSequence(10, 20, 3)
    assert iter(seq) is seq and list(seq) == [10, 13, 16, 19] and list(seq) == []
    assert list(IdSequence(1, 4)) == [1, 2, 3]

    @timed
    def work(n: int) -> int:
        """Docstring kept."""
        time.sleep(0.01)
        return n * 2

    assert work(21) == 42 and work(1) == 2
    assert work.__name__ == "work" and work.__doc__ == "Docstring kept."
    assert len(work.timings) == 2 and all(t >= 0.01 for t in work.timings)

    calls = {"flaky": 0, "fatal": 0}

    @retry(times=3, exceptions=(ConnectionError,))
    def flaky() -> str:
        calls["flaky"] += 1
        if calls["flaky"] < 3:
            raise ConnectionError("try again")
        return "ok"

    @retry(times=5, exceptions=(ConnectionError,))
    def fatal() -> None:
        calls["fatal"] += 1
        raise ValueError("not retryable")

    @retry(times=2)
    def always_down() -> None:
        raise ConnectionError("down")

    assert flaky() == "ok" and calls["flaky"] == 3
    try:
        fatal()
        raise AssertionError("expected ValueError")
    except ValueError:
        assert calls["fatal"] == 1, "non-retryable errors must not be retried"
    try:
        always_down()
        raise AssertionError("expected ConnectionError after retries")
    except ConnectionError:
        pass

    note = {"id": 1, "tags": ["ai"]}
    with temporary_tags(note, "draft", "wip") as n:
        assert n is note and n["tags"] == ["ai", "draft", "wip"]
    assert note["tags"] == ["ai"]
    try:
        with temporary_tags(note, "draft"):
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert note["tags"] == ["ai"], "tags must be restored even after an exception"
    print("All checks passed ✅")


if __name__ == "__main__":
    main()
