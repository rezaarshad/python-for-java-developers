# Lesson 04: Classes the Pythonic Way

Python has classes, inheritance, and interfaces (sort of), but idiomatic Python uses them **less**
than Java does. Rules of thumb:
- Data holder → `@dataclass` (≈ Java `record`, or Lombok `@Data`)
- Behaviour with no state → plain module-level functions, not a `Utils` class
- Interface → `Protocol` (structural typing, "duck typing with type checking")

## 1. A plain class

```java
public class Account {
    private final String owner;
    private double balance;
    public Account(String owner) { this.owner = owner; }
    public void deposit(double amt) { balance += amt; }
}
```

```python
class Account:
    interest_rate = 0.02                    # class attribute (≈ static field)

    def __init__(self, owner: str) -> None: # constructor; `self` is explicit (≈ this)
        self.owner = owner                  # instance attributes are created by assignment
        self._balance = 0.0                 # leading underscore = "private by convention"

    def deposit(self, amount: float) -> None:
        self._balance += amount
```

- No `new`: `acct = Account("Reza")`.
- No access modifiers. `_name` means "internal, don't touch"; `__name` triggers name mangling (rarely needed).
- No overloaded constructors; use default arguments or `@classmethod` factories.

## 2. Properties instead of getters/setters

Start with plain public attributes. If you later need logic, switch to a property, and **callers don't change**:

```python
class Account:
    @property
    def balance(self) -> float:             # acct.balance, no parentheses
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        if value < 0:
            raise ValueError("balance can't be negative")
        self._balance = value
```

## 3. Dunder ("double underscore") methods = operator overloading + interfaces

| Method                  | Triggered by            | Java equivalent                 |
|-------------------------|-------------------------|---------------------------------|
| `__init__`              | `Account(...)`          | constructor                     |
| `__repr__`              | `repr(x)`, debugger, REPL | `toString()` (for developers) |
| `__str__`               | `str(x)`, `print(x)`    | `toString()` (for users)        |
| `__eq__`, `__hash__`    | `==`, dict keys, sets   | `equals`, `hashCode`            |
| `__lt__`, `__le__` …    | `<`, `sorted()`         | `Comparable.compareTo`          |
| `__len__`               | `len(x)`                | `size()`                        |
| `__iter__`              | `for item in x`         | `Iterable`                      |
| `__contains__`          | `item in x`             | `contains()`                    |
| `__getitem__`           | `x[key]`                | `get()`                         |
| `__add__`               | `x + y`                 | (no operator overloading)       |
| `__enter__`/`__exit__`  | `with x:`               | `AutoCloseable` (Lesson 06)     |
| `__call__`              | `x()`                   | functional interface            |

Implement the dunders and your class plugs into the language: `len()`, `for`, `in`, `sorted`.

## 4. `@dataclass`: your new best friend

```python
from dataclasses import dataclass, field

@dataclass
class Note:
    title: str
    body: str = ""
    tags: set[str] = field(default_factory=set)   # mutable default → default_factory (Lesson 03 trap!)
```

You get `__init__`, `__repr__`, and `__eq__` for free. Options:
- `@dataclass(frozen=True)`: immutable (≈ `record`), and hashable, so it can be a dict key
- `@dataclass(order=True)`: generates `<`, `>` and friends, comparing fields in order
- `@dataclass(slots=True)`: less memory, faster attribute access
- `__post_init__(self)`: validation/normalisation after the generated `__init__`

## 5. Inheritance, `super()`, abstract classes

```python
from abc import ABC, abstractmethod

class Exporter(ABC):
    @abstractmethod
    def export(self, note: Note) -> str: ...

class MarkdownExporter(Exporter):
    def export(self, note: Note) -> str:
        return f"# {note.title}\n\n{note.body}"
```

Python supports multiple inheritance (with a defined method resolution order), but prefer
composition. `super().__init__(...)` calls the parent constructor.

## 6. Protocols: interfaces without `implements`

```python
from typing import Protocol

class Exporter(Protocol):
    def export(self, note: Note) -> str: ...

class HtmlExporter:                 # does NOT inherit anything
    def export(self, note: Note) -> str:
        return f"<h1>{note.title}</h1>"

def save(exporter: Exporter, note: Note): ...
save(HtmlExporter(), note)          # type checker accepts it: the shape matches
```

This is "duck typing": if it has `export()`, it's an Exporter. Protocols let mypy check it statically.

## 7. `@classmethod`, `@staticmethod`, `Enum`

```python
from enum import Enum

class Priority(Enum):
    LOW = 1
    HIGH = 3

class Note:
    @classmethod
    def from_dict(cls, data: dict) -> "Note":   # alternative constructor (factory)
        return cls(**data)

    @staticmethod
    def slugify(text: str) -> str:              # utility namespaced on the class
        return text.lower().replace(" ", "-")

Priority.HIGH.name, Priority.HIGH.value, Priority(3)    # 'HIGH', 3, Priority.HIGH
```

## 8. Run the examples

```bash
uv run python lessons/04_classes/classes_demo.py
```

## 9. Exercise: notes models

Replace the notes app's raw dicts with real types: a `Note` dataclass, a `Priority` enum, and a
`NoteStore` class that works with `len()`, `in`, `for`, and `[]`. Run `exercise.py` until it prints `All checks passed ✅`.
