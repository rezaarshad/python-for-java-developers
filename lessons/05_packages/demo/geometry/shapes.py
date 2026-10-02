import math
from dataclasses import dataclass


@dataclass
class Circle:
    radius: float

    def area(self) -> float:
        return math.pi * self.radius ** 2


@dataclass
class Rectangle:
    width: float
    height: float

    def area(self) -> float:
        return self.width * self.height
