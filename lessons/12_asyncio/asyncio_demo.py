"""Lesson 12 demo: asyncio essentials.

Run: uv run python lessons/12_asyncio/asyncio_demo.py
"""

import asyncio
import time

import httpx


async def fetch(name: str, delay: float) -> str:
    await asyncio.sleep(delay)          # stands in for a network call
    return f"{name} ({delay}s)"


def timer(label: str, start: float) -> None:
    print(f"  {label}: {time.perf_counter() - start:.2f}s")


async def sequential_vs_concurrent() -> None:
    print("sequential vs gather")
    start = time.perf_counter()
    for name in "abc":
        await fetch(name, 0.3)
    timer("sequential (3 × 0.3s)", start)

    start = time.perf_counter()
    results = await asyncio.gather(*(fetch(name, 0.3) for name in "abc"))
    timer(f"gather {results}", start)


async def task_group() -> None:
    print("TaskGroup (structured concurrency)")

    async def boom() -> None:
        await asyncio.sleep(0.1)
        raise ValueError("task failed")

    try:
        async with asyncio.TaskGroup() as tg:
            slow = tg.create_task(fetch("slow", 5))   # gets cancelled when boom() fails
            tg.create_task(boom())
    except* ValueError as eg:                         # except* handles ExceptionGroups (3.11+)
        print("  caught:", eg.exceptions, "| slow cancelled:", slow.cancelled())


async def timeouts() -> None:
    print("timeout")
    try:
        async with asyncio.timeout(0.2):
            await fetch("too slow", 1)
    except TimeoutError:
        print("  timed out after 0.2s")
    print("  wait_for:", await asyncio.wait_for(fetch("fast", 0.05), timeout=1))


async def semaphore() -> None:
    print("Semaphore(2): 6 jobs, at most 2 at a time")
    sem = asyncio.Semaphore(2)
    active = 0

    async def job(i: int) -> int:
        nonlocal active
        async with sem:
            active += 1
            print(f"  job {i} start (active={active})")
            await asyncio.sleep(0.1)
            active -= 1
            return i * i

    start = time.perf_counter()
    print("  results:", await asyncio.gather(*(job(i) for i in range(6))))
    timer("total (~3 × 0.1s)", start)


async def as_completed_demo() -> None:
    print("as_completed (fastest first)")
    for next_done in asyncio.as_completed([fetch("slow", 0.3), fetch("fast", 0.1), fetch("mid", 0.2)]):
        print("  ", await next_done)


async def queue_workers() -> None:
    print("Queue + workers")
    queue: asyncio.Queue[int] = asyncio.Queue()
    results: list[str] = []

    async def worker(wid: int) -> None:
        while True:
            n = await queue.get()
            await asyncio.sleep(0.05)
            results.append(f"w{wid}:{n}")
            queue.task_done()

    for n in range(6):
        queue.put_nowait(n)
    workers = [asyncio.create_task(worker(i)) for i in range(3)]
    await queue.join()                     # wait until every item is processed
    for w in workers:
        w.cancel()                         # workers loop forever, so stop them
    print("  ", results)


async def stream_tokens(text: str):
    for word in text.split():
        await asyncio.sleep(0.08)
        yield word + " "


async def streaming() -> None:
    print("async generator (like LLM streaming): ", end="")
    async for token in stream_tokens("tokens arrive one at a time"):
        print(token, end="", flush=True)
    print()


def blocking_cpu_work(n: int) -> int:
    return sum(i * i for i in range(n))


async def to_thread_demo() -> None:
    print("to_thread: run blocking code without freezing the loop")
    result, _ = await asyncio.gather(asyncio.to_thread(blocking_cpu_work, 2_000_000), fetch("meanwhile", 0.1))
    print("  ", result)


async def real_http() -> None:
    print("httpx.AsyncClient: 5 requests concurrently")
    try:
        async with httpx.AsyncClient(base_url="https://jsonplaceholder.typicode.com", timeout=5) as client:
            start = time.perf_counter()
            responses = await asyncio.gather(*(client.get(f"/posts/{i}") for i in range(1, 6)))
            print("  ", [r.json()["id"] for r in responses])
            timer("5 requests", start)
    except httpx.RequestError as e:
        print(f"   (network unavailable: {e!r})")


async def main() -> None:
    for demo in [sequential_vs_concurrent, task_group, timeouts, semaphore, as_completed_demo,
                 queue_workers, streaming, to_thread_demo, real_http]:
        await demo()


if __name__ == "__main__":
    asyncio.run(main())
