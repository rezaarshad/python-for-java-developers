"""A small module to demo pytest features."""

from collections.abc import Callable
from datetime import datetime


def add(a: float, b: float) -> float:
    return a + b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("division by zero is not allowed")
    return a / b


class History:
    def __init__(self, clock: Callable[[], datetime] = datetime.now) -> None:
        self._clock = clock              # injected clock → deterministic tests
        self.entries: list[tuple[datetime, str]] = []

    def record(self, expression: str) -> None:
        self.entries.append((self._clock(), expression))


def describe(value: float, formatter) -> str:
    """`formatter` is anything with a .format(value) method (duck typing)."""
    return f"Result: {formatter.format(value)}"
