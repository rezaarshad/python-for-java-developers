"""Run from this folder: uv run python app.py"""

import sys

import geometry                              # runs geometry/__init__.py
import geometry                              # cached in sys.modules, so nothing prints the second time
from geometry import Circle, Rectangle, total_area
from geometry.shapes import Circle as SameCircle

print(geometry.__version__, geometry.__all__)
print(Circle is SameCircle)                  # True: re-exported, same object
print(f"{total_area([Circle(1), Rectangle(2, 3)]):.2f}")
print("geometry" in sys.modules, sys.path[0])  # sys.path[0] = this script's folder
