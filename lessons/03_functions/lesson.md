# Lesson 03: Functions

Python functions are **first-class objects**: you can store them in variables, pass them around, and
return them from other functions, with no `Function<T, R>` interfaces needed. Overloading is replaced by
**default and keyword arguments**.

## 1. Anatomy

```python
def greet(name: str, greeting: str = "Hello") -> str:
    """Docstring: what it does (shown by help(greet) and your IDE)."""
    return f"{greeting}, {name}!"

greet("Reza")                    # positional
greet("Reza", greeting="Hi")     # keyword argument: order-independent, self-documenting
greet(greeting="Hi", name="Reza")
```

A function with no `return` returns `None` (like `void`, but it's a real value).

## 2. Parameter kinds

```python
def f(a, b=2, *args, c, d=4, **kwargs): ...
#     │  │     │      │  │     └─ extra keyword args → dict
#     │  │     │      └──┴─ keyword-only (after *args or a bare *)
#     │  │     └─ extra positional args → tuple   (≈ Java varargs String... args)
#     └──┴─ positional-or-keyword
```

```python
def connect(host: str, *, timeout: float = 5.0, retries: int = 3): ...
connect("db", timeout=1)        # OK
connect("db", 1)                # TypeError: the bare * forces keyword use → no "boolean trap"

def total(*numbers: int) -> int:
    return sum(numbers)
total(1, 2, 3)

def tag(**attrs: str) -> str:
    return " ".join(f'{k}="{v}"' for k, v in attrs.items())
tag(id="main", cls="big")
```

The `*` and `**` also **unpack** at the call site:

```python
args = [1, 2, 3]
total(*args)                    # total(1, 2, 3)
opts = {"timeout": 1, "retries": 0}
connect("db", **opts)           # connect("db", timeout=1, retries=0)
```

## 3. The mutable-default trap ⚠️

Defaults are evaluated **once**, when the function is defined, not on each call:

```python
def add_item(item, items=[]):      # BUG: one shared list for every call
    items.append(item)
    return items

add_item("a")   # ['a']
add_item("b")   # ['a', 'b']  😱

def add_item(item, items: list | None = None):   # the idiom
    if items is None:
        items = []
    items.append(item)
    return items
```

## 4. Type hints

```python
from collections.abc import Callable, Iterable

def apply(fn: Callable[[int], int], values: Iterable[int]) -> list[int]: ...
def find(name: str) -> User | None: ...        # Optional<User>; None if not found
type Predicate = Callable[[dict], bool]         # type alias (Python 3.12+)
```

Hints are **not enforced at runtime**. Tools like `mypy` (Lesson 16) and your IDE check them.
In practice, treat them like Java types: annotate every public function.

## 5. Functions are values

```python
def shout(s: str) -> str:
    return s.upper()

f = shout                     # no parentheses: the function object itself
f("hi")                       # 'HI'
list(map(shout, ["a", "b"]))  # ['A', 'B']  (comprehensions are usually clearer)

square = lambda x: x * x      # lambda = single-expression anonymous function
sorted(words, key=lambda w: (len(w), w))
```

Lambdas can only hold one expression. For anything more, write a named function. Don't assign
lambdas to names in real code (`def` is clearer); it's shown above just for illustration.

## 6. Closures & scope

A nested function captures variables from its enclosing scope, like a Java lambda capturing an
effectively-final local, except Python lets you **reassign** it with `nonlocal`:

```python
def make_counter():
    count = 0
    def increment() -> int:
        nonlocal count        # without this, `count += 1` would raise UnboundLocalError
        count += 1
        return count
    return increment

c = make_counter()
c(), c(), c()   # 1, 2, 3
```

Scope rule (LEGB): **L**ocal → **E**nclosing → **G**lobal (module) → **B**uilt-in.
`global x` exists, but if you need it, you probably want a class instead.

## 7. Functions returning functions (factories)

```python
def make_multiplier(n: int) -> Callable[[int], int]:
    return lambda x: x * n

double = make_multiplier(2)
double(21)   # 42
```

This pattern underlies decorators (Lesson 07).

## 8. Run the example

```bash
uv run python lessons/03_functions/functions_demo.py
```

## 9. Exercise: notes query helpers

`exercise.py` gives the notes app a small query toolkit built from functions: predicates,
combinators, and a closure-based id generator. Run it until it prints `All checks passed ✅`.
