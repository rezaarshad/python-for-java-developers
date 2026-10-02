# Lesson 07: Iterators, Generators & Decorators

These three features show up in every serious Python codebase: FastAPI routes are decorators,
pytest fixtures are generators, and LLM streaming responses are iterators.

## 1. The iterator protocol

`for x in obj` calls `iter(obj)` to get an iterator, then calls `next()` on it until `StopIteration`.
That's Java's `Iterable.iterator()` / `hasNext()` / `next()`, merged into one exception-terminated call.

```python
class Countdown:
    def __init__(self, start: int) -> None:
        self.current = start
    def __iter__(self):            # ≈ Iterable.iterator()
        return self
    def __next__(self) -> int:     # ≈ next(); raise StopIteration instead of hasNext() == false
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1
```

## 2. Generators: iterators the easy way

A function containing `yield` returns a **generator**: a lazy iterator that pauses at each `yield`.

```python
def countdown(start: int):
    while start > 0:
        yield start          # hand out a value and pause here until the next next()
        start -= 1

for n in countdown(3): print(n)     # 3 2 1
```

Why it matters:
- **Lazy & memory-efficient**: process a 10 GB log file line by line (≈ a Java `Stream` that's never collected).
- **Pipelines**: chain generators like Stream stages; nothing runs until someone consumes it.
- **Infinite sequences** are fine: `itertools.count()`.

```python
def read_lines(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n")

def non_empty(lines):
    return (l for l in lines if l.strip())          # generator expression

for line in non_empty(read_lines("huge.log")): ...  # streams; never loads the whole file
```

`yield from other_iterable` delegates to another generator. A generator can only be consumed **once**,
just like a Java `Stream`.

## 3. `itertools`: the Streams toolbox

```python
from itertools import islice, chain, groupby, batched, count, pairwise, accumulate
islice(gen, 5)                    # limit(5)
chain(a, b)                       # Stream.concat
batched(range(10), 3)             # (0,1,2) (3,4,5) (6,7,8) (9,)   (3.12+)
pairwise([1, 2, 3])               # (1,2) (2,3)
accumulate([1, 2, 3])             # 1 3 6   (running total)
groupby(sorted_items, key=fn)     # groups CONSECUTIVE equal keys; sort first!
```

## 4. Decorators

A decorator is a function that takes a function and returns a (usually wrapped) function.
`@decorator` is just syntax sugar:

```python
@timed
def work(): ...
# is exactly:
work = timed(work)
```

Think of it as lightweight AOP (Spring's `@Transactional`, `@Cacheable`) with no proxies or
reflection, just functions.

```python
import functools, time

def timed(fn):
    @functools.wraps(fn)                 # keep fn's __name__ and __doc__ on the wrapper
    def wrapper(*args, **kwargs):        # accept any signature
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"{fn.__name__} took {time.perf_counter() - start:.3f}s")
    return wrapper
```

**Decorators with arguments** need one more layer: a factory that *returns* a decorator:

```python
def retry(times: int):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if attempt == times - 1:
                        raise
        return wrapper
    return decorator

@retry(times=3)          # retry(3) runs first and returns the real decorator
def call_api(): ...
```

### Built-in decorators you'll use

| Decorator                          | Purpose                                         |
|------------------------------------|-------------------------------------------------|
| `@functools.cache` / `@lru_cache(maxsize=128)` | memoization (≈ `@Cacheable`)        |
| `@property`, `@classmethod`, `@staticmethod` | Lesson 04                             |
| `@dataclass`                       | Lesson 04 (a class decorator!)                  |
| `@contextlib.contextmanager`       | write a context manager as a generator          |
| `@app.get("/notes")`               | FastAPI routes (Lesson 11)                      |
| `@pytest.fixture`                  | test fixtures (Lesson 08)                       |

## 5. `@contextmanager`: context managers from generators

```python
from contextlib import contextmanager

@contextmanager
def timer(label: str):
    start = time.perf_counter()
    try:
        yield                           # the body of the `with` block runs here
    finally:
        print(f"{label}: {time.perf_counter() - start:.3f}s")

with timer("load"):
    load_everything()
```

Code before `yield` is `__enter__`, code after it is `__exit__`. Compare that with the `Timer` class in Lesson 06.

## 6. Run the example

```bash
uv run python lessons/07_generators_decorators/generators_decorators_demo.py
```

## 7. Exercise: notes streaming & cross-cutting concerns

`exercise.py`: stream notes lazily from a JSON-Lines file, batch them, and write `@timed`,
`@retry(...)`, and `@contextmanager` helpers.
