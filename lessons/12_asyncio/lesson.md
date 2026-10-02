# Lesson 12: Concurrency with `asyncio`

AI apps are mostly **waiting**: on LLM APIs, vector DBs, HTTP calls. `asyncio` lets one thread wait
on thousands of them at once. FastAPI, the Anthropic SDK (`AsyncAnthropic`), and httpx (`AsyncClient`) are all async-first.

## 1. Python's three concurrency models

| Model                     | Use for                     | Java equivalent                         |
|---------------------------|-----------------------------|-----------------------------------------|
| `asyncio` (coroutines)    | lots of I/O waiting         | virtual threads / `CompletableFuture` / WebFlux |
| `threading` / `ThreadPoolExecutor` | I/O with blocking libraries | `ExecutorService`               |
| `multiprocessing` / `ProcessPoolExecutor` | **CPU-bound** work  | separate JVMs                           |

**The GIL (Global Interpreter Lock):** in standard CPython, only one thread runs Python bytecode at a time.
Threads still help with I/O (the GIL is released while waiting), but **not for CPU-bound Python code**.
For that, use processes, or libraries like numpy that do the heavy work in C. Python 3.13+ has an
experimental free-threaded build that removes the GIL, but don't count on it yet.

## 2. Coroutines

```python
import asyncio

async def fetch(name: str, delay: float) -> str:   # `async def` → calling it returns a coroutine object
    await asyncio.sleep(delay)                    # `await` = "pause here, let other tasks run"
    return f"{name} done"

async def main():
    result = await fetch("a", 1)                  # sequential: 1s
    results = await asyncio.gather(               # concurrent: ~1s total, not 3s
        fetch("a", 1), fetch("b", 1), fetch("c", 1),
    )                                             # results in argument order

asyncio.run(main())                               # the entry point: starts the event loop
```

Rules:
- `await` only works inside `async def`.
- Calling `fetch()` without `await` does **nothing** (you get a "coroutine was never awaited" warning).
- **Never block the event loop**: no `time.sleep()`, `requests.get()`, or heavy CPU work inside async code.
  Use `await asyncio.sleep()`, async clients, or `await asyncio.to_thread(blocking_fn, ...)`.

## 3. The toolbox

```python
# Structured concurrency (3.11+), ≈ StructuredTaskScope: if one task fails, the others are cancelled
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(fetch("a", 1))
    t2 = tg.create_task(fetch("b", 2))
print(t1.result(), t2.result())

# Timeouts
async with asyncio.timeout(2):                  # raises TimeoutError if the block takes > 2s
    await slow_call()

# Limit concurrency (e.g. API rate limits), ≈ java.util.concurrent.Semaphore
sem = asyncio.Semaphore(5)
async def limited(i):
    async with sem:
        return await call_api(i)

# Producer/consumer
queue: asyncio.Queue[int] = asyncio.Queue()
await queue.put(item); item = await queue.get(); queue.task_done(); await queue.join()

# Process results as they finish
for next_done in asyncio.as_completed(coros):
    result = await next_done
```

## 4. Async iteration & context managers

```python
async def stream_tokens(text: str):            # async generator: how LLM streaming works
    for word in text.split():
        await asyncio.sleep(0.05)
        yield word

async for token in stream_tokens("hello async world"):
    print(token, end=" ", flush=True)

async with httpx.AsyncClient() as client:      # async context manager (__aenter__/__aexit__)
    r = await client.get("https://example.com")
```

## 5. In FastAPI

```python
@app.get("/summary/{note_id}")
async def summary(note_id: int):
    note, related = await asyncio.gather(load_note(note_id), find_related(note_id))
    ...
```

Use `async def` endpoints when you call async libraries. Use plain `def` for blocking ones: FastAPI runs those in a thread pool.

## 6. Testing async code

The simplest approach is to call `asyncio.run(...)` inside a normal test. For bigger suites, the
`pytest-asyncio` plugin lets you write `async def test_...` directly.

## 7. Run the example

```bash
uv run python lessons/12_asyncio/asyncio_demo.py
```

## 8. Exercise: concurrent note fetching

Implement `exercise/async_tools.py`: bounded concurrent fetching, timeouts, a worker pool built on
`asyncio.Queue`, and a streaming async generator.

```bash
uv run pytest lessons/12_asyncio/exercise -v
```
