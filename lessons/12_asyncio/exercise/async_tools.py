"""Lesson 12 exercise: concurrent note fetching.

Test: uv run pytest lessons/12_asyncio/exercise -v
"""

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable, Iterable

import httpx


class NoteNotFoundError(Exception):
    pass


async def fetch_note(client: httpx.AsyncClient, note_id: int) -> dict:
    """GET /notes/{note_id} and return the JSON dict. 404 → NoteNotFoundError(note_id).
    Other HTTP errors → raise_for_status()."""
    # TODO
    pass


async def fetch_many(client: httpx.AsyncClient, note_ids: Iterable[int], max_concurrency: int = 5) -> list[dict]:
    """Fetch all notes CONCURRENTLY, but never more than `max_concurrency` requests in flight
    (asyncio.Semaphore). Return results in the same order as note_ids (asyncio.gather keeps order)."""
    # TODO
    pass


async def fetch_many_safe(client: httpx.AsyncClient, note_ids: Iterable[int]) -> tuple[list[dict], list[int]]:
    """Like fetch_many, but missing notes don't fail the batch. Return (found_notes, missing_ids),
    both in input order. Hint: asyncio.gather(..., return_exceptions=True)."""
    # TODO
    pass


async def with_timeout[T](awaitable: Awaitable[T], seconds: float, default: T | None = None) -> T | None:
    """Await `awaitable`, but give up after `seconds` and return `default` instead.
    (The [T] makes this a generic function, Python 3.12 syntax ≈ <T> T withTimeout(...) in Java.)"""
    # TODO (asyncio.timeout or asyncio.wait_for)
    pass


async def process_with_workers[T, R](items: Iterable[T], handler: Callable[[T], Awaitable[R]],
                                     workers: int = 3) -> list[R]:
    """Producer/consumer: put every item on an asyncio.Queue, start `workers` worker tasks
    that each loop on queue.get() → await handler(item), and return all results in INPUT order.
    Hint: queue (index, item) pairs and write into a preallocated list. Cancel the workers at the end."""
    # TODO
    pass


async def stream_words(text: str, delay: float = 0.0) -> AsyncIterator[str]:
    """Async generator: yield each word of `text`, awaiting asyncio.sleep(delay) before each one."""
    # TODO
    yield ""   # placeholder so this is an async generator; replace it


async def collect_stream(stream: AsyncIterator[str]) -> str:
    """Consume an async iterator with `async for`, joining the words with single spaces."""
    # TODO
    pass
