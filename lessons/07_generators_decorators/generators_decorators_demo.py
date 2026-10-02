"""Lesson 07: iterators, generators, itertools, decorators, @contextmanager.

Run: uv run python lessons/07_generators_decorators/generators_decorators_demo.py
"""

import functools
import itertools
import time
from collections.abc import Iterable, Iterator
from contextlib import contextmanager


# --- Iterator protocol, by hand ------------------------------------------------
class Countdown:
    def __init__(self, start: int) -> None:
        self.current = start

    def __iter__(self) -> "Countdown":
        return self

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1


print(list(Countdown(3)))

it = iter([10, 20])                 # what `for` does under the hood
print(next(it), next(it), next(it, "done"))   # next() with a default instead of StopIteration


# --- Generators ------------------------------------------------------------------
def countdown(start: int) -> Iterator[int]:
    print("  (generator started)")   # runs only when the first value is requested
    while start > 0:
        yield start
        start -= 1


gen = countdown(3)                   # nothing printed yet: lazy!
print("created generator")
print(next(gen), list(gen))          # 3 [2, 1]
print(list(gen))                     # []: exhausted, like a consumed Stream


def fibonacci() -> Iterator[int]:    # infinite sequence, fine because it's lazy
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


print(list(itertools.islice(fibonacci(), 10)))


# Pipeline of generators ≈ Stream stages
def numbers(n: int) -> Iterator[int]:
    yield from range(n)              # delegate to another iterable


def evens(xs: Iterable[int]) -> Iterator[int]:
    return (x for x in xs if x % 2 == 0)


def squared(xs: Iterable[int]) -> Iterator[int]:
    for x in xs:
        yield x * x


print(list(squared(evens(numbers(10)))))        # [0, 4, 16, 36, 64]

# Memory: a list of a million ints vs a generator
big_list = [x for x in range(1_000_000)]
big_gen = (x for x in range(1_000_000))
import sys                                      # noqa: E402 (imported here for the demo)
print(sys.getsizeof(big_list), "bytes vs", sys.getsizeof(big_gen), "bytes")


# --- itertools -------------------------------------------------------------------
print(list(itertools.batched("ABCDEFG", 3)))     # [('A','B','C'), ('D','E','F'), ('G',)]
print(list(itertools.chain([1, 2], (3, 4))))
print(list(itertools.pairwise([1, 4, 9, 16])))   # differences come next:
print([b - a for a, b in itertools.pairwise([1, 4, 9, 16])])
print(list(itertools.accumulate([5, 10, 20])))
words = sorted(["apple", "avocado", "banana", "blueberry", "cherry"])
for letter, group in itertools.groupby(words, key=lambda w: w[0]):
    print(letter, list(group))
print(list(itertools.product("ab", [1, 2])))     # nested loops
print(list(itertools.combinations("abc", 2)))


# --- Decorators -------------------------------------------------------------------
def timed(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"  ⏱ {fn.__name__} took {(time.perf_counter() - start) * 1000:.2f} ms")
    return wrapper


@timed
def slow_sum(n: int) -> int:
    """Sum 0..n-1."""
    return sum(range(n))


print(slow_sum(2_000_000))
print(slow_sum.__name__, slow_sum.__doc__)      # preserved thanks to functools.wraps


def repeat(times: int):                          # decorator factory (decorator with arguments)
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return [fn(*args, **kwargs) for _ in range(times)]
        return wrapper
    return decorator


@repeat(times=3)
def roll() -> str:
    return "🎲"


print(roll())


def log_calls(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        params = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
        result = fn(*args, **kwargs)
        print(f"  {fn.__name__}({', '.join(params)}) → {result!r}")
        return result
    return wrapper


@log_calls
@timed                                            # stacking: applied bottom-up → log_calls(timed(add))
def add(a: int, b: int = 0) -> int:
    return a + b


add(2, b=3)


@functools.cache                                  # memoization in one line
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print(fib(100), fib.cache_info())                 # instant; without the cache it would never finish


# --- @contextmanager ---------------------------------------------------------------------
@contextmanager
def section(title: str):
    print(f"┌─ {title}")
    try:
        yield title.upper()                       # value bound by `as`
    finally:
        print(f"└─ end {title}")


with section("report") as heading:
    print("│ heading is", heading)
