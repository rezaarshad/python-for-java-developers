"""Lesson 04: classes, dataclasses, dunders, protocols.

Run: uv run python lessons/04_classes/classes_demo.py
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


# --- Plain class with a property --------------------------------------------
class Account:
    interest_rate = 0.02                     # class attribute, shared by all instances

    def __init__(self, owner: str, balance: float = 0.0) -> None:
        self.owner = owner
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        if value < 0:
            raise ValueError("balance can't be negative")
        self._balance = value

    def deposit(self, amount: float) -> None:
        self.balance += amount               # goes through the setter

    def __repr__(self) -> str:               # toString() for developers
        return f"Account(owner={self.owner!r}, balance={self._balance})"


acct = Account("Reza")
acct.deposit(100)
print(acct, acct.balance, Account.interest_rate)
try:
    acct.balance = -5
except ValueError as e:
    print("rejected:", e)


# --- Dataclass ≈ record -------------------------------------------------------
@dataclass
class Point:
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:   # quotes: the class isn't fully defined yet
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def __add__(self, other: "Point") -> "Point":     # operator overloading
        return Point(self.x + other.x, self.y + other.y)


p1, p2 = Point(0, 0), Point(3, 4)
print(p1, p2, p1.distance_to(p2))   # free __repr__
print(p1 == Point(0, 0))            # free __eq__ (value equality)
print(p1 + p2)


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int = 0
    patch: int = 0

    @classmethod
    def parse(cls, text: str) -> "Version":           # alternative constructor
        return cls(*(int(part) for part in text.split(".")))

    def __str__(self) -> str:                          # for users (print)
        return f"{self.major}.{self.minor}.{self.patch}"


versions = [Version.parse(v) for v in ["1.10.0", "1.2.3", "0.9"]]
print(sorted(versions))                  # order=True compares (major, minor, patch)
print(max(versions), {Version(1): "hashable because frozen"})


@dataclass
class Tagged:
    name: str
    tags: list[str] = field(default_factory=list)   # never `= []`

    def __post_init__(self) -> None:                 # runs after generated __init__
        self.name = self.name.strip()
        self.tags = [t.lower() for t in self.tags]


print(Tagged("  Reza ", ["Java", "Python"]))


# --- Making a class feel built-in -------------------------------------------
class Playlist:
    def __init__(self, *songs: str) -> None:
        self._songs = list(songs)

    def __len__(self) -> int:
        return len(self._songs)

    def __iter__(self):
        return iter(self._songs)

    def __contains__(self, song: str) -> bool:
        return song in self._songs

    def __getitem__(self, index: int) -> str:
        return self._songs[index]


pl = Playlist("Intro", "Main", "Outro")
print(len(pl), "Main" in pl, pl[0], pl[-1], list(pl))
for song in pl:
    print("♪", song)


# --- ABC vs Protocol ----------------------------------------------------------
class Shape(ABC):                         # nominal: subclasses must inherit
    @abstractmethod
    def area(self) -> float: ...

    def describe(self) -> str:            # concrete method shared by subclasses
        return f"{type(self).__name__} with area {self.area():.2f}"


class Circle(Shape):
    def __init__(self, r: float) -> None:
        self.r = r

    def area(self) -> float:
        return 3.14159 * self.r ** 2


class Square(Shape):
    def __init__(self, side: float) -> None:
        self.side = side

    def area(self) -> float:
        return self.side ** 2


for s in [Circle(1), Square(2)]:
    print(s.describe())
# Shape()  → TypeError: can't instantiate abstract class


class Greeter(Protocol):                  # structural: no inheritance required
    def greet(self, name: str) -> str: ...


class English:
    def greet(self, name: str) -> str:
        return f"Hello {name}"


class Persian:
    def greet(self, name: str) -> str:
        return f"Salam {name}"


def welcome(greeter: Greeter, name: str) -> None:
    print(greeter.greet(name))


welcome(English(), "Reza")
welcome(Persian(), "Reza")


# --- Enum ---------------------------------------------------------------------
class Status(Enum):
    TODO = "todo"
    DONE = "done"


print(Status.DONE, Status.DONE.value, Status("todo"), [s.name for s in Status])


# --- Inheritance & super() ---------------------------------------------------------
class SavingsAccount(Account):
    interest_rate = 0.05                  # override class attribute

    def __init__(self, owner: str, balance: float = 0.0, locked: bool = False) -> None:
        super().__init__(owner, balance)
        self.locked = locked

    def deposit(self, amount: float) -> None:
        if self.locked:
            raise RuntimeError("account locked")
        super().deposit(amount)


sav = SavingsAccount("Reza", 50)
sav.deposit(25)
print(sav, sav.interest_rate, isinstance(sav, Account))
