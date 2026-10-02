"""Runs on `python -m geometry`."""

from . import Circle, Rectangle, __version__, total_area

print(f"geometry {__version__}: demo total area = {total_area([Circle(1), Rectangle(2, 3)]):.2f}")
