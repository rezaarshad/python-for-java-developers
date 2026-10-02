from collections.abc import Iterable

from .shapes import Circle, Rectangle   # relative import within the package


def total_area(shapes: Iterable[Circle | Rectangle]) -> float:
    return sum(s.area() for s in shapes)
