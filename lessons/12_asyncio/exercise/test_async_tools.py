"""Provided tests. Run: uv run pytest lessons/12_asyncio/exercise -v

These call asyncio.run(...) inside normal test functions, so no plugin is needed.
"""

import asyncio
import time

import httpx
import pytest

from async_tools import (
    NoteNotFoundError,
    collect_stream,
    fetch_many,
    fetch_many_safe,
    fetch_note,
    process_with_workers,
    stream_words,
    with_timeout,
)


class SlowFakeServer:
    """Async MockTransport handler: each request takes `delay` seconds; tracks peak concurrency."""

    def __init__(self, delay: float = 0.05, missing: set[int] = frozenset()) -> None:
        self.delay = delay
        self.missing = missing
        self.active = 0
        self.peak = 0
        self.calls = 0

    async def __call__(self, request: httpx.Request) -> httpx.Response:
        self.calls += 1
        self.active += 1
        self.peak = max(self.peak, self.active)
        try:
            await asyncio.sleep(self.delay)
            note_id = int(request.url.path.rsplit("/", 1)[-1])
            if note_id in self.missing:
                return httpx.Response(404)
            if note_id == 500:
                return httpx.Response(500)
            return httpx.Response(200, json={"id": note_id, "title": f"Note {note_id}"})
        finally:
            self.active -= 1


def client_for(server: SlowFakeServer) -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url="https://notes.test", transport=httpx.MockTransport(server))


def run(coro_fn):
    """Run `async def` code from a sync test."""
    return asyncio.run(coro_fn())


def test_fetch_note():
    async def go():
        async with client_for(SlowFakeServer(delay=0)) as c:
            return await fetch_note(c, 7)
    assert run(go) == {"id": 7, "title": "Note 7"}


def test_fetch_note_missing():
    async def go():
        async with client_for(SlowFakeServer(delay=0, missing={3})) as c:
            await fetch_note(c, 3)
    with pytest.raises(NoteNotFoundError):
        run(go)


def test_fetch_note_server_error():
    async def go():
        async with client_for(SlowFakeServer(delay=0)) as c:
            await fetch_note(c, 500)
    with pytest.raises(httpx.HTTPStatusError):
        run(go)


def test_fetch_many_is_concurrent_ordered_and_bounded():
    server = SlowFakeServer(delay=0.1)

    async def go():
        async with client_for(server) as c:
            return await fetch_many(c, range(1, 11), max_concurrency=5)

    start = time.perf_counter()
    notes = run(go)
    elapsed = time.perf_counter() - start
    assert [n["id"] for n in notes] == list(range(1, 11)), "results must keep input order"
    assert server.peak == 5, f"expected exactly 5 concurrent requests, saw {server.peak}"
    assert elapsed < 0.5, f"10 × 0.1s with 5 at a time should take ~0.2s, took {elapsed:.2f}s"


def test_fetch_many_safe():
    async def go():
        async with client_for(SlowFakeServer(delay=0.01, missing={2, 4})) as c:
            return await fetch_many_safe(c, [1, 2, 3, 4, 5])
    found, missing = run(go)
    assert [n["id"] for n in found] == [1, 3, 5]
    assert missing == [2, 4]


def test_with_timeout_returns_value_when_fast():
    async def go():
        return await with_timeout(asyncio.sleep(0.01, result="fast"), 1)
    assert run(go) == "fast"


def test_with_timeout_returns_default_when_slow():
    async def go():
        return await with_timeout(asyncio.sleep(5, result="slow"), 0.05, default="gave up")
    start = time.perf_counter()
    assert run(go) == "gave up"
    assert time.perf_counter() - start < 1


def test_process_with_workers_order_and_parallelism():
    active = peak = 0

    async def handler(n: int) -> int:
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0.05 if n % 2 else 0.01)   # uneven durations: completion order ≠ input order
        active -= 1
        return n * 10

    async def go():
        return await process_with_workers(range(9), handler, workers=3)

    start = time.perf_counter()
    assert run(go) == [n * 10 for n in range(9)]
    assert peak == 3
    assert time.perf_counter() - start < 0.4


def test_process_with_workers_empty():
    async def handler(n):
        return n
    assert run(lambda: process_with_workers([], handler)) == []


def test_stream_words_is_async_generator():
    gen = stream_words("a b")
    assert hasattr(gen, "__anext__")
    assert run(lambda: collect_stream(stream_words("tokens  arrive one at a time"))) == "tokens arrive one at a time"


def test_stream_words_awaits_between_words():
    start = time.perf_counter()
    run(lambda: collect_stream(stream_words("a b c d", delay=0.05)))
    assert time.perf_counter() - start >= 0.2
