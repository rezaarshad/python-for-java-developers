"""Lesson 03: functions for Java developers.

Run: uv run python lessons/03_functions/functions_demo.py
"""

from collections.abc import Callable


# --- Defaults & keyword args replace overloading ----------------------------
def greet(name: str, greeting: str = "Hello", punctuation: str = "!") -> str:
    """Return a greeting. Java would need 3 overloads for this."""
    return f"{greeting}, {name}{punctuation}"


print(greet("Reza"))
print(greet("Reza", "Hi"))
print(greet("Reza", punctuation="?"))      # skip the middle parameter by name


# --- Keyword-only parameters (after a bare *) -------------------------------
def connect(host: str, *, timeout: float = 5.0, verbose: bool = False) -> str:
    return f"connect({host}, timeout={timeout}, verbose={verbose})"


print(connect("db.local", verbose=True))   # call sites read like named parameters
# connect("db.local", 1.0, True)           # TypeError: no "what does True mean?" calls


# --- *args and **kwargs -------------------------------------------------------
def total(*numbers: float) -> float:         # numbers is a tuple
    return sum(numbers)


def describe(**fields: object) -> str:     # fields is a dict
    return ", ".join(f"{k}={v!r}" for k, v in fields.items())   # !r → repr(), quotes strings


print(total(1, 2, 3.5))
print(describe(name="Reza", years=10))

values = [4, 5, 6]
print(total(*values))                      # unpack list into positional args
settings = {"timeout": 1.0, "verbose": True}
print(connect("db", **settings))           # unpack dict into keyword args


# --- Mutable default trap -----------------------------------------------------
def bad_append(item: str, items: list[str] = []) -> list[str]:   # noqa: B006 (deliberate bug)
    items.append(item)
    return items


print(bad_append("a"), bad_append("b"))    # ['a', 'b'] ['a', 'b']: same list, shared!


def good_append(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items


print(good_append("a"), good_append("b"))  # ['a'] ['b']


# --- Functions as values -----------------------------------------------------
def shout(s: str) -> str:
    return s.upper() + "!"


def whisper(s: str) -> str:
    return s.lower() + "..."


styles: dict[str, Callable[[str], str]] = {"shout": shout, "whisper": whisper}   # strategy pattern, no interfaces
for style_name, style in styles.items():
    print(style_name, "→", style("Hello"))


def apply_twice(fn: Callable[[int], int], x: int) -> int:
    return fn(fn(x))


print(apply_twice(lambda n: n * 3, 2))     # 18


# --- Closures --------------------------------------------------------------------
def make_counter(start: int = 0) -> Callable[[], int]:
    count = start

    def increment() -> int:
        nonlocal count
        count += 1
        return count

    return increment


counter = make_counter()
print(counter(), counter(), counter())    # 1 2 3
other = make_counter(100)
print(other(), counter())                 # 101 4: each closure has its own state


def make_multiplier(n: int) -> Callable[[int], int]:
    return lambda x: x * n


double, triple = make_multiplier(2), make_multiplier(3)
print(double(21), triple(7))


# --- Late binding gotcha in closures -----------------------------------------
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])               # [2, 2, 2]: closures capture the variable, not the value
funcs = [lambda i=i: i for i in range(3)]  # fix: bind the current value as a default
print([f() for f in funcs])               # [0, 1, 2]


# --- Recursion, docstrings, help() ---------------------------------------------
def factorial(n: int) -> int:
    """Return n! (Python ints never overflow, so factorial(100) is fine)."""
    return 1 if n <= 1 else n * factorial(n - 1)


print(factorial(25))
print(factorial.__doc__)
print(factorial.__name__, type(factorial))
